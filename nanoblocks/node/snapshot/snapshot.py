import joblib


class NodeSnapshot:
    """
    Represents a snapshot of the node blocks, accounts and history.

    A snapshot can be dumped to a file and loaded afterwards in an offline environment. This allows to generate
    offline transactions, which can be recorded back and serialized afterwards to be published in the future in an
    online environment.
    """
    def __init__(self, snapshot_struct):
        self._snapshot_struct = snapshot_struct

    @property
    def blocks(self):
        return self._snapshot_struct['snapshot_blocks']

    @property
    def accounts(self):
        return self._snapshot_struct['snapshot_accounts']

    @property
    def pending_blocks(self):
        return self._snapshot_struct['snapshot_pending_blocks']

    @property
    def history_blocks(self):
        return self._snapshot_struct['snapshot_history_blocks']

    @property
    def timestamp(self):
        return self._snapshot_struct['snapshot_date']

    @property
    def node_version(self):
        return self._snapshot_struct['snapshot_node_version']

    @property
    def node_source(self):
        return self._snapshot_struct['snapshot_node_source']

    def __repr__(self):
        return f"[SNAPSHOT {self.timestamp}; NODE_SOURCE: {self.node_source}] {len(self.accounts)} accounts; {len(self.blocks)} blocks."

    def __str__(self):
        return self.__repr__()

    def to_file(self, file):
        joblib.dump(self._snapshot_struct, file, compress=("lz4", 1))

    @classmethod
    def from_file(cls, file):
        snapshot_struct = joblib.load(file)
        instance = cls(snapshot_struct)
        return instance
