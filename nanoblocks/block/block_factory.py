from nanoblocks.block.block import Block
from nanoblocks.block.block_receive import BlockReceive
from nanoblocks.block.block_send import BlockSend


class BlockFactory:

    BLOCK_PROTO_MAP = {
        "receive": BlockReceive,
        "send": BlockSend
    }

    def __init__(self, node_backend, work_server):
        self._node_backend = node_backend
        self._work_server = work_server

    def build_block_object(self, account, block_definition):
        block_object = self.BLOCK_PROTO_MAP.get(block_definition['type'], Block)
        block_instance = block_object(account, block_definition, node_backend=self._node_backend, work_server=self._work_server)
        return block_instance
