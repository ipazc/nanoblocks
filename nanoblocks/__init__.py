from nanoblocks.config.config import rcParams
from nanoblocks.node.snapshot.snapshot import NodeSnapshot


def load_snapshot(filename):
    return NodeSnapshot.from_file(filename)


__version__ = "0.1.0"


__changelog__ = [
    {
        'version': "0.1.0",
        'changes': [
            "Refactorized classes: now classes are split into different files.",
            "Refactorized node backend calls: now the node class contains all the calls to the node, and can be subclassed to implement different node wrappers (like virtual nodes, for example).",
            "Added local work generation as default option so that it can run out-of-the-box.",
            "Added functionality for recording transactions in a 'tape' and restoring them later in an online node. Useful for offline signing.",
            "Added simplified methods for sending nano, receiving nano and changing representative. Now users can use this functionality out-of-the-box. Check `account.send_nano()`, `account.receive_nano()` and `account.change_representative()`.",
            "Added default public node backends.",
            "Several bugfixes (history retrieval, offline updates of transactions, ...)",
            "Added a base class that allows all the classes to access the nano network that they belong to, removing circular references and easing the code.",
            "Added cache layer for accounts in network class. Requesting same account provides same object no matter where. Once an account reference count goes to 0, the account is released.",
            "Added global configurations rcParams for handling display formats and global timeouts.",
            "Amount class now does not use Decimal backend due to a bug. Instead, recreated from scratch.",
            "Added Jupyter notebooks as examples.",
            "Added IPython widgets for accounts and blocks. Now Jupyter Notebooks show nice representations of these objects.",
            "Fixed account history retrieval issue not reporting more than 10 blocks when iterating slices."
            "Fixed IPython block representations when using iterator on accounts history.",
            "Added TimedVariable class with monotonic timers for handling elapsed times on certain variables.",
            "Added a @cache decorator for certain node calls to avoid unnecesary spamming to the node (like telemetry for retrieving versions).",
            "Added healthy attribute to nodes to know whether the node is responsive or not.",
            "Added failover functionality for nodes and set as default backend (with 5 public nodes and a virtual) in out-of-the-box network objects.",
            "Added centralization of websockets in a NodeWebsocket class handled by the node itself.",
            "Added some exceptions and cleaned up unused code."
        ]
    },
    {
        'version': "0.0.x",
        'changes': [
            "First implementations of Nanoblocks package."
        ]
    },
]