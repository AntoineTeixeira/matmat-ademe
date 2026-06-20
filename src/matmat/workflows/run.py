import os
import shutil

from matmat.workflows.identity import AbstractWorkflowIdentity
from matmat.workflows.core import AbstractWorkflow
from matmat.utils import constants as cst, logging as log


class WorkflowExecution:
    """
    Workflow execution manager for handling workflow initialization and execution.

    Attributes
    ----------
    _workflow_class : type[AbstractWorkflow]
        The workflow class to be executed.
    _identity_class : type[AbstractWorkflowIdentity]
        The identity class used to load workflow settings.
    """

    def __init__(
        self,
        identity_class: type[AbstractWorkflowIdentity],
        workflow_class: type[AbstractWorkflow],
    ):
        self._identity_class = identity_class
        self._workflow_class = workflow_class

    def kind(self) -> str:
        return self._workflow_class.kind()

    def name(self) -> str:
        return self._workflow_class.name()

    def copy_settings(self, path_from: str, path_to: str):
        """
        Copy settings file from source to destination directory.

        The destination path is structured as:
        `<path_to>/<workflow_kind>s/<workflow_name>_settings.json`.

        Parameters:
            path_from (str):
                Source directory containing the settings file.
            path_to (str):
                Destination directory where settings will be copied.
        """
        path_settings_file = str(os.path.join(path_from, cst.FILE_SETTINGS))
        os.makedirs(
            os.path.join(
                path_to,
                cst.MAP_WORKFLOW_KIND_TO_DIRECTORY[
                    self._workflow_class.kind()
                ],
            ),
            exist_ok=True,
        )

        dest = os.path.join(
            path_to,
            cst.MAP_WORKFLOW_KIND_TO_DIRECTORY[self._workflow_class.kind()],
            f"{self._workflow_class.name()}_{cst.FILE_SETTINGS}",
        )

        # If file already exists, ask for confirmation before overriding
        if os.path.exists(dest):
            answer = input(f"File '{dest}' already exists. Overwrite? [y/N] ")
            if answer.strip().lower() != "y":
                log.info(f"Skip {os.path.basename(dest)}")
                return

        log.info(f"Generate settings file '{os.path.basename(dest)}'")
        shutil.copy(path_settings_file, dest)

    def run(
        self,
        path_settings_file: str,
        load_cache: bool,
        save_cache: bool,
        clear_cache: bool,
        no_confirm: bool,
        dev: bool,
    ):
        """
        Execute the workflow with the given settings and caching options.

        Parameters:
            path_settings_file (str):
                Path to the JSON settings file.
            load_cache (bool):
                Whether to load cached data at startup.
            save_cache (bool):
                Whether to save data to cache after execution.
            clear_cache (bool):
                Whether to clear the cache after execution.
            no_confirm (bool):
                Whether to skip confirmation prompt (default is False).
            dev (bool):
                Whether to enable development mode (default is False).
        """

        # Retrieve settings
        id_ = self._identity_class.load_from_json(path_settings_file)

        # Create and execute workflow
        workflow = self._workflow_class(id_=id_, no_confirm=no_confirm)
        workflow.execute(
            load_cache=load_cache,
            save_cache=save_cache,
            clear_cache=clear_cache,
            dev=dev,
        )
