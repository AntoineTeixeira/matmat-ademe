"""
Presentation
************

Constants related to the MatMat model core.

The warning 'DO NOT CHANGE' is written for data-related constants. Indeed,
these constants are intimately related to MatMat core classes, and shall not
be changed without deep understanding of MatMat software architecture.
"""

# DATA
# ----
# DO NOT CHANGE
UNIT = "unit"

# System data
# DO NOT CHANGE
A = "A"
K = "K"
L = "L"
L_K = "L_k"
X = "x"
Y = "Y"
Y_K = "Y_k"
Z = "Z"
LIST_OF_SYSTEM_DATA = [A, K, L, L_K, X, Y, Y_K, Z, UNIT]

# Extension data
# DO NOT CHANGE
F_X_DOM = "F_x_dom"
F_Y = "F_Y"
F_Z = "F_Z"
S_X_DOM = "S_x_dom"
S_Y = "S_Y"
S_Z = "S_Z"
M_ROW = "M_RoW"
D_IMP = "d_imp"
M = "M"
M_K = "M_k"
D_CBA = "d_cba"
D_CBA_K = "d_cba_k"
MAPPING = "mapping"
MAPPING_K = "mapping_k"
LIST_OF_EXTENSION_DATA = [
    F_X_DOM,
    F_Y,
    F_Z,
    S_X_DOM,
    S_Y,
    S_Z,
    M_ROW,
    D_IMP,
    M,
    M_K,
    D_CBA,
    D_CBA_K,
    MAPPING,
    MAPPING_K,
    UNIT,
]

# Shock data
# DO NOT CHANGE
IMP_DOM_RATIO = "imp_dom_ratio"
D_A = f"d{A}"
D_K = f"d{K}"
D_Y = f"d{Y}"
D_Y_K = f"d{Y_K}"
D_Z = f"d{Z}"
D_S_X_DOM = f"d{S_X_DOM}"
D_S_Y = f"d{S_Y}"
D_S_Z = f"d{S_Z}"
D_M_ROW = f"d{M_ROW}"
LIST_OF_SYSTEM_SHOCK_DATA = [D_A, D_K, D_Y, D_Y_K, D_Z]
LIST_OF_EXTENSION_SHOCK_DATA = [D_S_X_DOM, D_S_Y, D_S_Z, D_M_ROW]

# Null data
# DO NOT CHANGE
NULL = "null"

# SYSTEM CALCUL STRATEGIES
# ------------------------
STRATEGY_STANDARD = "standard"
STRATEGY_EXO_INVEST_MATRIX = "exo_invest_matrix"
STRATEGY_ENDO_INVEST_MATRIX = "endo_invest_matrix"

# EXTENSION CALCUL STRATEGIES
# ---------------------------
STRATEGY_USE_BASED = "use_based"
STRATEGY_GROSS_OUTPUT_BASED = "gross_output_based"
STRATEGY_EMBODIED_IN_IMPORT = "embodied_in_import"
