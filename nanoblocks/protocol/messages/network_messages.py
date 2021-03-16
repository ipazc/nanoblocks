
class NetworkMessages:
    """
    This class crafts messages for the network section of the Nano RPC.

    All the messages listed here serves for interacting with the network itself.
    """

    @staticmethod
    def AVAILABLE_SUPPLY():
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#available_supply
        """
        return {
            "action": "available_supply"
        }

    @staticmethod
    def ACTIVE_DIFICULTY(include_trend=False):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#active_difficulty
        """
        return {
            "action": "active_difficulty",
            "include_trend": include_trend
        }

    @staticmethod
    def PEERS():
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#peers
        """
        return {
          "action": "peers"
        }

    @staticmethod
    def TELEMETRY():
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#telemetry
        """
        return {
            "action": "telemetry"
        }

    @staticmethod
    def REPRESENTATIVES(weight=True):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#representatives
        """
        return {
            "action": "representatives",
            "weight": weight
        }

    @staticmethod
    def REPRESENTATIVES_ONLINE(weight=True):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#representatives_online
        """
        return {
            "action": "representatives_online",
            "weight": weight
        }

