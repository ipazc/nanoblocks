import asyncio
import concurrent
import json
import time
from datetime import datetime

import qrcode
import websockets

from nanoblocks.block.block import Blocks
from nanoblocks.currency import Amount
from nanoblocks.exceptions.payment_timeout_error import PaymentTimeoutError
from nanoblocks.protocol.messages.node_messages import NodeWebSocketMessages


async def subscribe_to_account(uri, addresses, payment_init, timeout, desired_amount):

    subscription = NodeWebSocketMessages.CONFIRMATION(addresses)
    paid = False
    paid_hash = None

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps(subscription))

        while not paid and (datetime.now() - payment_init).total_seconds() < timeout:
            result = json.loads(await asyncio.wait_for(ws.recv(), timeout))

            if result.get('topic', None) != "confirmation":
                continue

            if not desired_amount or Amount(result['message']['amount']) == desired_amount:
                # Payment received!
                paid = True
                paid_hash = result['message']['hash']

    return paid, paid_hash


class Payment:
    """
    Gives an easy interface to handle payments for a given account.
    """

    def __init__(self, account_owner, amount, node_backend, work_server):
        self._account_owner = account_owner
        self._amount = amount
        self._node_backend = node_backend
        self._work_server = work_server

        # First we ensure the account is up-to-date
        self._account_owner.update()

        # We take the current balance
        self._initial_balance = self._account_owner.balance.as_raw()
        self._last_confirmation_hash = None

        if self._account_owner.is_virtual:
            self._account_owner.pending_transactions.update()
            if len(self._account_owner.pending_transactions) > 0:
                self._last_confirmation_hash = self._account_owner.pending_transactions[0].hash

    @property
    def uri(self):
        """
        Generates the payment URI
        """
        return f"nano:{self._account_owner.address}?amount={(self._amount.as_raw().int_str())}"

    @property
    def qr_code(self):
        """
        Retrieves a PIL image with the QR code for the payment that can be scanned by modern wallets.
        """
        return qrcode.make(self.uri)

    def wait(self, timeout=30, peek_interval=5, match_exact_quantity=True):
        """
        Waits for the payment to be done.

        If a websocket is available, it will subscribe itself to the account for incoming transactions.
        Otherwise, a peek every `peek_seconds` will be used instead.

        The expected payment must match the exact amount.

        If timedout, call this method again to resume checking. If payment was done between calls stopped by timeout,
        it will still be able to notify it.

        :param timeout:
            Time in seconds to wait for the payment. Set it to 0 to wait indefinitely.

        :param peek_seconds:
            Peek interval when no websocket is available.

        :param match_exact_quantity:
            Boolean flag to force wait until the payment matches the expected quantity

        :return:
            Returns the block that needs to be confirmed.
        """

        self._account_owner.update()

        if (self._account_owner.balance - self._initial_balance) == 0:
            paid = False

            payment_init = datetime.now()

            if self._node_backend.ws_available:
                try:

                    paid, paid_hash = asyncio.get_event_loop().run_until_complete(subscribe_to_account(self._node_backend.ws, [self._account_owner.address], payment_init, timeout, self._amount))

                except concurrent.futures._base.TimeoutError:
                    raise PaymentTimeoutError(f"Payment timeout ({timeout} seconds)") from None

                last_pending_block = Blocks(self._node_backend, self._work_server)[paid_hash]

            else:

                while not paid and (datetime.now() - payment_init).total_seconds() < timeout:
                    time.sleep(peek_interval)

                    if self._account_owner.is_virtual:
                        # If it is virtual (a new account) we need to check the pending blocks instead
                        pending_transactions = self._account_owner.pending_transactions.update(minimum_quantity=self._amount, count=100)
                        paid = len(self._account_owner.pending_transactions) > 0
                    else:
                        self._account_owner.update()
                        new_balance = self._account_owner.balance
                        paid = (new_balance - self._initial_balance) >= self._amount

                if not paid:
                    raise PaymentTimeoutError(f"Payment timeout ({timeout} seconds)") from None

                # We search the last pending block with this quantity
                if match_exact_quantity:
                    self._account_owner.pending_transactions.update(minimum_quantity=self._amount)
                else:
                    self._account_owner.pending_transactions.update()

                last_pending_block = self._account_owner.pending_transactions[0]

        else:
            last_pending_block = self._account_owner.pending_transactions[0]

        return last_pending_block
