"""
Presentation
************
    This module contains the definition of identity classes for extensions.

Content
*******
    - :class:`ExtensionIdentity`
"""

__all__ = ["ExtensionIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractIdentity


@dataclass(kw_only=True)
class ExtensionIdentity(AbstractIdentity):
    """
    This class is the extension identity card.
    It contains all the settings and characteristic of an extension.

    Attributes
    ----------
        extension_name : str
            The name of the extension
        strategy : str
            The calcul strategy
    """

    extension_name: str
    strategy: str

    @property
    def name(self):
        return self.extension_name
