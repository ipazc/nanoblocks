from nanoblocks.block import Blocks
from nanoblocks.account import Accounts
from nanoblocks.currency import Amount
from nanoblocks.node import PUBLIC_FAILOVER_NODE
from nanoblocks.work import LOCAL_WORK_SERVER
from nanoblocks.wallet import Wallets


class NanoNetwork:
    """
    This class represents the Nano network and provides methods to easily interact with it.
    """
    def __init__(self, node_backend=PUBLIC_FAILOVER_NODE, work_server=LOCAL_WORK_SERVER, cache_accounts=True):
        """
        Creates an object that allows interaction with the Nano network through the specified node backend
        in several protocols (RPC through HTTP or WebSocket).

        This class allows you to view accounts, check transactions history from each, and create new wallets and
        accounts.

        :param node_backend:
            Node backend that serves as the link point for accessing the network.

        :param work_server:
            API REST url of a work server. Useful if it is wanted to have work automatically computed when building
            blocks.

        :param cache_accounts:
            Boolean that specifies whether this instance is going to cache accounts or not.
            Caching accounts allows to reuse the same account object in many places, meaning that a change in one
            affects immediately in every variable that references it.
        """
        self._node_backend = node_backend
        self._work_server = work_server

        self._accounts = Accounts(nano_network=self, cache_accounts=cache_accounts)
        self._wallets = Wallets(nano_network=self)
        self._blocks = Blocks(nano_network=self)

    @property
    def work_server(self):
        return self._work_server

    @work_server.setter
    def work_server(self, new_work_server):
        self._work_server = new_work_server

    @property
    def node_backend(self):
        """
        Returns the Node object that contains information of the node.
        """
        return self._node_backend

    @node_backend.setter
    def node_backend(self, new_node_backend):
        self._node_backend = new_node_backend

    @property
    def accounts(self):
        """
        Handles the account API for the Nano protocol.
        By default all the accounts that can be accessed are read-only.

        An existing account can be accessed as follows:
        `wallet = nano_network.accounts[nano_address]`

        If a private key is available, it can be unlocked with the method `unlock(priv_key)`.
        """
        return self._accounts

    @property
    def wallets(self):
        """
        Handles the wallets API for the Nano protocol.
        Allows to create new accounts or manage existing ones.

        A new account can be created as follows:
        `wallet = nano_network.wallets.create()`

        An existing wallet can be accessed as follows:
        `wallet = nano_network.wallets[seed]`
        """
        return self._wallets

    @property
    def blocks(self):
        """
        Handles the blocks API for the Nano Protocol.
        Allows to peek blocks and broadcast new blocks to the network.

        A new block can be broadcasted as follows:
        `block = nano_network.blocks.broadcast(state_block)`
        """
        return self._blocks

    def active_dificulty(self, include_trend=False):
        """
        Returns the difficulty values (16 hexadecimal digits string, 64 bit) for the minimum required on the network
        (network_minimum) as well as the current active difficulty seen on the network (network_current,
        10 second trended average of adjusted difficulty seen on prioritized transactions, refreshed every 500ms)
        which can be used to perform rework for better prioritization of transaction processing.

        A multiplier of the network_current from the base difficulty of network_minimum is also provided for comparison.
        Network_receive_minimum and network_receive_current are also provided as lower thresholds exclusively for
        receive blocks.

        :param include_trend:
            Boolean, false by default. Returns the trend of difficulty seen on the network as a list of multipliers.
            Sampling occurs every 500ms. The list is ordered such that the first value is the most recent sample.
        """
        response = self._node_backend.active_difficulty(include_trend)
        return response

    @property
    def available_supply(self):
        """
        Returns the amount of NANO that are available in the public supply.
        """
        response = self._node_backend.available_supply()
        amount = Amount(response['available'], unit="raw")

        return amount

    @property
    def peers(self):
        """
        Returns a list of pairs of online peer IPv6:port and its node protocol network version
        """
        response = self._node_backend.peers()
        return response

    @property
    def telemetry(self):
        """
        Return metrics from other nodes on the network. By default, returns a summarized view of the whole network.
        """
        response = self._node_backend.telemetry()

        if not response:
            response = {'peer_count': 0}

        return response

    @property
    def representatives(self):
        """
        Returns a list of representatives accounts of the network.
        """
        representatives = self._node_backend.representatives()

        representative_accounts = self.accounts[list(representatives)]

        for (representative_address, weight_value), representative_account in zip(representatives.items(), representative_accounts):
            representative_account._account_info['weight'] = weight_value

        return representative_accounts

    @property
    def representatives_count(self):
        """
        Retrieves the number of representatives in the network.
        """
        return len(self._node_backend.representatives()['representatives'])

    @property
    def representatives_online(self):
        """
        Returns a list of online representatives accounts of the network.
        The ones that recently voted.
        """
        representatives = self._node_backend.representatives_online()['representatives']

        representative_accounts = self.accounts[list(representatives)]

        for (representative_address, weight_value), representative_account in zip(representatives.items(), representative_accounts):
            representative_account._account_info['weight'] = weight_obj['weight']

        return representative_accounts

    @property
    def representatives_online_count(self):
        """
        Retrieves the number of online representatives in the network.
        """
        return len(self._node_backend.representatives_online(weight=False)['representatives'])

    def __str__(self):
        return f"[Nano Network] {len(self)} peers; {len(self.accounts)} accounts; node backend: \n {str(self._node_backend)}"

    def __repr__(self):
        return str(self)

    def __len__(self):
        """
        Returns the number of active nodes in the network
        """
        return int(self.telemetry.get('peer_count', 0))
