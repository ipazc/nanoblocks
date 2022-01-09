What is Nano?
=============

Nano is a **decentralized cryptocurrency** that was born in 2015 under the wings of the Nano Foundation,
led by Colin LeMahieu. It is claimed to be one of the fastests cryptocurrencies in the cryptomarket, as **the transactions can be instant
and fee-less**. Furthermore, **there is no mining required**, all the coins are already distributed and it can be considered one of the
**greenest cryptocurrencies available**.

There are a total of 133.248.290 Nano coins available, even though each can be divided up to 30 decimals.
This division makes it suitable for microtransactions.


How does Nano work?
-------------------
Nano is formed by a set of servers (called nodes) running the `Nano node software <http://github.com/nanocurrency/nano-node>`_.
It is open-sourced (under the License BSD 3-Clause), meaning that every person can contribute to the code
and host a node server.

All the nodes are interconnected forming the *Nano network*. Every node in the network contains the full ledger of
transactions done since the very first transaction. Every time a transaction is attempted, all the nodes negotiate among
them the validity of the transaction until the majority (66%) agree in confirmation, which is also known as
Open-Representative-Voting. For this reason, Nano is considered a Peer2Peer decentralized cryptocurrency.

Unlike other cryptocurrencies where there is a single blockchain for all the operations, in Nano there are as many
blockchains as accounts in the network. Furthermore, all the blockchains are ruled by a single structure based on a Direct Acyclic Graph (DAG)
 which is called **block-lattice**.

Nano is scalable due to every account ruling its own blockchain and no other's. However, every block that is going
to be inserted in any blockchain must be confirmed by most of the nodes at any time. This makes the network secure and
avoids double spend problems.


How to interact with the network?
---------------------------------

The entry point to the network is the Nano node. In order to check accounts and make transactions, the Nano node software
usually publish an API in the http (TCP 7076) and websocket (TCP 7078) protocols.
The node operators usually restrict the access to these node APIs to avoid saturation and hacking. However, there is
still a certain set of public API exposed through SSL layers, like for example the ones exposed in `https://publicnodes.somenano.com/ <https://publicnodes.somenano.com/>`_.

Every wallet software, like Natrium, Nalli or Nault, use a private (sometimes public) node to operate.
For this reason, if the wallet's node shuts down, the wallet might lose the service.
However, since the account data is stored in every node's ledger, its control can be retrieved by using any other
wallet software, or even your own wallet built with nanoblocks.


Can I host a node?
------------------

Definitely Yes, and you should if you want to have a serious development with this library, even though it is not mandatory.
For experimental setups, public nodes can be used instead; however, it is highly encouraged to host your own node due to security concerns.
Also, some operations can be applied offline where no nodes are required at all.

nanoblocks points to a public node by default (Mynano.ninja), which allows to be used out-of-the-box.
In case more advanced configuration is required, a tutorial on how to set up a node can be `found here <https://docs.nano.org/running-a-node/overview/>`_.
