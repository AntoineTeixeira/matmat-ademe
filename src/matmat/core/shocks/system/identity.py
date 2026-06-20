"""
Presentation
************
This module contains the definition of identity classes for system shocks.

Content
*******
    - :class:`SystemShockIdentity`
"""

__all__ = ["SystemShockIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractIdentity


@dataclass(kw_only=True)
class SystemShockIdentity(AbstractIdentity):
    """
    This class is the system shock identity card.
    It contains all the settings and characteristics of a system shock.
    """
