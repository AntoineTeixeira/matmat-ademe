"""
Presentation
************
This module contains the definition of abstract identity class for data and
more complex objects such as accounts, system, extension and shocks.

Content
*******
- Classes:
    - :class:`AbstractBaseIdentity`
    - :class:`AbstractIdentity`
"""

__all__ = ["AbstractBaseIdentity", "AbstractIdentity"]

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from matmat.utils.mixins import JsonMixin


@dataclass(kw_only=True)
class AbstractBaseIdentity(ABC, JsonMixin):
    """
    This class is the base identity class.

    Attributes
    ----------
    No attributes
    """
    pass


@dataclass(kw_only=True)
class AbstractIdentity(AbstractBaseIdentity):
    """
    This class represents an identity card.
    It contains all the basic information used in various MatMat identity
    classes (system, extension, accounts, shock)

    Attributes
    ----------
        base_year : int
            The base_year
        proj_year : int
            The projection year
        scenario_name: str
            The name of the scenario
    """

    base_year: int
    proj_year: Optional[int] = None
    scenario_name: Optional[str] = None
