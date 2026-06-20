import os

from matmat.workflows.run import WorkflowExecution
from matmat.workflows.engines.eeio import (
    identity,
    core,
)
from matmat.utils import constants as cst


def get_workflow() -> WorkflowExecution:
    """
    Return the workflow execution object
    """
    return WorkflowExecution(
        identity_class=identity.EngineEEIOIdentity,
        workflow_class=core.EngineEEIO,
    )


def copy_settings(path: str):
    """
    Copy the local settings file to path

    Parameters:
        path (str):
            The path to the directory to copy the file to
    """

    get_workflow().copy_settings(
        path_from=os.path.dirname(__file__),
        path_to=path,
    )


def main(
    path_settings_file: str = None,
    load_cache: bool = False,
    save_cache: bool = False,
    clear_cache: bool = False,
    no_confirm: bool = False,
    dev: bool = False,
):
    """
    Execute the main workflow with configurable settings and caching options.

    Parameters:
        path_settings_file (str):
            Path to the settings file. Defaults to the local settings file
            if not provided.
        load_cache (bool):
            Whether to load cached data at startup (default is False).
        save_cache (bool):
            Whether to save data to cache after execution (default is False).
        clear_cache (bool):
            Whether to clear the cache after execution (default is False).
        no_confirm (bool):
            Whether to skip confirmation prompt (default is False).
        dev (bool):
            Whether to enable development mode (default is False).
    """


    if path_settings_file is None:
        local_path = os.path.dirname(__file__)
        path_settings_file = str(os.path.join(local_path, cst.FILE_SETTINGS))

    get_workflow().run(
        path_settings_file=path_settings_file,
        load_cache=load_cache,
        save_cache=save_cache,
        clear_cache=clear_cache,
        no_confirm=no_confirm,
        dev=dev,
    )


if __name__ == "__main__":
    main()
