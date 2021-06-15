import datetime
import requests

from nanoblocks.protocol.messages.node_messages import NodeMessages

from tzlocal import get_localzone

SYSTEM_TIMEZONE = str(get_localzone())


class NanoNode:
    """
    Stores information of the Node backend.
    """

    def __init__(self, rest_api_url, websocket_api_url, timezone=SYSTEM_TIMEZONE):
        self._rest_api_url = rest_api_url
        self._websocket_api_url = websocket_api_url
        self._timezone = timezone

    @property
    def is_online(self):
        return self._rest_api_url is not None

    @property
    def ws_available(self):
        return self._websocket_api_url is not None

    @property
    def timezone(self):
        return self._timezone

    @property
    def rest(self):
        return self._rest_api_url

    @property
    def ws(self):
        return self._websocket_api_url

    @ws.setter
    def ws(self, new_ws_api_url):
        self._websocket_api_url = new_ws_api_url

    @rest.setter
    def rest(self, new_rest_api_url):
        self._rest_api_url = new_rest_api_url

    @property
    def version(self):
        """
        Returns the node information and version.
        """
        v = self.ask(NodeMessages.VERSION())

        if not v:
            v = {'node_vendor': 'OFFLINE'}

        return v

    def __str__(self):
        return f"[Node {self.rest} ({self.version['node_vendor']})]"

    def __repr__(self):
        return str(self)

    def ask(self, message):
        """
        Makes a call to the rest api with the specified message and returns the result.

        :param message:
            A message defined in any file inside `nanoblocks/protocol/messages/`.
        """

        if not self.is_online:
            return None

        return requests.post(self.rest, json=message).json()


NO_NODE = NanoNode(None, None)
