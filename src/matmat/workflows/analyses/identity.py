__all__ = ["AbstractAnalysisIdentity"]

from abc import ABC
from dataclasses import dataclass

from matmat.workflows.identity import AbstractWorkflowIdentity


@dataclass(kw_only=True)
class AbstractAnalysisIdentity(AbstractWorkflowIdentity, ABC):
    """
    Abstract identity for analysis
    """
