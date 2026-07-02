"""
Presentation
************
This module contains the definition of identity classes for extension data.

Content
*******
    - :class:`ExtensionDataIdentity`
"""

__all__ = ["ExtensionDataIdentity"]


from dataclasses import dataclass

from matmat.core.base.identity import AbstractBaseIdentity


@dataclass(kw_only=True)
class ExtensionDataIdentity(AbstractBaseIdentity):
    """
    This class is the identity card of an extension data.
    It contains all the settings and characteristics of an extension data.

    Attributes
    ----------
        extension_name (str):
            The name of the extension owning the data
    """

    extension_name: str
