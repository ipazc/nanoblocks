from nanoblocks.node.node_interface import NodeInterface, SYSTEM_TIMEZONE


class NodeVirtual(NodeInterface):

    # Inheriting the docstrings from the interface
    __doc__ = NodeInterface.__doc__ + (__doc__ if __doc__ is not None else "")

    def __init__(self, timezone=SYSTEM_TIMEZONE, internal_accounts=None, internal_accounts_history=None,
                 internal_accounts_pending=None, internal_blocks=None):
        super().__init__(timezone=timezone)

        if internal_blocks is None:
            internal_blocks = {}

        if internal_accounts is None:
            internal_accounts = {}

        if internal_accounts_history is None:
            internal_accounts_history = {}

        if internal_accounts_pending is None:
            internal_accounts_pending = {}

        self._internal_accounts = internal_accounts
        self._internal_accounts_history = internal_accounts_history
        self._internal_accounts_pending = internal_accounts_pending
        self._internal_blocks = internal_blocks
        self._last_snapshot = None

    @property
    def http_url(self):
        return "Virtual"

    @property
    def ws_url(self):
        return "Virtual"

    def __str__(self):
        base_str = f"[Node http={self.http_url}"

        if self.ws_url is not None:
            base_str += f"; ws={self.ws_url}"

        base_str += f" ({self.version['node_vendor']})]"

        if self._last_snapshot is not None:
            base_str += f" Last snapshot loaded: {self._last_snapshot}"

        return base_str

    def __repr__(self):
        return str(self)

    @property
    def version(self):
        result = {
            "rpc_version": "1",
            "store_version": "14",
            "protocol_version": "17",
            "node_vendor": "Nano 22.1",
            "store_vendor": "VIRTUAL",
            "network": "VIRTUAL",
            "network_identifier": "VIRTUAL",
            "build_info": "NANOBLOCKS VIRTUAL NETWORK"
        }

        return result

    def available_supply(self):
        result = {
            "available": "133248061996216572282917317807824970865"
        }

        return result

    def active_difficulty(self, include_trend=False):
        result = {
            'deprecated': '1',
            'network_minimum': 'fffffff800000000',
            'network_receive_minimum': 'fffffe0000000000',
            'network_current': 'fffffff800000000',
            'network_receive_current': 'fffffe0000000000',
            'multiplier': '1'
        }

        return result

    def peers(self):
        result = {'peers': {}}
        return result

    def telemetry(self):
        result = {
            'block_count': len(self._internal_blocks),
            'cemented_count': len(self._internal_blocks),
            'unchecked_count': 0,
            'account_count': len(self._internal_accounts),
            'bandwidth_cap': 0,
            'peer_count': 0,
            'protocol_version': '18',
            'uptime': '0',
            'genesis_block': '991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948',
            'major_version': '22',
            'minor_version': '1',
            'patch_version': '0',
            'pre_release_version': '0',
            'maker': '0',
            'timestamp': '1639240170835',
            'active_difficulty': 'fffffff800000000'
        }

        result = {k: str(v) for k, v in result.items()}

        return result

    def representatives(self, count=10, sorting=False):
        result = {
            "representatives": {}
        }

        return result

    def representatives_online(self, weight=True, accounts=None):
        result = {
            "representatives": {
                "nano_1gemini56efw4qrfzfcc71cky1wj7a6673fu5ue5afyyz55zb1cxkj8rkr1n": {
                    "weight": "22281860055566536284103071287606747"
                }
            }
        }

        return result

    def account_info(self, nano_address, representative=False, weight=False, pending=True, include_confirmed=False):
        result = self._internal_accounts.get(nano_address, {'error': 'Account not found'})
        return result

    def account_history(self, nano_address, raw=False, count=10, previous=None, head=None, reverse=None, offset=None,
                        account_filter=None):
        default_response = {
            'account': nano_address,
            'history': ''
        }

        result = self._internal_accounts_history.get(nano_address, default_response)

        return result

    def accounts_balances(self, addresses):
        result = {
            'balances': {
                address: {
                    'balance': self._internal_accounts[address]['balance'] if address in self._internal_accounts else 0,
                    'pending': self._internal_accounts[address]['pending'] if address in self._internal_accounts else 0,
                }
                for address in addresses
            }
        }

        return result

    def accounts_frontiers(self, addresses):
        result = {
            'frontiers': {
                address: self._internal_accounts[address]['frontier']
                for address in addresses if address in self._internal_accounts
            }
        }
        return result

    def accounts_pending(self, accounts, threshold=None, source=False, count=1, include_active=False, sorting=True,
                         include_only_confirmed=True):
        result = {
            'blocks': {
                address: {self._internal_accounts_pending[address]: self._internal_blocks[self._internal_accounts_pending[address]]['balance']}
                for address in accounts
            }

        }
        return result

    def block_count(self, include_cemented=True):
        result = {
            'count': str(len(self._internal_blocks)),
            'unchecked': '0',
            'cemented': str(len(self._internal_blocks))
        }
        return result

    def block_info(self, block_hash, json_block=True):
        result = self._internal_blocks.get(block_hash, {'error': 'Block not found'})
        return result

    def blocks_info(self, blocks_hashes, json_block=True, include_not_found=False):
        blocks = {}
        no_blocks = []

        for block_hash in blocks_hashes:
            block_info = self.block_info(block_hash)

            if 'error' not in block_info:
                blocks[block_hash] = block_info
            else:
                no_blocks.append(block_hash)

        if include_not_found:
            result = {'blocks': blocks, 'blocks_not_found': no_blocks}
        else:
            result = {'error': 'Block not found'}

        return result

    def block_confirm(self, block_hash):
        if block_hash in self._internal_blocks:
            result = {'started': '0'}
        else:
            result = {'error': 'Block not found'}

        return result

    def load_snapshot(self, snapshot):
        """
        Loads a node snapshot into this virtual instance.
        A snapshot contains all the required information to make offline operations on certain accounts.

        Incremental updates are supported by default, meaning that the internal state of this virtual node can be
        updated with sequential loads of snapshots.

        :param snapshot: snapshot of accounts, blocks and transactions history from a real node.
        """
        self._internal_accounts.update(snapshot.accounts)
        self._internal_blocks.update(snapshot.blocks)
        self._internal_accounts_pending.update(snapshot.pending_blocks)
        self._internal_accounts_history.update(snapshot.history_blocks)
        self._last_snapshot = snapshot

    def process(self, block_definition, subtype=None):
        """
        Virtual process -- No signatures are checked, no correctness is checked.

        Operates the accounts referenced by the `block_definition` without ensuring its correctness.
        """

        if self._tape_record is not None:
            self._tape_record.append({'subtype': subtype, 'block_definition': block_definition})

        pass

    def healthy(self):
        return True

    @property
    def ws(self):
        return None
