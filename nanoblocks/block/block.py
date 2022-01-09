import datetime
from time import sleep

import pandas as pd

from nanoblocks.base import NanoblocksClass


class Block(NanoblocksClass):
    """
    Represents a block in the Nano network.

    Gives an easy interface to access the metadata of the block.
    """

    def __init__(self, account, block_definition, nano_network):
        """
        Constructor of the class

        :param block_definition:
            Dict returned by the Nano node containing all the information of the block.

        :param nano_network:
            A network object giving access to node and work backends.

        """
        super().__init__(nano_network)
        self._block_definition = block_definition
        self._account_owner = account

    @classmethod
    def from_dict(cls, dict_data, nano_network, initial_update=True):
        """
        Builds the block from a definition dictionary
        """
        if initial_update:
            account = nano_network.accounts[dict_data['account']]
        else:
            account = nano_network.accounts.lazy_fetch(dict_data['account'])

        return cls(account, dict_data, nano_network=nano_network)

    def wait_for_confirmation(self, timeout_seconds=30, check_interval_secs=1):
        """
        Waits until the block has been confirmed.
        This method forces a confirmation on the block and waits until it has been solved.
        """

        if self.confirmed:
            return True

        # We ask our node to request confirmation for the block
        self.node_backend.block_confirm(self.hash)

        # Now we wait until the block is confirmed
        start_time = datetime.datetime.now()

        while (datetime.datetime.now() - start_time).total_seconds() < timeout_seconds and not self.confirmed:
            sleep(check_interval_secs)

        # TODO: Confirmation should be centralized by a service that uses websockets if available.
        if not self.confirmed:
            raise Exception("Could not confirm the block in the requested timeout window.")

    @property
    def confirmed(self):
        """
        Checks whether this block has been confirmed or not.
        This is a sync method that actively ask the node backend.
        """
        if self._block_definition.get('confirmed', False) in ['true', True]:
            return True

        confirmed = self.node_backend.block_info(self.hash).get('confirmed', False) == 'true'

        self._block_definition['confirmed'] = confirmed

        return confirmed

    @property
    def broadcastable(self):
        """
        Retrieves whether this block can be broadcasted to the network or not.
        This will be true in the case it is recently built, signed and has a work hash attached.
        """
        return self._block_definition.get("signature") is not None and self._block_definition.get("work") is not None

    @property
    def type(self):
        return self._block_definition['type']

    @property
    def subtype(self):
        return self._block_definition.get('subtype', None)

    @property
    def account_owner(self):
        return self._account_owner

    def to_dict(self):
        """
        Retrieves the dictionary version of this block.
        """
        return self._block_definition

    def __str__(self):
        str_result = f"[Block #{self.height} from account {self.account_owner.address}]\n\tType: {self.subtype if self.subtype is not None else self.type}\n\t" \
               f"Hash: {self.hash}\n"

        return str_result

    @property
    def local_timestamp(self):
        """
        Retrieves the local timestamp of this block.
        """
        block_time = self._block_definition.get('local_timestamp', 0)

        if block_time == 'Unknown':
            block_time = 0

        m_datetime = pd.to_datetime(
            pd.Timestamp(int(block_time) * 1000000000).to_pydatetime()).tz_localize(
            "UTC").tz_convert(self.node_backend.timezone)

        return m_datetime

    @property
    def hash(self):
        """
        Retrieves the hash of this block
        """
        return self.__hash__()

    def __hash__(self):
        return self._block_definition.get('hash', 'Unknown')

    @property
    def height(self):
        """
        Retrieves the height of this block in the account history
        """
        return self._block_definition.get('height', 'Unknown')

    def __repr__(self):
        return str(self)

    @property
    def is_first(self):
        """
        Retrieves whether this block is the first (all 0s) or not
        """
        return str(self.hash) == "0000000000000000000000000000000000000000000000000000000000000000"
