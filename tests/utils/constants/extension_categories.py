import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
import matmat.utils.constants as cst

EXT_NAME_USE_BASED = "ext_use_based"
EXT_NAME_GROSS_OUTPUT_BASED = "ext_gross_output_based"
EXT_NAME_EMBODIED_IN_IMPORT = "ext_embodied_in_import"

# Level 1
EXT_CATS_1 = [
    "ext_cat_1",
    "ext_cat_2",
]
# Level 2
EXT_CATS_2 = [
    "ext_cat_1",
    "ext_cat_1",
    "ext_cat_2",
    "ext_cat_2",
]
EXT_SECTORS_2 = [
    "ext_sector_11",
    "ext_sector_12",
    "ext_sector_21",
    "ext_sector_22",
]
# Level 3
EXT_CATS_3 = [
    "ext_cat_1",
    "ext_cat_1",
    "ext_cat_1",
    "ext_cat_2",
    "ext_cat_2",
]
EXT_SECTORS_3 = [
    "ext_sector_11",
    "ext_sector_12",
    "ext_sector_13",
    "ext_sector_21",
    "ext_sector_22",
]

DL_EXT_CATS_1 = dl.ExtensionCategoriesDL(
    extension_name="extension_categories",
    df=pd.DataFrame({cst.IDX_PERIMETER: EXT_CATS_1}),
)
DL_EXT_CATS_2 = dl.ExtensionCategoriesDL(
    extension_name="extension_categories",
    df=pd.DataFrame(
        {
            cst.IDX_PREFIX_EXT + cst.IDX_CATEGORY: EXT_CATS_2,
            cst.IDX_PREFIX_EXT + cst.IDX_SECTOR: EXT_SECTORS_2,
        }
    ),
)
DL_EXT_CATS_3 = dl.ExtensionCategoriesDL(
    extension_name="extension_categories",
    df=pd.DataFrame(
        {
            cst.IDX_PREFIX_EXT + cst.IDX_CATEGORY: EXT_CATS_3,
            cst.IDX_PREFIX_EXT + cst.IDX_SECTOR: EXT_SECTORS_3,
        }
    ),
)


# Bridge from level 2 to level 1
DF_BRIDGE_EXT_CATS_FROM_2_TO_1 = pd.DataFrame(
    index=DL_EXT_CATS_2.get_dl_as_multi_index(),
    columns=DL_EXT_CATS_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_EXT_CATS_FROM_2_TO_1.iloc[0, 0] = 1  # ext_sector_11 -> ext_cat_1
DF_BRIDGE_EXT_CATS_FROM_2_TO_1.iloc[1, 0] = 1  # ext_sector_12 -> ext_cat_1
DF_BRIDGE_EXT_CATS_FROM_2_TO_1.iloc[2, 1] = 1  # ext_sector_21 -> ext_cat_2
DF_BRIDGE_EXT_CATS_FROM_2_TO_1.iloc[3, 1] = 1  # ext_sector_22 -> ext_cat_2

BRIDGE_EXT_CATS_FROM_2_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.EXTENSION_CATEGORIES,
    df=DF_BRIDGE_EXT_CATS_FROM_2_TO_1,
)


# Bridge from level 3 to level 1
DF_BRIDGE_EXT_CATS_FROM_3_TO_1 = pd.DataFrame(
    index=DL_EXT_CATS_3.get_dl_as_multi_index(),
    columns=DL_EXT_CATS_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_EXT_CATS_FROM_3_TO_1.iloc[0, 0] = 1  # ext_sector_11 -> ext_cat_1
DF_BRIDGE_EXT_CATS_FROM_3_TO_1.iloc[1, 0] = 1  # ext_sector_12 -> ext_cat_1
DF_BRIDGE_EXT_CATS_FROM_3_TO_1.iloc[2, 0] = 1  # ext_sector_13 -> ext_cat_1
DF_BRIDGE_EXT_CATS_FROM_3_TO_1.iloc[3, 1] = 1  # ext_sector_21 -> ext_cat_2
DF_BRIDGE_EXT_CATS_FROM_3_TO_1.iloc[4, 1] = 1  # ext_sector_22 -> ext_cat_2

BRIDGE_EXT_CATS_FROM_3_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.EXTENSION_CATEGORIES,
    df=DF_BRIDGE_EXT_CATS_FROM_3_TO_1,
)


# Bridge from level 1 to level 2
BRIDGE_EXT_CATS_FROM_1_TO_2 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.EXTENSION_CATEGORIES,
    df=BRIDGE_EXT_CATS_FROM_2_TO_1.df.T,
)

# Bridge from level 1 to level 3
BRIDGE_EXT_CATS_FROM_1_TO_3 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.EXTENSION_CATEGORIES,
    df=BRIDGE_EXT_CATS_FROM_3_TO_1.df.T,
)

# MultiBridge
MULTI_BRIDGE_EXT_CATS = bridge.MultiBridge.init_from_bridges(
    kind=dl.DetailLevelKind.EXTENSION_CATEGORIES,
    bridges={
        "2_to_1": BRIDGE_EXT_CATS_FROM_2_TO_1,
        "3_to_1": BRIDGE_EXT_CATS_FROM_3_TO_1,
    },
)

# Default extension categories for tests
DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS: dl.ExtensionCategoriesDL = (
    dl.ExtensionCategoriesDL(
        extension_name="extension_categories",
        df=pd.DataFrame(
            {
                cst.IDX_PREFIX_EXT
                + cst.IDX_CATEGORY: [
                    "extension_cat_1",
                    "extension_cat_1",
                    "extension_cat_1",
                    "extension_cat_2",
                    "extension_cat_2",
                ],
                cst.IDX_PREFIX_EXT
                + cst.IDX_SECTOR: [
                    "extension_sector_11",
                    "extension_sector_12",
                    "extension_sector_13",
                    "extension_sector_21",
                    "extension_sector_22",
                ],
            }
        ),
    )
)

DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL: dl.ExtensionCategoriesDL = (
    dl.ExtensionCategoriesDL(
        extension_name="extension_categories",
        df=pd.DataFrame(
            {
                cst.IDX_PERIMETER: [
                    "extension_cat_1",
                    "extension_cat_2",
                ]
            }
        ),
    )
)

DEFAULT_EXTENSION_CATEGORIES: dl.ExtensionCategoriesDL = (
    DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS.copy()
)
