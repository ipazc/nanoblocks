from nanoblocks.exceptions.no_healthy_nodes_available import NoHealthyNodesAvailable
from nanoblocks.exceptions.node_limit_reached import NodeLimitReached
from nanoblocks.exceptions.node_timedout import NodeTimedOut
from nanoblocks.exceptions.node_unreachable import NodeUnreachable
from nanoblocks.node import NodeRemote
from nanoblocks.utils.time import SYSTEM_TIMEZONE


class NodeFailover(NodeRemote):
    """
    A Node Failover is node class that forwards its requests to the first healthy node in a list of failover nodes.
    The first healthy node found in the list is the one used for performing the requests.

    When a node fails in providing a response, the next node in the list is taken instead. It is transparent to the
    user, ensuring that an answer is retrieved.
    """
    # Inheriting the docstrings from the NodeRemote
    __doc__ = NodeRemote.__doc__ + (__doc__ if __doc__ is not None else "")

    def __init__(self, nodes_list, timezone=SYSTEM_TIMEZONE):
        """
        Constructor of the NodeFailover class.

        This class behaves like a node, but it forwards the requests to the first healthy node in the nodes list.

        :param nodes_list:
            list of nodes to use as failover.
        """
        super().__init__(http_url=None, ws_url=None, timezone=SYSTEM_TIMEZONE)
        self._nodes_list = list(nodes_list)
        self._target_node = None
        self.find_healthy()

    @property
    def failover_nodes(self):
        return list(self._nodes_list)

    def add_failover_node(self, failover_node):
        self._nodes_list.append(failover_node)

    def remove_failover_node(self, failover_node):
        try:
            self._nodes_list.remove(failover_node)
            self.find_healthy()
        except ValueError:  # We dont have the node in the list
            pass

    @property
    def http_url(self):
        return self._target_node.http_url

    @property
    def ws_url(self):
        return self._target_node.ws_url

    @property
    def ws(self):
        return self._target_node.ws

    def __str__(self):

        nodes_info = []

        for node in self._nodes_list:
            if node == self._target_node:
                node_info = "\t[x] "
            else:
                node_info = "\t[ ] "

            try:
                nodes_info.append(node_info + str(node))

            except (NodeTimedOut, NodeUnreachable, NodeLimitReached) as e:
                node_info += f"[Node http={node.http_url}"

                if node.ws_url is not None:
                    node_info += f"; ws={node.ws_url}]"
                else:
                    node_info += "]"

                nodes_info.append(node_info)

        base_str = "\n".join([f"[FAILOVER NODE]", ] + nodes_info)
        return base_str

    def find_healthy(self):
        """
        Seeks for a healthy node in the list of nodes.
        When a node is found, it is set as the target node of this instance.
        :return:
        """
        for node in self._nodes_list:
            if node.healthy():
                # We found a new node. We abort the current WebSocket connection in case it was detected
                self.ws.stop()
                self._target_node = node

                # And we re-start the websocket connection with this new one
                self.ws.start()
                return
        raise NoHealthyNodesAvailable("No healthy nodes available in the failover list.")

    def _ask(self, message):
        """
        Makes a call to the rest api with the specified message and returns the result.

        If a node fails answering, a new node from the failover list is taken automatically.

        :param message:
            A crafted JSON message.
        """
        response = None

        while response is None:
            # A response is tried until no healthy nodes are available.
            try:
                # noinspection PyProtectedMember
                response = self._target_node._ask(message)

            except (NodeTimedOut, NodeUnreachable, NodeLimitReached) as e:
                self.find_healthy()

        return response
