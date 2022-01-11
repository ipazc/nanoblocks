"""
The :mod:`nanoblocks.node` module implements
Nano node wrapper.
"""

from .node_remote import NodeRemote
from .node_virtual import NodeVirtual
from .failover.node_failover import NodeFailover


# SOURCE: https://publicnodes.somenano.com/
RAINSTORM_NODE = NodeRemote(http_url='https://rainstorm.city/api', ws_url='wss://rainstorm.city/websocket')
NINJA_NODE = NodeRemote(http_url='https://mynano.ninja/api/node', ws_url='wss://ws.mynano.ninja/')
NANOS_NODE = NodeRemote(http_url='https://proxy.nanos.cc/proxy', ws_url='wss://socket.nanos.cc/')
SOMENANO_NODE = NodeRemote(http_url='https://node.somenano.com/proxy', ws_url='wss://node.somenano.com/websocket')
POWERAPI_NODE = NodeRemote(http_url='https://proxy.powernode.cc/proxy', ws_url='wss://ws.powernode.cc/')

NO_NODE = NodeVirtual()

# The NodeFailover ensures responses when a node fails.
PUBLIC_FAILOVER_NODE = NodeFailover([
    NINJA_NODE,
    SOMENANO_NODE,
    RAINSTORM_NODE,
    NANOS_NODE,
    POWERAPI_NODE,
    NO_NODE,
])


__all__ = ["NodeRemote", "NodeVirtual", "NodeFailover",
           "PUBLIC_FAILOVER_NODE",
           "RAINSTORM_NODE", "NINJA_NODE", "NANOS_NODE", "SOMENANO_NODE", "POWERAPI_NODE", "NO_NODE"]
