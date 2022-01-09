
class BlockError(Exception):
    def __init__(self, message, block, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self._block = block

    @property
    def block(self):
        return self._block
