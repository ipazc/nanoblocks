import requests
from nanoblocks.account.account import Account
from nanoblocks.protocol.messages.work_server_messages import WorkServerMessages
from nanoblocks.work.work_server import WorkServer


class NanoWorkServer(WorkServer):
    """
    https://github.com/nanocurrency/nano-work-server
    """
    def __init__(self, work_server_api):
        self._work_server_api = work_server_api

    def generate_work_send(self, account: Account, work_difficulty=0xfffffff800000000, multiplier=1.0):
        return self.ask(WorkServerMessages.WORK_GENERATE(account.frontier.hash, hex(work_difficulty)[2:], str(multiplier)))['work']

    def generate_work_change(self, account: Account, work_difficulty=0xfffffff800000000, multiplier=1.0):
        return self.ask(WorkServerMessages.WORK_GENERATE(account.frontier.hash, hex(work_difficulty)[2:], str(multiplier)))['work']

    def generate_work_receive(self, account: Account, work_difficulty=0xfffffe0000000000, multiplier=1.0):
        return self.ask(WorkServerMessages.WORK_GENERATE(account.frontier.hash, hex(work_difficulty)[2:], str(multiplier)))['work']

    def ask(self, message):
        """
        Makes a call to the rest api with the specified message and returns the result.

        :param message:
            A message defined in any file inside `nanoblocks/protocol/messages/nano_server_messages`.
        """
        response = requests.post(self._work_server_api, json=message)
        return response.json()
