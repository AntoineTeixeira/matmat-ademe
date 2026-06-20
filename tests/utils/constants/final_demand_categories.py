import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
import matmat.utils.constants as cst


def dl_final_demand_categories(categories_, sub_categories_):
    return dl.FinalDemandCategoriesDL(
        pd.MultiIndex.from_arrays(
            arrays=[
                categories_,
                sub_categories_,
            ],
            names=[
                cst.IDX_Y_CATEGORY,
                cst.IDX_Y_SUB_CATEGORY,
            ],
        ).to_frame(index=False)
    )


# Level 1
FD_CATS_1 = [
    cst.IDX_HOUSEHOLDS,
    cst.IDX_GOVERNMENT,
    cst.IDX_INVESTMENT,
    cst.IDX_EXPORTS,
]
FD_SUB_CATS_1 = [
    cst.IDX_HOUSEHOLDS_C,
    cst.IDX_GOVERNMENT_G,
    cst.IDX_INVESTMENT_I,
    cst.IDX_EXPORTS_E,
]
# Level 2
FD_CATS_2 = [
    cst.IDX_HOUSEHOLDS,
    cst.IDX_HOUSEHOLDS,
    cst.IDX_HOUSEHOLDS,
    cst.IDX_GOVERNMENT,
    cst.IDX_INVESTMENT,
    cst.IDX_EXPORTS,
]
FD_SUB_CATS_2 = [
    "Residential",
    "Transport",
    "Other",
    cst.IDX_GOVERNMENT_G,
    cst.IDX_INVESTMENT_I,
    cst.IDX_EXPORTS_E,
]
# Level 3
FD_CATS_3 = [
    cst.IDX_HOUSEHOLDS,
    cst.IDX_HOUSEHOLDS,
    cst.IDX_HOUSEHOLDS,
    cst.IDX_GOVERNMENT,
    cst.IDX_GOVERNMENT,
    cst.IDX_GOVERNMENT,
    cst.IDX_INVESTMENT,
    cst.IDX_EXPORTS,
]
FD_SUB_CATS_3 = [
    "Residential",
    "Transport",
    "Other",
    "Environment",
    "Foreign Policy",
    "Other",
    cst.IDX_INVESTMENT_I,
    cst.IDX_EXPORTS_E,
]

DL_FDC_1 = dl_final_demand_categories(
    categories_=FD_CATS_1,
    sub_categories_=FD_SUB_CATS_1,
)
DL_FDC_2 = dl_final_demand_categories(
    categories_=FD_CATS_2,
    sub_categories_=FD_SUB_CATS_2,
)
DL_FDC_3 = dl_final_demand_categories(
    categories_=FD_CATS_3,
    sub_categories_=FD_SUB_CATS_3,
)

# Bridge from level 2 to level 1
DF_BRIDGE_FDC_FROM_2_TO_1 = pd.DataFrame(
    index=DL_FDC_2.get_dl_as_multi_index(),
    columns=DL_FDC_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_FDC_FROM_2_TO_1.iloc[0, 0] = 1  # Residential -> Households
DF_BRIDGE_FDC_FROM_2_TO_1.iloc[1, 0] = 1  # Transport -> Households
DF_BRIDGE_FDC_FROM_2_TO_1.iloc[2, 0] = 1  # Other -> Households
DF_BRIDGE_FDC_FROM_2_TO_1.iloc[3, 1] = 1  # Government -> Government
DF_BRIDGE_FDC_FROM_2_TO_1.iloc[4, 2] = 1  # Investment -> Investment
DF_BRIDGE_FDC_FROM_2_TO_1.iloc[5, 3] = 1  # Exports -> Exports

BRIDGE_FDC_FROM_2_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
    df=DF_BRIDGE_FDC_FROM_2_TO_1,
)


# Bridge from level 3 to level 1
DF_BRIDGE_FDC_FROM_3_TO_1 = pd.DataFrame(
    index=DL_FDC_3.get_dl_as_multi_index(),
    columns=DL_FDC_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[0, 0] = 1  # Residential -> Households
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[1, 0] = 1  # Transport -> Households
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[2, 0] = 1  # Other (HH) -> Households
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[3, 1] = 1  # Environment -> Government
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[4, 1] = 1  # Foreign Policy -> Government
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[5, 1] = 1  # Other (Gov) -> Government
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[6, 2] = 1  # Investment -> Investment
DF_BRIDGE_FDC_FROM_3_TO_1.iloc[7, 3] = 1  # Exports -> Exports

BRIDGE_FDC_FROM_3_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
    df=DF_BRIDGE_FDC_FROM_3_TO_1,
)

# Bridge from level 1 to level 2
BRIDGE_FDC_FROM_1_TO_2 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
    df=BRIDGE_FDC_FROM_2_TO_1.df.T,
)

# Bridge from level 1 to level 3
BRIDGE_FDC_FROM_1_TO_3 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
    df=BRIDGE_FDC_FROM_3_TO_1.df.T,
)

# MultiBridge
MULTI_BRIDGE_FDC = bridge.MultiBridge.init_from_bridges(
    kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
    bridges={
        "2_to_1": BRIDGE_FDC_FROM_2_TO_1,
        "3_to_1": BRIDGE_FDC_FROM_3_TO_1,
    },
)

# Disaggregated final demand categories for tests
Y_CATEGORIES_DISAGG: dl.FinalDemandCategoriesDL = dl.FinalDemandCategoriesDL(
    pd.DataFrame(
        {
            cst.IDX_Y_CATEGORY: [
                cst.IDX_HOUSEHOLDS,
                cst.IDX_HOUSEHOLDS,
                cst.IDX_HOUSEHOLDS,
                cst.IDX_GOVERNMENT,
                cst.IDX_INVESTMENT,
                cst.IDX_EXPORTS,
            ],
            cst.IDX_Y_SUB_CATEGORY: [
                "Residential",
                "Transport",
                "Other",
                cst.IDX_GOVERNMENT_G,
                cst.IDX_INVESTMENT_I,
                cst.IDX_EXPORTS_E,
            ],
        }
    )
)

# Aggregated final demand categories for tests
Y_CATEGORIES_AGG: dl.FinalDemandCategoriesDL = dl.FinalDemandCategoriesDL(
    pd.DataFrame(
        {
            cst.IDX_Y_CATEGORY: [
                cst.IDX_HOUSEHOLDS,
                cst.IDX_GOVERNMENT,
                cst.IDX_INVESTMENT,
                cst.IDX_EXPORTS,
            ],
            cst.IDX_Y_SUB_CATEGORY: [
                cst.IDX_HOUSEHOLDS_C,
                cst.IDX_GOVERNMENT_G,
                cst.IDX_INVESTMENT_I,
                cst.IDX_EXPORTS_E,
            ],
        }
    )
)

# Default final demand categories for tests
DEFAULT_Y_CATEGORIES: dl.FinalDemandCategoriesDL = Y_CATEGORIES_AGG.copy()
