from nanoblocks.account.account import Account


class WorkServer:
    """
    Represents a work server.
    Allows to generate work for a given account by using an external work server.
    """

    def generate_work_send(self, account: Account, work_difficulty=None, multiplier=1.0):
        pass

    def generate_work_change(self, account: Account, work_difficulty=None, multiplier=1.0):
        pass

    def generate_work_receive(self, account: Account, work_difficulty=None, multiplier=1.0):
        pass
