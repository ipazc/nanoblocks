# NanoBlocks

<span style="color:red">Note: this package is in _alpha_ state, meaning that it should not be used under production environments, and only for testing purposes!!</span>

[NANO](https://nano.org/) is a cryptocurrency that allows instant and feeless transactions, making it a viable solution for micropayments. 

`NanoBlocks` is an **unofficial** Python package built to ease the access to [NANO cryptocurrency](https://nano.org/). It is intended to give an easy interface for programmers to play with the Nano Network, allowing most Nano common operations which includes creating new wallets and accounts, checking accounts information, making transactions and more.

An extensive documentation of the possibilites can be found by [reading the docs](https://readthedocs.org/projects/nanoblocks/). 
 
# Installation

`NanoBlocks` can be installed through pip:

```bash
pip install nanoblocks
```

# Getting started

It is required to have a Nano node installed and configured in order to release all the functionalities that this package can give; even though it can still work offline for certain operations (like creating wallets, accounts, and building and signing blocks). 

It is highly encouraged to get access to the node RPC and WebSocket servers. A guide for installation of the node can be found [here](https://docs.nano.org/running-a-node/overview/). Furthermore, a [nano-work-server](https://github.com/nanocurrency/nano-work-server) access for work generation is also recommended.  

Everything starts with the `NanoNode` and the `NanoNetwork` classes:

```python
>> from nanoblocks.node import NanoNode
>> from nanoblocks.network import NanoNetwork

>> node = NanoNode("http://localhost:7076", "ws://localhost:7078")
>> node
[Node http://localhost:7076 (Nano V21.2)]

>> network = NanoNetwork(node)
>> network
[Node http://localhost:7076 (Nano V21.2)] (270 peers; 15362838 account)
```

## Handling accounts in the network

Having a `NanoNetwork` class instance, accounts in the network can be accessed as easy as follows:

```python
>> account = network.accounts["nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi"]
```

You might have noticed well: `network.accounts[]` behaves like a python dictionary, which in turns makes it easy to access any account in the network.
In `NanoBlocks`, every account is wrapped inside an `Account` class which gives basic functionality for account handling:


```python
>> account
nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi (
	Total blocks: 733
	Total balance: 0.000002000000000000000000000002 NANO
	Confirmed balance: 0.000000000000000000000000000000 NANO
	Pending balance: 0.000002000000000000000000000002 NANO
	Last confirmed payment: 2020-12-02 01:30:39+01:00
	Is virtual: False
)
>> account.balance
0.000002000000000000000000000002 NANO

>> account.pending_balance
0.000002000000000000000000000002 NANO

>> account.confirmed_balance
0.000000000000000000000000000000 NANO

>> account.public_key
9D050D7C3DD1D87F7C3F8EA8A83B9A8BF52AE6EB4562D945D563A1C0384C691F

# The representative is another account object
>> account.representative
nano_16u1uufyoig8777y6r8iqjtrw8sg8maqrm36zzcm95jmbd9i9aj5i8abr8u5 (
	Total blocks: 6
	Total balance: 0.000000000000000000000000000000 NANO
	Confirmed balance: 0.000000000000000000000000000000 NANO
	Pending balance: 0.000000000000000000000000000000 NANO
	Last confirmed payment: 2020-12-02 01:57:11+01:00
	Is virtual: False
)

>> account.frontier
FED268136D2931EDEA61057D91C3C250894EF95C14C0D16CA0D126D99579C53C
```

Do you want to check the blockchain of an account? `Account` class contains the attribute `history` to do so:

```python
>> account.history
nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi History: 733 blocks

# Retrieving the number of blocks in the chain
>> len(account.history)
733

# Retrieving the first block of the chain
>> account.history[0]
[Block #1 from account nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi]
	Type: receive
	Hash: D255CE60964219EB614DC9ED6295C587B9C3225B25E177E3C45C651044C9982D
	Source account: nano_3dcfozsmekr1tr9skf1oa5wbgmxt81qepfdnt7zicq5x3hk65fg4fqj58mbr
	Amount: 0.000170000000000000013254000640
	Local date: 1970-01-01 01:00:00+01:00

# Retrieving the last block of the chain
>> account.history[-1]
[Block #731 from account nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi]
	Type: send
	Hash: 2950AD21978D1898CA5CFDE2E5AB4D30746DD5E55D5BB96D69B1509A37C39D85
	Destination account: nano_1j6q8xh9rw3sr9o6jgwys7u5ntzcq6ktx386e3tdoy9skdq9meqhngq7yp7d
	Amount: 0.000002000000000000000000000000
	Local date: 2019-03-14 08:04:41+01:00

# Iterating over the block chain of the account

>> for block in account.history:
>>    print(block.hash)
FED268136D2931EDEA61057D91C3C250894EF95C14C0D16CA0D126D99579C53C
2950AD21978D1898CA5CFDE2E5AB4D30746DD5E55D5BB96D69B1509A37C39D85
BBFA2CF652F3B080DE2F1A7F282270CE80DB86E78102E4EF60F42B5A9179CF8D
01A4ACD8A91F1FBCE4866F44D5A01004915DF8F610D105B31323BAEE9DA82042
50CE731BCD930EF96D14F61523F1D3A13B23883D3EA3D5A365BBFF002862C796
54CF614092ED046775D5954BE5E0C116EB4FBD2354E100F666783DA3F3E1DCDB
...
``` 

# Accessing wallets

The `NanoBlocks` package bundles cryptographic functions that allows handling wallets and accounts creation even without requiring a node, which makes it possible to run it offline.
Thus, it is extremely easy to access or create new wallets by using the `wallets` attribute from the `Network` class.

```python
# To access an existing wallet by using the 64-Bytes seed:
>> wallet = network.wallets["7F632A80ECCC54A058602CD64A81D23A6B4D7320562E4767C9EB0BBB1151CDF2"]

# Alternatively, it can be accessed with the BIP-39 24 words:
>> wallet = network.wallets[['legal', 'bone', 'parent', 'sunset', 'shed', 'expand', 'ghost', 'airport', 'stone', 'favorite', 'innocent', 'inquiry', 'regular', 'ridge', 'life', 'shift', 'electric', 'dinner', 'kiss', 'blast', 'rain', 'pottery', 'daughter', 'execute']]

# Or it can be created from scratch (using a the system's cryptographic-safe number generator)
>> wallet = network.wallets.create()

# Wallet information can be printed out
>> print(wallet.seed)
7F632A80ECCC54A058602CD64A81D23A6B4D7320562E4767C9EB0BBB1151CDF2

>> print(wallet.mnemonic)
['legal', 'bone', 'parent', 'sunset', 'shed', 'expand', 'ghost', 'airport', 'stone', 'favorite', 'innocent', 'inquiry', 'regular', 'ridge', 'life', 'shift', 'electric', 'dinner', 'kiss', 'blast', 'rain', 'pottery', 'daughter', 'execute']
```

Do you want to access or create new accounts for this wallet? easy:

```python
>> account_0 = wallet.accounts[0]
>> account_0
nano_1kbdepwojawpwnigx8i4sxzgstuzcgo9uygn8jmidsezhgjmgm6e9kq3s17e (
	Total blocks: 0
	Total balance: 0.000000000000000000000000000000 NANO
	Confirmed balance: 0.000000000000000000000000000000 NANO
	Pending balance: 0.000000000000000000000000000000 NANO
	Last confirmed payment: 2021-03-16 00:41:40+01:00
	Is virtual: True
)

>> account_1 = wallet.accounts[1]
>> account_1
nano_37jp35s74dj78bc9i6fhg7ww1n137i1yfdqmdeodxfx655trg4kdnq8qfdcm (
	Total blocks: 0
	Total balance: 0.000000000000000000000000000000 NANO
	Confirmed balance: 0.000000000000000000000000000000 NANO
	Pending balance: 0.000000000000000000000000000000 NANO
	Last confirmed payment: 2021-03-16 00:41:40+01:00
	Is virtual: True
)
```

Since the accounts in Nano are deterministic, they are created on-demand by using any integer index value for the `wallet.accounts[]` array.
Of course, if the account already exists, it will be loaded accordingly.

## Handling balances

Nano uses huge numbers representation that does not fit well the Python's integer.
This package offers a class that behaves like a Python's integer but can deal with the amounts:

```python
>> from nanoblocks.currency import Amount
>> amount = Amount("10") # 10 RAW
>> amount
0.000000000000000000000000000010 NANO
>> amount.as_raw()
10 raw
>> amount.as_unano()
0.000000000000000010 unano
>> amount.as_knano()
0.000000000000000000000000000000010 Gnano
``` 

Amounts can be summed, substracted, multiplied, divided and every arithmetic operation an integer can have, with other amounts or with pure integers.

```python
>> amount * 3
0.000000000000000000000000000030 NANO

>> amount + 3
0.000000000000000000000000000013 NANO

>> amount * amount
0.000000000000000000000000000100 NANO
``` 

## Sending/receiving transactions

`NanoBlocks` allows to sign transactions offline but a work-server is required as this package does not bundle any work-generation process. If a nano-work-server is available, it can be attached to the `network` object as follows:
```python
    from nanoblocks.work.backend.nano_work_server import NanoWorkServer

    work_server = NanoWorkServer('http://192.168.1.46:7076')
    network.work_server = work_server
```

If the network has a work server, the accounts can automatically request work generation to the server: 

```python
>> send_block = account.build_send_block("nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi", "0.00001")
# send_block is an already signed and ready block to be broadcasted to the network

# If no work server available, the work hash for the account's frontier must be provided:
>> send_block = account.build_send_block("nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi", "0.00001", work_hash=WORK_HASH)
```

Every block can be broadcasted to the network by using the `blocks` attribute of the `Network` class:
```python
>> network.blocks.broadcast(send_block)
```

## Handling blocks

The `network.blocks` attribute gives direct access to the blocks of the whole network. Like `accounts` and `wallets`, having the identifier hash of the blocks, they can be accessed like if it was a dictionary:

```python
>> block = network.blocks["4FEC4BDD078C741F599221C67C8BE6493C872EF9B30968BBF4991640FFF42DA2"]
>> block
[Block #4 from account nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi]
	Type: receive
	Hash: 4FEC4BDD078C741F599221C67C8BE6493C872EF9B30968BBF4991640FFF42DA2
	Source account: nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi
	Amount: 0.000040000000000000000000000000
	Local date: 1970-01-01 01:00:00+01:00
``` 

Every Block is wrapped inside a `Block` class, which gives basic functionality for handling blocks.

## Requesting payments

In `NanoBlocks`, requesting a payment is as simple as follows:
```python
>> payment = account.request_payment("0.01")  # in NANO unit measure by default

# Alternatively, it can be forced a specified unit measure
>> from nanoblocks.currency import Amount
>> payment = account.request_payment(Amount("1"))  # In RAW unit measure

>> qr_code = payment.qr_code  # PILLOW image
>> qr_code.show()

>> block = payment.wait(timeout=60)
```

If the websocket is available in the node, the payment will be subscribed for the specified amount of time, and the payment block will be returned. In case that no websocket is available, the payment will fall-back to give the same functionality by continuous polling.

# LICENSE

This package is license under the MIT license.