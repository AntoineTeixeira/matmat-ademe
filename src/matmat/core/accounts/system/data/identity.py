"""
Presentation
************
This module contains the definition of identity classes for system data.

Content
*******
    - :class:`SystemDataIdentity`
"""

__all__ = ["SystemDataIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractBaseIdentity


@dataclass(kw_only=True)
class SystemDataIdentity(AbstractBaseIdentity):
    """
    This class is the identity card of a system data.
    It contains all the settings and characteristics of a system data.
    """
