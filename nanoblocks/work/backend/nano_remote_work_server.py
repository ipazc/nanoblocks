import requests
from nanoblocks.account.account import Account
from nanoblocks.protocol.messages.work_server_messages import WorkServerMessages
from nanoblocks.work.work_server import WorkServer


class NanoRemoteWorkServer(WorkServer):
    """
    https://github.com/nanocurrency/nano-work-server
    """
    def __init__(self, work_server_http_url):
        self._work_server_http_url = work_server_http_url

    def generate_work_send(self, account: Account, work_difficulty=0xfffffff800000000, multiplier=1.0):
        return self._work_generate(account.frontier.hash, hex(work_difficulty)[2:], str(multiplier))['work']

    def generate_work_change(self, account: Account, work_difficulty=0xfffffff800000000, multiplier=1.0):
        return self._work_generate(account.frontier.hash, hex(work_difficulty)[2:], str(multiplier))['work']

    def generate_work_receive(self, account: Account, work_difficulty=0xfffffe0000000000, multiplier=1.0):
        hash_value = account.frontier.hash if not account.frontier.is_first else account.public_key
        return self._work_generate(hash_value, hex(work_difficulty)[2:], str(multiplier))['work']

    def _work_generate(self, hash_value, difficulty, multiplier=None):
        message = {
            "action": "work_generate",
            "hash": hash_value,
            "difficulty": difficulty,
            "multiplier": multiplier
        }

        response = requests.post(self._work_server_http_url, json=message)
        return response.json()

    def __repr__(self):
        return f"Remote Work server [{self._work_server_http_url}]"

    def __str__(self):
        return self.__repr__()
