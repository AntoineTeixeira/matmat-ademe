__all__ = ["AbstractAdapterIdentity"]

from abc import ABC
from dataclasses import dataclass

from matmat.workflows.identity import AbstractWorkflowIdentity


@dataclass(kw_only=True)
class AbstractAdapterIdentity(AbstractWorkflowIdentity, ABC):
    """
    Abstract identity for adapters
    """

    pass
