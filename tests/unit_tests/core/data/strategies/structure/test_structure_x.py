import pytest
import pandas as pd

from matmat.core.data.strategies import structure
from matmat.core.detail_level import core as dl
from matmat.utils import constants as cst


class TestStructureX:
    """
    Test class for the class StructureX
    """

    @pytest.fixture
    def structure_x(
        self, dl_regions_1, dl_sectors_1, dl_final_demand_categories_1
    ):
        return structure.StructureX(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
        )

    def test_rows_specs(self, structure_x):
        """
        Test property `rows_specs`
        """
        assert structure_x.rows_specs == {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_x):
        """
        Test property `columns_specs`
        """
        assert structure_x.columns_specs is None

    def test_build_columns(self, structure_x):
        """
        Test method `_build_columns`

        Expected results:
            As StructureX has no columns specs, ensure that the method
            `_build_columns` is overridden properly, i.e. df_columns
            is properly built.
        """
        assert structure_x.df_columns.equals(pd.MultiIndex.from_arrays(
            [[cst.X]], names=[cst.IDX_VARIABLE]
        ))
