from nanoblocks.base import NanoblocksClass
from nanoblocks.wallet.wallet import Wallet


class Wallets(NanoblocksClass):
    """
    Represents a set of wallets in the Nano ecosystem.

    It allows to create or use existing wallets by their seed or mnemonic.
    """

    def create(self):
        """
        Creates a new wallet with a randomized seed.
        """
        return Wallet(nano_network=self.network)

    def __getitem__(self, seed_or_wordlist):
        """
        Accesses a wallet by the given seed or mnemonic

        :param seed_or_wordlist:
            seed string or word list to access the wallet.
        """

        if type(seed_or_wordlist) is list:
            wallet = Wallet.from_mnemonic(words_list=seed_or_wordlist, nano_network=self.network)
        else:
            wallet = Wallet(nano_network=self.network, seed=seed_or_wordlist)

        return wallet

    def __repr__(self):
        return "Wallet creator (NanoBlocks)"

    def __str__(self):
        return self.__repr__()
