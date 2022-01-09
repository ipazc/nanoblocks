from nanoblocks.base import NanoblocksClass


class AccountHistory(NanoblocksClass):
    """
    Manages the blocks history of a given account.

    Provides a simple interface to access the account block history.
    """
    def __init__(self, account_owner, nano_network, history_filter_accounts=None):
        """
        Constructor of the historic class.

        :param account_owner:
            Account object whose historic is wanted to be inspected.

        :param nano_network:
            A network object giving access to node and work backends.

        :param history_filter_accounts:
            List of accounts objects to filter the transaction list so that send/receive blocks matches any of those.
            The accounts must be Account objects.
        """
        super().__init__(nano_network)
        self._account_owner = account_owner
        self._history_filter_accounts = history_filter_accounts

    def __len__(self):
        """
        Returns the number of blocks published for this account.
        """
        return int(self._account_owner.block_count)

    def __str__(self):
        return f"{self._account_owner.address} History: {len(self)} blocks"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        blocks_factory = self.blocks.factory

        for block_definition in self._customized_iter():
            block = blocks_factory.build(self._account_owner, block_definition)
            yield block

    def filter(self, accounts_list):
        """
        Filters the history so that only transactions regarding the specified accounts (send to, or receive from) do
        match any of the provided accounts.

        :param accounts_list:
            List of accounts. Either string addresses "nano_..." or Account objects are supported.

        :return:
            An account history object that filters by default the requested history.
        """
        accounts_list = [self.accounts.lazy_fetch(account) for account in accounts_list]

        return AccountHistory(self._account_owner, nano_network=self.network,
                              history_filter_accounts=[account.address for account in accounts_list])

    def _customized_iter(self, offset=None, count=10, reverse=None, account_filter=None):
        """
        Custom iterator for the block history of this account.

        Allows to iterate using the RPC to go back and forth in the blocks history of the account.

        :param offset:
            Position to start the iteration from.

        :param count:
            Number of elements to iterate.

        :param reverse:
            Order of the iteration (Boolean flag).

        :param account_filter:
            Filter history by accounts.
        """
        previous = None
        first = True

        def request_history(prev_hash):
            response = self.node_backend.account_history(
                self._account_owner.address,
                raw=True,
                count=count,
                reverse=reverse,
                previous=prev_hash,
                offset=offset,
                account_filter=account_filter
            )

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
        was_int = False
        reverse = True

        if type(block_indexes) is int:
            block_indexes = slice(block_indexes, block_indexes+1)
            was_int = True

        start = block_indexes.start
        end = block_indexes.stop

        count = len(self)

        if start is None:
            start = 0

        if start < 0:
            start = count + start

        if end is None:
            end = count

        if end < 0:
            end = count + end

        if was_int and end < start:
            end = start + 1

        start_end_range = end - start

        result = []
        account_owner = self._account_owner

        block_factory = self.blocks.factory

        for i, block_definition in enumerate(self._customized_iter(start, reverse=reverse,
                                                                   account_filter=self._history_filter_accounts)):
            # History blocks are already confirmed by default.
            block_definition['confirmed'] = True

            # We iterate until we met the desired range
            if i >= start_end_range:
                break

            if 'subtype' not in block_definition:
                continue  # We skip blocks without subtypes

            block = block_factory.build(account_owner, block_definition, type_key='subtype')
            result.append(block)

        if len(result) == 1 and was_int:
            result = result[0]

        return result
