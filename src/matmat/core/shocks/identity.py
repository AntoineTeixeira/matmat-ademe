"""
Presentation
************
This module contains the definition of identity classes for accounts shocks.

Content
*******
    - :class:`AccountsShockIdentity`
"""

__all__ = ["AccountsShockIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractIdentity


@dataclass(kw_only=True)
class AccountsShockIdentity(AbstractIdentity):
    """
    This class is the accounts shock identity card.
    It contains all the settings and characteristics of an accounts shock.

    Attributes
    ----------
        extension_names : list[str]
            The list of the names of the extension shocks included in the
            shock
    """

    extension_names: list[str]

    def add_extension(self, name: str):
        self.extension_names.append(name)

    def remove_extension(self, name: str):
        if name in self.extension_names:
            self.extension_names.remove(name)
