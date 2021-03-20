Getting started
===============

In order to start, make sure a communication to a node RPC http and WebSocket is available. Otherwise, most of the examples presented in this page won't work properly.

Check the following section to know how to install a node.

Set-up a Node
-------------

`NanoBlocks` can release all its functionality by accessing a Node API. You can either get access to a public Node http REST API and WebSockets, or mount your own node instead (which is highly encouraged).
If you want to install the Nano node, you should try to set up a Node `by following the official installation guide <https://docs.nano.org/running-a-node/overview/>`_.

Take note of the rest API address *(usually TCP node_host:7076)* and the WebSocket address *(usually TCP node_host:7078)*, as you are going to need them from now on.

Also, note that having a dedicated work server for generating work hashes is highly encouraged. check out the `nano work server <https://github.com/nanocurrency/nano-work-server>`_. Each Nano transaction requires a work hash attached, and generating the hash is a heavy process which usually requires a dedicated GPU to fit in time. Even though this problem can be circumvented by caching the work hash for each account frontier, having a dedicated work server separated from the node is still encouraged.

Interacting with the network
----------------------------

The entry point to the network is the class :class:`NanoNetwork <nanoblocks.network.nano_network.NanoNetwork>`:

.. code-block:: python

    >>> from nanoblocks.node import NanoNode
    >>> from nanoblocks.network import NanoNetwork

    >>> node = NanoNode(rest_api_url="http://localhost:7076",
                        websocket_api_url="ws://localhost:7078")
    >>> node
    [Node http://localhost:7076 (Nano V21.3)]

    >>> network = NanoNetwork(node)
    >>> network
    [Node http://localhost:7076 (Nano V21.3)] (270 peers; 15362838 account)


The `network` object contains access to three basic members: the `blocks` in the network, the `accounts` globally registered and the `wallets`.

Accessing an account
--------------------

Given the `network` object, accessing an account can be done as follows:

.. code-block:: python

    >>> account = network.accounts["nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi"]
    >>> account
    nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi (
        Total blocks: 733
        Total balance: 0.000002000000000000000000000002 NANO
        Confirmed balance: 0.000000000000000000000000000000 NANO
        Pending balance: 0.000002000000000000000000000002 NANO
        Last confirmed payment: 2020-12-02 01:30:39+01:00
        Is virtual: False
    )


You might have noticed well: `network.accounts[]` behaves like a python dictionary, which in turns makes it easy to access any account in the network.
In `NanoBlocks`, every account is wrapped inside the class :class:`Account <nanoblocks.account.account.Account>` which gives basic functionality for account handling:

.. code-block:: python

    >>> account.balance
    0.000002000000000000000000000002 NANO

    >>> account.pending_balance
    0.000002000000000000000000000002 NANO

    >>> account.confirmed_balance
    0.000000000000000000000000000000 NANO

    >>> account.public_key
    9D050D7C3DD1D87F7C3F8EA8A83B9A8BF52AE6EB4562D945D563A1C0384C691F

    >>> account.frontier
    FED268136D2931EDEA61057D91C3C250894EF95C14C0D16CA0D126D99579C53C

    >>> account.representative  # The representative is another account object
    nano_16u1uufyoig8777y6r8iqjtrw8sg8maqrm36zzcm95jmbd9i9aj5i8abr8u5 (
        Total blocks: 6
        Total balance: 0.000000000000000000000000000000 NANO
        Confirmed balance: 0.000000000000000000000000000000 NANO
        Pending balance: 0.000000000000000000000000000000 NANO
        Last confirmed payment: 2020-12-02 01:57:11+01:00
        Is virtual: False
    )

Accessing a block
-----------------

If you know a block hash and you want to check its information, it can be done in a similar way than with accounts, but with the `blocks` member:

.. code-block:: python

    >>> block = network.blocks["4FEC4BDD078C741F599221C67C8BE6493C872EF9B30968BBF4991640FFF42DA2"]
    >>> block
    [Block #4 from account nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi]
        Type: receive
        Hash: 4FEC4BDD078C741F599221C67C8BE6493C872EF9B30968BBF4991640FFF42DA2
        Source account: nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi
        Amount: 0.000040000000000000000000000000
        Local date: 1970-01-01 01:00:00+01:00

Every Block is wrapped inside the class derived from :class:`Block <nanoblocks.block.block.Block>`, which can in turn be a :class:`BlockSend <nanoblocks.block.block_send.BlockSend>`, a :class:`BlockReceive <nanoblocks.block.block_receive.BlockReceive>` or a :class:`BlockState <nanoblocks.block.block_send.BlockState>`.
The main difference between each `block` implementation is the arrangement of the fields and the way they are displayed when printed.

Check the block docs to know what methods and attributes are available for each.

Accessing a wallet
------------------

Likely to the rest, the wallets can be accessed in the exact same way. The property `wallets` in the `network` object
gives access to a wallet by the seed or the bip39-mnemonic 24-word phrase.

.. code-block:: python

    # To access an existing wallet by using the 64-Bytes seed:
    >>> wallet = network.wallets["7F632A80ECCC54A058602CD64A81D23A6B4D7320562E4767C9EB0BBB1151CDF2"]

    # Alternatively, it can be accessed with the BIP-39 24 words:
    >>> wallet = network.wallets[['legal', 'bone', 'parent', 'sunset', 'shed', 'expand', 'ghost', 'airport', 'stone', 'favorite', 'innocent', 'inquiry', 'regular', 'ridge', 'life', 'shift', 'electric', 'dinner', 'kiss', 'blast', 'rain', 'pottery', 'daughter', 'execute']]

    # Wallet information can be printed out
    >>> print(wallet.seed)
    7F632A80ECCC54A058602CD64A81D23A6B4D7320562E4767C9EB0BBB1151CDF2

    >>> print(wallet.mnemonic)
    ['legal', 'bone', 'parent', 'sunset', 'shed', 'expand', 'ghost', 'airport', 'stone', 'favorite', 'innocent', 'inquiry', 'regular', 'ridge', 'life', 'shift', 'electric', 'dinner', 'kiss', 'blast', 'rain', 'pottery', 'daughter', 'execute']
