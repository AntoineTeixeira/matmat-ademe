"""
Presentation
************
This module contains the definition of identity classes for extensions shocks
data.

Content
*******
    - :class:`ExtensionShockDataIdentity`
"""

__all__ = ["ExtensionShockDataIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractBaseIdentity


@dataclass(kw_only=True)
class ExtensionShockDataIdentity(AbstractBaseIdentity):
    """
    This class is the identity card of an extension shock data.
    It contains all the settings and characteristics of an extension shock
    data.

    Attributes
    ----------
        extension_name (str):
            The name of the extension shock owning the data
    """
    extension_name: str
