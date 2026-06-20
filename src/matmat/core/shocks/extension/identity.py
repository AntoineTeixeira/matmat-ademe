"""
Presentation
************
This module contains the definition of identity classes for extensions shocks.

Content
*******
    - :class:`ExtensionShockIdentity`
"""

__all__ = ["ExtensionShockIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractIdentity


@dataclass(kw_only=True)
class ExtensionShockIdentity(AbstractIdentity):
    """
    This class is the extension shock identity card.
    It contains all the settings and characteristics of an extension shock.

    Attributes
    ----------
        extension_name : str
            The name of the extension to shock
    """

    extension_name: str

    @property
    def name(self):
        return self.extension_name
