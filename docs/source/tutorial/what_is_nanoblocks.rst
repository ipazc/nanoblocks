What is NanoBlocks
==================

`NanoBlocks` is an **unofficial** Python package built to ease the access to `NANO cryptocurrency <https://nano.org/>`_. It is intended to give an easy interface for programmers to play with the Nano Network, allowing most Nano common operations which includes creating new wallets and accounts, checking accounts information, making transactions and more.

In the following sections, you will learn how `NanoBlocks` is built and what are the basic concepts required to deal with the package.

Basic concepts
--------------

`NanoBlocks` is a composition of a few main concepts as shown in the following schema:

.. image:: /tutorial/images/NanoBlocks_schema.png

This schema is implemented as-is in NanoBlocks, meaning that there exist the corresponding classes :class:`NanoNode <nanoblocks.node.nanonode.NanoNode>`, :class:`NanoNetwork <nanoblocks.network.nano_network.NanoNetwork>`, `Blocks <../nanoblocks.block.html>`_, :class:`Account <nanoblocks.account.account.Account>` and :class:`Wallet <nanoblocks.wallet.wallet.Wallet>`.
These 5 classes are interrelated to each other as shown by the arrows present in the schema image, which makes it extremely easy to flow.

 * :class:`NanoNode <nanoblocks.node.nanonode.NanoNode>` Is a class that contains the addresses of the RPC HTTP, WebSocket and RemoteWorkServer (if available). It also wraps simple communication mechanism for each. All the objects in the package usually have access to this object.

 * :class:`NanoNetwork <nanoblocks.network.nano_network.NanoNetwork>` Is a class that gives a simple interface to the Nano network. It provides access to accounts, blocks and wallets. Also, it is responsible of broadcasting blocks to the network.

 * :class:`Account <nanoblocks.account.account.Account>` Is a class that interfaces one account. It gives access to the account information (balance, representative, frontier, ...) and more complex information like the blockchain history and pending transactions. Furthermore, allows to build transaction blocks, which can be later broadcasted to the network.

 * `Blocks <../nanoblocks.block.html>`_ Is a set of classes that interfaces the basic blocks operations in Nano. In this package, the blocks are specialized into 3 classes: `BlockSend`, `BlockReceive` and `BlockState`. If you still don't know what a block in Nano is, you should first read the `official documentation of Nano <https://docs.nano.org/integration-guides/the-basics/>`_ to get full overview.

 * :class:`Wallet <nanoblocks.wallet.wallet.Wallet>` Is a class that allows handling a wallet. It can access existing wallets through the seed or the BIP39 mnemonic word list, or generate new cryptographic secure wallets. This class can even work offline, without a node attached to the network, meaning that you can access or create wallets without internet.
