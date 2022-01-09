import joblib


class TapeRecord(list):
    """
    Stores all the transactions performed in the node (blocks sent and received).

    This tape record can be inputted into any `node.process()` call method and all its operations will be broadcast
    into the specified node.
    """
    def __repr__(self):
        return f"[TAPE_RECORD] {len(self)} operations tracked."

    def __str__(self):
        return self.__repr__()

    def to_file(self, file):
        joblib.dump(self, file, compress=("lz4", 1))

    @staticmethod
    def from_file(cls, file):
        return joblib.load(file)
