"""
Presentation
************
    This module contains the definition of identity classes for accounts.

Content
*******
- Classes:
    - :class:`AccountsIdentity`
"""

__all__ = ["AccountsIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractIdentity


@dataclass(kw_only=True)
class AccountsIdentity(AbstractIdentity):
    """
    This class is the accounts identity card.
    It contains all the settings and characteristics of an accounts.

    Attributes
    ----------
        extension_names : list[str]
            The list of the names of the extension included in the accounts
    """

    extension_names: list[str]

    def add_extension(self, name: str):
        self.extension_names.append(name)

    def remove_extension(self, name: str):
        if name in self.extension_names:
            self.extension_names.remove(name)
