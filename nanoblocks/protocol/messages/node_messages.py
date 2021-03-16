
class NodeMessages:
    """
    This class crafts messages for the node section of the Nano RPC.

    All the messages listed here serves for interacting with the node itself.
    """

    @staticmethod
    def VERSION():
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#version
        """
        return {
            "action": "version"
        }

    @staticmethod
    def BOOTSTRAP_INFO():
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#bootstrap_status
        """
        return {
            "action": "bootstrap_status"
        }

    @staticmethod
    def BLOCK_COUNT():
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#block_count
        """
        return {
            "action": "block_count"
        }

    @staticmethod
    def BLOCK_INFO(block_hash):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#block_info
        """
        return {
            "action": "block_info",
            "json_block": "true",
            "hash": block_hash
        }

    @staticmethod
    def PROCESS(block_definition, subtype=None):
        """
        https://docs.nano.org/commands/rpc-protocol/#process
        """
        message = {
          "action": "process",
          "json_block": "true",
          "block": block_definition
        }

        if subtype:
            message.update({'subtype': subtype})

        return message


class NodeWebSocketMessages:
    """
    This class crafts messages for the node websockets.
    """

    @staticmethod
    def CONFIRMATION(addresses):
        """
        Subscription message for incoming transactions under websocket.
        """
        message = {
            "action": 'subscribe',
            "topic": 'confirmation',
            "ack": True,
            "options": {
                "accounts": addresses
            }
        }

        return message
