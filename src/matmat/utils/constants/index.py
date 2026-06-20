"""
Presentation
************

Constants related to dataframe indexation
"""

import pandas as pd

# Null index
NULL_INDEX = pd.Index(["null"])

# Level names
IDX_ORIGIN = "origin"
IDX_REGION = "region"
IDX_SECTOR = "sector"
IDX_CATEGORY = "category"
IDX_SUB_CATEGORY = "sub_category"
IDX_Y_CATEGORY = "Y_category"
IDX_Y_SUB_CATEGORY = "Y_sub_category"
IDX_PERIMETER = "perimeter"
IDX_VARIABLE = "variable"
IDX_PREFIX_EXT = "ext__"
IDX_SOURCE = "source"
IDX_GAS = "gas"

# Level values
IDX_DOMESTIC = "domestic"
IDX_IMPORT = "import"
IDX_HOUSEHOLDS = "Households"
IDX_HOUSEHOLDS_C = "C"
IDX_GOVERNMENT = "Government"
IDX_GOVERNMENT_G = "G"
IDX_INVESTMENT = "GFCF"
IDX_INVESTMENT_I = "I"
IDX_EXPORTS = "Exports"
IDX_EXPORTS_E = "E"
IDX_REST_OF_THE_WORLD = "RoW"
IDX_FRANCE = "France"

# Limit of multi index levels
MAX_NUMBER_OF_MULTI_INDEX_LEVELS = 7
