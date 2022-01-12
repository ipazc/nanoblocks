import atexit
import json
import asyncio
import socket
import threading
import numpy as np
from threading import Thread, Lock, Event

import websockets

from nanoblocks.node.websocket.tracking.tracking import Tracking

# TODO: Allow "update" on subscriptions. When they update the proxies.


class NodeWebsocket:
    """
    Centralizes websocket operations, like subscriptions to confirmations.
    This is a thread-safe class.
    """
    def __init__(self, ws_url, topic="confirmation"):
        """
        :param ws_url:
            Websocket URL. WSS is also supported.
        :param topic:
            Topic to subscribe to. Default is "confirmation".
        """
        self._ws_url = ws_url
        self._lock = Lock()
        self._callback_event = Event()
        self._connection_success_event = Event()

        self._thread = None
        self._terminate = False
        self._topic = topic
        self._actions_list = []
        self._callbacks = {}
        self._error = None

        # Since websockets are wrapped in a thread, this is required to safely release resources when application
        # is closed.
        atexit.register(self.stop)

    @property
    def accounts_tracked(self) -> list:
        """
        Retrieves the accounts that are being watched by this instance.
        :return:
            Accounts being watched by this instance.
        """

        with self._lock:
            accounts_list = [[acc for acc in accounts if acc != "all"] for c, accounts in self._callbacks.items()]

        return [acc for acc in np.unique(np.hstack(accounts_list))] if len(accounts_list) > 0 else []

    @property
    def callbacks(self):
        return dict(self._callbacks)

    @property
    def running(self):
        """
        :return:
            Retrieves whether the thread is running or not.
        """
        return self._thread is not None and self._thread.is_alive()

    def _thread_loop(self):
        """
        Body of the thread function.
        """
        async def _handler():
            try:
                connection = await websockets.connect(self._ws_url)
            except Exception as e:
                connection = None
                with self._lock:
                    self._error = e

            self._connection_success_event.set()
            self._connection_success_event.clear()

            if self._error is not None:
                return

            while not self._terminate or len(self._actions_list) > 0:
                # We pick actions and execute them
                #if actions is None or len(actions) == 0:
                #    actions = self._actions

                #if len(actions) > 0:
                #    action = actions.pop(0)
                for action in self._actions:
                    print(action)
                    await connection.send(json.dumps(action))

                try:
                    message = json.loads(await asyncio.wait_for(connection.recv(), 0.5))
                    print(message)
                except asyncio.futures.TimeoutError:
                    continue

                # A message was received. We store it in the queue if needed.
                self._queue_message(message)

                self._callback_event.set()
                self._callback_event.clear()

            await connection.close()

        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(_handler())
        event_loop.close()

        with self._lock:
            self._thread = None

    def track_confirmations(self, accounts_list, callback):
        return Tracking(self, accounts_list, callback)

    @property
    def _finish(self):
        return self._terminate

    @_finish.setter
    def _finish(self, value):
        with self._lock:
            self._terminate = value

    @property
    def _actions(self):
        with self._lock:
            actions = list(self._actions_list)
            self._actions_list.clear()

        return actions

    def _pop_messages(self, callback, accounts_list):
        """
        Pops the stored messages from the given accounts.
        Note that popping messages implies cleaning the queue for the given accounts.

        :param callback:
            callback to retrieve messages from.

        :param accounts_list:
            List of account whose messages should be retrieved.

        :return:
            Messages list popped from the buffer
        """
        with self._lock:
            callback_key = self._get_callback_key(callback)
            messages = []

            for account in accounts_list:
                callback_accounts = self._callbacks.get(callback_key, {})
                messages += callback_accounts.get(account, [])
                callback_accounts[account] = []

            if len(accounts_list) == 0:
                callback_accounts = self._callbacks.get(callback_key, {})
                messages += callback_accounts.get("all", [])
                callback_accounts["all"] = []

        return messages

    def _queue_action(self, action):
        with self._lock:
            self._actions_list.append(action)

    def _queue_message(self, message):
        """
        Queues a message to the corresponding queues lists.

        :param message:
            Message retrieved by the websocket listener, in JSON format.

        """

        # First we check which account does this message belong to.
        # There is a special case: we populate send blocks to sender and to receiver.
        # This is useful for payments.
        account = message.get("message", {}).get("account")
        link_as_account = message.get("message", {}).get("block", {}).get("link_as_account")
        is_send = message.get("message", {}).get("block", {}).get("subtype") == "send"
        error = message.get('error', None)

        if error is not None:
            raise ConnectionError(error)

        if account is None:
            return

        with self._lock:
            # Then, we add this message to the corresponding queues.
            for callback_key, accounts_dict in self._callbacks.items():
                if account in accounts_dict:
                    accounts_dict[account].append(message)

                if is_send and link_as_account in accounts_dict:
                    accounts_dict[link_as_account].append(message)

                # In case a subscription to all acounts is configured:
                if "all" in accounts_dict:
                    accounts_dict["all"].append(message)

    def start(self, timeout_seconds=10):
        if not self.running:
            self._thread = Thread(target=self._thread_loop, daemon=True)
            self._finish = False
            #self._subscribe()
            self._thread.start()

            # We seek for the connection to succeed before returning
            if not self._connection_success_event.wait(timeout_seconds):
                raise TimeoutError("Could not connect to the websocket server.")

            error = self._error

            if error is not None:
                raise error

    def stop(self):
        if self.running and not self._finish:
            self._finish = True
            try:
                self._thread.join()
            except RuntimeError:
                pass

            with self._lock:
                self._thread = None
        self._callbacks = {}

    def _start_confirmation_tracking(self, accounts_list, callback):
        accounts_to_subscribe_list = [acc for acc in np.unique(np.hstack([self.accounts_tracked, accounts_list]))]
        self._subscribe(accounts_to_subscribe_list)

        """action_start_confirmation_tracking = {
            "action": "update",
            "topic": "confirmation",
            "options": {
                "accounts_add": accounts_list,
            }
        }"""

        with self._lock:
            callback_key = self._get_callback_key(callback)
            self._callbacks.setdefault(callback_key, {})
            self._callbacks[callback_key].update({a:[] for a in accounts_list})

            if len(accounts_list) == 0:
                self._callbacks[callback_key]['all'] = []

        #if len(accounts_list) > 0:
        #    self._queue_action(action_start_confirmation_tracking)

    def _end_confirmation_tracking(self, accounts_list, callback):
        if self.running:
            accounts_to_subscribe_list = [acc for acc in self.accounts_tracked if acc not in accounts_list]
            self._unsubscribe(accounts_list)
            if len(accounts_to_subscribe_list) > 0:
                self._subscribe(accounts_to_subscribe_list)

            """action_end_confirmation_tracking = {
                "action": "update",
                "topic": "confirmation",
                "options": {
                    "accounts_del": accounts_list,
                }
            }"""

            with self._lock:
                callback_key = self._get_callback_key(callback)
                del self._callbacks[callback_key]

            #if len(accounts_list) > 0:
            #    self._queue_action(action_end_confirmation_tracking)

    def _subscribe(self, initial_accounts=None):
        """
        Performs a subscription to the websocket.

        :param initial_accounts:
            List of accounts to subscribe to. The initial accounts can be updated later by
            `_start_confirmation_tracking()` and `_end_confirmation_tracking()` methods.

            The following options are special cases:

                * If None, it will not track any account until updated by the `_start_confirmation_tracking()` method.
                * If empty list, it will notify every confirmation independently of the procedence.
                    Note that not all the nodes support this operation.
        """
        if initial_accounts is None:
            initial_accounts = []

        action = {
            "action": "subscribe",
            "topic": self._topic,
        }

        if len(initial_accounts) > 0:
            action['options'] = {"accounts": initial_accounts}

        self._queue_action(action)

    def _unsubscribe(self, initial_accounts=None):
        """
        Removes the subscription from the websocket.
        """
        if initial_accounts is None:
            initial_accounts = []

        action = {
            "action": "unsubscribe",
            "topic": self._topic,
        }

        if len(initial_accounts) > 0:
            action['options'] = {"accounts": initial_accounts}

        self._queue_action(action)

    def _get_callback_key(self, callback):
        return f"[{threading.get_ident()}] {str(callback)}"

    def healthy(self):
        if self.running:
            return True

        try:
            self.start(timeout_seconds=10)

        except (websockets.exceptions.InvalidStatusCode, TimeoutError, socket.gaierror):
            return False

        finally:
            self.stop()

        return True
