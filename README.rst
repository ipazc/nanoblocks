.. image:: https://github.com/ipazc/nanoblocks/raw/main/docs/source/tutorial/images/logo_big.png
    :target: https://nanoblocks.readthedocs.io/en/latest/

.. image:: https://badge.fury.io/py/nanoblocks.svg
    :target: https://badge.fury.io/py/nanoblocks


`nanoblocks` is an **unofficial** Python package built to ease the access to `NANO cryptocurrency <https://nano.org/>`_. It is intended to give an easy interface for programmers to play with the Nano Network, allowing most Nano common operations which includes creating new wallets and accounts, checking accounts information, making transactions and more.

An extensive documentation of the package can be found by `reading the docs <https://nanoblocks.readthedocs.io/en/latest/>`_.
 
Installation
------------

`nanoblocks` can be installed through pip:


.. code-block:: bash

    pip install nanoblocks

Getting started
---------------

Accessing the Nano network can be done as follows:

.. code-block:: python

    >>> from nanoblocks.network import NanoNetwork

    >> network = NanoNetwork()
    >> network
    [Node https://mynano.ninja/api/node (Nano V22.1)] (262 peers; 26300103 account)

By default, a public nano RPC server is used (mynano.ninja) as the backend, which allows the package to be ran out-of-the-box.
Even though a list of available public nodes can be found at `https://publicnodes.somenano.com/ <https://publicnodes.somenano.com/>`_, it is highly encouraged to run your own Nano node.


Having a `NanoNetwork` class instance, accounts in the network can be accessed as follows:

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
        Last update: 2021-11-17T01:30:04.348637+01:00 (0.02 seconds ago)
    )

Blocks can be accessed as follows:

.. code-block:: python

    >>> block = network.blocks["4FEC4BDD078C741F599221C67C8BE6493C872EF9B30968BBF4991640FFF42DA2"]
    >>> block
    [Block #4 from account nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi]
        Type: receive
        Hash: 4FEC4BDD078C741F599221C67C8BE6493C872EF9B30968BBF4991640FFF42DA2
        Source account: nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi
        Amount: 0.000040000000000000000000000000
        Local date: 1970-01-01 01:00:00+01:00


And wallets can be accessed as follows:

.. code-block:: python

    # To create a new wallet
    >>> wallet = network.wallets.create()

    # To access an existing wallet by using the 64-Bytes seed:
    >>> wallet = network.wallets["7F632A80ECCC54A058602CD64A81D23A6B4D7320562E4767C9EB0BBB1151CDF2"]

    # Alternatively, it can be accessed with the BIP-39 24 words:
    >>> wallet = network.wallets[['legal', 'bone', 'parent', 'sunset', 'shed', 'expand', 'ghost', 'airport', 'stone', 'favorite', 'innocent', 'inquiry', 'regular', 'ridge', 'life', 'shift', 'electric', 'dinner', 'kiss', 'blast', 'rain', 'pottery', 'daughter', 'execute']]

    # Wallet information can be printed out
    >>> print(wallet.seed)
    7F632A80ECCC54A058602CD64A81D23A6B4D7320562E4767C9EB0BBB1151CDF2

    >>> print(wallet.mnemonic)
    ['legal', 'bone', 'parent', 'sunset', 'shed', 'expand', 'ghost', 'airport', 'stone', 'favorite', 'innocent', 'inquiry', 'regular', 'ridge', 'life', 'shift', 'electric', 'dinner', 'kiss', 'blast', 'rain', 'pottery', 'daughter', 'execute']

Controlling a wallet seed allows to access accounts deterministically:

.. code-block:: python

    >>> account_0 = wallet.accounts[0]
    >>> account_1 = wallet.accounts[1]


And transacting Nano can be done as follows:

.. code-block:: python

    >>> account_0.send_nano(account_1, "0.0001")
    >>> account_1.receive_nano()  # Receives the last pending transaction. Can be repeated until no pending transactions remain.


Easy, right? Check what you can do by `reading the docs <https://nanoblocks.readthedocs.io/en/latest/>`_!

LICENSE
-------

This package is license under the MIT license.