"""
Presentation
************
    This module contains the definition of identity classes for systems.

Content
*******
    - :class:`SystemIdentity`
"""

__all__ = ["SystemIdentity"]

from dataclasses import dataclass

from matmat.core.base.identity import AbstractIdentity


@dataclass(kw_only=True)
class SystemIdentity(AbstractIdentity):
    """
    This class is the system identity card.
    It contains all the settings and characteristics of a system.

    Attributes
    ----------
        strategy : str
            The calcul strategy
    """

    strategy: str
