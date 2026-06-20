__all__ = ["AbstractEngineIdentity"]

from abc import ABC
from dataclasses import dataclass

from matmat.workflows.identity import AbstractWorkflowIdentity


@dataclass(kw_only=True)
class AbstractEngineIdentity(AbstractWorkflowIdentity, ABC):
    """
    Abstract identity for engines
    """

    pass
