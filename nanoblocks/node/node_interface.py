from contextlib import contextmanager

import numpy as np

from nanoblocks.node.snapshot import NodeSnapshot
from nanoblocks.node.tape_record import TapeRecord
from nanoblocks.utils.time import SYSTEM_TIMEZONE, now


class NodeInterface:
    """
    Interface access to a Node.
    """

    def __init__(self, timezone=SYSTEM_TIMEZONE):
        self._timezone = timezone
        self._tape_record = None

    @property
    def timezone(self):
        return self._timezone

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()

    @property
    def version(self):
        """
        Returns the node information and version.

        Source: https://docs.nano.org/commands/rpc-protocol/#version
        """
        raise NotImplementedError()

    def available_supply(self):
        """
        Returns how many raw are in the public supply.

        Source: https://docs.nano.org/commands/rpc-protocol/#available_supply
        """
        raise NotImplementedError()

    def active_difficulty(self, include_trend=False):
        """
        Returns the difficulty values (16 hexadecimal digits string, 64 bit) and related multiplier from base
        difficulty.
        [DEPRECATED as of V22]

        Source: https://docs.nano.org/commands/rpc-protocol/#active_difficulty

        :param include_trend:
            Boolean, false by default. Also returns the trend of difficulty seen on the network as a list of
            multipliers.
        """
        raise NotImplementedError()

    def peers(self):
        """
        Returns a list of pairs of online peer IPv6:port and its node protocol network version.

        Source: https://docs.nano.org/commands/rpc-protocol/#peers
        """
        raise NotImplementedError()

    def telemetry(self):
        """
        Return metrics from other nodes on the network. By default, returns a summarized view of the whole network.

        Source: https://docs.nano.org/commands/rpc-protocol/#telemetry
        """
        raise NotImplementedError()

    def representatives(self, count=None, sorting=False):
        """
        Returns a list of pairs of representative and their voting weight.

        Source: https://docs.nano.org/commands/rpc-protocol/#representatives

        :param count:
            Number. Returns a list of pairs of representative and their voting weight up to count.

        :param sorting:
            Boolean, false by default. Additional sorting representatives in descending order.
            NOTE: The "count" option is ignored if "sorting" is specified
        """
        raise NotImplementedError()

    def representatives_online(self, weight=True, accounts=None):
        """
        Returns a list of online representative accounts that have voted recently.

        Source: https://docs.nano.org/commands/rpc-protocol/#representatives_online

        :param weight:
            Boolean, false by default. Returns voting weight for each representative.

        :param accounts:
            Array of accounts. Returned list is filtered for only these accounts.

        """
        raise NotImplementedError()

    def account_info(self, nano_address, representative=False, weight=False, pending=True, include_confirmed=False):
        """
        Returns frontier, open block, change representative block, balance, last modified timestamp from local database
        & block count for account.

        WARNING: Only works for accounts that have received their first transaction and have an entry on the ledger,
        will return "Account not found" otherwise.

        Source: https://docs.nano.org/commands/rpc-protocol/#account_info

        :param nano_address:
            Address of the account with format "NANO_...".

        :param representative:
            Boolean, false by default. Additionally, returns representative for account.

        :param weight:
            Boolean, false by default. Additionally, returns voting weight for account.

        :param pending:
            Boolean, false by default. Additionally, returns receivable balance for account.

        :param include_confirmed:
            Boolean, false by default. Adds new return fields with prefix of confirmed_ for consistency:

                * confirmed_balance: balance for only blocks on this account that have already been confirmed
                * confirmed_height: matches confirmation_height value
                * confirmed_frontier: matches confirmation_height_frontier value

            If representative option also true,
                * confirmed_representative included (representative account from the confirmed frontier block)

            If receivable option also true,
                * confirmed_receivable included (balance of all receivable amounts where the matching incoming send
                blocks have been confirmed on their account)
        """
        raise NotImplementedError()

    def account_history(self, nano_address, raw=False, count=10, head=None, reverse=None, offset=None,
                        account_filter=None):
        """
        Reports send/receive information for an account.
        Returns only send & receive blocks by default (unless raw is set to true - see optional parameters below):
        change, state change & state epoch blocks are skipped, open & state open blocks will appear as receive,
        state receive/send blocks will appear as receive/send entries.

        Response will start with the latest block for the account (the frontier), and will list all blocks back to the
        open block of this account when "count" is set to "-1".

        Note: "local_timestamp" returned since version 18.0, "height" field returned since version 19.0.

        Source: https://docs.nano.org/commands/rpc-protocol/#account_history


        :param nano_address:
            Address of the account with format "NANO_...".

        :param raw:
            Boolean, False by default. if set to true, instead of outputting a simplified send or receive explanation
            of blocks (intended for wallets), output all parameters of the block itself as seen in block_create or other
            APIs returning blocks.

            It still includes the "account" and "amount" properties you'd see without this option.
            State/universal blocks in the raw history will also have a subtype field indicating their equivalent
            "old" block. Unfortunately, the "account" parameter for open blocks is the account of the source block,
            not the account of the open block, to preserve similarity with the non-raw history.

        :param count:
            Number of blocks to retrieve in a single call to the node. By default, it is 10 blocks.

        :param head:
            head (64 hexadecimal digits string, 256 bit). Default is the latest block.
            Use this block as the head of the account instead. Useful for pagination.

        :param offset:
            offset (decimal integer). Skips a number of blocks starting from head (if given). Not often used.
            Available since version 11.0

        :param reverse:
            Boolean, False by default. If set to True, the response starts from head (if given, otherwise the first
            block of the account), and lists blocks up to the frontier (limited by "count").

            Note: the field previous in the response changes to next. Available since version 19.0

        :param account_filter:
            List  of public addresses. If set, results will be filtered to only show sends/receives connected to the
            provided account(s).

            Available since version 19.0. Note: In v19.0, this option does not handle receive blocks; fixed in v20.0.
        """
        raise NotImplementedError()

    def accounts_balances(self, addresses):
        """
        Returns how much RAW is owned and how many have not yet been received by accounts list.

        Source: https://docs.nano.org/commands/rpc-protocol/#accounts_balances

        :param addresses:
            List of "NANO_..." addresses.

        """
        raise NotImplementedError()

    def accounts_frontiers(self, addresses):
        """
        Returns a list of pairs of account and block hash representing the head block for accounts list.

        Source: https://docs.nano.org/commands/rpc-protocol/#accounts_frontiers

        :param addresses:
            List of "NANO_..." addresses.
        """

        raise NotImplementedError()

    def accounts_pending(self, accounts, threshold=None, source=False, count=1, include_active=False, sorting=True,
                         include_only_confirmed=True):
        """
        Returns a list of confirmed block hashes which have not yet been received by these accounts

        source: https://docs.nano.org/commands/rpc-protocol/#accounts_pending

        :param accounts:
            List of accounts ["nano_...", "nano_..."] to check for pending blocks.

        :param threshold:
            Number (128 bit, decimal), default None. Returns a list of receivable block hashes with amount more or equal
            to threshold.

        :param source:
            Boolean, False by default. Returns a list of receivable block hashes with amount and source accounts.

        :param count:
            Number, 1 by default. Specifies the number of pending blocks to be retrieved.

        :param include_active:
            Boolean, false by default. Include active (not confirmed) blocks.

        :param sorting:
            Boolean, false by default. Additionally, sorts each account's blocks by their amounts in descending order.

        :param include_only_confirmed:
            Boolean, true by default.
            Only returns blocks which have their confirmation height set or are undergoing confirmation height
            processing. If false, unconfirmed blocks will also be returned.
        """

        raise NotImplementedError()

    def block_count(self, include_cemented=True):
        """
        Reports the number of blocks in the ledger and unchecked synchronizing blocks.

        Source: https://docs.nano.org/commands/rpc-protocol/#block_count

        :param include_cemented:
            Default True. If True, "cemented" in the response will contain the number of cemented blocks.
        """

        raise NotImplementedError()

    def block_info(self, block_hash, json_block=True):
        """
        Retrieves a json representation of the block in contents along with:

            * since version 18.0: block_account, transaction amount, block balance, block height in account chain, block
              local modification timestamp.
            * since version 19.0: Whether block was confirmed, subtype (for state blocks) of send, receive, change or
              epoch.

        Source: https://docs.nano.org/commands/rpc-protocol/#block_info

        :param block_hash:
            Hash of the block to check.

        :param json_block:
            Default False. If True, "contents" will contain a JSON subtree instead of a JSON string.
        """
        raise NotImplementedError()

    def blocks_info(self, blocks_hashes, json_block=True, include_not_found=False):
        """
        Retrieves a json representations of blocks in contents along with:

            * since version 18.0: block_account, transaction amount, block balance, block height in account chain,
                block local modification timestamp.

            * since version 19.0: Whether block was confirmed, subtype (for state blocks) of send, receive, change or
                epoch.

            * since version 23.0: successor returned.

        Using the optional json_block is recommended since v19.0.

        Source: https://docs.nano.org/commands/rpc-protocol/#blocks_info

        :param blocks_hashes:
            List of blocks hashes to retrieve

        :param json_block:
            Default False. If True, "contents" will contain a JSON subtree instead of a JSON string.

        :param include_not_found:
            Default False. If True, an additional key "blocks_not_found" is provided in the response, containing a list
            of the block hashes that were not found in the local database. Previously to this version an error would be
            produced if any block was not found.
        """
        raise NotImplementedError()

    def block_confirm(self, block_hash):
        """
        Request asynchronous confirmation for block from known online representative nodes.
        Once the confirmation is requested to the node, a confirmation process starts.

        It is required to peek for confirmation results at confirmation history.

        Source: https://docs.nano.org/commands/rpc-protocol/#block_confirm

        NOTE: Unless there was an error encountered during the command execution, the response will always return
        "started": "1".

             This response does not indicate the block was successfully confirmed, only that an error did not occur.
        This response happens even if the block has already been confirmed previously and notifications will be
        triggered for this block (via HTTP callbacks or WebSockets) in all cases. This behavior may change in a
        future release.

        :param block_hash:
            Hash of the block to check.
        """
        raise NotImplementedError()

    def process(self, block_definition, subtype=None):
        """
        Publish a block to the network.

        https://docs.nano.org/commands/rpc-protocol/#process

        :param block_definition:
            A JSON block definition of the block to be published.

        :param subtype:
            A subtype string defining the type of block.
        """
        raise NotImplementedError()

    def process_tape_record(self, tape_record):
        """
        Publishes many blocks to the network, all at once.

        :param tape_record:
            A tape record that contains all the blocks' definition recorded from hooking a node `process()` method.
        """
        for record in tape_record:
            self.process(**record)

    def snapshot(self, accounts_list, blocks_list=None, shallow_history=True, max_pending=100, pending_threshold=None,
                 missing='raise'):
        """
        Exports the network information of the given accounts and blocks list up to the current date.
        The network information can be used as a snapshot to be loaded in an offline environment, under a NodeVirtual
        class object.

        :param accounts_list:
            List of 'NANO_...' accounts to be exported. This includes their internal blocks.

        :param blocks_list:
            List of individual blocks to be exported.

        :param shallow_history:
            If True, Only the frontier (the latest block) of every account is included in the snapshot. Otherwise, all
            blocks are exported.

        :param max_pending:
            Maximum number of pending blocks to be stored in the snapshot for each account.

        :param pending_threshold:
            Minimum amount threshold of pending blocks (to filter).

        :param missing:
            Action to be done in case a missing account/block in the network is detected. The following values are
            accepted:
                * 'raise' raises a KeyError exception.
                * 'skip' ignores the error and skips the account/block.

        :return:
            Snapshot object that can be exported to a file or loaded into a VirtualNode.
        """
        def fetch_account(address):
            account_info = self.account_info(nano_address=address, representative=True, weight=True, pending=True)
            if account_info.get('error', None) == 'Account not found':
                if missing == 'raise':
                    raise KeyError(f"Account {address} not found in the ledger.")
                else:
                    account_info = None

            return account_info

        if type(accounts_list) is str:
            accounts_list = [accounts_list]

        if blocks_list is None:
            blocks_list = []

        current_date = now(self._timezone)

        # 1. We retrieve every account
        snapshot_accounts = {address: fetch_account(address) for address in accounts_list}
        snapshot_accounts = {k: v for k, v in snapshot_accounts.items() if v is not None}

        # 2. We retrieve pending blocks of every account
        snapshot_pending_blocks = self.accounts_pending(accounts_list, source=True, count=max_pending,
                                                        threshold=pending_threshold)['blocks']
        snapshot_pending_blocks = {k: v for k, v in snapshot_pending_blocks.items() if v != ''}

        # 3. We retrieve history blocks of every account
        snapshot_history_blocks = {
            address: self.account_history(nano_address=address, count=(1 if shallow_history else -1))['history']
            for address in accounts_list
        }

        blocks_to_fetch = [list(blocks.keys()) for address, blocks in snapshot_pending_blocks.items()]
        if len(blocks_to_fetch):
            blocks_to_fetch = np.hstack(blocks_to_fetch)

        blocks_to_fetch = list(blocks_to_fetch)
        blocks_to_fetch += blocks_list

        for address, history in snapshot_history_blocks.items():
            for block in history:
                blocks_to_fetch.append(block['hash'])

        blocks_to_fetch = np.unique(blocks_to_fetch).tolist()

        blocks_info = self.blocks_info(blocks_to_fetch, include_not_found=True)
        snapshot_blocks = blocks_info['blocks']

        if len(blocks_info.get('blocks_not_found', [])) > 0 and missing == 'raise':
            raise KeyError(f"The following blocks were not found in the ledger: {blocks_info['blocks_not_found']}")

        snapshot_struct = {
            "snapshot_node_source": "virtual",
            "snapshot_node_version": self.version,
            "snapshot_date": current_date,
            "snapshot_accounts": snapshot_accounts,
            "snapshot_pending_blocks": snapshot_pending_blocks,
            "snapshot_history_blocks": snapshot_history_blocks,
            "snapshot_blocks": snapshot_blocks
        }

        return NodeSnapshot(snapshot_struct)

    @contextmanager
    def tape_record(self):
        """
        Yields a tape record object that contains all the blocks' definition for the hooked `process()` method.
        This method is decorated with a context manager.

        The tape record object can be reprocessed again in any node by passing it as an argument to
        the `process_tape_record()` method. This is useful under offline environments: all the processed blocks can be
        recorded in the offline environment and then republished again in an online environment.

        Usage example:
        ```
            >>> with node.tape_record() as rec:
            >>>     node.process(block_definition)
            >>> print(rec)
            [TAPE_RECORD] 1 operations tracked.
        ```
        """
        self._tape_record = TapeRecord()
        yield self._tape_record
        self._tape_record = None
