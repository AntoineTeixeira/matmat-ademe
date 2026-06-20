__all__ = ["AbstractAnalysis"]

from abc import ABC

from matmat.workflows.core import AbstractWorkflow, WorkflowStep
from matmat.workflows.analyses.identity import AbstractAnalysisIdentity
from matmat.utils import constants as cst


class AbstractAnalysis(AbstractWorkflow, ABC):
    """
    Abstract class for analysis workflow
    """

    _id: AbstractAnalysisIdentity

    @property
    def enabled_steps(self) -> set[WorkflowStep]:
        return {
            WorkflowStep.STEP_LOAD,
            WorkflowStep.STEP_PROCESS,
            WorkflowStep.STEP_POST_PROCESS,
            WorkflowStep.STEP_SAVE,
        }

    @classmethod
    def kind(cls) -> str:
        return cst.WF_ANALYSIS

    def calculate(self):
        pass
