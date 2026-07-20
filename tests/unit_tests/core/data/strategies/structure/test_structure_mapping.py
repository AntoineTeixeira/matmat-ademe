import pytest

from matmat.core.data.strategies import structure
from matmat.core.detail_level import core as dl
from matmat.core.base import filter
from unit_tests.conftest import dl_extension_categories_1


class TestStructureMappingDirect:
    """
    Test class for the class StructureMappingDirect
    """

    @pytest.fixture
    def structure_mapping(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureMappingDirect(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_mapping):
        """
        Test property `rows_specs`
        """
        assert structure_mapping.rows_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_mapping):
        """
        Test property `columns_specs`
        """
        assert structure_mapping.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class TestStructureMappingIndirect:
    """
    Test class for the class StructureMappingIndirect
    """

    @pytest.fixture
    def structure_mapping(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureMappingIndirect(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_mapping):
        """
        Test property `rows_specs`
        """
        assert structure_mapping.rows_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_import_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_mapping):
        """
        Test property `columns_specs`
        """
        assert structure_mapping.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class TestStructureMappingKDirect:
    """
    Test class for the class StructureMappingKDirect
    """

    @pytest.fixture
    def structure_mapping(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureMappingKDirect(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_mapping):
        """
        Test property `rows_specs`
        """
        assert structure_mapping.rows_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_mapping):
        """
        Test property `columns_specs`
        """
        assert structure_mapping.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class TestStructureMappingKIndirect:
    """
    Test class for the class StructureMappingKIndirect
    """

    @pytest.fixture
    def structure_mapping(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureMappingKIndirect(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_mapping):
        """
        Test property `rows_specs`
        """
        assert structure_mapping.rows_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_import_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_mapping):
        """
        Test property `columns_specs`
        """
        assert structure_mapping.columns_specs == {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }
