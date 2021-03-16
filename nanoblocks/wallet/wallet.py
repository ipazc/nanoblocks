from nanoblocks.account.account import Account
from nanoblocks.node.nanonode import NO_NODE
from nanoblocks.protocol.crypto.crypto_functions import make_seed, derive_seed, derive_bip39, account_privkey, \
    account_pubkey, account_address


class Wallets:
    """
    Represents a set of wallets in the Nano ecosystem.

    It allows to create or use existing wallets by their seed or mnemonic.
    """

    def __init__(self, node_backend, work_server=None):
        """
         Instantiates the class.

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the creation of accounts without access to a Nano node
            or even internet.

        :param work_server:
            Work server to use by default. Optional
        """
        self._node_backend = node_backend
        self._work_server = work_server

    def create(self):
        """
        Creates a new wallet with a randomized seed.
        """
        return Wallet(node_backend=self._node_backend)

    def __getitem__(self, seed_or_wordlist):
        """
        Accesses a wallet by the given seed or mnemonic

        :param seed_or_wordlist:
            seed string or word list to access the wallet.
        """

        if type(seed_or_wordlist) is list:
            wallet = Wallet.from_mnemonic(seed_or_wordlist, node_backend=self._node_backend,
                                          work_server=self._work_server)
        else:
            wallet = Wallet(seed_or_wordlist, node_backend=self._node_backend, work_server=self._work_server)

        return wallet


class Wallet:
    """
    Represents a Wallet in the Nano ecosystem.

    This is class does not use any backend for creating or managing account keys.

    Keep in mind that this class holds private keys, thus should be secured.
    """

    def __init__(self, seed=None, node_backend=NO_NODE, work_server=None):
        """
        Creates a new Wallet.

        :param seed:
            Seed to use for the accounts management within the wallet.
            If None, a random seed will be sampled from a valid cryptographic randomizer.

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the creation of accounts without access to a Nano node
            or even internet.

        :param work_server:
            Work server ot use by default. Optional.
        """
        if seed is None:
            seed = make_seed()

        self._seed = seed
        self._node_backend = node_backend
        self._work_server = work_server

    @classmethod
    def from_mnemonic(cls, words_list, node_backend=NO_NODE, work_server=None):
        """
        Instantiates this class based on a bip39 mnemonic list of keywords.

        :param words_list:
            List of 24 words to use for importing the seed.

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the creation of accounts without access to a Nano node
            or even internet.

        :param work_server:
            Work server ot use by default. Optional.
        """
        if len(words_list) != 24:
            raise KeyError("The length of the list should be 24, no more, no less words")

        seed = derive_seed(words_list)

        return cls(seed, node_backend=node_backend, work_server=work_server)

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
        return WalletAccounts(self._seed, self._node_backend, work_server=self._work_server)


class WalletAccounts:
    """
    Class to handle the automatic creation of accounts inside a wallet
    """

    def __init__(self, seed, node_backend=NO_NODE, work_server=None):
        """
        Instantiates this class.

        :param seed:
            the wallet seed required to create accounts on demand.

        :param node_backend:
            A Node object pointing to a working Nano node.
            Note that this class may work off-line, which allows the creation of accounts without access to a Nano node
            or even internet.

        :param work_server:
            Server for work computation.
        """
        self._seed = seed
        self._node_backend = node_backend
        self._work_server = work_server

    def __getitem__(self, account_index):
        """
        Retrieves the account given at a specific position within this wallet seed.

        :param account_index:
            index of the account. Could be any value between 1 and 2**32.
        """
        account_private_key = account_privkey(self._seed, account_index)
        account_public_key = account_pubkey(account_private_key)
        account_public_address = account_address(account_public_key)

        account = Account(account_public_address, self._node_backend, default_work_server=self._work_server)
        account.unlock(account_private_key)
        account.update()

        return account

    def __setitem__(self, key, value):
        raise NotImplementedError("Manually setting an account is not supported by the Nano Network")
