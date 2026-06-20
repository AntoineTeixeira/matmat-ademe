__all__ = ["AbstractEngine"]

from abc import ABC
from matmat.workflows.core import AbstractWorkflow, WorkflowStep
from matmat.workflows.engines.identity import AbstractEngineIdentity
from matmat.utils import constants as cst


class AbstractEngine(AbstractWorkflow, ABC):
    """
    Abstract class for engine workflow
    """

    _id: AbstractEngineIdentity

    @property
    def enabled_steps(self) -> set[WorkflowStep]:
        return {
            WorkflowStep.STEP_LOAD,
            WorkflowStep.STEP_PROCESS,
            WorkflowStep.STEP_CALCULATE,
            WorkflowStep.STEP_SAVE,
        }

    @classmethod
    def kind(cls) -> str:
        return cst.WF_ENGINE

    def post_process(self):
        pass
