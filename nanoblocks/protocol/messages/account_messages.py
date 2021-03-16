
class AccountMessages:
    """
    This class crafts messages for the Account section of the Nano RPC.

    All the messages listed here serves for interacting with the accounts.
    """

    @staticmethod
    def ACCOUNT_INFO(nano_address, representative=False, weight=False, pending=True):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#account_info
        """
        return {
            "action": "account_info",
            "representative": representative,
            "account": nano_address,
            "weight": weight,
            "pending": pending
        }

    @staticmethod
    def ACCOUNT_KEY(nano_address):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#account_key
        """
        return {
            "action": "account_key",
            "account": nano_address
        }

    @staticmethod
    def ACCOUNT_GET(account_pub_key):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#account_get
        """
        return  {
            "action": "account_get",
            "account": account_pub_key
        }

    @staticmethod
    def ACCOUNT_REPRESENTATIVE(nano_address):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#account_representative
        """
        return {
            "action": "account_representative",
            "account": nano_address
        }

    @staticmethod
    def ACCOUNT_WEIGHT(nano_address):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#account_weight
        """
        return {
            "action": "account_weight",
            "account": nano_address
        }

    @staticmethod
    def ACCOUNT_BLOCKS(nano_address):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#account_block_count
        """

        return {
            "action": "account_block_count",
            "account": nano_address
        }

    @staticmethod
    def ACCOUNT_HISTORY(nano_address, count=10, previous=None, head=None, reverse=None, offset=None):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#account_history
        """

        message = {
            "action": "account_history",
            "account": nano_address,
            "count": count
        }

        if previous:
            message['head'] = previous

        if head:
            message['head'] = head

        if reverse:
            message['reverse'] = reverse

        if offset:
            message['offset'] = offset

        return message

    @staticmethod
    def ACCOUNTS_BALANCES(addresses):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#accounts_balances
        """

        return {
            "action": "accounts_balances",
            "accounts": addresses
        }

    @staticmethod
    def ACCOUNTS_FRONTIERS(addresses):
        """
        Source: https://docs.nano.org/commands/rpc-protocol/#accounts_frontiers
        """

        return {
            "action": "accounts_frontiers",
            "accounts": addresses
        }

    @staticmethod
    def ACCOUNTS_PENDING(accounts, count=1, sorting=True, minimum_balance=None):
        """
        https://docs.nano.org/commands/rpc-protocol/#accounts_pending
        """
        message = {
            "action": "accounts_pending",
            "accounts": accounts,
            "count": count,
            "source": "true",
            "sorting": sorting,
            "threshold": minimum_balance,
            "include_only_confirmed": "true"
        }

        return message
