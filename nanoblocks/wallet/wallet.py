from nanoblocks.base import NanoblocksClass
from nanoblocks.utils.crypto_functions import make_seed, derive_seed, derive_bip39, fill_bip39_words
from nanoblocks.wallet.wallet_accounts import WalletAccounts


class Wallet(NanoblocksClass):
    """
    Represents a Wallet in the Nano ecosystem.

    This is class does not use any backend for creating or managing account keys.

    Keep in mind that this class holds private keys, thus should be secured.
    """

    def __init__(self, nano_network, seed=None):
        """
        Creates a new Wallet.

        :param nano_network:
            A network object giving access to node and work backends.

        :param seed:
            Seed to use for the accounts management within the wallet.
            If None, a random seed will be sampled from a valid cryptographic randomizer.

        """
        super().__init__(nano_network)

        if seed is None:
            seed = make_seed()

        self._seed = seed

    @classmethod
    def from_mnemonic(cls, words_list, nano_network):
        """
        Instantiates this class based on a bip39 mnemonic list of keywords.

        This method tolerates missing words in the list (set to None). In case it detects missing words, the method
        will attempt to refill them with a random word.

        :param words_list:
            List of 24 words to use for importing the seed.

        :param nano_network:
            A network object giving access to node and work backends.

        """
        if len(words_list) != 24:
            raise KeyError("The length of the list should be 24, no more, no less words")

        if any([x is None for x in words_list]):
            words_list = fill_bip39_words(words_list)

        seed = derive_seed(words_list)

        return cls(nano_network=nano_network, seed=seed)

    @property
    def seed(self):
        """
        Retrieves the seed of this wallet
        """
        return self._seed

    @property
    def mnemonic(self):
        """
        Derives the bip39 mnemonic for the seed of this wallet.
        """
        return derive_bip39(self._seed)

    @property
    def accounts(self):
        """
        Retrieves access to the accounts from this wallet.
        """
        return WalletAccounts(self._seed, nano_network=self.network)

    def __repr__(self):
        return "Nano Wallet (Type wallet.accounts[integer_index] to access an account)."

    def __str__(self):
        return self.__repr__()
