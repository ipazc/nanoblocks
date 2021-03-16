
class WorkServerMessages:
    """
    This class crafts messages for the Nano Work Server API.

    """

    @staticmethod
    def WORK_GENERATE(hash, difficulty, multiplier):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#version
        """
        return {
            "action": "work_generate",
            "hash": hash,
            "difficulty": difficulty,
            "multiplier": multiplier
        }
