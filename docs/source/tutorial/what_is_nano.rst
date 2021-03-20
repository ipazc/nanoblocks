What is Nano?
=============

Nano is a **decentralized cryptocurrency** that was born in 2015 under the wings of the Nano Foundation,
led by Colin LeMahieu. It is claimed to be one of the fastests cryptocurrencies in the cryptomarket, as **the transactions can be instant
and feeless**. Furthermore, **there is no mining required** due to all the coins being already distributed which makes it also one of the
**greenest cryptocurrencies available**.

There are a total of 133.248.290 Nano coins available in total, even though each can be divided up to 30 decimals.
This division makes it suitable for microtransactions.


How Nano works?
---------------
Nano is formed by a set of servers (called nodes) running the `Nano node software <http://github.com/nanocurrency/nano-node>`_.
It is open-sourced (under the License BSD 3-Clause), meaning that every person can contribute to the code
and host a node server.

All the nodes are interconnected forming the *Nano network*. Every node in the network contains the full ledger of
transactions done since the very first transaction. Every time a transaction is attempted, all the nodes negotiate each
other the validity of the transaction until the majority (51%) agree in confirmation, which is also known as
Open-Representative-Voting. For this reason, Nano is considered a Peer2Peer decentralized currency.

Unlike other cryptocurrencies where there is a single blockchain for all the operations, in Nano there are as many
blockchains as accounts in the network. Furthermore, all the blockchains are ruled by a single Direct Acyclic Graph (DAG)
structure that is called **block-lattice**.

Nano is scalable due to every account ruling its own blockchain and no other's. However, every block that is going
to be inserted in any blockchain must be confirmed by most of the nodes at any time. This makes the network secure and
avoids double spend problems.


How to interact with the network?
---------------------------------

The entry point to the network is the Nano node. In order to check accounts and make transactions, the Nano node software
usually publish an API in the http (TCP 7076) and websocket (TCP 7078) protocols.
The node operators usually restrict the access to these node APIs to avoid saturation and hacking.

Every wallet software, like Natrium, Nalli or Nault, use a private (sometimes public) node to operate.
For this reason, if the wallet's node shuts down, the wallet might lose the service.
However, since the account data is stored in every node's ledger, its control can be retrieved by using any other
wallet software, or even your own wallet.


Can I host a node?
---------------------------------

Definitely Yes, and you should if you want to develop with this library, even though it is not completely required.
Some operations can be applied offline, some others can be relied into a public node. But it is completely advisable to
run your own node.

A tutorial on how to set up a node can be `found here <https://docs.nano.org/running-a-node/overview/>`_

If you want to develop any solution based on Nano, ensure to get access to a Node RPC.

