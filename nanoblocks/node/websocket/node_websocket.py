import atexit
import json
import asyncio
from threading import Thread, Lock, Event

import websockets

from nanoblocks.utils import TimedVariable


class NodeWebsocket:

    def __init__(self, ws_url, topic="confirmation"):
        self._ws_url = ws_url
        self._lock = Lock()
        self._callback_event = Event()
        self._thread = Thread(target=self._thread_loop, daemon=True)
        self._terminate = False
        self._topic = topic
        self._actions_list = []
        self._messages_list = []
        self._subscribed_accounts = []
        atexit.register(self.stop)
        self._started = False

    @property
    def started(self):
        return self._started

    @property
    def accounts_tracked(self):
        with self._lock:
            return list(self._subscribed_accounts)

    def _thread_loop(self):
        async def _handler():
            connection = await websockets.connect(self._ws_url)

            while not self._terminate or len(self._actions_list) > 0:
                # We pick actions and execute them
                actions = self._actions
                for action in actions:
                    print("registering action: ", action)
                    await connection.send(json.dumps(action))

                try:
                    message = json.loads(await asyncio.wait_for(connection.recv(), 0.5))
                except asyncio.futures.TimeoutError:
                    continue

                self._queue_message(message)

                self._callback_event.set()
                self._callback_event.clear()

            await connection.close()

        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(_handler())
        event_loop.close()

    def track_confirmations(self, accounts_list, callback, timeout_seconds=None):
        if len(accounts_list) is None:
            self._unsubscribe()
            self._subscribe(initial_accounts=[])

        self._start_confirmation_tracking(accounts_list)
        callback_result = True

        start = TimedVariable(None)
        while callback_result:
            # We iterate constantly over the messages until no messages are found, or until False is returned in the
            # callback.
            messages = self._messages

            for message in messages:
                callback_result = callback(message)

                if not callback_result:
                    break

            # This locks the thread until unlocked by the other
            self._callback_event.wait(timeout_seconds)

            if timeout_seconds is not None and start.last_update_elapsed_time >= timeout_seconds:
                callback_result = False

        self._end_confirmation_tracking(accounts_list)

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

    @property
    def _messages(self):
        with self._lock:
            messages = list(self._messages_list)
            self._messages_list.clear()

        return messages

    def _queue_action(self, action):
        with self._lock:
            self._actions_list.append(action)

    def _queue_message(self, message):
        with self._lock:
            self._messages_list.append(message)

    def start(self):
        self._terminate = False
        self._subscribe()
        self._thread.start()
        self._started = True

    def stop(self):
        if not self._finish:
            self._unsubscribe()
            self._finish = True
            self._thread.join()
        self._started = False

    def _start_confirmation_tracking(self, accounts_list):

        action_start_confirmation_tracking = {
            "action": "update",
            "topic": "confirmation",
            "options": {
                "accounts_add": accounts_list,
            }
        }

        with self._lock:
            self._subscribed_accounts += accounts_list

        self._queue_action(action_start_confirmation_tracking)

    def _end_confirmation_tracking(self, accounts_list):

        action_end_confirmation_tracking = {
            "action": "update",
            "topic": "confirmation",
            "options": {
                "accounts_del": accounts_list,
            }
        }

        with self._lock:
            for account in accounts_list:
                try:
                    self._subscribed_accounts.remove(account)
                except ValueError:
                    pass

        self._queue_action(action_end_confirmation_tracking)

    def _subscribe(self, initial_accounts=None):
        if initial_accounts is None:
            initial_accounts = ["nano_ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"]  # By default we need one account. After we can add more.

        action = {
            "action": "subscribe",
            "topic": self._topic,
            "options": {
                "accounts": initial_accounts
            }
        }

        self._queue_action(action)

    def _unsubscribe(self):
        action = {
            "action": "unsubscribe",
            "topic": self._topic,
        }

        self._queue_action(action)
