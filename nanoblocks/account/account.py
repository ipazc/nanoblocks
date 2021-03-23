import pandas as pd

from datetime import datetime

from nanoblocks.account.payment.payment import Payment
from nanoblocks.block.block_factory import BlockFactory
from nanoblocks.block.block_state import BlockState
from nanoblocks.currency import Amount
from nanoblocks.exceptions.block_not_broadcastable_error import BlockNotBroadcastableError
from nanoblocks.exceptions.insufficient_funds import InsufficientFunds
from nanoblocks.exceptions.node_backend_required_error import NodeBackendRequiredError
from nanoblocks.exceptions.work_error import WorkError
from nanoblocks.node.nanonode import NO_NODE
from nanoblocks.protocol.crypto import address_pubkey, account_pubkey, account_address, hash_block, sign_block
from nanoblocks.protocol.messages import NetworkMessages
from nanoblocks.protocol.messages.account_messages import AccountMessages


class Accounts:
    """
    Handles the account interaction through the node API
    """

    def __init__(self, node_backend=NO_NODE, work_server=None):
        """
        Constructor of the class

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the retrieval of public keys.

        :param work_server:
            Work server object to process work automatically. Optional.
        """
        self._node_backend = node_backend
        self._work_server = work_server

    def __getitem__(self, nano_account_address):
        """
        Retrieves nanoblocks accounts from the network, given the nanoblocks address.

        It may be provided a single string of the nanoblocks account or a list of many nanoblocks accounts. If a list is provided,
        the result information of the accounts might be stripped to the minimal supported by bulk operations in the
        backend. For instance, the last modification and the representative properties are not retrieved.

        :param nano_account_address:
            Address of the account. Eg "nano_..."
                or
            A list of addresses. Eg ["nano_account1", "nano_account2", ...]
        """
        if type(nano_account_address) is list:
            # Bulk retrieval of accounts. We take minimum information for each account
            accounts = {address: Account(address, node_backend=self._node_backend,
                                         default_work_server=self._work_server,
                                         initial_update=False) for address in nano_account_address}

            if self._node_backend.is_online:
                balances = self._node_backend.ask(AccountMessages.ACCOUNTS_BALANCES(nano_account_address))['balances']
                frontiers = self._node_backend.ask(AccountMessages.ACCOUNTS_FRONTIERS(nano_account_address))['frontiers']

                for nano_address in nano_account_address:
                    nano_account = accounts[nano_address]
                    nano_balances = balances[nano_address]
                    nano_frontier = frontiers[nano_address]

                    nano_account.offline_update({
                        'balance': nano_balances['balance'],
                        'pending': nano_balances['pending'],
                        'frontier': nano_frontier,
                        'block_count': 'unknown',
                        'modified_timestamp': 0
                    })

            result = accounts
        else:
            result = Account(nano_account_address, node_backend=self._node_backend,
                             default_work_server=self._work_server)

        return result

    def __len__(self):
        """
        Returns the number of accounts registered in the network, in case the backend is available.
        """
        response = self._node_backend.ask(NetworkMessages.TELEMETRY())

        if not response:
            response = {'account_count': 0}

        return int(response['account_count'])

    def __str__(self):
        return f"{str(self._node_backend)} Total accounts: {len(self)}"

    def from_private_key(self, account_privatekey):
        """
        Retrieves a nanoblocks account given the private key.
        Note that this account is fully controllable, since it can sign transactions.

        :param account_privatekey:
            Private key of the account (string of 64 values in hexadecimal)
        """
        return Account.from_priv_key(account_privatekey, node_backend=self._node_backend,
                                     default_work_server=self._work_server)


class Account:
    """
    Handles a single account in the Nano network.

    Contains all the methods that allows to interact with accounts, like reading the state, sending/receiving amounts or
    reading the blockchain of the account.

    By default every account is read-only, unless a private key is available.

    :param nano_address:
        Nano address of the account. E.g "nano_3pyz..".

    :param node_backend:
        A Node object pointing to a working Nano node.
        Note that this class may work off-line, which allows the retrieval of public keys.

    :param initial_update:
        Flag to determine if the account should be updated at start or not.

    :param default_work_server:
        The default work_server to use in case no work is provided.
    """

    def __init__(self, nano_address, node_backend=NO_NODE, initial_update=True, default_work_server=None):
        """

        :param nano_address:
            Nano address of the account. E.g "nano_3pyz...".

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the retrieval of public keys.

        :param initial_update:
            Flag to determine if the account should be updated at start or not.

        :param default_work_server:
            The default work_server to use in case no work is provided.
        """

        self._nano_address = nano_address
        self._node_backend = node_backend
        self._public_key = address_pubkey(nano_address)  # If the address is not valid -> Exception raised here
        self._private_key = None
        self._account_info = {}
        self._work_server = default_work_server
        self._pending_transactions_history = AccountPendingHistory(self, self._node_backend,
                                                                   work_server=self._work_server)
        self.update(initial_update)

    @classmethod
    def from_priv_key(cls, private_key, node_backend=NO_NODE, default_work_server=None):
        """
        Tries to access an account from the specified private key.

        No addresses or public keys are required, as they can be derived from the private key itself.

        :param private_key:
            private key to derive the account from.

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the retrieval of public keys.

        :param default_work_server:
            Default work server object to generate work automatically. Optional.
        """
        public_key = account_pubkey(private_key)
        account = cls.from_pub_key(public_key, node_backend=node_backend, default_work_server=default_work_server)
        account._private_key = private_key
        return account

    @classmethod
    def from_pub_key(cls, pub_key, node_backend=NO_NODE, default_work_server=None):
        """
        Gives access to the specified account by its public key.

        This method is read-only unless the account is `unlocked()` with the private key.

        :param pub_key:
            Public key for the nanoblocks account.

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the retrieval of public keys/addresses.

        :param default_work_server:
            Default work server object to generate work automatically. Optional.
        """
        nano_address = account_address(pub_key)
        account = cls(nano_address, node_backend=node_backend, default_work_server=default_work_server)
        return account

    @property
    def unlocked(self):
        """
        Retrieves whether this account is unlocked with the private key or not.
        """
        return self._private_key is not None

    def unlock(self, private_key):
        """
        Tries to unlock this account with the given private key.

        If the specified private key does not derive the public key of the account, an exception is raised.

        Note that a private key that does not belong to the account's public key can't be used to sign the blocks, as
        the network is going to reject them.

        :param private_key:
            String hexadecimal representing the private key of the account.
        """
        public_key = account_pubkey(private_key)

        if public_key != self._public_key:
            raise KeyError("The provided private key does not unlock this account")

        self._private_key = private_key

    @property
    def address(self):
        """
        Provides the account nanoblocks address of this account. E.g. "nano_3pyz..."
        """
        return self._nano_address

    @property
    def public_key(self):
        """
        Provides the public key of this account.
        """
        return self._public_key

    @property
    def private_key(self):
        """
        Provides the private key of this account, if unlocked.
        """
        return self._private_key

    @property
    def frontier(self):
        """
        Provides the frontier block hash for this account.
        In case of a new account, this frontier is 0.
        """

        if self._node_backend.is_online:
            from nanoblocks.block import Blocks
            blocks = Blocks(node_backend=self._node_backend, work_server=self._work_server)
            frontier_block = blocks[self._account_info['frontier']]

        else:
            from nanoblocks.block import Block
            frontier_block = Block(self, {'type': 'Unknown', 'balance': 'Unknown', 'hash': self._account_info['frontier']}, node_backend=self._node_backend,
                                   work_server=self._work_server)

        return frontier_block

    @property
    def info(self):
        """
        Retrieves the cached account information.
        Note: a call to `update()` before `account_info()` is highly encouraged!!
        """
        return dict(self._account_info)

    def update(self, query_node=True):
        """
        Retrieves the account information from the node (if available) and caches it inside the object.
        """
        if self._node_backend.is_online and query_node:
            account_info = self._node_backend.ask(AccountMessages.ACCOUNT_INFO(self._nano_address, representative=True,
                                                                               weight=True, pending=True))
        else:
            account_info = {"error": "Account not found"}

        if account_info.get("error", None) == 'Account not found':
            public_key = self.public_key

            account_info = {
                'frontier': "0".zfill(64),
                'block_count': 0,
                'representative': public_key,
                'weight': 0,
                'status': 'virtual',
                'balance': 0,
                'pending': 0,
                'modified_timestamp': datetime.now().timestamp()
            }

        self._account_info = account_info

    def offline_update(self, account_info):
        """
        Performs an offline update with the given account_info.
        This method does not interact with a node and can be executed offline to update the information of an account
        object given (for example, taking this info from a local json file).

        :param account_info:
            Dictionary containing information of the account (frontier, block_count, representative, weight, status,
            balance, pending, modified_timestamp, ...).
        """
        self._account_info.update(account_info)

    def offline_update_by_block(self, block_state):
        """
        Updates the account with the provided block state.

        The block state must be crafted for the current account.

        :param block_state:
            BlockState object signed, with work.
        """

        if not block_state.broadcastable:
            raise BlockNotBroadcastableError("The provided block must be signed and complemented with a work hash.")

        if block_state.account.address != self.address:
            raise KeyError("The block account does not match this account, can't be offline broadcasted.")

        # 1. Hash of the block is the new frontier of the account
        self._account_info['frontier'] = block_state.hash

        # 2. Representative of the account
        self._account_info['representative'] = block_state.representative

        # 3. Confirmed balance of the account
        pending_balance_consumed = min(self.confirmed_balance - block_state.balance, 0)
        self._account_info['balance'] = block_state.balance.as_raw().int_str()
        self._account_info['pending'] = (self.pending_balance + pending_balance_consumed).as_raw().int_str()

        if self._account_info['block_count'] != "Unknown":
            self._account_info['block_count'] = int(self._account_info['block_count']) + 1

    @property
    def confirmed_balance(self):
        """
        Provides the confirmed balance for this account.

        Note: a call to `update()` or `offline_update()` before `confirmed_balance` is highly encouraged!!
        """
        return Amount(self._account_info['balance'])

    @property
    def pending_balance(self):
        """
        Provides the pending balance for this account.

        Note: a call to `update()` or `offline_update()` before `pending_balance` is highly encouraged!!
        """
        return Amount(self._account_info['pending'])

    @property
    def pending_transactions(self):
        """
        Retrieves the pending transactions for the account.
        """
        # if node is online, we refresh the transactions list
        if self._node_backend.is_online:
            self._pending_transactions_history.update()

        return self._pending_transactions_history

    @property
    def balance(self):
        """
        Provides the total balance for this account.

        Note: a call to `update()` or `offline_update()` before `balance` is highly encouraged!!

        """
        return self.confirmed_balance + self.pending_balance

    @property
    def modified_date(self):
        """
        Provides the last modified date for this account.

        Note: a call to `update()` or `offline_update()` before `modified_date` is highly encouraged!!
        """
        m_datetime = pd.to_datetime(
            pd.Timestamp(int(self._account_info['modified_timestamp']) * 1000000000).to_pydatetime()).tz_localize(
            "UTC").tz_convert(self._node_backend.timezone)

        return m_datetime

    @property
    def block_count(self):
        """
        Provides the number of block counts for this account.

        Note: a call to `update()` or `offline_update()` before `block_count` is highly encouraged!!
        """
        return self._account_info['block_count']

    def request_payment(self, nano_units_amount):
        """
        Generates the payment object which contains payment handle for the given amount

        :param nano_units_amount:
            Amount of NANO.
            If a different unit measure is required, wrap it into an `Amount()` class.
        """
        if type(nano_units_amount) is not Amount:
            nano_units_amount = Amount.from_NANO(str(nano_units_amount))

        payment = Payment(self, nano_units_amount, node_backend=self._node_backend, work_server=self._work_server)
        return payment

    @property
    def is_virtual(self):
        """
        Retrieves whether this account exists or not in the network.

        A new account does not exist until a "receive" block is emitted in its blockchain.
        """
        return self._account_info.get('status', 'real') == 'virtual'

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.address} (\n\t" \
               f"Total blocks: {self.block_count}\n\t" \
               f"Total balance: {str(self.balance)}\n\t" \
               f"Confirmed balance: {str(self.confirmed_balance)}\n\t" \
               f"Pending balance: {str(self.pending_balance)}\n\t" \
               f"Last confirmed payment: {self.modified_date}\n\t" \
               f"Is virtual: {self.is_virtual}\n)"

    @property
    def representative(self):
        """
        Provides the representative for this account.

        Note: a call to `update()` or `offline_update()` before `representative` is highly encouraged!!
        """
        representative = self._account_info['representative']
        return Account(representative, node_backend=self._node_backend, default_work_server=self._work_server)

    @property
    def weight(self):
        """
        Provides the weight for this account.

        Note: a call to `update()` or `offline_update()` before `weight` is highly encouraged!!
        """
        weight = self._account_info['weight']
        return int(weight)

    @property
    def history(self):
        return AccountHistory(self, node_backend=self._node_backend, work_server=self._work_server)

    def fill_account_info(self, account_info):
        """
        Fills the internal account info cached data.
        This is useful if signing is required and no node is available to query (e.g. under offline computers).

        When an account info is filled within the account object, you are then able to send or receive blocks

        .. code-block:: python

            account_info_example = {
                "frontier": "FF84533A571D953A596EA401FD41743AC85D04F406E76FDE4408EAED50B473C5",
                "open_block": "991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948",
                "representative_block": "991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948",
                "balance": "235580100176034320859259343606608761791",
                "modified_timestamp": "1501793775",
                "block_count": "33",
                "confirmation_height" : "28",
                "confirmation_height_frontier" : "34C70FCA0952E29ADC7BEE6F20381466AE42BD1CFBA4B7DFFE8BD69DF95449EB",
                "account_version": "1"
            }
        """
        self._account_info = account_info

    def build_send_block(self, account_target, nano_amount, work_hash=None):
        """
        Builds and signs the send transaction block and returns it.

        Note that this method does not broadcast the block, but returns it wrapped in a :class:`nanoblocks.block.BlockSend` class.

        The returned block object can be broadcasted using the method :meth:`~nanoblocks.block.Blocks.broadcast`
        from the property :attr:`~nanoblocks.network.NanoNetwork.blocks` of the class :class:`nanoblocks.network.NanoNetwork`.

        :param account_target:
            Account target for the send. It can be either an Account object or a string with the public address.

        :param nano_amount:
            Amount of nanoblocks to send. It can be an Amount() object or an amount in "Nano" units.

        :param work_hash:
            Hash result of work for this transaction. A WorkServer can be used to build the hash for an account.
            If None, it will try to use a local work server.

        :returns:
            Returns the send block, signed, ready to broadcast to the network.
        """
        if self._private_key is None:
            raise KeyError("No private key available for this account. Can't send valid blocks.")

        if type(nano_amount) is not Amount:
            nano_amount = Amount.from_NANO(str(nano_amount))

        if type(account_target) is str:
            account_target = Account(account_target, node_backend=self._node_backend, default_work_server=self._work_server)

        block_final_balance = (self.confirmed_balance - nano_amount)

        if block_final_balance < 0:
            raise InsufficientFunds(f"Account {self.address} doesn't have enough funds ({self.confirmed_balance}) "
                                    f"to send the requested quantity ({nano_amount}).")

        if work_hash is None:

            if self._work_server is None:
                raise WorkError("No work provided for the transaction.")

            work_hash = self._work_server.generate_work_send(self)

        block_state = self._craft_block_state(subtype="send", link=account_target.public_key,
                                              balance=block_final_balance, representative=self.representative,
                                              work_hash=work_hash)

        return block_state

    def build_receive_block(self, pending_block, work_hash=None):
        """
        Builds and signs the receive transaction block for the specified pending block and returns it.

        Note that this method does not broadcast the block, but returns it wrapped in a :class:`nanoblocks.block.BlockReceive` class.

        The returned block object can be broadcasted using the method :meth:`~nanoblocks.block.Blocks.broadcast`
        from the property :attr:`~nanoblocks.network.NanoNetwork.blocks` of the class :class:`nanoblocks.network.NanoNetwork`.

        A pending block can be obtained by iterating over the :attr:`~nanoblocks.account.Account.pending_transactions` property
        of the class :class:`nanoblocks.account.Account`.

        :param pending_block:
            Pending block to receive from.

        :param work_hash:
            work hash for the receive transaction.
        """

        if self._private_key is None:
            raise KeyError("No private key available for this account. Can't send valid blocks.")

        if work_hash is None:

            if self._work_server is None:
                raise WorkError("No work provided for the transaction.")

            work_hash = self._work_server.generate_work_receive(self)

        if pending_block.destination_account.address != self.address:
            raise KeyError("The block target does not belong to this account")

        send_block_hash = pending_block.hash
        block_amount = pending_block.amount

        block_final_balance = (self.confirmed_balance + block_amount)

        block_state = self._craft_block_state(subtype="receive", link=send_block_hash, balance=block_final_balance,
                                              representative=self.representative, work_hash=work_hash)

        return block_state

    def build_change_representative_block(self, new_representative, work_hash):
        """
        Build the state block for changing the representative for this account and returns it.

        :param new_representative:
            Account or string for the new representative

        :param work_hash:
            Work hash for changing the representative. If no work_hash is provided, the change will be local and not
            propagated through the nodes.
        """

        if self._private_key is None:
            raise KeyError("No private key available for this account. Can't send valid blocks.")

        if work_hash is None:

            if self._work_server is None:
                raise WorkError("No work provided for the transaction.")

            work_hash = self._work_server.generate_work_change(self)

        if type(new_representative) is str:
            new_representative = Account(new_representative, node_backend=self._node_backend, default_work_server=self._work_server, initial_update=False)

        block_state = self._craft_block_state(subtype="change", link="0"*64, balance=self.confirmed_balance,
                                              representative=new_representative, work_hash=work_hash)

        return block_state

    def _craft_block_state(self, subtype, link, balance, representative, work_hash):
        """
        Crafts the state block given the block parameters and signs it.
        """
        # We setup the block content in a JSON object
        block_content = {
            "preamble": "6".zfill(64),
            "account": self.public_key,
            "link": link,
            "balance": balance.as_raw().to_hex(16),
            "previous": self.frontier.hash,
            "representative": representative.public_key
        }

        block_order = ["preamble", "account", "previous", "representative", "balance", "link"]

        # Then we build the block hash
        block_hex = "".join([block_content[b] for b in block_order])
        block_hash = hash_block(block_hex)

        # Finally we sign it
        block_signature = sign_block(block_hash, self.private_key, self.public_key)

        block_json = {
            "type": "state",
            "subtype": subtype,
            "account": self.address,
            "previous": self.frontier.hash,
            "representative": representative.address,
            "link": link,
            "balance": balance.as_raw().int_str(),
            "signature": block_signature,
            "work": work_hash
        }

        return BlockState(self, block_json, block_hash, node_backend=self._node_backend, work_server=self._work_server)

    def offline_update_representative(self, new_representative):
        """
        Sets the representative for this account locally, useful under offline environments or for local updates.

        :param new_representative:
            Account or string for the new representative

        """

        if type(new_representative) is str:
            new_representative = Account(new_representative, node_backend=self._node_backend, default_work_server=self._work_server)

        self.offline_update({'representative': new_representative})


class AccountHistory:
    """
    Manages the blocks history of a given account.

    Provides a simple interface to access the account block history.
    """
    def __init__(self, account_owner, node_backend=NO_NODE, work_server=None):
        """
        Constructor of the historic class.

        :param account_owner:
            Account object whose historic is wanted to be inspected.

        :param node_backend:
            A Node object pointing to a working Nano node.

        :param work_server:
            The work server to request work. Optional.
        """
        self._account_owner = account_owner
        self._node_backend = node_backend
        self._work_server = work_server

    def __len__(self):
        """
        Returns the number of blocks published for this account.
        """
        return int(self._account_owner.block_count)

    def __str__(self):
        return f"{self._account_owner.address} History: {len(self)} blocks"

    def __iter__(self):
        for block_definition in self._customized_iter():
            block = BlockFactory(self._node_backend, work_server=self._work_server).build_block_object(self._account_owner, block_definition)
            yield block

    def _customized_iter(self, offset=None, count=100, reverse=None):
        """
        Custom iterator for the block history of this account.

        Allows to iterate using the RPC to go back and forth in the blocks history of the account.

        :param offset:
            Position to start the iteration from.

        :param count:
            Number of elements to iterate.

        :param reverse:
            Order of the iteration (Boolean flag).
        """
        previous = None
        first = True

        def request_history(prev_hash):
            response = self._node_backend.ask(AccountMessages.ACCOUNT_HISTORY(
                         self._account_owner.address,
                         count=count,
                         reverse=reverse,
                         previous=prev_hash,
                         offset=offset
                     ))

            if not response:
                response = {
                    'history': []
                }

            prev_hash = response.get('previous', None)
            return response['history'], prev_hash

        while previous is not None or first:
            first = False
            history, previous = request_history(previous)
            yield from history

    def __getitem__(self, block_indexes):
        reverse = True

        if type(block_indexes) is int:
            block_indexes = slice(block_indexes, block_indexes)

        start = block_indexes.start
        end = block_indexes.stop

        if end is not None:
            end = end - 1

        if start < 0:
            reverse = False
            start = start * -1

        result = []
        account_owner = self._account_owner
        for i, block_definition in enumerate(self._customized_iter(start, reverse=reverse)):

            block = BlockFactory(self._node_backend, work_server=self._work_server).build_block_object(account_owner, block_definition)
            result.append(block)

            if end is not None and ((reverse and i >= end-start) or (not reverse and i <= start-end)):
                break

        if start is not None and end is not None and start >= end:
            result = result[0]

        return result


class AccountPendingHistory:
    """
    Interface for pending blocks.

    Gives an easy interface to deal with pending transactions.

    This is an iterable object, which also allows to filter the pending transactions by quantity or to skip small
    transactions to avoid pending history spam attack.
    """

    def __init__(self, account_owner, node_backend=NO_NODE, work_server=None):
        """
        Instance of the account pending transactions history class.

        :param account_owner:
            Account object owner of this history object.

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, in case the pending history is serialized and locally updated.

        :param work_server:
            Work server to use by default. Optional.
        """
        self._account_owner = account_owner
        self._node_backend = node_backend
        self._work_server = work_server
        self._pending_transactions = {}
        self._last_update = "Unknown"

    def __len__(self):
        return len(self._pending_transactions)

    def update(self, minimum_quantity=Amount(1), descending=True, count=10, clear_previous_cache=True):
        """
        Asks to the backend for a list of pending transaction hashes and then updates the internal cache.

        :param minimum_quantity:
            Filter by minimum quantity. It can be an Amount object or a string/integer in NANO units.

        :param descending:
            Sorts the hashes in descending order, showing first the higher amounts. This is True by default.

        :param count:
            Cache size (in number of hashes)

        :param clear_previous_cache:
            If True, the previous cache is cleared. Otherwise, old cached hashes are kept until manual confirmation.
            By default it is True.
        """

        if not self._node_backend.is_online:
            raise NodeBackendRequiredError("A node backend is required")

        if type(minimum_quantity) is not Amount:
            minimum_quantity = Amount(minimum_quantity)

        # We request the pending blocks to the network
        response = self._node_backend.ask(AccountMessages.ACCOUNTS_PENDING([self._account_owner.address],
                                                                           count=count,
                                                                           sorting=descending,
                                                                           minimum_balance=minimum_quantity.as_raw().int_str()))

        # We store the new block hashes into the cache
        blocks = response['blocks'][self._account_owner.address]
        if len(blocks) > 0:
            self.offline_update(blocks, clear_previous_cache=clear_previous_cache)

    def offline_update(self, pending_hashes, clear_previous_cache=True):
        """
        Updates the local pending hashes with the specified ones.

        :param pending_hashes:
            Dictionary containing the {hash:{amount:x, source:y}} pending elements.

        :param clear_previous_cache:
            If True, the previous cache is cleared. Otherwise, old cached hashes are kept until manual confirmation.
            By default it is True.
        """

        if clear_previous_cache:
            self._pending_transactions.clear()

        block_factory = BlockFactory(self._node_backend, work_server=self._work_server)

        blocks_cache = {
            block_hash: block_factory.build_block_object(Account(block_def['source'],
                                                                 node_backend=self._node_backend), {
                'height': 'unknown',
                'type': 'send',
                'link_as_account': self._account_owner.address,
                'amount': Amount(block_def['amount']),
                'hash': block_hash,
                'local_timestamp': 'Unknown'
            }) for block_hash, block_def in pending_hashes.items()
        }

        self._pending_transactions.update(blocks_cache)
        self._last_update = datetime.now()

    def confirm_transaction(self, pending_hash):
        """
        Confirms the specified pending hash to remove it from the local cache without requiring querying the node.
        """
        if pending_hash in self._pending_transactions:
            del self._pending_transactions[pending_hash]

    def __getitem__(self, index):
        """
        Retrieves a cached pending block by index.

        :param index:
            Local index of the pending block. Check len(pending_blocks) to know how many are there available.
        """
        return list(self._pending_transactions.values())[index]

    def __iter__(self):
        """
        Iterates over the local cached pending blocks.
        Ensure to call update() or offline_update() first. Otherwise there won't be hashes to iterate.
        """
        for block in self._pending_transactions.values():
            yield block

    def to_dict(self):
        """
        Returns a dict representation of the object.
        """
        return dict(self._pending_transactions)

    def __str__(self):
        return f"[Account: {self._account_owner}] \n" \
               f"Pending blocks: {len(self)}; \n" \
               f"Last pending blocks update: {self._last_update}\n"

    def __repr__(self):
        return str(self)
