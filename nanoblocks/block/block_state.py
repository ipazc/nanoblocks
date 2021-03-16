import pandas as pd

from nanoblocks.block.block import Block
from nanoblocks.node.nanonode import NO_NODE


class BlockState(Block):
    """
    Represents a state block.

    Gives an easy interface for state blocks.
    """

    def __init__(self, account, block_definition, block_hash, node_backend=NO_NODE, work_server=None):
        """
        Constructor of the class

        :param account:
            Account owner of this block

        :param block_definition:
            Dict returned by the Nano node containing all the information of the block.

        :param block_hash:
            Hash of this block

        :param node_backend:
            Node backend to contact.

        :param work_server:
            Work server object to use by default. Optional.
        """
        super().__init__(account, block_definition, node_backend, work_server=work_server)
        self._block_definition = block_definition
        self._node_backend = node_backend
        self._block_hash = block_hash
        self._account_owner = account

    def __hash__(self):
        return self._block_hash

    @property
    def balance(self):
        """
        Retrieves the total balance of the account after block confirmation.
        """
        from nanoblocks.currency import Amount

        result = Amount(self._block_definition['balance'])

        return result

    @property
    def account(self):
        return self._account_owner

    @property
    def signature(self):
        return self._block_definition['signature']

    @property
    def previous(self):
        return self._block_definition['previous']

    @property
    def link(self):
        return self._block_definition['link']

    @property
    def work(self):
        return self._block_definition['work']

    @work.setter
    def work(self, value):
        self._block_definition['work'] = work

    @property
    def subtype(self):
        return self._block_definition['subtype']

    @property
    def representative(self):
        return self._block_definition['representative']

    def __str__(self):
        string = super().__str__()
        string += f"\tSubtype: {self.subtype}\n" + \
                  f"\tLink: {self.link}\n" + \
                  f"\tBalance: {self.balance}\n" + \
                  f"\tSignature: {self.signature}\n" + \
                  f"\tWork: {self.work}\n"
        return string
