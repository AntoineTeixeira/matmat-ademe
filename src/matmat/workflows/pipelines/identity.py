__all__ = ["AbstractPipelineIdentity"]

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from matmat.workflows.identity import AbstractWorkflowIdentity


@dataclass(kw_only=True)
class AbstractPipelineIdentity(AbstractWorkflowIdentity, ABC):
    """
    Abstract identity for pipelines

    Attributes
    ----------
        base_year : int
            The base_year
        proj_year : int
            The projection year
        scenario_name: str
            The name of the scenario
    """

    base_year: Optional[int] = None
    proj_year: Optional[int] = None
    scenario_name: Optional[str] = None
