import datetime

import pandas as pd

from nanoblocks.exceptions.block_not_broadcastable_error import BlockNotBroadcastableError
from nanoblocks.node.nanonode import NO_NODE
from nanoblocks.protocol.messages import NodeMessages, NetworkMessages


class Blocks:
    """
    Handles the block interaction through the node API
    """

    def __init__(self, node_backend=NO_NODE, work_server=None):
        """
        Constructor of the class

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the retrieval of public keys.

        :param work_server:
            Work server to use by default. Optional
        """
        self._node_backend = node_backend
        self._work_server = work_server

    def __getitem__(self, block_hash):
        """
        Retrieves a specific block information

        :param block_hash:
            Address of the account. Eg "nano_..."
        """
        response = self._node_backend.ask(NodeMessages.BLOCK_INFO(block_hash))

        block_info = {
            'type': response.get('subtype', response.get('contents', {'type': 'Unknown'})['type']),
            'confirmed': response.get('confirmed', False),
            'account': response['block_account'],
            'amount': response['amount'],
            'local_timestamp': response['local_timestamp'],
            'height': response['height'],
            'link_as_account': response['contents'].get('link_as_account', None),
            'hash': block_hash
        }

        from nanoblocks.block.block_factory import BlockFactory
        from nanoblocks.account.account import Account
        account = Account(response['block_account'], node_backend=self._node_backend)

        block = BlockFactory(self._node_backend, work_server=self._work_server).build_block_object(account, block_info)

        return block

    def __len__(self):
        """
        Returns the number of blocks in the network, in case the backend is available.
        """
        response = self._blocks_telemetry()

        if not response:
            response = {'count': 0}

        return int(response['count'])

    def _blocks_telemetry(self):
        return self._node_backend.ask(NodeMessages.BLOCK_COUNT())

    def broadcast(self, block):
        """
        Broadcasts the given block to the network and returns the processed block.

        Under offline environments, the block will not be broadcasted to the nodes. Instead, it will be updated locally.
        This allows to update an account ledger offline, and accumulate the state blocks by chaining their hashes.
        Those accumulated state blocks can be later used to broadcast in batch to a NanoNetwork object with a node set.

        The offline collected blocks are only valid while the online ledger for the account is not modified by a third
        party. Remember that all the offline blocks are chained among them, being the first one chained with the last
        known frontier of the account.

        Important: the account being updated must be already instantiated and the python's Account object must be
        linked to the block. The network does not hold this information in offline environments. An example of this
        problem below.

            Wrong example:
                >>> account1 = NanoNetwork.wallet["seed"].accounts[0]
                >>> account2 = NanoNetwork.wallet["seed"].accounts[0] # same account actually, but second instance
                >>> receive_block = account1.build_receive_block(work_hash)
                >>> NanoNetwork.blocks.broadcast(receive_block)
                >>> receive_block2 = account2.build_receive_block(work_hash2) ## Account2 does not reflect changes in account 1, even though they point to the same address!!

            Correct example:
                >>> account = NanoNetwork.wallet["seed"].accounts[0]
                >>> receive_block = account.build_receive_block(work_hash)
                >>> NanoNetwork.blocks.broadcast(receive_block)
                >>> receive_block2 = account.build_receive_block(work_hash2) ## Using the same account object is mandatory for correct chain updates.

            Alternatively:
                >>> account1 = NanoNetwork.wallet["seed"].accounts[0]
                >>> account2 = NanoNetwork.wallet["seed"].accounts[0] # same account actually, but second instance
                >>> receive_block = account1.build_receive_block(work_hash)
                >>> account1.offline_update_by_block(receive_block)
                >>> account2.offline_update_by_block(receive_block)
                >>> receive_block2 = account2.build_receive_block(work_hash2)


        :param block:
            Block Status to broadcast to the network
        """
        if not block.broadcastable:
            raise BlockNotBroadcastableError("The specified block does not have any signature nor work attached. "
                                             "Can't be broadcasted to the network or updated locally.")

        if self._node_backend.is_online:
            # Node available. Bubble up the update of the account ledger to the node.
            response = self._node_backend.ask(NodeMessages.PROCESS(block.to_dict()))
            block_hash = response['hash']
            block_result = self[block_hash]
            account = block.account_owner
            account.offline_update_by_block(block)

        else:
            # No node available. Update the account ledger offline
            account = block.account_owner
            account.offline_update_by_block(block)
            block_result = block

        return block_result

    def __str__(self):
        blocks_info = self._blocks_telemetry()
        return f"Blocks ({str(self._node_backend)})\n\tBlocks count: {blocks_info['count']}; Unchecked: " \
               f"{blocks_info['unchecked']}; Cemented: {blocks_info['cemented']}"


class Block:
    """
    Represents a block in the Nano network.

    Gives an easy interface to access the metadata of the block.
    """

    def __init__(self, account, block_definition, node_backend=NO_NODE, work_server=None):
        """
        Constructor of the class

        :param block_definition:
            Dict returned by the Nano node containing all the information of the block.

        :param node_backend:
            Node backend to contact.

        :param work_server:
            Work server to generate work. Optional.
        """
        self._block_definition = block_definition
        self._node_backend = node_backend
        self._work_server = work_server
        self._account_owner = account

    @classmethod
    def from_dict(cls, dict_data, node_backend=NO_NODE, work_server=None):
        """
        Builds the block from a definition dictionary
        """
        from nanoblocks.account.account import Account
        account = Account(dict_data['account'], node_backend=node_backend, default_work_server=work_server)
        cls(account, dict_data, node_backend=node_backend, work_server=work_server)

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
    def account_owner(self):
        return self._account_owner

    def to_dict(self):
        """
        Retrieves the dictionary version of this block.
        """
        return self._block_definition

    def __str__(self):
        str_result = f"[Block #{self.height} from account {self.account_owner.address}]\n\tType: {self.type}\n\t" \
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
            "UTC").tz_convert(self._node_backend.timezone)

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
