import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.utils import constants as cst


def dl_sectors(categories_, sub_categories_, sectors_):
    return dl.SectorsDL(
        pd.MultiIndex.from_arrays(
            arrays=[
                categories_,
                sub_categories_,
                sectors_,
            ],
            names=[
                cst.IDX_CATEGORY,
                cst.IDX_SUB_CATEGORY,
                cst.IDX_SECTOR,
            ],
        ).to_frame(index=False)
    )


# Level 1
CATEGORIES_1 = ["C", "A"]
SUB_CATEGORIES_1 = ["C_SC1", "A_SC2"]
SECTORS_1 = ["C_SC1_total", "A_SC2_total"]
# Level 2
CATEGORIES_2 = ["C1", "A2", "A2", "B3"]
SUB_CATEGORIES_2 = ["C_SC11", "A_SC21", "A_SC22", "B_SC3"]
SECTORS_2 = ["C_SC11_total", "A_S21", "A_SC22_total", "B_S31"]
# Level 3
CATEGORIES_3 = ["C1", "C1", "A2", "A2", "A2", "B3"]
SUB_CATEGORIES_3 = ["C_SC11", "C_SC11", "A_SC21", "A_SC22", "A_SC22", "B_SC3"]
SECTORS_3 = ["C_S11", "C_S12", "A_S21", "A_S22", "A_S23", "B_S31"]

DL_SECTORS_1 = dl_sectors(
    categories_=CATEGORIES_1,
    sub_categories_=SUB_CATEGORIES_1,
    sectors_=SECTORS_1,
)

DL_SECTORS_2 = dl_sectors(
    categories_=CATEGORIES_2,
    sub_categories_=SUB_CATEGORIES_2,
    sectors_=SECTORS_2,
)

DL_SECTORS_3 = dl_sectors(
    categories_=CATEGORIES_3,
    sub_categories_=SUB_CATEGORIES_3,
    sectors_=SECTORS_3,
)

# Bridge from level 2 to level 1
DF_BRIDGE_SECTORS_FROM_2_TO_1 = pd.DataFrame(
    index=DL_SECTORS_2.get_dl_as_multi_index(),
    columns=DL_SECTORS_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_SECTORS_FROM_2_TO_1.iloc[0, 0] = 1
DF_BRIDGE_SECTORS_FROM_2_TO_1.iloc[1, 1] = 1
DF_BRIDGE_SECTORS_FROM_2_TO_1.iloc[2, 1] = 1

BRIDGE_SECTORS_FROM_2_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.SECTORS,
    df=DF_BRIDGE_SECTORS_FROM_2_TO_1,
)

# Bridge from level 3 to 1
DF_BRIDGE_SECTORS_FROM_3_TO_1 = pd.DataFrame(
    index=DL_SECTORS_3.get_dl_as_multi_index(),
    columns=DL_SECTORS_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_SECTORS_FROM_3_TO_1.iloc[0, 0] = 1
DF_BRIDGE_SECTORS_FROM_3_TO_1.iloc[1, 0] = 1
DF_BRIDGE_SECTORS_FROM_3_TO_1.iloc[2, 1] = 1
DF_BRIDGE_SECTORS_FROM_3_TO_1.iloc[3, 1] = 1
DF_BRIDGE_SECTORS_FROM_3_TO_1.iloc[4, 1] = 1

BRIDGE_SECTORS_FROM_3_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.SECTORS,
    df=DF_BRIDGE_SECTORS_FROM_3_TO_1,
)


# Bridge from level 1 to 3
BRIDGE_SECTORS_FROM_1_TO_3 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.SECTORS,
    df=BRIDGE_SECTORS_FROM_3_TO_1.df.T,
)

# Bridge from level 1 to 2
BRIDGE_SECTORS_FROM_1_TO_2 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.SECTORS,
    df=BRIDGE_SECTORS_FROM_2_TO_1.df.T,
)

# MultiBridge
MULTI_BRIDGE_SECTORS = bridge.MultiBridge.init_from_bridges(
    kind=dl.DetailLevelKind.SECTORS,
    bridges={
        "2_to_1": BRIDGE_SECTORS_FROM_2_TO_1,
        "3_to_1": BRIDGE_SECTORS_FROM_3_TO_1,
    },
)
