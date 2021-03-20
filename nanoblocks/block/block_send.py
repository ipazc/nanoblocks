from nanoblocks.block.block import Block


class BlockSend(Block):
    """
    Represents a send block.

    Gives an easy interface for send blocks.
    """

    @property
    def destination_account(self):
        """
        Retrieves the account target for the amount.
        It is the account where this amount is sent to.
        """
        from nanoblocks.account.account import Account

        account_address = self._block_definition.get('link_as_account', self._block_definition.get('account', None))

        account = Account(account_address, node_backend=self._node_backend, default_work_server=self._work_server)

        return account

    @property
    def amount(self):
        """
        Retrieves the amount of Nano received in case the block is read from the ledger.
        """
        from nanoblocks.currency import Amount

        result = Amount(self._block_definition['amount'])

        return result

    def __str__(self):
        string = super().__str__()
        string += f"\tDestination account: {self.destination_account.address if self.destination_account else 'Unknown (check block directly by hash)'}\n\tAmount: {self.amount}\n\tLocal date: {self.local_timestamp}\n"
        return string
