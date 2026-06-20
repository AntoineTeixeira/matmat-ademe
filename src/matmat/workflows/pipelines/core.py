__all__ = ["AbstractPipeline"]

from abc import ABC

from matmat.workflows.core import AbstractWorkflow, WorkflowStep
from matmat.workflows.pipelines.identity import AbstractPipelineIdentity
from matmat.utils import constants as cst


class AbstractPipeline(AbstractWorkflow, ABC):
    """
    Abstract class for pipeline workflow
    """

    _id: AbstractPipelineIdentity

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
        return cst.WF_PIPELINE

    def post_process(self):
        pass
