"""
Presentation
************
This module contains configuration constants. These constants are used
to configure the program execution.
"""

import logging
import os
import tomllib
from pathlib import Path

from matmat.utils import constants as cst

def generate_config_file(path: str):
    """
    Generate a TOML configuration file from default configuration dictionaries.

    Parameters:
        path (str):
            Path where the configuration file will be written.
    """
    lines = []

    def to_toml(value) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

    def generate_section(name: str, defaults: dict):
        lines.append(f"[{name}]\n")
        for key, value in defaults.items():
            lines.append(f"{key} = {to_toml(value)}\n")

    generate_section(name="log", defaults=_DEFAULTS_LOG_CONFIG)
    generate_section(name="run", defaults=_DEFAULTS_RUN_CONFIG)

    with open(path, "w") as f:
        f.writelines(lines)

def _load_config(name: str, defaults: dict) -> dict:
    """
    Load and merge configuration from a TOML file with default values.

    Parameters:
        name (str):
            Section name in the TOML configuration file.
        defaults (dict):
            Default configuration values to use if the file or section
            does not exist.

    Returns:
        dict : Merged configuration dictionary with user values overriding
            defaults.
    """

    config_path = (Path.cwd() / cst.FILE_CONFIG).as_posix()
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            user_config = tomllib.load(f)
            return {**defaults, **user_config.get(name, {})}
    return defaults


# Functions to update configuration during execution
# --------------------------------------------------
def deactivate_data_structure_check():
    global CHECK_INPUT_DATA_STRUCTURE
    CHECK_INPUT_DATA_STRUCTURE = False


def activate_data_structure_check():
    global CHECK_INPUT_DATA_STRUCTURE
    CHECK_INPUT_DATA_STRUCTURE = True


# Logging configuration
# ---------------------
logging_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

# Default logging configuration values
_DEFAULTS_LOG_CONFIG = {
    "log_file": "matmat_log_file.log",
    "logger_level": "info",
    "verbose": False,
}
_config_log = _load_config(name="log", defaults=_DEFAULTS_LOG_CONFIG)

LOG_FILE = _config_log["log_file"]
"""This constant defines the name of the program log file"""
LOGGER_LEVEL = logging_levels[_config_log["logger_level"]]
"""This constant defines the level of logging. 
It can be ERROR (40), WARNING (30), INFO (20), DEBUG (10)"""
VERBOSE = _config_log["verbose"]
"""This constant is True if verbose logging is activated. 
If this is the case, more information about execution will be logged."""


# MatMat configuration
# --------------------

# Default run configuration values
_DEFAULTS_RUN_CONFIG = {
    "data_dir": (Path.cwd() / cst.DIR_DATA).as_posix(),
    "settings_dir": (Path.cwd() / cst.DIR_SETTINGS).as_posix(),
    "stop_on_error": False,
    "enable_performance_measurements": False,
    "stop_if_system_is_not_balanced": False,
    "clean_residual_nan_and_inf": True,
    "check_input_data_structure": True,
    "allow_heterogeneous_aggregation": False,
}

_config_run = _load_config(name="run", defaults=_DEFAULTS_RUN_CONFIG)

DATA_DIR = _config_run["data_dir"]
"""This constant defines the absolute path towards the directory containing the data used in MatMat.
All relative paths are defined relatively to this directory."""

SETTINGS_DIR = _config_run["settings_dir"]
"""This constant defines the absolute path towards the directory containing the
settings used to run MatMat workflows"""

STOP_ON_ERROR = _config_run["stop_on_error"]
"""This constant is True if the program shall be stopped as soon as an error
is logged"""

ENABLE_PERFORMANCE_MEASUREMENTS = _config_run["enable_performance_measurements"]
"""This constant is True if performance measurements shall be activated"""

STOP_IF_SYSTEM_IS_NOT_BALANCED = _config_run["stop_if_system_is_not_balanced"]
"""This constant is True if the program shall be stopped 
when a system is not balanced"""

CLEAN_RESIDUAL_NAN_AND_INF = _config_run["clean_residual_nan_and_inf"]
"""This constant is True if residual NaN / INF shall be cleaned 
from read dataframes"""

CHECK_INPUT_DATA_STRUCTURE = _config_run["check_input_data_structure"]
"""This constant is True if the structure of input dataframes shall be
verified w.r.t. predefined rows and columns index before loading the values"""

ALLOW_HETEROGENEOUS_AGGREGATION = _config_run["allow_heterogeneous_aggregation"]
"""This constant is True if aggregation of heterogeneous data 
(i.e. with different units) is allowed.
If False, then MatMat will raise an error if it happens."""
