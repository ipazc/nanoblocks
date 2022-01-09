from nanoblocks.base import NanoblocksClass
from nanoblocks.block.block_factory import BlockFactory

#TODO: expose exceptions in module __init__
from nanoblocks.exceptions.block_error import BlockError
from nanoblocks.exceptions.block_not_broadcastable_error import BlockNotBroadcastableError

# This is the first block in every uncreated account. It doesn't exist in the network.
_FIRST_BLOCK_DEFINITION = {
    "subtype": "initial",
    "confirmed": True,
    "account": "all",
    "amount": 0,
    "local_timestamp": "n/A",
    "height": 0,
    "link_as_account": None,
    "block_account": "nano_000000000000000000000000000000000000000000000000000000000000",
    "block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
    "contents": {
        "type": "initial",
        "link_as_account": None,
    },
}


class Blocks(NanoblocksClass):
    """
    Handles the block interaction through the node API
    """

    def __init__(self, nano_network):
        """
        Constructor of the class

        :param nano_network:
            A network object giving access to node and work backends.

        """
        super().__init__(nano_network)
        self._factory = BlockFactory(nano_network)

    @property
    def factory(self):
        return self._factory

    def __getitem__(self, block_hashes):
        """
        Retrieves information from specific blocks.

        :param block_hashes:
            Single hash or list of block hashes to retrieve from the network.
        """

        if type(block_hashes) is not list:
            block_hashes = [block_hashes]

        response = self.node_backend.blocks_info(block_hashes, include_not_found=True)['blocks']

        blocks = []

        for block_hash in block_hashes:

            if block_hash == _FIRST_BLOCK_DEFINITION['block_hash']:
                response = _FIRST_BLOCK_DEFINITION
                account = None

            else:
                response = response[block_hash]
                account = self.accounts.lazy_fetch(response['block_account'])

            block_info = {
                'type': response.get('subtype') or response.get('contents', {'type': 'Unknown'})['type'],
                'confirmed': response.get('confirmed', False),
                'account': response['block_account'],
                'amount': response['amount'],
                'local_timestamp': response['local_timestamp'],
                'height': response['height'],
                'link_as_account': response['contents'].get('link_as_account'),
                'representative': response['contents'].get('representative'),
                'hash': block_hash
            }

            blocks_factory = self.blocks.factory
            block = blocks_factory.build(account, block_info)
            blocks.append(block)

        return blocks[0] if len(blocks) == 1 and len(block_hashes) == 1 else blocks

    def __len__(self):
        """
        Returns the number of blocks in the network, in case the backend is available.
        """
        response = self._blocks_telemetry()

        if not response:
            response = {'count': 0}

        return int(response['count'])

    def _blocks_telemetry(self):
        return self.network.node_backend.block_count()

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
                >>> account1 = NanoNetwork.wallets["seed"].accounts[0]
                >>> account2 = NanoNetwork.wallets["seed"].accounts[0] # same account actually, but second instance
                >>> receive_block = account1.build_receive_block(work_hash)
                >>> NanoNetwork.blocks.broadcast(receive_block)
                >>> receive_block2 = account2.build_receive_block(work_hash2) ## Account2 does not reflect changes in account 1, even though they point to the same address!!

            Correct example:
                >>> account = NanoNetwork.wallets["seed"].accounts[0]
                >>> receive_block = account.build_receive_block(work_hash)
                >>> NanoNetwork.blocks.broadcast(receive_block)
                >>> receive_block2 = account.build_receive_block(work_hash2) ## Using the same account object is mandatory for correct chain updates.

            Alternatively:
                >>> account1 = NanoNetwork.wallets["seed"].accounts[0]
                >>> account2 = NanoNetwork.wallets["seed"].accounts[0] # same account actually, but second instance
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

        response = self.network.node_backend.process(block.to_dict())

        if 'error' in response:
            raise BlockError(response['error'], block=block)

        block_hash = response['hash']
        block_result = self[block_hash]
        account = block.account_owner
        account.offline_update_by_block(block)

        return block_result

    def __repr__(self):
        blocks_info = self._blocks_telemetry()
        return f"Blocks ({str(self.network.node_backend)})\n\tBlocks count: {blocks_info['count']}; Unchecked: " \
               f"{blocks_info['unchecked']}; Cemented: {blocks_info['cemented']}"

    def __str__(self):
        return self.__repr__()
