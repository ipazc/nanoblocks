import qrcode

from nanoblocks.base import NanoblocksClass
from nanoblocks.currency import Amount
from nanoblocks.utils import TimedVariable


class Payment(NanoblocksClass):
    """
    Gives an easy interface to handle payments for a given account.
    """

    def __init__(self, account_owner, amount, nano_network):
        super().__init__(nano_network)

        if amount is None:
            raise ValueError("Requesting a payment requires an amount.")

        self._account_owner = account_owner
        self._amount = Amount(amount)
        """
        
        # First we ensure the account is up-to-date
        self._account_owner.update()
        
        # We take the current balance
        self._initial_balance = self._account_owner.balance.as_unit("raw")
        self._last_confirmation_hash = None

        if self._account_owner.is_virtual:
            self._account_owner.pending_transactions.update()
            if len(self._account_owner.pending_transactions) > 0:
                self._last_confirmation_hash = self._account_owner.pending_transactions[0].hash
        """

    @property
    def uri(self):
        """
        Generates the payment URI
        """
        uri = f"nano:{self._account_owner.address}"

        if self._amount is not None:
            uri += f"?amount={str(self._amount.as_unit('raw'))}"

        return uri

    @property
    def qr_code(self):
        """
        Retrieves a PIL image with the QR code for the payment that can be scanned by modern wallets.
        """
        return qrcode.make(self.uri)

    def wait(self, timeout_seconds=None):
        """
        Waits for the payment to be done.

        The expected payment must match the exact amount.

        :param timeout_seconds:
            Time in seconds to wait for the payment. Set it to None to wait indefinitely.

        :return:
            Returns the block that needs to be confirmed.
        """
        payment_block = TimedVariable(None)

        def callback(block, payment_storage):
            if block.amount == self._amount:
                payment_storage.value = block
                return False  # we received it, so we stop returning False
            return True

        with self.network.track_confirmation_blocks([self._account_owner],
                                                    callback,
                                                    payment_storage=payment_block) as tracking:
            tracking.join(timeout_seconds)

        if payment_block.value is None:
            raise TimeoutError(f"No payment fulfilled in time ({timeout_seconds} seconds)")

        block = payment_block.value
        block.wait_for_confirmation()
        return block
