"""
The account subpackage contains classes to manage the accounts in the Nano network.

This subpackage is indirectly handled by the :class:`nanoblocks.network.NanoNetwork` class and should not be
instantiated manually.
"""
from nanoblocks.account.account import Accounts, Account

__all__ = [
    "Accounts",
    "Account"
]
