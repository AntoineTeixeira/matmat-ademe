import pytest
import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.base import filter
from matmat.core.data.strategies import structure
import matmat.utils.constants as cst

from tests.utils import builders, constants as tests_cst


class TestStructureY:
    """
    Test class for the following classes:
        - AbstractDataStructure
        - StructureY
    """

    sectors = builders.get_test_sectors()
    regions = tests_cst.REGIONS_W_IMPORT
    final_demand_categories = tests_cst.DEFAULT_Y_CATEGORIES

    @pytest.fixture
    def structure_y(
        self, dl_regions_1, dl_sectors_1, dl_final_demand_categories_1
    ):
        return structure.StructureY(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
        )

    def test_rows_specs(self, structure_y):
        """
        Test property `rows_specs`
        """
        assert structure_y.rows_specs == {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_y):
        """
        Test property `columns_specs`
        """
        assert structure_y.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
        }

    def test_diagonalize_final_demand(self):
        """
        Test function `diagonalize` of class `StructureY`.

        Expected results:
            - Check that the obtained dataframe is diagonalized per region and
            per column properly, which means for each region block:
                - only zeros at (i, j) if i != j
                - the expected value at (i, i)
        """
        y = builders.build_test_y()
        builders.randomize(y.df)

        y_diag = y.structure.diagonalize(df=y.df)

        def check_subsets(y_subset: pd.Series, y_diag_subset: pd.DataFrame):
            for i in range(0, y_subset.shape[0]):
                assert y_subset.iloc[i] == y_diag_subset.iloc[i, i]
                for j in range(0, y_diag_subset.shape[1]):
                    if j != i:
                        assert y_diag_subset.iloc[i, j] == 0.0

        # Loop on columns
        for column in y.df_columns:
            # Loop on domestic regions
            for dom_region in y.get_domestic_regions_list():
                check_subsets(
                    y_subset=y.get_domestic_origin().loc[dom_region][column],
                    y_diag_subset=y_diag.loc[(cst.IDX_DOMESTIC, dom_region)][
                        column
                    ],
                )
            # Loop on import regions
            for imp_region in y.get_import_regions_list():
                check_subsets(
                    y_subset=y.get_import_origin().loc[imp_region][column],
                    y_diag_subset=y_diag.loc[(cst.IDX_IMPORT, imp_region)][
                        column
                    ],
                )
