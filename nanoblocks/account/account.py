import base64
import sys
from io import BytesIO

import pandas as pd
import numpy as np
import qrcode

from nanoblocks import rcParams
from nanoblocks.account.account_history import AccountHistory
from nanoblocks.account.account_pending_history import AccountPendingHistory
from nanoblocks.base import NanoblocksClass

from nanoblocks.account.payment.payment import Payment
from nanoblocks.currency import Amount
from nanoblocks.exceptions.block_not_broadcastable_error import BlockNotBroadcastableError
from nanoblocks.exceptions.insufficient_funds import InsufficientFunds
from nanoblocks.exceptions.work_error import WorkError
from nanoblocks.ipython.html import get_html
from nanoblocks.ipython.img import get_svg
from nanoblocks.utils.crypto import address_pubkey, account_pubkey, account_address, hash_block, sign_block
from nanoblocks.utils.time import now


class Account(NanoblocksClass):
    """
    Handles a single account in the Nano network.

    Contains all the methods that allows to interact with accounts, like reading the state, sending/receiving amounts or
    reading the blockchain of the account.

    By default every account is read-only, unless a private key is available.

    :param nano_address:
        Nano address of the account. E.g "nano_3pyz..".

    :param nano_network:
        The nano network owning this account.

    :param initial_update:
        Flag to determine if the account should be updated at start or not. Updating an account requires querying the
        backend node.
    """

    def __init__(self, nano_address, nano_network, initial_update=True):
        """

        :param nano_address:
            Nano address of the account. E.g "nano_3pyz...".

        :param nano_network:
            The nano network owning this account.

        :param initial_update:
            Flag to determine if the account should be updated at start or not.

        """

        super().__init__(nano_network)

        self._nano_address = nano_address
        self._public_key = address_pubkey(nano_address)  # If the address is not valid -> Exception raised here
        self._private_key = None
        self._account_info = {
            'frontier': "0".zfill(64),
            'block_count': 0,
            'representative': self.address,
            'weight': 0,
            'status': 'Update required',
            'balance': 0,
            'pending': 0,
            'modified_timestamp': now(self.network.node_backend.timezone).timestamp()
        }
        self._pending_transactions_history = AccountPendingHistory(self, nano_network=nano_network)
        self._last_update = None

        if initial_update:
            self.update()

    @classmethod
    def from_priv_key(cls, private_key, nano_network):
        """
        Tries to access an account from the specified private key.

        No addresses or public keys are required, as they can be derived from the private key itself.

        :param private_key:
            private key to derive the account from.

        :param nano_network:
            The nano network owning this account.

        """
        public_key = account_pubkey(private_key)
        account = cls.from_pub_key(public_key, nano_network=nano_network)
        account._private_key = private_key
        return account

    @classmethod
    def from_pub_key(cls, pub_key, nano_network):
        """
        Gives access to the specified account by its public key.

        This method is read-only unless the account is `unlocked()` with the private key.

        :param pub_key:
            Public key for the nanoblocks account.

        :param nano_network:
            The nano network owning this account.
        """
        nano_address = account_address(pub_key)
        account = cls(nano_address, nano_network=nano_network)
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
        frontier_hash = self._account_info.get('frontier')

        if frontier_hash is None:
            return 0

        try:
            frontier_block = self.blocks[frontier_hash]

            if frontier_block.is_first:
                frontier_block._account_owner = self

        except KeyError:
            factory = self.blocks.factory
            factory.build()
            frontier_block = self.blocks.new_block(hash_block=frontier_hash)

        return frontier_block

    @property
    def qr_code(self):
        """
        Generates a QR code representation of this account in PIL format.

        If a payment is desired, use the .request_payment(...).qr_code method instead.

        :return:
            QR code representation of the account
        """
        uri = f"nano:{self.address}"
        return qrcode.make(uri)

    def to_dict(self):
        """
        Retrieves the cached account information.
        Note: a call to `update()` before `info()` is highly encouraged!!
        """
        return dict(self._account_info)

    def update(self):
        """
        Retrieves the account information from the node (if available) and caches it inside the object.
        """
        account_info = self.node_backend.account_info(self._nano_address, representative=True, weight=True,
                                                      pending=True)

        if account_info.get("error", None) == 'Account not found':
            account_info = {
                'frontier': "0".zfill(64),
                'block_count': 0,
                'representative': self.address,
                'weight': 0,
                'status': 'virtual',
                'balance': 0,
                'pending': 0,
                'modified_timestamp': now(self.node_backend.timezone).timestamp()
            }

            # We try to get if are there pending blocks for this account.
            # This could happen if it is a new account in the ledger.
            if len(self.pending_transactions) > 0:
                account_info['pending'] = self.pending_transactions[-1].amount

        self._account_info = account_info
        self._last_update = now(self.node_backend.timezone)

    def offline_update(self, account_info):
        """
        Performs an offline update with the given account_info.
        This method does not interact with a node and can be executed offline to update the information of an account
        object (for example, taking this info from a local json file).

        :param account_info:
            Dictionary containing information of the account (frontier, block_count, representative, weight, status,
            balance, pending, modified_timestamp, ...).
        """
        self._account_info.update(account_info)
        self._last_update = now(self.node_backend.timezone)

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

        # In a reception, the balance of the block is higher than the confirmed balance. We recompute manually the
        # pending balance.
        if block_state.balance >= self.confirmed_balance:
            self._account_info['pending'] = self.balance - block_state.balance

        # 3. Now we update the confirmed balance of the account
        self._account_info['balance'] = int(str(block_state.balance))

        if self._account_info['block_count'] != "Unknown":
            self._account_info['block_count'] = int(self._account_info['block_count']) + 1

        self._last_update = now(self.node_backend.timezone)

    @property
    def confirmed_balance(self):
        """
        Provides the confirmed balance for this account.

        Note: a call to `update()` or `offline_update()` before `confirmed_balance` is highly encouraged!!
        """
        return Amount(self._account_info['balance'], unit="raw")

    @property
    def pending_balance(self):
        """
        Provides the pending balance for this account.

        Note: a call to `update()` or `offline_update()` before `pending_balance` is highly encouraged!!
        """
        return Amount(self._account_info['pending'], unit="raw")

    @property
    def pending_transactions(self):
        """
        Retrieves the pending transactions for the account.
        """
        # if node is online, we refresh the transactions list
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
            "UTC").tz_convert(self.node_backend.timezone)

        return m_datetime

    @property
    def block_count(self):
        """
        Provides the number of block counts for this account.

        Note: a call to `update()` or `offline_update()` before `block_count` is highly encouraged!!
        """
        return self._account_info['block_count']

    def request_payment(self, nano_units_amount=None):
        """
        Generates the payment object which contains payment handle for the given amount

        :param nano_units_amount:
            Amount of NANO to hook payment for.
            If a different unit measure is required, wrap it into an `Amount()` class.
            If no amount is required, set it to None.
        """
        if nano_units_amount is not None:
            nano_units_amount = Amount(nano_units_amount)

        payment = Payment(self, nano_units_amount, nano_network=self.network)
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

    def _repr_html_(self):
        template_html = get_html("account")

        date_format = rcParams["display.date_format"]

        with BytesIO() as b:
            self.qr_code.save(b, format="JPEG")
            img_str = str(base64.b64encode(b.getvalue()), "UTF-8")

        representation_formatted = template_html.format(**{
            'is_virtual': ("[VIRTUAL] " if self.is_virtual else ""),
            'account_address': self.address,
            'total_blocks': self.block_count,
            'total_balance': self.balance.as_unit("NANO").format(),
            'total_balance_str': self.balance.as_unit("NANO"),
            'confirmed_balance': self.confirmed_balance.as_unit("NANO").format(),
            'confirmed_balance_str': self.confirmed_balance.as_unit("NANO"),
            'pending_balance': self.pending_balance.as_unit("NANO").format(),
            'pending_balance_str': self.pending_balance.as_unit("NANO"),
            'last_transaction_date': self.modified_date.strftime(date_format),
            'last_update': self.last_update.strftime(date_format),
            'last_update_seconds_elapsed': self.last_update_elapsed_seconds,
            'copy_to_clipboard_image': get_svg('clipboard'),
            'total_balance_image': get_svg('total_balance'),
            'confirmed_balance_image': get_svg('confirmed_balance'),
            'pending_balance_image': get_svg('pending_balance'),
            'representative_address': self.representative.address,
            'account_qrcode': img_str
        })

        return representation_formatted

    def __str__(self):
        return f"{self.address} (\n\t" \
               f"Total blocks: {self.block_count}\n\t" \
               f"Total balance: {self.balance.as_unit(rcParams['currency.unit']).format()}\n\t" \
               f"Confirmed balance: {self.confirmed_balance.as_unit(rcParams['currency.unit']).format()}\n\t" \
               f"Pending balance: {self.pending_balance.as_unit(rcParams['currency.unit']).format()}\n\t" \
               f"Last confirmed payment: {self.modified_date}\n\t" \
               f"Is virtual: {self.is_virtual}\n\t" \
               f"Last update: {self._last_update.isoformat()} ({self.last_update_elapsed_seconds} seconds ago)\n)"

    @property
    def last_update_elapsed_seconds(self):
        return np.round((now(self.node_backend.timezone) - self._last_update).total_seconds(), 2)

    @property
    def last_update(self):
        """
        :return:
        Datetime of the last update of this account.
        """
        return self._last_update

    @property
    def representative(self):
        """
        Provides the representative for this account.

        Note: a call to `update()` or `offline_update()` before `representative` is highly encouraged!!
        """
        representative_account_address = self._account_info['representative']
        return self.accounts[representative_account_address]

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
        return AccountHistory(self, nano_network=self.network)

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

    def build_send_block(self, account_target, nano_amount, work_hash=None, new_representative=None):
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

        :param new_representative:
            Representative account to set in this transaction (can be changed on any transaction). None to set the
            same representative.

        :returns:
            Returns the send block, signed, ready to broadcast to the network.
        """
        if self._private_key is None:
            raise KeyError("No private key available for this account. Can't send valid blocks.")

        nano_amount = Amount(nano_amount)

        if type(account_target) is str:
            account_target = self.accounts[account_target]

        if nano_amount > self.confirmed_balance:
            raise InsufficientFunds(f"Account {self.address} doesn't have enough funds ({self.confirmed_balance}) "
                                    f"to send the requested quantity ({nano_amount}).")

        block_final_balance = (self.confirmed_balance - nano_amount)

        if work_hash is None:

            if self.work_server is None:
                raise WorkError("No work provided for the transaction.")

            work_hash = self.work_server.generate_work_send(self)

        new_representative = new_representative if new_representative is not None else self.representative

        if type(new_representative) is str:
            new_representative = self.accounts.lazy_fetch(new_representative)

        block_state = self._craft_block_state(subtype="send", link=account_target.public_key,
                                              balance=block_final_balance, representative=new_representative,
                                              work_hash=work_hash)

        return block_state

    def build_receive_block(self, pending_block, work_hash=None, new_representative=None):
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

        :param new_representative:
            Representative account object to set in this transaction (can be changed on any transaction). None to set
            the same representative.
        """

        if self._private_key is None:
            raise KeyError("No private key available for this account. Can't send valid blocks.")

        if pending_block.destination_account.address != self.address:
            raise KeyError("The block target does not belong to this account")

        if work_hash is None:

            if self.work_server is None:
                raise WorkError("No work provided for the transaction.")

            work_hash = self.work_server.generate_work_receive(self)

        send_block_hash = pending_block.hash
        block_amount = pending_block.amount

        block_final_balance = (self.confirmed_balance + block_amount)

        new_representative = new_representative if new_representative is not None else self.representative

        if type(new_representative) is str:
            new_representative = self.accounts.lazy_fetch(new_representative)

        block_state = self._craft_block_state(subtype="receive", link=send_block_hash, balance=block_final_balance,
                                              representative=new_representative, work_hash=work_hash)

        return block_state

    def build_change_representative_block(self, new_representative, work_hash=None):
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

            if self.work_server is None:
                raise WorkError("No work provided for the transaction.")

            work_hash = self.work_server.generate_work_change(self)

        if type(new_representative) is str:
            new_representative = self.accounts.lazy_fetch(new_representative)

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
            "balance": balance.to_hex(16),
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
            "previous": self._account_info.get('frontier'),
            "representative": representative.address,
            "link": link,
            "balance": str(balance),
            "signature": block_signature,
            "work": work_hash,
            "hash": block_hash
        }

        block_factory = self.blocks.factory
        block = block_factory.build(self, block_json)

        return block

    def offline_update_representative(self, new_representative):
        """
        Sets the representative for this account locally, useful under offline environments or for local updates.

        :param new_representative:
            Account or string for the new representative

        """

        if type(new_representative) is Account:
            new_representative = new_representative.address

        self.offline_update({'representative': new_representative})

    def change_representative(self, new_account_representative, wait_confirmation=True, confirmation_timeout_secs=30):
        """
             Easy interface for changing the representative. Builds, signs and broadcasts the change block to the network.


             Example:
                 account.change_representative("nano_..")  # Changes the representative to "nano_..."

        :param new_account_representative:
            Nano account (string "nano_..." or Account object) destination.

        :param wait_confirmation:
            Boolean flag to wait for the network to confirm the block.

        :param confirmation_timeout_secs:
            Number of seconds to wait for confirmation of the block.

        :return:
            Returns the published block.
        """

        block_result = self.build_change_representative_block(new_account_representative)
        block_change = self.blocks.broadcast(block_result)

        # TODO: Confirmation should be handled also in virtual nodes environments.
        # TODO: Confirmation should be handled by a centralized websocket service
        if wait_confirmation:
            block_change.wait_for_confirmation(timeout_seconds=confirmation_timeout_secs)

        return block_change

    def send_nano(self, account_target, nano_amount, wait_confirmation=True, confirmation_timeout_secs=30):
        """
        Easy interface for sending a transaction. Builds, signs and broadcasts the send block to the network.


        Example:
            account.send_nano("nano_..", "0.01")  # Sends 0.01 Nano to the account 'nano_'


        :param account_target:
            Nano account (string "nano_..." or Account object) destination.

        :param nano_amount:
            Amount of Nano to send (string or Amount object).

        :param wait_confirmation:
            Boolean flag to wait for the network to confirm the block.

        :param confirmation_timeout_secs:
            Number of seconds to wait for confirmation of the block.

        :return:
            Returns the published block.
        """
        block_result = self.build_send_block(account_target, nano_amount)
        block_sent = self.blocks.broadcast(block_result)

        # TODO: Confirmation should be handled also in virtual nodes environments.
        if wait_confirmation:
            block_sent.wait_for_confirmation(timeout_seconds=confirmation_timeout_secs)

        return block_sent

    def receive_nano(self, block_to_receive=None, wait_confirmation=True, confirmation_timeout_secs=30):
        """
        Easy interface for receiving a transaction. Builds, signs and broadcasts the receive block to the network.


        Example:
            account.receive_nano()  # Receives the next pending transaction (if any)


        :param block_to_receive:
            Pending transaction to receive (can be obtained from account.pending_transactions list). In case of None,
            the method automatically peeks for the next pending transaction.

        :param wait_confirmation:
            Boolean flag to wait for the network to confirm the block.

        :param confirmation_timeout_secs:
            Number of seconds to wait for confirmation of the block.

        :return:
            Returns the published block. None if no pending transactions.
        """
        if block_to_receive is None:
            pending_transactions = self.pending_transactions

            if len(pending_transactions) == 0:
                return None  # Guard clause: no pending transactions. Nothing to do.

            block_to_receive = pending_transactions[-1]

        block_result = self.build_receive_block(block_to_receive)
        block_received = self.blocks.broadcast(block_result)

        if wait_confirmation:
            block_received.wait_for_confirmation(timeout_seconds=confirmation_timeout_secs)

        return block_received

    def refcount(self):
        """
        Retrieves how many references to this account are active.
        :return: the number of active references to this account.
        """
        return max(sys.getrefcount(self) - 3, 0)
