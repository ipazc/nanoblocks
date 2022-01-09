from nanoblocks.base import NanoblocksClass
from nanoblocks.currency import Amount
from nanoblocks.utils.time import now


class AccountPendingHistory(NanoblocksClass):
    """
    Interface for pending blocks.

    Gives an easy interface to deal with pending transactions.

    This is an iterable object, which also allows to filter the pending transactions by quantity or to skip small
    transactions to avoid pending history spam attack.
    """

    def __init__(self, account_owner, nano_network):
        """
        Instance of the account pending transactions history class.

        :param account_owner:
            Account object owner of this history object.

        :param nano_network:
            A network object giving access to node and work backends.
        """
        super().__init__(nano_network)
        self._account_owner = account_owner
        self._pending_transactions = {}
        self._last_update = "Unknown"

    def __len__(self):
        return len(self._pending_transactions)

    def update(self, minimum_quantity=Amount("1", unit="raw"), descending=True, count=10, clear_previous_cache=True):
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
        if type(minimum_quantity) is not Amount:
            minimum_quantity = Amount(minimum_quantity, unit="raw")

        # We request the pending blocks to the network
        response = self.node_backend.accounts_pending([self._account_owner.address],
                                                      count=count,
                                                      sorting=descending,
                                                      threshold=str(minimum_quantity),
                                                      source=True)

        if 'error' in response:
            raise KeyError(f"Pending blocks error: {response['error']}")

        # We store the new block hashes into the cache
        blocks = response['blocks'][self._account_owner.address]
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

        self._last_update = now(self.node_backend.timezone)

        if clear_previous_cache:
            self._pending_transactions.clear()

        if len(pending_hashes) == 0:
            return

        block_factory = self.blocks.factory

        blocks_cache = {
            block_hash: block_factory.build(self.accounts.lazy_fetch(block_def['source']), {
                'height': 'unknown',
                'type': 'send',
                'link_as_account': self._account_owner.address,
                'amount': Amount(block_def['amount'], unit="raw"),
                'hash': block_hash,
                'local_timestamp': 'Unknown'
            }) for block_hash, block_def in pending_hashes.items()
        }

        self._pending_transactions.update(blocks_cache)

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
