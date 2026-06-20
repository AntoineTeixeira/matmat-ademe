"""
Overview
********
This module contains the configuration map(s) of an extension dataset.
"""

from matmat.core.dataset.config import DataSetMap, DataSetConversions
from matmat.utils import constants as cst


DATASET_MAP_WRT_SYSTEM_CALCUL_STRATEGY = DataSetMap(
    map_={
        cst.STRATEGY_STANDARD: {
            cst.S_X_DOM,
            cst.S_Y,
            cst.S_Z,
            cst.F_X_DOM,
            cst.F_Y,
            cst.F_Z,
            cst.M_ROW,
            cst.D_IMP,
            cst.M,
            cst.D_CBA,
            cst.MAPPING,
            cst.UNIT,
        },
        cst.STRATEGY_EXO_INVEST_MATRIX: {
            cst.S_X_DOM,
            cst.S_Y,
            cst.S_Z,
            cst.F_X_DOM,
            cst.F_Y,
            cst.F_Z,
            cst.M_ROW,
            cst.D_IMP,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
            cst.MAPPING,
            cst.MAPPING_K,
            cst.UNIT,
        },
        cst.STRATEGY_ENDO_INVEST_MATRIX: {
            cst.S_X_DOM,
            cst.S_Y,
            cst.S_Z,
            cst.F_X_DOM,
            cst.F_Y,
            cst.F_Z,
            cst.M_ROW,
            cst.D_IMP,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
            cst.MAPPING,
            cst.MAPPING_K,
            cst.UNIT,
        },
    }
)
DATASET_MAP_WRT_EXTENSION_CALCUL_STRATEGY = DataSetMap(
    map_={
        cst.STRATEGY_USE_BASED: {
            cst.S_Y,
            cst.S_Z,
            cst.F_Y,
            cst.F_Z,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
            cst.UNIT,
        },
        cst.STRATEGY_GROSS_OUTPUT_BASED: {
            cst.S_X_DOM,
            cst.F_X_DOM,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
            cst.MAPPING,
            cst.MAPPING_K,
            cst.UNIT,
        },
        cst.STRATEGY_EMBODIED_IN_IMPORT: {
            cst.M_ROW,
            cst.D_IMP,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
            cst.MAPPING,
            cst.MAPPING_K,
            cst.UNIT,
        },
    }
)


class ExtensionDataSetConversions(DataSetConversions):

    @staticmethod
    def conversion__use_based_to_gross_output_based(in_dataset, out_dataset):
        if not in_dataset.F_Z.is_df_empty():
            out_dataset.F_x_dom.update_values(
                in_dataset.F_Z.df.groupby(
                    level=in_dataset.sectors.get_level_names(),
                    sort=False,
                )
                .sum()
            )
