import asyncio
import json
import time
from datetime import datetime

import qrcode
import websockets

from nanoblocks.base import NanoblocksClass
from nanoblocks.currency import Amount
from nanoblocks.exceptions.payment_timeout_error import PaymentTimeoutError
from nanoblocks.protocol.messages.node_messages import NodeWebSocketMessages

# TODO: Crear un gestor de websockets a nivel NanoNetwork para controlar las suscripciones de pagos y confirmaciones.


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

            if desired_amount is None or Amount(result['message']['amount'], unit="raw") == desired_amount:
                # Payment received!
                paid = True
                paid_hash = result['message']['hash']
                paid_source = result['message']['account']
                paid_amount = Amount(result['message']['amount'], unit="raw")

    return paid, paid_hash, paid_source, paid_amount


async def subscribe_to_account_by_handler(uri, addresses, desired_amount, async_handler_func):

    subscription = NodeWebSocketMessages.CONFIRMATION(addresses)

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps(subscription))

        finish = False

        while not finish:
            result = json.loads(await ws.recv())

            if result.get('topic', None) != "confirmation":
                continue

            if desired_amount is None or Amount(result['message']['amount'], unit="raw") == desired_amount:
                paid_hash = result['message']['hash']
                paid_source = result['message']['account']
                paid_amount = Amount(result['message']['amount'], unit="raw")

                finish = await async_handler_func(paid_hash, paid_source, paid_amount)

    return True


class Payment(NanoblocksClass):
    """
    Gives an easy interface to handle payments for a given account.
    """

    def __init__(self, account_owner, amount, nano_network):
        super().__init__(nano_network)
        self._account_owner = account_owner
        self._amount = amount

        # First we ensure the account is up-to-date
        self._account_owner.update()

        # We take the current balance
        self._initial_balance = self._account_owner.balance.as_unit("raw")
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
        uri = f"nano:{self._account_owner.address}"

        if self._amount is not None:
            uri += f"?amount={str(self._amount)}"

        return uri

    @property
    def qr_code(self):
        """
        Retrieves a PIL image with the QR code for the payment that can be scanned by modern wallets.
        """
        return qrcode.make(self.uri)

    def wait(self, timeout=30, peek_interval=5):
        """
        Waits for the payment to be done.

        If a websocket is available, it will subscribe itself to the account for incoming transactions.
        Otherwise, a peek every `peek_seconds` will be used instead.

        The expected payment must match the exact amount.

        If timedout, call this method again to resume checking. If payment was done between calls stopped by timeout,
        it will still be able to notify it.

        :param timeout:
            Time in seconds to wait for the payment. Set it to 0 to wait indefinitely.

        :param peek_interval:
            Peek interval when no websocket is available.

        :return:
            Returns the block that needs to be confirmed.
        """
        amount = self._amount

        if amount is None:
            amount = Amount("1 raw")

        self._account_owner.update()

        if (self._account_owner.balance - self._initial_balance) == 0:
            paid = False

            payment_init = datetime.now()

            if self.node_backend.ws_available:
                try:

                    paid, paid_hash, paid_source, paid_amount = asyncio.get_event_loop().run_until_complete(subscribe_to_account(self.node_backend.ws,
                                                                                                                                 [self._account_owner.address],
                                                                                                                                 payment_init, timeout, self._amount))

                except TimeoutError:
                    raise PaymentTimeoutError(f"Payment timeout ({timeout} seconds)") from None

                last_pending_block = self.blocks[paid_hash]

            else:

                while not paid and (datetime.now() - payment_init).total_seconds() < timeout:
                    time.sleep(peek_interval)

                    if self._account_owner.is_virtual:
                        # If it is virtual (a new account) we need to check the pending blocks instead
                        pending_transactions = self._account_owner.pending_transactions.update(minimum_quantity=amount, count=100)
                        # paid = len(self._account_owner.pending_transactions) > 0
                        paid = len(pending_transactions) > 0
                    else:
                        self._account_owner.update()
                        new_balance = self._account_owner.balance
                        paid = (new_balance - self._initial_balance) >= amount

                if not paid:
                    raise PaymentTimeoutError(f"Payment timeout ({timeout} seconds)") from None

                # We search the last pending block with this quantity
                if self._amount is not None:
                    self._account_owner.pending_transactions.update(minimum_quantity=amount)
                else:
                    self._account_owner.pending_transactions.update()

                last_pending_block = self._account_owner.pending_transactions[-1]

        else:
            last_pending_block = self._account_owner.pending_transactions[-1]

        return last_pending_block

    def async_handler(self, async_handler_func):
        """
        Provides an async handler for payments.
        Requires the WS version of the node.
        """

        if not self.node_backend.ws_available:
            raise Exception("WS backend is required for an async handler.")

        asyncio.get_event_loop().run_until_complete(
            subscribe_to_account_by_handler(self.node_backend.ws, [self._account_owner.address], self._amount,
                                            async_handler_func))
