from nanoblocks import rcParams
from nanoblocks.account.account import Account
from nanoblocks.base import NanoblocksClass
from nanoblocks.utils.time import now


class Accounts(NanoblocksClass):
    """
    Handles the account interactions
    """

    def __init__(self, nano_network, cache_accounts=True):
        """
        Constructor of the class

        :param nano_network:
            A network object giving access to node and work backends.

        :param cache_accounts:
            Boolean that specifies whether this instance is going to cache accounts or not.
            Caching accounts allows to reuse the same account object in many places, meaning that a change in one
            affects immediately in every variable that references it.

        """
        super().__init__(nano_network)
        self._cached_accounts = {}
        self._cache_enabled = cache_accounts
        self._last_cache_cleanup = now()

    def is_cached(self, account_address):
        """
        Checks whether a given account address is cached or not.

        :param account_address: a "nano_..." address

        :return: True if the account is cached. False otherwise.
        """
        return account_address in self._cached_accounts

    def cleanup_cache(self):
        """
        Clears the cache objects when corresponding accounts do not hold any references.
        """
        if self._cache_enabled:
            new_cache = {}

            for account_address in self._cached_accounts:
                account = self._cached_accounts[account_address]

                # When account has 3 refs (this account, the stored in cache and an unknown one) then it has lost all
                # the needed references, so we can clean it up.
                refcount = account.refcount()

                if refcount > 3:
                    new_cache[account_address] = account

            self._cached_accounts = new_cache
            self._last_cache_cleanup = now()

    def _cache_accounts(self, accounts_dict):
        """
        Caches the specified accounts in the internal accounts cache.

        In case cleanup is required (checked by rcParams['account.cache.cleanup_interval_seconds']) the cache is
        cleaned up from the account references that do not hold longer than specified seconds.

        :param accounts_dict: a dictionary containing {nano_address:Account} format.
        """
        self._cached_accounts.update(accounts_dict)

        # Let's check if a cleanup is required
        cache_cleanup_interval_seconds = rcParams['accounts.cache.cleanup_interval_seconds']

        cleanup_required = (now() - self._last_cache_cleanup).total_seconds() > cache_cleanup_interval_seconds

        if cleanup_required:
            self.cleanup_cache()

    def __getitem__(self, nano_account_address):
        """
        Retrieves nanoblocks accounts from the network, given the nano address.

        It may be provided a single string of the nano account or a list of many nano accounts. If a list is provided,
        the result information of the accounts might be stripped to the minimal supported by bulk operations in the
        backend. For instance, the last modification and the representative properties are not retrieved.

        :param nano_account_address:
            Address of the account. Eg "nano_..."
                or
            A list of addresses. Eg ["nano_account1", "nano_account2", ...]
        """
        if type(nano_account_address) is list:

            # Bulk retrieval of accounts. We take minimum information for each account. If a cache is enabled, we try to
            # fetch them first from the cache. In case of a cache miss, we instance the account.
            accounts = {address: (self._cached_accounts.get(address) or Account(address, nano_network=self.network, initial_update=False))
                        for address in nano_account_address}

            balances = self.node_backend.accounts_balances(nano_account_address)['balances']
            frontiers = self.node_backend.accounts_frontiers(nano_account_address)['frontiers']

            for nano_address in nano_account_address:
                nano_account = accounts[nano_address]
                nano_balances = balances[nano_address]
                nano_frontier = frontiers[nano_address]

                dict_update = {
                    'balance': nano_balances['balance'],
                    'pending': nano_balances['pending'],
                    'frontier': nano_frontier,
                }

                # We don't override block_count or modified_timestamp in cached accounts.
                if nano_address in self._cache_accounts:
                    dict_update.update({
                        'block_count': 'unknown',
                        'modified_timestamp': 0  # TODO: maybe we should update modified timestamp and set now() here?
                    })

                nano_account.offline_update(dict_update)

            result = accounts
        else:
            result = self._cached_accounts.get(nano_account_address) or Account(nano_account_address, nano_network=self.network)

        # If there is a cache enabled, we cache the accounts objects so that further calls reuse the same object.
        if self._cache_enabled:
            self._cache_accounts(result if type(result) is dict else {nano_account_address: result})

        return result

    def lazy_fetch(self, nano_account_address):
        """
        Fetchs an account lazily, without querying the node.

        If the cache is enabled, the account will be fetched from the cache in case there is a cache hit.

        The account will have no information attached (only address and pub/priv key) unless it was previously cached.

        :param nano_account_address:
            Nano account address with format "nano_..."

        :return:
            Nano Account object.
        """
        if type(nano_account_address) is Account:
            account = nano_account_address
            nano_account_address = account.address
        else:
            account = self._cached_accounts.get(nano_account_address) or Account(nano_account_address, self.network, initial_update=False)

        # If there is a cache enabled, we cache the accounts objects so that further calls reuse the same object.
        if self._cache_enabled:
            self._cache_accounts({nano_account_address: account})

        return account

    def __len__(self):
        """
        Returns the number of accounts registered in the network, in case the backend is available.
        """
        response = self.node_backend.telemetry()

        if not response:
            response = {'account_count': 0}

        return int(response.get('account_count', 0))

    def __str__(self):
        return f"{str(self.node_backend)} Total accounts: {len(self)}"

    def from_private_key(self, account_privatekey):
        """
        Retrieves a nanoblocks account given the private key.
        Note that this account is fully controllable, since it can sign transactions.

        :param account_privatekey:
            Private key of the account (string of 64 values in hexadecimal)
        """
        return Account.from_priv_key(account_privatekey, nano_network=self.network)

    def from_public_key(self, account_publickey):
        """
        Retrieves a nanoblocks account given the public key.

        :param account_publickey:
            Public key of the account (string of 64 values in hexadecimal)
        """
        return Account.from_pub_key(account_publickey, nano_network=self.network)
