import os
import json
import platform
import socket
import getpass
from datetime import datetime, timezone

from matmat.workflows.identity import AbstractWorkflowIdentity
from matmat.utils import constants as cst, logging as log


class RunData:
    """
    Metadata associated to a run
    """

    def __init__(self):
        now = datetime.now(timezone.utc)
        self.data_utc = now.date().isoformat()
        self.time_utc = now.time().replace(microsecond=0).isoformat()
        self.datetime_utc = (now.replace(microsecond=0).isoformat(),)


class EnvironmentData:
    """
    Metadata associated to the execution environment
    """

    def __init__(self):
        self.python_version = platform.python_version()
        self.python_implementation = platform.python_implementation()
        self.platform = platform.platform()
        self.hostname = socket.gethostname()
        self.user = getpass.getuser()


class MatmatData:
    """
    Metadata associated to the MatMat model used
    """

    def __init__(self):
        self.version = cst.MATMAT_VERSION


class MetaData:
    """
    Global metadata class
    """

    FILE_NAME = "metadata.json"

    def __init__(
        self,
        workflow_kind: str,
        workflow_name: str,
        id_: AbstractWorkflowIdentity,
    ):
        self.id = id_
        self.workflow_kind = workflow_kind
        self.workflow_name = workflow_name
        self.environment_data = EnvironmentData()
        self.matmat_data = MatmatData()

    def _build_dict(self) -> dict:
        """
        Build the metadata payload to be serialized as JSON
        """
        return {
            "matmat": self.matmat_data.__dict__,
            "environment": self.environment_data.__dict__,
            "run": RunData().__dict__,
            "workflow": {
                "kind": self.workflow_kind,
                "name": self.workflow_name,
                "identity": self.id.to_json_dict(),
            },
        }

    def save_to_path(self, path: str):
        """
        Save the metadata to path in a JSON file 'metadata.json'

        Parameters:
            path (str):
                The path to the directory to save the JSON file into
        """
        log.info(f"Save metadata JSON file to {path}")
        with open(
            os.path.join(path, self.FILE_NAME), "w", encoding="utf-8"
        ) as f:
            json.dump(
                self._build_dict(),
                f,
                ensure_ascii=False,
                indent=4,
                sort_keys=False,
            )
