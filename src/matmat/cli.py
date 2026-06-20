import argparse
import os
import logging
from types import ModuleType

import matmat.utils.logging as log
import matmat.utils.constants as cst
import matmat.utils.config as config

# MatMat adapter modes
ADAPTER_EXIOBASE = "exiobase3_eeio"
ADAPTER_MANUAL = "manual"
ADAPTER_CHOICES = [
    ADAPTER_EXIOBASE,
    ADAPTER_MANUAL,
]

# MatMat pipeline modes
PIPELINE_UNION = "union"
PIPELINE_GMRIO_TO_SNAC_S = "gmrio_to_snac_s"
PIPELINE_AGGREGATION = "aggregation"
PIPELINE_CHOICES = [
    PIPELINE_UNION,
    PIPELINE_GMRIO_TO_SNAC_S,
    PIPELINE_AGGREGATION,
]

# MatMat engine modes
ENGINE_EEIO = "eeio"
ENGINE_CHOICES = [
    ENGINE_EEIO,
]

# MatMat analysis modes
ANALYSIS_CHOICES = []

def get_settings_directory(
    workflow_kind: str,
    workflow_name: str,
    args_settings: str,
) -> str:
    """
    Retrieve the path to the settings file for a given workflow.

    Parameters:
        workflow_kind (str):
            Type/category of the workflow.
        workflow_name (str):
            Name of the workflow.
        args_settings (str):
            Path to the settings file provided as argument.
            If None, checks config variable for default location.
    Returns:
        str : Path to the settings file if found, otherwise None.
    """
    if args_settings is None:
        path_to_settings_file = os.path.join(
            config.SETTINGS_DIR,
            cst.MAP_WORKFLOW_KIND_TO_DIRECTORY[workflow_kind],
            f"{workflow_name}_{cst.FILE_SETTINGS}",
        )
        if not os.path.isfile(path_to_settings_file):
            path_to_settings_file = None

    else:
        path_to_settings_file = args_settings

    return path_to_settings_file


def run_workflow(
    args,
    workflow_run: ModuleType,
):
    """
    Execute a workflow with the given parameters.

    Parameters:
        args :
            Command-line arguments containing workflow execution settings.
        workflow_run (ModuleType):
            Module containing the workflow's main function.
    """
    workflow_run.main(
        path_settings_file=get_settings_directory(
            workflow_kind=workflow_run.get_workflow().kind(),
            workflow_name=workflow_run.get_workflow().name(),
            args_settings=args.settings,
        ),
        load_cache=args.load_cache,
        save_cache=args.save_cache,
        clear_cache=args.clear_cache,
        no_confirm=args.no_confirm,
        dev=args.dev,
    )


def copy_workflows_settings():
    """
    Copy all workflow settings files to a centralized settings directory.

    The settings files are copied from their respective source locations
    to `src/settings/` with their original naming conventions.
    """
    path_settings = os.path.join(os.getcwd(), cst.DIR_SETTINGS)
    # Create directory if necessary
    os.makedirs(path_settings, exist_ok=True)

    # Pipelines
    from matmat.workflows.pipelines.shocks.union import run as pipeline_union
    pipeline_union.copy_settings(path_settings)

    from matmat.workflows.pipelines.accounts.gmrio_to_snac_s import (
        run as pipeline_gmrio_to_snac_s,
    )
    pipeline_gmrio_to_snac_s.copy_settings(path_settings)

    from matmat.workflows.pipelines.accounts.aggregation import (
        run as pipeline_aggregation,
    )
    pipeline_aggregation.copy_settings(path_settings)

    # Engines
    from matmat.workflows.engines.eeio import run as engine_eeio
    engine_eeio.copy_settings(path_settings)

    # Adapters
    from matmat.workflows.adapters.accounts.exiobase3_eeio import (
        run as adapter_exiobase3_eeio,
    )
    adapter_exiobase3_eeio.copy_settings(path_settings)

    from matmat.workflows.adapters.shocks.manual import (
        run as adapter_manual,
    )
    adapter_manual.copy_settings(path_settings)

    # Analysis
    # ToDo

def set_up_logging(args):
    """
    Configure logging level based on command-line arguments.

    Parameters:
        args :
            Command-line arguments containing logging preferences.
            Expected attributes:
                - silent (bool): If True, sets logging to WARNING level.
                - verbose (bool): If True, sets logging to INFO level.
                - debug (bool): If True, sets logging to DEBUG level.
    """

    if args.silent:
        config.LOGGER_LEVEL = logging.WARNING
        config.verbose = False
    elif args.verbose:
        config.LOGGER_LEVEL = logging.INFO
        config.VERBOSE = True
    elif args.debug:
        config.LOGGER_LEVEL = logging.DEBUG
        config.VERBOSE = True
    log.configure_logging()


def cli_entry_point():

    parser = define_parser()
    args = parser.parse_args()

    set_up_logging(args)

    if args.version:
        print(cst.MATMAT_VERSION)

    # Initialization mode:
    #   1. Generate default config file
    #   2. Copy default workflows settings
    elif args.init:
        path_to_config_file = os.path.join(os.getcwd(), cst.FILE_CONFIG)
        if not os.path.exists(path_to_config_file):
            log.info(
                "Generate config file "
                f"'{os.path.basename(path_to_config_file)}'"
            )
            config.generate_config_file(path_to_config_file)
        copy_workflows_settings()

    # Adapter mode
    elif args.adapter is not None:

        # Exiobase data adaptation
        if args.adapter == ADAPTER_EXIOBASE:
            from matmat.workflows.adapters.accounts.exiobase3_eeio import (
                run as adapter_exiobase3_eeio,
            )

            run_workflow(
                args=args,
                workflow_run=adapter_exiobase3_eeio,
            )

        # Manual relative variation adaptation
        elif args.adapter == ADAPTER_MANUAL:
            from matmat.workflows.adapters.shocks.manual import run as adapter_manual

            run_workflow(
                args=args,
                workflow_run=adapter_manual,
            )

    elif args.pipeline is not None:

        # GMRIO to SNAC_S pipeline
        if args.pipeline == PIPELINE_GMRIO_TO_SNAC_S:
            from matmat.workflows.pipelines.accounts.gmrio_to_snac_s import (
                run as pipeline_gmrio_to_snac_s,
            )

            run_workflow(
                args=args,
                workflow_run=pipeline_gmrio_to_snac_s,
            )

        # Aggregation pipeline
        if args.pipeline == PIPELINE_AGGREGATION:
            from matmat.workflows.pipelines.accounts.aggregation import (
                run as pipeline_aggregation,
            )

            run_workflow(
                args=args,
                workflow_run=pipeline_aggregation,
            )

        # Union pipeline
        if args.pipeline == PIPELINE_UNION:
            from matmat.workflows.pipelines.shocks.union import run as pipeline_union

            run_workflow(
                args=args,
                workflow_run=pipeline_union,
            )

    elif args.engine is not None:
        # EEIO engine
        if args.engine == ENGINE_EEIO:
            from matmat.workflows.engines.eeio import run as engine_eeio

            run_workflow(
                args=args,
                workflow_run=engine_eeio,
            )

    elif args.analysis is not None:
        pass

    # Sandbox mode
    elif args.sandbox:
        pass

    else:
        log.error(f"Can't process arguments: {args}")


def define_parser():
    parser = argparse.ArgumentParser(
        prog="MatMat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"""
    MatMat (Material Matrices) is a modular open-source Python framework 
    for Environmentally-Extended Input-Output (EEIO) modelling and 
    prospective environmental and socio-economic impact assessment. The 
    framework is designed to assess the environmental pressures and 
    socio-economic implications of global, regional and country-driven 
    transition pathways along global supply chains. It enables the 
    consistent evaluation of current and future sustainability challenges 
    associated with global, regional and national climate, energy, 
    industrial, and resource strategies.
    """,
        epilog=f"""Examples:
    python -m matmat.cli -a exiobase3_eeio
    python -m matmat.cli -e eeio -v --settings /home/john/Documents/matmat_settings/eeio_run_settings.json
    python -m matmat.cli -p union -d

Settings resolution (by priority):
  1. --settings <path>     
      Explicit path to a JSON settings file.

  2. config.toml 
      Configuration variable 'settings_dir' defined in 'config.toml' pointing 
      to a directory containing settings files stored as <kind>s/<name>_settings.json 
      e.g. adapters/threeme_settings.json

  3. If neither is provided, the fallback is to use the default settings
     file associated with the workflow being executed.""",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--init",
        help="Initialize MatMat configuration file 'config.toml', "
        "and copy default settings files to 'settings' in current directory.",
        action="store_true",
    )
    group.add_argument(
        "-a",
        f"--{cst.WF_ADAPTER}",
        help="Adapter mode",
        choices=ADAPTER_CHOICES,
    )
    group.add_argument(
        "-p",
        f"--{cst.WF_PIPELINE}",
        help="Pipeline mode",
        choices=PIPELINE_CHOICES,
    )
    group.add_argument(
        "-e",
        "-eg",
        f"--{cst.WF_ENGINE}",
        help="Engine mode",
        choices=ENGINE_CHOICES,
    )
    group.add_argument(
        "-an",
        f"--{cst.WF_ANALYSIS}",
        help="Analysis mode",
        choices=ANALYSIS_CHOICES,
    )
    group.add_argument(
        "-sb", "--sandbox", help="Sandbox mode", action="store_true"
    )
    group.add_argument(
        "-V", "--version", help="Show MatMat version", action="store_true"
    )
    parser.add_argument("-st", "--settings", help="Path to the settings file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Activate additional logs"
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Hide all logs below warning level",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Activate debug logs"
    )
    parser.add_argument(
        "-lc",
        "--load_cache",
        action="store_true",
        help="Enable cache loading",
    )
    parser.add_argument(
        "-sc",
        "--save_cache",
        action="store_true",
        help="Enable cache saving",
    )
    parser.add_argument(
        "-cc",
        "--clear_cache",
        action="store_true",
        help="To clear cache",
    )
    parser.add_argument(
        "--no_confirm",
        action="store_true",
        help="Do not ask for confirmation for risky operations",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable workflow development mode",
    )
    return parser


if __name__ == "__main__":
    cli_entry_point()
