"""
Presentation
************

Constants related to I/O
"""

import os

# DF TYPES
# --------
DTYPE_FLOAT = "float"
DTYPE_STRING = "string"
DTYPE_UINT8 = "UInt8"

# FORMATS
# -------
FORMAT_EMPTY = ""
FORMAT_PICKLE = "pickle"
FORMAT_EXCEL = "excel"
FORMAT_CSV = "csv"

# DIRECTORIES
# -----------
DIR_DATA = "data"
DIR_SETTINGS = "settings"
DIR_SYSTEM = "system"
DIR_EXTENSIONS = "extensions"
DIR_SHOCKS = "shocks"

# DF STRUCTURE INFO
# -----------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DL_FILE = "detail_levels.xlsx"
BRIDGES_FILE = "bridge_matrices.xlsx"

# CONFIG
# ------
FILE_CONFIG = "config.toml"

# SETTINGS
# --------
FILE_INFO = "info.json"
FILE_SETTINGS = "settings.json"
KEY_ACCOUNTS = "accounts"  # ToDo: to check if it is ok here?
KEY_SHOCKS = "shocks"  # ToDo: to check if it is ok here?
KEY_SYSTEM = "system"
KEY_EXTENSIONS = "extensions"
KEY_STRATEGY = "strategy"
KEY_BASE_YEAR = "base_year"
KEY_EXTENSION_NAME = "extension_name"
KEY_OUTPUT = "output"

# WORKFLOWS
# ---------
WF_ADAPTER = "adapter"
WF_PIPELINE = "pipeline"
WF_ENGINE = "engine"
WF_ANALYSIS = "analysis"
MAP_WORKFLOW_KIND_TO_DIRECTORY = {
    WF_ADAPTER: "adapters",
    WF_ANALYSIS: "analyses",
    WF_ENGINE: "engines",
    WF_PIPELINE: "pipelines",
}
