import pytest

from matmat.core.data.strategies import structure
from matmat.core.detail_level import core as dl
from matmat.core.base import filter


class TestStructureZ:
    """
    Test class for the class StructureZ
    """

    @pytest.fixture
    def structure_z(
        self, dl_regions_1, dl_sectors_1, dl_final_demand_categories_1
    ):
        return structure.StructureZ(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
        )

    def test_rows_specs(self, structure_z):
        """
        Test property `rows_specs`
        """
        assert structure_z.rows_specs == {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_z):
        """
        Test property `columns_specs`
        """
        assert structure_z.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }
