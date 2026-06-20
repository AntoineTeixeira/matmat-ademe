import numpy as np
import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge

from matmat.core.dataset.core import AbstractDataSet

from matmat.core.accounts.system.core import System
import matmat.core.accounts.system.builder as sys_builders
import matmat.core.accounts.system.data.factory as sys_data_factory
import matmat.core.accounts.system.data.core as system_data
import matmat.core.accounts.system.dataset.core as system_dataset

from matmat.core.accounts.extension.core import Extension
import matmat.core.accounts.extension.builder as ext_builders
import matmat.core.accounts.extension.data.factory as ext_data_factory
import matmat.core.accounts.extension.data.core as extension_data
import matmat.core.accounts.extension.dataset.core as extension_dataset

import matmat.core.shocks.system.data.factory as sys_shock_factory
from matmat.core.shocks.system.core import SystemShock
import matmat.core.shocks.system.data.core as sys_shock_data
import matmat.core.shocks.system.builder as sys_shock_builders
import matmat.core.shocks.system.dataset.core as system_shock_dataset

import matmat.core.shocks.extension.data.factory as ext_shock_factory
from matmat.core.shocks.extension.core import ExtensionShock
import matmat.core.shocks.extension.data.core as ext_shock_data
import matmat.core.shocks.extension.builder as ext_shock_builders
import matmat.core.shocks.extension.dataset.core as extension_shock_dataset

import matmat.utils.constants as cst

import tests.utils.config as tests_config
import tests.utils.constants as tests_cst

# GLOBAL VARIABLES

# Sectors detail levels
test_sectors: dl.SectorsDL = None
test_agg_sectors: dl.SectorsDL = None

# Bridges
# - for regions
test_regions_bridge_for_agg: bridge.Bridge = None
test_regions_bridge_for_disagg: bridge.Bridge = None
# - for sectors
test_sectors_bridge_for_agg: bridge.Bridge = None
test_sectors_bridge_for_disagg: bridge.Bridge = None
# - for final demand categories
test_final_demand_categories_bridge_agg: bridge.Bridge = None
test_final_demand_categories_bridge_disagg: bridge.Bridge = None
# - for extension categories
test_extension_categories_bridge_agg: bridge.Bridge = None
test_extension_categories_bridge_disagg: bridge.Bridge = None


def generate_sectors(
    categories: list,
    sub_categories: list,
    sectors: list,
) -> pd.DataFrame:
    if categories and sub_categories and sectors:
        return pd.MultiIndex.from_arrays(
            arrays=[categories, sub_categories, sectors],
            names=[
                cst.IDX_CATEGORY,
                cst.IDX_SUB_CATEGORY,
                cst.IDX_SECTOR,
            ],
        ).to_frame(index=False)
    if sub_categories and sectors:
        return pd.MultiIndex.from_arrays(
            arrays=[sub_categories, sectors],
            names=[
                cst.IDX_SUB_CATEGORY,
                cst.IDX_SECTOR,
            ],
        ).to_frame(index=False)
    else:
        return pd.MultiIndex.from_arrays(
            arrays=[sectors],
            names=[
                cst.IDX_SECTOR,
            ],
        ).to_frame(index=False)


def generate_final_demand_categories(
    categories: list,
    sub_categories: list,
) -> pd.DataFrame:
    if categories and sub_categories:
        return pd.MultiIndex.from_arrays(
            arrays=[categories, sub_categories],
            names=[
                cst.IDX_Y_CATEGORY,
                cst.IDX_Y_SUB_CATEGORY,
            ],
        ).to_frame(index=False)
    if categories:
        return pd.MultiIndex.from_arrays(
            arrays=[categories],
            names=[
                cst.IDX_Y_CATEGORY,
            ],
        ).to_frame(index=False)
    if sub_categories:
        return pd.MultiIndex.from_arrays(
            arrays=[sub_categories],
            names=[
                cst.IDX_Y_SUB_CATEGORY,
            ],
        ).to_frame(index=False)
    raise NotImplementedError


def get_test_sectors() -> dl.SectorsDL:
    """
    Returns a sectors detail level object dedicated to MatMat tests.

    The index is composed by:
        - 3 categories C1, A2, B3
        - 4 sub-categories C_SC11, A_SC21, A_SC22, B_SC3
        - 6 sectors C_S11, C_S12, A_S21, A_S22, A_S23, B_S31
    """
    global test_sectors
    if test_sectors is None:
        categories = ["C1", "C1", "A2", "A2", "A2", "B3"]
        sub_categories = [
            "C_SC11",
            "C_SC11",
            "A_SC21",
            "A_SC22",
            "A_SC22",
            "B_SC3",
        ]
        sectors = ["C_S11", "C_S12", "A_S21", "A_S22", "A_S23", "B_S31"]

        test_sectors = dl.SectorsDL(
            generate_sectors(
                categories=categories,
                sub_categories=sub_categories,
                sectors=sectors,
            )
        )
    return test_sectors


def get_test_agg_sectors() -> dl.SectorsDL:
    """
    Returns a sectors detail level object
    dedicated to MatMat aggregation tests.

    The index is composed by:
        - 3 categories C1, A2, B3
        - 4 sub-categories SC11, SC21, SC22, SC23
        - 4 sectors SC11_total, S21, SC22_total, S31
    """
    global test_agg_sectors
    if test_agg_sectors is None:
        categories = ["C1", "A2", "A2", "B3"]
        sub_categories = ["C_SC11", "A_SC21", "A_SC22", "B_SC3"]
        sectors = ["C_SC11_total", "A_S21", "A_SC22_total", "B_S31"]

        test_agg_sectors = dl.SectorsDL(
            generate_sectors(
                categories=categories,
                sub_categories=sub_categories,
                sectors=sectors,
            )
        )
    return test_agg_sectors


def get_test_regions_bridge(disagg: bool = False) -> bridge.Bridge:
    global test_regions_bridge_for_agg, test_regions_bridge_for_disagg

    if (
        test_regions_bridge_for_agg is None
        or test_regions_bridge_for_disagg is None
    ):
        test_agg_matrix = pd.DataFrame(
            index=tests_cst.DEFAULT_MULTI_REGIONS.get_dl_as_multi_index(),
            columns=tests_cst.REGIONS_W_IMPORT.get_dl_as_multi_index(),
            dtype=cst.DTYPE_FLOAT,
        )
        test_agg_matrix.iloc[:, :] = 0.0
        test_agg_matrix.iloc[0, 0] = 1.0
        test_agg_matrix.iloc[1, 0] = 1.0
        test_agg_matrix.iloc[2, 0] = 1.0
        test_agg_matrix.iloc[3, 1] = 1.0
        test_agg_matrix.iloc[4, 1] = 1.0

        test_regions_bridge_for_disagg = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.REGIONS,
            df=test_agg_matrix.T,
        )
        test_regions_bridge_for_agg = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.REGIONS,
            df=test_agg_matrix,
        )

    if disagg:
        return test_regions_bridge_for_disagg
    return test_regions_bridge_for_agg


def get_test_sectors_bridge(disagg: bool = False) -> bridge.Bridge:
    global test_sectors_bridge_for_agg, test_sectors_bridge_for_disagg

    if test_sectors_bridge_for_agg is None:
        test_agg_matrix = pd.DataFrame(
            index=get_test_sectors().get_dl_as_multi_index(),
            columns=get_test_agg_sectors().get_dl_as_multi_index(),
            dtype=cst.DTYPE_FLOAT,
        )
        test_agg_matrix.loc[:, :] = 0.0

        test_agg_matrix.iloc[0, 0] = 1.0
        test_agg_matrix.iloc[1, 0] = 1.0
        test_agg_matrix.iloc[2, 1] = 1.0
        test_agg_matrix.iloc[3, 2] = 1.0
        test_agg_matrix.iloc[4, 2] = 1.0
        test_agg_matrix.iloc[5, 3] = 1.0

        test_sectors_bridge_for_agg = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=test_agg_matrix,
        )
        test_sectors_bridge_for_disagg = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=test_agg_matrix.T,
        )

    if disagg:
        return test_sectors_bridge_for_disagg
    return test_sectors_bridge_for_agg


def get_test_extension_categories_bridge(
    disagg: bool = False,
) -> bridge.Bridge:
    global test_extension_categories_bridge_agg, test_extension_categories_bridge_disagg

    if (
        test_extension_categories_bridge_agg is None
        or test_extension_categories_bridge_disagg is None
    ):
        test_agg_matrix = pd.DataFrame(
            index=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS.get_dl_as_multi_index(),
            columns=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.get_dl_as_multi_index(),
            dtype=cst.DTYPE_FLOAT,
        )
        test_agg_matrix.iloc[:, :] = 0.0
        test_agg_matrix.iloc[0, 0] = 1.0
        test_agg_matrix.iloc[1, 0] = 1.0
        test_agg_matrix.iloc[2, 0] = 1.0
        test_agg_matrix.iloc[3, 1] = 1.0
        test_agg_matrix.iloc[4, 1] = 1.0

        test_extension_categories_bridge_agg = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.EXTENSION_CATEGORIES,
            df=test_agg_matrix,
        )
        test_extension_categories_bridge_disagg = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.EXTENSION_CATEGORIES,
            df=test_agg_matrix.T,
        )

    if disagg:
        return test_extension_categories_bridge_disagg
    return test_extension_categories_bridge_agg


def get_test_final_demand_categories_bridge(
    disagg: bool = False,
) -> bridge.Bridge:
    global test_final_demand_categories_bridge_agg, test_final_demand_categories_bridge_disagg

    if (
        test_final_demand_categories_bridge_agg is None
        or test_final_demand_categories_bridge_disagg is None
    ):
        test_agg_matrix = pd.DataFrame(
            index=tests_cst.Y_CATEGORIES_DISAGG.get_dl_as_multi_index(),
            columns=tests_cst.Y_CATEGORIES_AGG.get_dl_as_multi_index(),
            dtype=cst.DTYPE_FLOAT,
        )
        test_agg_matrix.iloc[:, :] = 0.0
        test_agg_matrix.iloc[0, 0] = 1.0
        test_agg_matrix.iloc[1, 0] = 1.0
        test_agg_matrix.iloc[2, 0] = 1.0
        test_agg_matrix.iloc[3, 1] = 1.0
        test_agg_matrix.iloc[4, 2] = 1.0
        test_agg_matrix.iloc[5, 3] = 1.0

        test_final_demand_categories_bridge_agg = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
            df=test_agg_matrix,
        )
        test_final_demand_categories_bridge_disagg = (
            bridge.Bridge.init_from_df(
                kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
                df=test_agg_matrix.T,
            )
        )

    if disagg:
        return test_final_demand_categories_bridge_disagg
    return test_final_demand_categories_bridge_agg


def get_test_extension_categories_equivalent_to_sectors(
    extension_name: str,
) -> dl.ExtensionCategoriesDL:
    result = get_test_sectors().get_as_extension_categories_dl(
        extension_name=extension_name
    )
    result.prefix_level_names_if_duplicates(
        prefix=cst.IDX_PREFIX_EXT, other_dl=get_test_sectors()
    )
    return result


def get_test_extension_categories_equivalent_to_agg_sectors(
    extension_name: str,
) -> dl.ExtensionCategoriesDL:
    result = get_test_agg_sectors().get_as_extension_categories_dl(
        extension_name=extension_name
    )
    result.prefix_level_names_if_duplicates(
        prefix=cst.IDX_PREFIX_EXT, other_dl=get_test_sectors()
    )
    return result


def get_test_extension_categories_with_1_level(
    extension_name: str,
) -> dl.ExtensionCategoriesDL:
    return dl.ExtensionCategoriesDL(
        extension_name=extension_name,
        df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.df,
    )


def get_test_extension_categories_with_2_levels(
    extension_name: str,
) -> dl.ExtensionCategoriesDL:
    return dl.ExtensionCategoriesDL(
        extension_name=extension_name,
        df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS.df,
    )


def build_test_x() -> system_data.XData:
    return build_test_system_data(name=cst.X)


def build_test_y() -> system_data.YData:
    return build_test_system_data(name=cst.Y)


def build_test_z() -> system_data.ZData:
    return build_test_system_data(name=cst.Z)


def build_test_l() -> system_data.LData:
    return build_test_system_data(name=cst.L)


def build_test_l_k() -> system_data.LKData:
    return build_test_system_data(name=cst.L_K)


def build_test_a() -> system_data.AData:
    return build_test_system_data(name=cst.A)


def build_test_system_unit() -> system_data.UnitSystemData:
    return build_test_system_data(name=cst.UNIT)


def build_test_k() -> system_data.KData:
    return build_test_system_data(name=cst.K)


def build_test_y_k() -> system_data.YKData:
    return build_test_system_data(name=cst.Y_K)


def build_test_system_data(
    name: str,
    regions: dl.RegionsDL = tests_cst.DEFAULT_REGIONS,
    sectors: dl.SectorsDL = get_test_sectors(),
    final_demand_categories: dl.FinalDemandCategoriesDL = tests_cst.DEFAULT_Y_CATEGORIES,
):
    """
    Returns:
        AbstractSystemData : the instantiated data w.r.t given parameters
    """
    return sys_data_factory.make_data(
        name=name,
        regions=regions,
        sectors=sectors,
        final_demand_categories=final_demand_categories,
    )


def build_test_system_dataset(
    calcul_strategy: str,
) -> system_dataset.SystemDataSet:
    return system_dataset.SystemDataSet(
        sectors=get_test_sectors(),
        regions=tests_cst.DEFAULT_REGIONS,
        final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        config__system_calcul_strategy=calcul_strategy,
    )


def build_test_system_shock_dataset(
    data_list: list = None,
) -> system_shock_dataset.SystemShockDataSet:
    return system_shock_dataset.SystemShockDataSet(
        sectors=get_test_sectors(),
        regions=tests_cst.DEFAULT_REGIONS,
        final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        data_list=data_list,
    )


def build_test_extension_shock_dataset(
    data_list: list = None,
    extension_name="test_extension",
    extension_categories: dl.ExtensionCategoriesDL = tests_cst.DEFAULT_EXTENSION_CATEGORIES,
) -> extension_shock_dataset.ExtensionShockDataSet:
    return extension_shock_dataset.ExtensionShockDataSet(
        sectors=get_test_sectors(),
        regions=tests_cst.DEFAULT_REGIONS,
        final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        data_list=data_list,
        extension_name=extension_name,
        extension_categories=extension_categories,
    )


def build_test_da() -> sys_shock_data.AShockData:
    return build_test_system_shock_data(name=cst.D_A)


def build_test_dy() -> sys_shock_data.YShockData:
    return build_test_system_shock_data(name=cst.D_Y)


def build_test_dz() -> sys_shock_data.ZShockData:
    return build_test_system_shock_data(name=cst.D_Z)


def build_test_dk() -> sys_shock_data.KShockData:
    return build_test_system_shock_data(name=cst.D_K)


def build_test_dy_k() -> sys_shock_data.YkShockData:
    return build_test_system_shock_data(name=cst.D_Y_K)


def build_test_ds_x_dom() -> ext_shock_data.SxDomShockData:
    return build_test_extension_shock_data(name=cst.D_S_X_DOM)


def build_test_ds_y() -> ext_shock_data.SyShockData:
    return build_test_extension_shock_data(name=cst.D_S_Y)


def build_test_ds_z() -> ext_shock_data.SzShockData:
    return build_test_extension_shock_data(name=cst.D_S_Z)


def build_test_dm_row() -> ext_shock_data.MRoWShockData:
    return build_test_extension_shock_data(name=cst.D_M_ROW)


def build_test_system_shock_data(
    name: str,
    regions: dl.RegionsDL = tests_cst.DEFAULT_REGIONS,
    sectors: dl.SectorsDL = get_test_sectors(),
    final_demand_categories: dl.FinalDemandCategoriesDL = tests_cst.DEFAULT_Y_CATEGORIES,
):
    """
    Returns:
        AbstractShockData : the instantiated data w.r.t given parameters
    """
    return sys_shock_factory.make_data(
        name=name,
        regions=regions,
        sectors=sectors,
        final_demand_categories=final_demand_categories,
    )


def build_test_extension_shock_data(
    name: str,
    regions: dl.RegionsDL = tests_cst.DEFAULT_REGIONS,
    extension_name: str = "test_extension",
    sectors: dl.SectorsDL = get_test_sectors(),
    final_demand_categories: dl.FinalDemandCategoriesDL = tests_cst.DEFAULT_Y_CATEGORIES,
    extension_categories: dl.ExtensionCategoriesDL = tests_cst.DEFAULT_EXTENSION_CATEGORIES,
):
    """
    Returns:
        AbstractShockData : the instantiated data w.r.t given parameters
    """
    return ext_shock_factory.make_data(
        name=name,
        regions=regions,
        extension_name=extension_name,
        sectors=sectors,
        final_demand_categories=final_demand_categories,
        extension_categories=extension_categories,
    )


def build_test_s_x_dom() -> extension_data.SxDomData:
    return build_test_extension_data(name=cst.S_X_DOM)


def build_test_s_y() -> extension_data.SyData:
    return build_test_extension_data(name=cst.S_Y)


def build_test_f_y() -> extension_data.FyData:
    return build_test_extension_data(name=cst.F_Y)


def build_test_s_z() -> extension_data.SzData:
    return build_test_extension_data(name=cst.S_Z)


def build_test_f_z() -> extension_data.FzData:
    return build_test_extension_data(name=cst.F_Z)


def build_test_f_x_dom() -> extension_data.FxDomData:
    return build_test_extension_data(name=cst.F_X_DOM)


def build_test_m_row() -> extension_data.MRoWData:
    return build_test_extension_data(name=cst.M_ROW)


def build_test_d_imp() -> extension_data.DImpData:
    return build_test_extension_data(name=cst.D_IMP)


def build_test_m() -> extension_data.MData:
    return build_test_extension_data(name=cst.M)


def build_test_m_k() -> extension_data.MKData:
    return build_test_extension_data(name=cst.M_K)


def build_test_d_cba() -> extension_data.DCbaData:
    return build_test_extension_data(name=cst.D_CBA)


def build_test_d_cba_k() -> extension_data.DCbaKData:
    return build_test_extension_data(name=cst.D_CBA_K)


def build_test_extension_unit() -> extension_data.UnitExtensionData:
    return build_test_extension_data(name=cst.UNIT)


def build_test_extension_data(
    name: str,
    regions: dl.RegionsDL = tests_cst.DEFAULT_REGIONS,
    extension_name: str = "test_extension",
    sectors: dl.SectorsDL = get_test_sectors(),
    final_demand_categories: dl.FinalDemandCategoriesDL = tests_cst.DEFAULT_Y_CATEGORIES,
    extension_categories: dl.ExtensionCategoriesDL = tests_cst.DEFAULT_EXTENSION_CATEGORIES,
    strategy: str = None,
):
    """
    Returns:
        AbstractExtensionData : the instantiated data w.r.t given parameters
    """
    return ext_data_factory.make_data(
        name=name,
        regions=regions,
        extension_name=extension_name,
        sectors=sectors,
        final_demand_categories=final_demand_categories,
        extension_categories=extension_categories,
        strategy=strategy,
    )


def build_test_extension_dataset(
    extension_calcul_strategy: str,
    system_calcul_strategy: str = cst.STRATEGY_EXO_INVEST_MATRIX,
    extension_name: str = "test_extension",
    extension_categories: dl.ExtensionCategoriesDL = tests_cst.DEFAULT_EXTENSION_CATEGORIES,
) -> extension_dataset.ExtensionDataSet:
    return extension_dataset.ExtensionDataSet(
        sectors=get_test_sectors(),
        regions=tests_cst.DEFAULT_REGIONS,
        final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        extension_categories=extension_categories,
        extension_name=extension_name,
        config__extension_calcul_strategy=extension_calcul_strategy,
        config__system_calcul_strategy=system_calcul_strategy,
    )


def build_standard_system(random: bool = False) -> System:

    sys_director = sys_builders.get_director()

    sys_director.reset()
    sys_director.set_regions(tests_cst.DEFAULT_REGIONS)
    sys_director.set_sectors(get_test_sectors())
    sys_director.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
    sys_director.id.base_year = 2019

    system = sys_director.make_standard_system()

    if random:
        randomize_system(system)
    return system


def build_exo_invest_matrix_system(random: bool = False) -> System:
    sys_director = sys_builders.get_director()

    sys_director.reset()
    sys_director.set_regions(tests_cst.DEFAULT_REGIONS)
    sys_director.set_sectors(get_test_sectors())
    sys_director.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
    sys_director.id.base_year = 2019

    system = sys_director.make_exo_invest_matrix_system()

    if random:
        randomize_system(system)
    return system


def build_endo_invest_matrix_system(random: bool = False) -> System:
    sys_director = sys_builders.get_director()

    sys_director.reset()
    sys_director.set_regions(tests_cst.DEFAULT_REGIONS)
    sys_director.set_sectors(get_test_sectors())
    sys_director.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
    sys_director.id.base_year = 2019

    system = sys_director.make_endo_invest_matrix_system()

    if random:
        randomize_system(system)
    return system


def build_use_based_extension(
    name: str,
    regions: dl.RegionsDL = tests_cst.DEFAULT_REGIONS,
    sectors: dl.SectorsDL = get_test_sectors(),
    final_demand_categories: dl.FinalDemandCategoriesDL = tests_cst.DEFAULT_Y_CATEGORIES,
    extension_categories: dl.ExtensionCategoriesDL = tests_cst.DEFAULT_EXTENSION_CATEGORIES,
    random: bool = False,
) -> Extension:
    ext_director = ext_builders.get_director()

    ext_director.reset()
    ext_director.set_regions(regions)
    ext_director.set_sectors(sectors)
    ext_director.set_final_demand_categories(final_demand_categories)
    ext_director.set_extension_categories(extension_categories)

    extension = ext_director.make_use_based_extension(name=name)

    if random:
        randomize_extension(extension)
    return extension


def build_gross_output_based_extension(
    name: str,
    regions: dl.RegionsDL = tests_cst.DEFAULT_REGIONS,
    sectors: dl.SectorsDL = get_test_sectors(),
    final_demand_categories: dl.FinalDemandCategoriesDL = tests_cst.DEFAULT_Y_CATEGORIES,
    extension_categories: dl.ExtensionCategoriesDL = tests_cst.DEFAULT_EXTENSION_CATEGORIES,
    random: bool = False,
) -> Extension:
    ext_director = ext_builders.get_director()

    ext_director.reset()
    ext_director.set_regions(regions)
    ext_director.set_sectors(sectors)
    ext_director.set_final_demand_categories(final_demand_categories)
    ext_director.set_extension_categories(extension_categories)

    extension = ext_director.make_gross_output_based_extension(name=name)

    if random:
        randomize_extension(extension)
    return extension


def build_embodied_in_import_extension(
    name: str,
    regions: dl.RegionsDL = tests_cst.DEFAULT_REGIONS,
    sectors: dl.SectorsDL = get_test_sectors(),
    final_demand_categories: dl.FinalDemandCategoriesDL = tests_cst.DEFAULT_Y_CATEGORIES,
    extension_categories: dl.ExtensionCategoriesDL = tests_cst.DEFAULT_EXTENSION_CATEGORIES,
    random: bool = False,
) -> Extension:
    ext_director = ext_builders.get_director()

    ext_director.reset()
    ext_director.set_regions(regions)
    ext_director.set_sectors(sectors)
    ext_director.set_final_demand_categories(final_demand_categories)
    ext_director.set_extension_categories(extension_categories)

    extension = ext_director.make_embodied_in_import_extension(name=name)

    if random:
        randomize_extension(extension)
    return extension


def build_system_shock() -> SystemShock:
    shock_dir = sys_shock_builders.get_director()
    shock_dir.reset()
    shock_dir.id.base_year = 2019
    shock_dir.set_regions(tests_cst.DEFAULT_REGIONS)
    shock_dir.set_sectors(get_test_sectors())
    shock_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
    return shock_dir.make_shock_complete()


def build_system_y_shock() -> SystemShock:
    shock_dir = sys_shock_builders.get_director()
    shock_dir.reset()
    shock_dir.id.base_year = 2019
    shock_dir.set_regions(tests_cst.DEFAULT_REGIONS)
    shock_dir.set_sectors(get_test_sectors())
    shock_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
    return shock_dir.make_shock_y()


def build_extension_shock(extension: Extension) -> ExtensionShock:
    shock_dir = ext_shock_builders.get_director()
    shock_dir.reset()
    shock_dir.set_regions(extension.dataset.regions)
    shock_dir.set_sectors(extension.dataset.sectors)
    shock_dir.set_final_demand_categories(
        extension.dataset.final_demand_categories
    )
    shock_dir.set_extension_categories(
        categories=extension.dataset.extension_categories
    )

    return shock_dir.make_shock_complete(name=extension.name)


def build_extension_shock_only_s_x(extension: Extension):
    shock_dir = ext_shock_builders.get_director()
    shock_dir.reset()
    shock_dir.set_regions(extension.dataset.regions)
    shock_dir.set_sectors(extension.dataset.sectors)
    shock_dir.set_final_demand_categories(
        extension.dataset.final_demand_categories
    )
    shock_dir.set_extension_categories(
        categories=extension.dataset.extension_categories
    )
    shock = shock_dir.make_shock_s_x(name=extension.name)

    return shock


def build_extension_shock_only_s_y(extension: Extension) -> ExtensionShock:
    shock_dir = ext_shock_builders.get_director()
    shock_dir.reset()
    shock_dir.set_regions(extension.dataset.regions)
    shock_dir.set_sectors(extension.dataset.sectors)
    shock_dir.set_final_demand_categories(
        extension.dataset.final_demand_categories
    )
    shock_dir.set_extension_categories(
        categories=extension.dataset.extension_categories
    )
    shock = shock_dir.make_shock_s_y(name=extension.name)

    return shock


def build_extension_shock_only_s_z(extension: Extension) -> ExtensionShock:
    shock_dir = ext_shock_builders.get_director()
    shock_dir.reset()
    shock_dir.set_regions(extension.dataset.regions)
    shock_dir.set_sectors(extension.dataset.sectors)
    shock_dir.set_final_demand_categories(
        extension.dataset.final_demand_categories
    )
    shock_dir.set_extension_categories(
        categories=extension.dataset.extension_categories
    )
    shock = shock_dir.make_shock_s_z(name=extension.name)

    return shock


def randomize_dataset(
    dataset: AbstractDataSet,
    with_zeros: bool = False,
    proportion_to_randomize: float = 1.0,
):
    for data_name in dataset.list_data():
        if data_name != cst.UNIT:
            randomize(
                getattr(dataset, data_name).df,
                with_zeros=with_zeros,
                proportion_to_randomize=proportion_to_randomize,
            )
        else:
            randomize_string_df(getattr(dataset, data_name).df)


def randomize_system(system: System):
    randomize_dataset(system.dataset)


def randomize_extension(extension: Extension):
    randomize_dataset(extension.dataset)


def randomize(
    df: pd.DataFrame | pd.Series,
    with_zeros: bool = False,
    with_nans: bool = False,
    proportion_to_randomize: float = 1.0,
    full_randomization: bool = tests_config.FULL_RANDOMIZATION,
):
    if full_randomization:
        for i in range(len(df.index)):
            if isinstance(df, pd.DataFrame):
                for j in range(len(df.columns)):
                    if np.random.random() < proportion_to_randomize:
                        # Generate a random float number between 0.0 and 100.0
                        df.iat[i, j] = np.random.random() * 100
            if isinstance(df, pd.Series):
                if np.random.random() < proportion_to_randomize:
                    # Generate a random float number between 0.0 and 100.0
                    df.iat[i] = np.random.random() * 100
    else:
        df.loc[:, :] = np.random.random() * 100

    if with_zeros:
        # Add a few zeros at random positions in the dataframe
        add_random_number(df, 0.0)
    if with_nans:
        # Add a few NaNs at random position in the dataframe
        add_random_number(df, np.nan)


def randomize_string_df(
    df: pd.DataFrame,
    full_randomization: bool = tests_config.FULL_RANDOMIZATION,
):
    def gen_random_letter() -> chr:
        return chr(np.random.randint(1, 27) + 64)

    if full_randomization:
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                # Generate a random string
                df.iat[i, j] = gen_random_letter()
    else:
        df.loc[:, :] = gen_random_letter()


def add_random_number(
    df: pd.DataFrame | pd.Series, number: int | float, occurrences: int = 3
):
    for n in range(occurrences):
        i = np.random.randint(low=0, high=len(df.index))
        if isinstance(df, pd.DataFrame):
            j = np.random.randint(low=0, high=len(df.columns))
            df.iat[i, j] = number
        if isinstance(df, pd.Series):
            df.iat[i] = number
