import pytest

from matmat.core.data.strategies import structure
from matmat.core.detail_level import core as dl
from matmat.core.base import filter
from unit_tests.conftest import dl_extension_categories_1


class TestStructureMRoW:
    """
    Test class for the class StructureMRoW
    """

    @pytest.fixture
    def structure_m_row(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureMRoW(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_m_row):
        """
        Test property `rows_specs`
        """
        assert structure_m_row.rows_specs == {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    def test_columns_specs(self, structure_m_row):
        """
        Test property `columns_specs`
        """
        assert structure_m_row.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_import_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }
