from nanoblocks.block.block import Block


class BlockReceive(Block):
    """
    Represents a receive block.

    Gives an easy interface for receive blocks.
    """
    @property
    def source_account(self):
        """
        Retrieves the account source of the amount.
        It is the account that sent the amount of this block.
        """
        from nanoblocks.account.account import Account
        return Account(self._block_definition['account'], node_backend=self._node_backend, default_work_server=self._work_server)

    @property
    def amount(self):
        """
        Retrieves the amount of Nano received.
        """
        from nanoblocks.currency import Amount
        return Amount(self._block_definition['amount'])

    def __str__(self):
        string = super().__str__()
        string += f"\tSource account: {self.source_account.address}\n\tAmount: {self.amount}\n\tLocal date: {self.local_timestamp}\n"
        return string
