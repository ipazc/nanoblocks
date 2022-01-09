from nanoblocks.base import NanoblocksClass
from nanoblocks.block.block import Block
from nanoblocks.block.block_change import BlockChange
from nanoblocks.block.block_receive import BlockReceive
from nanoblocks.block.block_send import BlockSend
from nanoblocks.block.block_state import BlockState


class BlockFactory(NanoblocksClass):

    BLOCK_PROTO_MAP = {
        "receive": BlockReceive,
        "send": BlockSend,
        "change": BlockChange,
        "state": BlockState,
        "initial": Block,
        "unknown": Block,
    }

    def build(self, account, block_definition, type_key='type'):
        block_object = self.BLOCK_PROTO_MAP.get(block_definition.get(type_key, BlockChange), Block)
        block_instance = block_object(account, block_definition, nano_network=self.network)
        return block_instance
