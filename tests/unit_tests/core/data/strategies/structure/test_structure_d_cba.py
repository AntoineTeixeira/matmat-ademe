import pytest

from matmat.core.data.strategies import structure
from matmat.core.detail_level import core as dl
from matmat.core.base import filter
from unit_tests.conftest import dl_extension_categories_1


class TestStructureDCbaBySector:
    """
    Test class for the class StructureDCbaBySector
    """

    @pytest.fixture
    def structure_d_cba(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureDCbaBySector(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_d_cba):
        """
        Test property `rows_specs`
        """
        assert structure_d_cba.rows_specs == {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_d_cba):
        """
        Test property `columns_specs`
        """
        assert structure_d_cba.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class TestStructureDCbaKBySector:
    """
    Test class for the class StructureDCbaKBySector
    """

    @pytest.fixture
    def structure_d_cba(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureDCbaKBySector(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_d_cba):
        """
        Test property `rows_specs`
        """
        assert structure_d_cba.rows_specs == {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_d_cba):
        """
        Test property `columns_specs`
        """
        assert structure_d_cba.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }

class TestStructureDCbaByExtensionCategory:
    """
    Test class for the class StructureDCbaByExtensionCategory
    """

    @pytest.fixture
    def structure_d_cba(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureDCbaByExtensionCategory(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_d_cba):
        """
        Test property `rows_specs`
        """
        assert structure_d_cba.rows_specs == {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    def test_columns_specs(self, structure_d_cba):
        """
        Test property `columns_specs`
        """
        assert structure_d_cba.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class TestStructureDCbaKByExtensionCategory:
    """
    Test class for the class StructureDCbaKByExtensionCategory
    """

    @pytest.fixture
    def structure_d_cba(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureDCbaKByExtensionCategory(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_d_cba):
        """
        Test property `rows_specs`
        """
        assert structure_d_cba.rows_specs == {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    def test_columns_specs(self, structure_d_cba):
        """
        Test property `columns_specs`
        """
        assert structure_d_cba.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }

