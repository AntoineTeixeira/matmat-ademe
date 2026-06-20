import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
import matmat.utils.constants as cst


def dl_regions(dom_regions, imp_regions):
    return dl.RegionsDL(
        pd.DataFrame(
            {
                cst.IDX_ORIGIN: [cst.IDX_DOMESTIC] * len(dom_regions)
                + [cst.IDX_IMPORT] * len(imp_regions),
                cst.IDX_REGION: dom_regions + imp_regions,
            }
        )
    )


# Level 1
REGIONS_DOM_1 = ["France"]
REGIONS_IMP_1 = ["RoW"]
# Level 2
REGIONS_DOM_2 = ["France", "Rest Of Europe"]
REGIONS_IMP_2 = ["America", "RoW"]
# Level 3
REGIONS_DOM_3 = ["France", "Italy", "Portugal", "Rest Of Europe"]
REGIONS_IMP_3 = ["America", "Oceania", "Africa", "Asia", "RoW"]

DL_REGIONS_1 = dl_regions(
    dom_regions=REGIONS_DOM_1,
    imp_regions=REGIONS_IMP_1,
)

DL_REGIONS_2 = dl_regions(
    dom_regions=REGIONS_DOM_2,
    imp_regions=REGIONS_IMP_2,
)

DL_REGIONS_3 = dl_regions(
    dom_regions=REGIONS_DOM_3,
    imp_regions=REGIONS_IMP_3,
)

# Bridge from level 2 to level 1
DF_BRIDGE_REGIONS_FROM_2_TO_1 = pd.DataFrame(
    index=DL_REGIONS_2.get_dl_as_multi_index(),
    columns=DL_REGIONS_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_REGIONS_FROM_2_TO_1.iloc[0, 0] = 1  # France -> France
DF_BRIDGE_REGIONS_FROM_2_TO_1.iloc[1, 0] = 1  # Rest Of Europe -> France
DF_BRIDGE_REGIONS_FROM_2_TO_1.iloc[2, 1] = 1  # America -> RoW
DF_BRIDGE_REGIONS_FROM_2_TO_1.iloc[3, 1] = 1  # RoW -> RoW

BRIDGE_REGIONS_FROM_2_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.REGIONS,
    df=DF_BRIDGE_REGIONS_FROM_2_TO_1,
)


# Bridge from level 3 to level 1
DF_BRIDGE_REGIONS_FROM_3_TO_1 = pd.DataFrame(
    index=DL_REGIONS_3.get_dl_as_multi_index(),
    columns=DL_REGIONS_1.get_dl_as_multi_index(),
    dtype=cst.DTYPE_UINT8,
    data=0,
)
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[0, 0] = 1  # France -> France
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[1, 0] = 1  # Italy -> France
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[2, 0] = 1  # Portugal -> France
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[3, 0] = 1  # Rest Of Europe -> France
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[4, 1] = 1  # America -> RoW
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[5, 1] = 1  # Oceania -> RoW
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[6, 1] = 1  # Africa -> RoW
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[7, 1] = 1  # Asia -> RoW
DF_BRIDGE_REGIONS_FROM_3_TO_1.iloc[8, 1] = 1  # RoW -> RoW

BRIDGE_REGIONS_FROM_3_TO_1 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.REGIONS,
    df=DF_BRIDGE_REGIONS_FROM_3_TO_1,
)


# Bridge from level 1 to level 2
BRIDGE_REGIONS_FROM_1_TO_2 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.REGIONS,
    df=BRIDGE_REGIONS_FROM_2_TO_1.df.T,
)

# Bridge from level 1 to level 3
BRIDGE_REGIONS_FROM_1_TO_3 = bridge.Bridge.init_from_df(
    kind=dl.DetailLevelKind.REGIONS,
    df=BRIDGE_REGIONS_FROM_3_TO_1.df.T,
)

# MultiBridge
MULTI_BRIDGE_REGIONS = bridge.MultiBridge.init_from_bridges(
    kind=dl.DetailLevelKind.REGIONS,
    bridges={
        "2_to_1": BRIDGE_REGIONS_FROM_2_TO_1,
        "3_to_1": BRIDGE_REGIONS_FROM_3_TO_1,
    },
)

# Regions with both domestic and import regions
REGIONS_W_IMPORT: dl.RegionsDL = dl.RegionsDL(
    pd.DataFrame(
        {
            cst.IDX_ORIGIN: [cst.IDX_DOMESTIC, cst.IDX_IMPORT],
            cst.IDX_REGION: ["France", "RoW"],
        }
    )
)
# Regions with both domestic and import regions (but France is import)
REGIONS_W_IMPORT_INV: dl.RegionsDL = dl.RegionsDL(
    pd.DataFrame(
        {
            cst.IDX_ORIGIN: [cst.IDX_DOMESTIC, cst.IDX_IMPORT],
            cst.IDX_REGION: ["RoW", "France"],
        }
    )
)

# Regions without import regions
REGIONS_WO_IMPORT: dl.RegionsDL = dl.RegionsDL(
    pd.DataFrame(
        {
            cst.IDX_ORIGIN: [cst.IDX_DOMESTIC],
            cst.IDX_REGION: ["France"],
        }
    )
)

# Default regions dataframe for tests
DEFAULT_REGIONS: dl.RegionsDL = REGIONS_W_IMPORT.copy()

# Default multi-regions for tests
DEFAULT_MULTI_REGIONS: dl.RegionsDL = dl.RegionsDL(
    pd.DataFrame(
        {
            cst.IDX_ORIGIN: [
                cst.IDX_DOMESTIC,
                cst.IDX_DOMESTIC,
                cst.IDX_DOMESTIC,
                cst.IDX_IMPORT,
                cst.IDX_IMPORT,
            ],
            cst.IDX_REGION: ["R1", "R2", "R3", "R4", "R5"],
        }
    )
)
