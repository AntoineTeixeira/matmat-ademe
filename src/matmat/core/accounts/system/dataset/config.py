"""
Overview
********
This module contains the configuration map(s) of a system dataset.
"""

from matmat.core.dataset.config import DataSetMap, DataSetConversions
from matmat.utils import constants as cst


DATASET_MAP_WRT_SYSTEM_CALCUL_STRATEGY = DataSetMap(
    map_={
        cst.STRATEGY_STANDARD: {
            cst.A,
            cst.L,
            cst.UNIT,
            cst.X,
            cst.Y,
            cst.Z,
        },
        cst.STRATEGY_EXO_INVEST_MATRIX: {
            cst.A,
            cst.L,
            cst.L_K,
            cst.K,
            cst.UNIT,
            cst.X,
            cst.Y,
            cst.Y_K,
            cst.Z,
        },
        cst.STRATEGY_ENDO_INVEST_MATRIX: {
            cst.A,
            cst.L,
            cst.L_K,
            cst.K,
            cst.UNIT,
            cst.X,
            cst.Y,
            cst.Y_K,
            cst.Z,
        },
    }
)


class SystemDataSetConversions(DataSetConversions):
    # No conversions defined for a system dataset
    pass
