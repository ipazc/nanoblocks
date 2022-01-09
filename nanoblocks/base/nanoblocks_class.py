

class NanoblocksClass:
    """
    Global class that should be inherited by any Nanoblocks class that requires access to the network.
    """
    def __init__(self, nano_network):
        self._nano_network = nano_network

    @property
    def network(self):
        return self._nano_network

    @property
    def node_backend(self):
        return self.network.node_backend

    @property
    def work_server(self):
        return self.network.work_server

    @property
    def accounts(self):
        return self.network.accounts

    @property
    def blocks(self):
        return self.network.blocks
