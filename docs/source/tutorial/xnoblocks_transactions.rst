nanoblocks transactions
=======================

Likely to all the functionality from the package, handling transactions in `nanoblocks` is also simplified to the
minimum expression, but it requires a deeper knowledge of the network to understand how and why it is structured as is.
In the following sections we will try to explain what is behind blocks, work, transactions, how are they related to
each other and how can be handled in `nanoblocks`.

What is a block?
----------------

In Nano, like most cryptocurrencies, everything is built on top of `Blocks`. A `Block` is a set of bytes that explains a
change in an account, like a modification of the balance or a change of its representative. If you want a deep
introduction to blocks, the best resource for this is the `official documentation from Nano <https://docs.nano.org/protocol-design/blocks/>`_.

Every account in Nano is linked to the last block (last modification) that was published for it, a.k.a **frontier** block.
Every block is also linked to the previous block - chained up to the first block of the account. This is essentially a
block-chain, and every account contains a single block-chain of operations. You can access the `frontier` block of an
account as follows:

.. code-block:: python

    >>> from nanoblocks.node import NanoNode
    >>> from nanoblocks.network import NanoNetwork

    >>> node = NanoNode("http://node_host:7076")
    >>> network = NanoNetwork(node)

    >>> account = network.accounts["nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi"]
    >>> print(account.frontier)
    [Block #733 from account nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi]
        Type: send
        Hash: FED268136D2931EDEA61057D91C3C250894EF95C14C0D16CA0D126D99579C53C
        Destination account: nano_3qma6u8sgsbbfson9owacobnj93b64qrw8astsq8ugprco1z8gqztoncjbh8
        Amount: 0.085261000000000000026440892414
        Local date: 2020-12-02 01:30:39+01:00



Since there are as many block-chains as accounts, it makes operations in Nano asynchronous due to not having a single
global block-chain.


What is "Work" and what is it for?
----------------------------------

`Work` in Nano is a small proof of computation that validates a transaction. This means that **every block published into
the network must have a valid work attached in order to be valid**.

It was born as an anti-spam mechanism, as it is computationally expensive to be built (it requires several seconds in a modern computer,
hundreds of milliseconds in the most powerful GPU up to date of this writing). Moreover, the work difficulty is variable
and depends on the status of the network, meaning that it might increase or decrease (several times) from time to time.
It is used as a prioritization metric for new transactions, as the difficulty of work can be manually adjusted when
generated.

The result of a `work` computation is a hash value which is appended to the `block` itself in order to make it valid.

One of the most exciting features of `work` in Nano is that it can be **precached**. This is due to the block hash being
constructed only in function of the hash of the `frontier` of an account. This means that you can precompute work for
the next block of your account, no matter what kind of block (send/receive/representative change), as far as you know the
frontier block hash of your account. Moreover, since you can build the new block, compute its work and generate the
new block hash, you can use this created hash as the hypothetical new frontier of your account even before broadcasting it.
This allows you to create and chain many blocks offline, and then publish them all almost together.

Precaching work gives the illusion that Nano can be almost instant. And most of the times, it will be.

`nanoblocks` does not bundle the needed tools to generate work for a transaction, but this process can be relied to a nano node or a
nano work server as follows:


.. code-block:: python

    >>> from nanoblocks.node import NanoNode
    >>> from nanoblocks.work.backend import NanoWorkServer
    >>> from nanoblocks.network import NanoNetwork

    >>> nano_work_server = NanoWorkServer("http://work_server_host:7076")  # GPU host would be advisable to speed up computations
    >>> node = NanoNode("http://node_host:7076")
    >>> network = NanoNetwork(node, work_server=nano_work_server)

There's a tool called `nano-work-server <https://github.com/nanocurrency/nano-work-server>`_. You may want to
install it in case you want to play with transactions using `nanoblocks`.


Sending and receiving transactions
----------------------------------

*PS: Ensure you have a work server attached to the `network` object in order to continue.*

Once you have a `network` object running, you can start sending or receiving blocks for any account as far as you own
the private key required to sign these transactions.

The process consist of two parts:

    1. A block is built with the account transaction, worked and signed.
    2. The block is broadcasted to the network.

The following example illustrates how to build a send block between two accounts:

.. code-block:: python

    >>> account1 = network.accounts['nano_account1']
    >>> account2 = network.accounts['nano_account2']

    >>> account1.unlock("PRIVATEKEY_ACCOUNT1")

    # account1 sends a transaction to account2
    >>> send_block = account1.build_send_block(account_target=account2, nano_amount="0.00001")

    >>> network.blocks.broadcast(send_block)  # Sent to the network!

And now to receive it:

.. code-block:: python

    >>> account2.unlock("PRIVATEKEY_ACCOUNT2")

    # account2 receives the transaction from account1
    >>> receive_block = account2.build_receive_block(pending_block=send_block)
    >>> network.blocks.broadcast(receive_block)

This example shows the nature of the block-lattice: every account is the solely responsible for modifying its block-chain.
That is the reason that the sender account can build a send block, but it is also required that the receiver account builds the
corresponding receive block in the other end in order to receive the funds.

**What happens if a block is sent but not received?** When a block is sent, the sender is writing into his blockchain
a send transaction that will be stored forever in the block-lattice. This means that it is not reversible. Since the
very moment the sender sent this block, he updated his account balance (reducing it) thus he can't spend it anymore.
These transactions are called **pending transactions** and can stay forever in the network in this state.

The receiver can't spend this balance neither until he updates his own balance (increasing it) by the amount of the
corresponding send block. He is allowed to update his balance with a corresponding send block from other account
block-chain at any time. So no funds are ever lost, even if the pending transactions are not received. They can be
received in the future.

