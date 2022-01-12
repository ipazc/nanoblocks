import hashlib
import random
from nanoblocks.account.account import Account
from nanoblocks.work.work_server import WorkServer
import warnings


class NanoLocalWorkServer(WorkServer):
    """
    Local work generation.
    No remote server required, but slower.
    """
    def generate_work_send(self, account: Account, work_difficulty=0xfffffff800000000, multiplier=1.0):
        warnings.warn("Generating work locally for send blocks might take a lot of time (in the order of minutes). Using a remote work server with a GPU is highly encouraged for this task.")
        return self._work_generate(account.frontier.hash, hex(work_difficulty)[2:], multiplier)

    def generate_work_change(self, account: Account, work_difficulty=0xfffffff800000000, multiplier=1.0):
        warnings.warn("Generating work locally for change of representative might take a lot of time (in the order of minutes). Using a remote work server with a GPU is highly encouraged for this task.")
        return self._work_generate(account.frontier.hash, hex(work_difficulty)[2:], multiplier)

    def generate_work_receive(self, account: Account, work_difficulty=0xfffffe0000000000, multiplier=1.0):
        hash_value = account.frontier.hash if not account.frontier.is_first else account.public_key
        return self._work_generate(hash_value, hex(work_difficulty)[2:], multiplier)

    @staticmethod
    def _work_generate(_hash, difficulty, multiplier=None):
        """
        Checks whether work is valid for hash.
        Extracted from https://github.com/npy0/nanopy/blob/c65a752bd21168ef5e4be25fc4658381d4df4f22/nanopy/__init__.py#L251
        Adapted for nanoblocks.

        :param hash:
            64 hex-char hash
        :param difficulty:
            16 hex-char difficulty
        :param multiplier:
            positive number, overrides difficulty
        :return:
            16 hex-char work
        """
        assert len(_hash) == 64
        _hash = bytes.fromhex(_hash)
        b2b_h = bytearray.fromhex("0" * 16)

        if multiplier is not None:
            difficulty = NanoLocalWorkServer._from_multiplier(difficulty, multiplier)

        difficulty = bytes.fromhex(difficulty)

        work = None

        while b2b_h < difficulty:

            work = bytearray((random.getrandbits(8) for i in range(8)))

            for r in range(0, 256):
                work[7] = (work[7] + r) % 256
                b2b_h = bytearray(hashlib.blake2b(work + _hash, digest_size=8).digest())
                b2b_h.reverse()
                if b2b_h >= difficulty:
                    break

        if work is not None:
            work.reverse()
            result = work.hex()

        else:
            result = None

        return result

    @staticmethod
    def _from_multiplier(difficulty_base, multiplier):
        """
        Get difficulty from multiplier.
        Extracted from https://github.com/npy0/nanopy/blob/c65a752bd21168ef5e4be25fc4658381d4df4f22/nanopy/__init__.py#L171
        Adapted for nanoblocks.

        :param difficulty_base:
            16 hex-char base difficulty

        :param multiplier:
            positive number

        :return:
            16 hex-char difficulty
        """
        return format(
            int((int(difficulty_base, 16) - (1 << 64)) / multiplier + (1 << 64)), "016x"
        )

    def __repr__(self):
        return f"Local Work server"

    def __str__(self):
        return self.__repr__()
