from nanoblocks.base import NanoblocksClass
from nanoblocks.protocol.crypto import account_privkey, account_pubkey, account_address


class WalletAccounts(NanoblocksClass):
    """
    Class to handle the automatic creation of accounts inside a wallet
    """

    def __init__(self, seed, nano_network):
        """
        Instantiates this class.

        :param seed:
            the wallet seed required to create accounts on demand.

        :param nano_network:
            A network object giving access to node and work backends.

        """
        super().__init__(nano_network)
        self._seed = seed

    def __repr__(self):
        return "Accounts from Nano Wallet (accounts can be accessed through indexes)"

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, account_index):
        """
        Retrieves the account given at a specific position within this wallet seed.

        :param account_index:
            index of the account. Could be any value between 1 and 2**32.
        """
        account_private_key = account_privkey(self._seed, account_index)
        account_public_key = account_pubkey(account_private_key)
        account_public_address = account_address(account_public_key)

        account = self.accounts[account_public_address]
        account.unlock(account_private_key)

        if account.last_update_elapsed_seconds > 15:
            account.update()

        return account

    def __setitem__(self, key, value):
        raise NotImplementedError("Manually setting an account is not supported by the Nano Network")
