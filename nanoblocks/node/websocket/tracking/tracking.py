from nanoblocks.utils import TimedVariable


class Tracking:
    def __init__(self, ws, accounts_list, callback):
        self._ws = ws
        self._accounts_list = accounts_list
        self._callback = callback

    def begin(self):
        if len(self._accounts_list) == 0:
            self._ws._unsubscribe()
            self._ws._subscribe(initial_accounts=[])

        self._ws._start_confirmation_tracking(self._accounts_list, self._callback)

    def join(self, timeout_seconds=None):
        callback_result = True

        start = TimedVariable(None)
        while callback_result:
            # We iterate constantly over the messages until no messages are found, or until False is returned in the
            # callback.
            if not self._ws.running:
                raise ConnectionResetError("Websocket disconnected.")

            messages = self._ws._pop_messages(self._callback, self._accounts_list)

            for message in messages:
                callback_result = self._callback(message)

                if not callback_result:
                    break

            # This locks the thread until unlocked by the websocket or until 3 seconds passed
            self._ws._callback_event.wait(3)

            if timeout_seconds is not None and start.last_update_elapsed_time >= timeout_seconds:
                callback_result = False

    def end(self):
        self._ws._end_confirmation_tracking(self._accounts_list, self._callback)
