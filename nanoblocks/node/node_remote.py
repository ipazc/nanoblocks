import requests

from nanoblocks.node.node_interface import NodeInterface, SYSTEM_TIMEZONE


class NodeRemote(NodeInterface):

    # Inheriting the docstrings from the interface
    __doc__ = NodeInterface.__doc__ + (__doc__ if __doc__ is not None else "")

    def __init__(self, http_url, ws_url=None, timezone=SYSTEM_TIMEZONE):
        super().__init__(timezone=timezone)
        self._http_url = http_url
        self._ws_url = ws_url

    @property
    def http_url(self):
        return self._http_url

    @property
    def ws_url(self):
        return self._ws_url

    def __str__(self):
        base_str = f"[Node http={self.http_url}"

        if self._ws_url is not None:
            base_str += f"; ws={self.ws_url}"

        base_str += f" ({self.version['node_vendor']})]"
        return base_str

    def __repr__(self):
        return str(self)

    def _ask(self, message):
        """
        Makes a call to the rest api with the specified message and returns the result.

        :param message:
            A crafted JSON message.
        """
        response = requests.post(self.http_url, json=message).json()
        return response

    @property
    def version(self):
        message = {
            "action": "version"
        }

        return self._ask(message)

    def available_supply(self):
        message = {
            "action": "available_supply"
        }

        return self._ask(message)

    def active_difficulty(self, include_trend=False):
        message = {
            "action": "active_difficulty",
            "include_trend": include_trend
        }

        return self._ask(message)

    def peers(self):
        message = {
            "action": "peers"
        }

        return self._ask(message)

    def telemetry(self):
        message = {
            "action": "telemetry"
        }

        return self._ask(message)

    def representatives(self, count=None, sorting=False):
        message = {
            "action": "representatives",
            "sorting": sorting
        }

        if count:
            message['count'] = count

        return self._ask(message)

    def representatives_online(self, weight=True, accounts=None):
        message = {
            "action": "representatives_online",
            "weight": weight
        }

        if accounts is not None:
            message['accounts'] = accounts

        return self._ask(message)

    def account_info(self, nano_address, representative=False, weight=False, pending=True, include_confirmed=False):
        message = {
            "action": "account_info",
            "representative": representative,
            "account": nano_address,
            "weight": weight,
            "pending": pending,
            "include_confirmed": include_confirmed
        }

        return self._ask(message)

    def account_history(self, nano_address, raw=False, count=10, previous=None, head=None, reverse=None, offset=None,
                        account_filter=None):
        message = {
            "action": "account_history",
            "account": nano_address,
            "count": count
        }

        if raw:
            message['raw'] = raw

        if previous:
            message['head'] = previous

        if head:
            message['head'] = head

        if reverse:
            message['reverse'] = reverse

        if offset:
            message['offset'] = offset

        if account_filter:
            message['account_filter'] = account_filter

        return self._ask(message)

    def accounts_balances(self, addresses):
        message = {
            "action": "accounts_balances",
            "accounts": addresses
        }

        return self._ask(message)

    def accounts_frontiers(self, addresses):
        message = {
            "action": "accounts_frontiers",
            "accounts": addresses
        }

        return self._ask(message)

    def accounts_pending(self, accounts, threshold=None, source=False, count=1, include_active=False, sorting=True,
                         include_only_confirmed=True):

        message = {
            "action": "accounts_pending",
            "accounts": accounts,
            "count": count,
            "source": source,
            "sorting": sorting,
            "include_active": include_active,
            "include_only_confirmed": include_only_confirmed
        }

        if threshold is not None:
            message['threshold'] = threshold

        return self._ask(message)

    def block_count(self, include_cemented=True):
        message = {
            "action": "block_count"
        }

        return self._ask(message)

    def block_info(self, block_hash, json_block=True):
        message = {
            "action": "block_info",
            "json_block": json_block,
            "hash": block_hash
        }

        return self._ask(message)

    def blocks_info(self, blocks_hashes, json_block=True, include_not_found=False):
        message = {
            "action": "blocks_info",
            "receivable": True,
            "source": True,
            "balance": True,
            "include_not_found": include_not_found,
            "json_block": json_block,
            "hashes": blocks_hashes
        }

        return self._ask(message)

    def block_confirm(self, block_hash):
        message = {
            "action": "block_confirm",
            "hash": block_hash
        }

        return self._ask(message)

    def process(self, block_definition, subtype=None):
        message = {
            "action": "process",
            "json_block": "true",
            "block": block_definition
        }

        if subtype:
            message.update({'subtype': subtype})

        if self._tape_record is not None:
            self._tape_record.append({'subtype': subtype, 'block_definition': block_definition})

        return self._ask(message)

    def snapshot(self, accounts_list, blocks_list=None, shallow_history=True, max_pending=100, pending_threshold=None,
                 missing='raise'):
        snapshot = super().snapshot(accounts_list, blocks_list, shallow_history, max_pending, pending_threshold,
                                    missing)

        # noinspection PyProtectedMember
        snapshot._snapshot_struct['snapshot_node_source'] = self.http_url
        return snapshot
