__all__ = ["AbstractAdapter"]

from abc import ABC

import pandas as pd

from matmat.workflows.core import AbstractWorkflow, WorkflowStep
from matmat.workflows.adapters.identity import AbstractAdapterIdentity
from matmat.utils import constants as cst

# ToDo: add in doc the distinction between adapter and workflow


class AbstractAdapter(AbstractWorkflow, ABC):
    """
    Base class for adapter workflow
    """

    _id: AbstractAdapterIdentity

    @property
    def enabled_steps(self) -> set[WorkflowStep]:
        return {
            WorkflowStep.STEP_LOAD,
            WorkflowStep.STEP_PROCESS,
            WorkflowStep.STEP_SAVE,
        }

    @classmethod
    def kind(cls) -> str:
        return cst.WF_ADAPTER

    def calculate(self):
        pass

    def post_process(self):
        pass

    def export_df(self, df: pd.DataFrame, path: str, file_name: str):
        for format_ in self._export_formats:
            format_.export(df=df, path=path, file_name=file_name)
