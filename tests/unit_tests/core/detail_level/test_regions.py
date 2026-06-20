from matmat.core.detail_level import core as dl
from matmat.utils import constants as cst

from tests.unit_tests.core.detail_level.base import TestDetailLevel


class TestRegions(TestDetailLevel):

    def test_regions_load_from_path(self):
        """
        Test function `load_from_path` for regions detail level

        Expected results:
            - The read matrix in the "regions" sheet
              matches the one exported in the Excel file
        """

        dl_regions = dl.RegionsDL()
        dl_regions.load_from_path(self.dl_path)

        assert dl_regions.df.equals(self.dl_regions)

    def test_sectors_get_level_names(self):
        """
        Test function `get_level_names` for regions detail level

        Expected results:
            - The level names are equal to the columns titles
        """

        dl_regions = dl.RegionsDL()
        dl_regions.load_from_path(self.dl_path)

        assert (
            dl_regions.get_level_names() == self.dl_regions.columns.to_list()
        )

    def test_get_dl_as_dict(self):
        """
        Test function `get_dl_as_dict` for regions detail level

        Expected results:
            - The dictionary is built correctly from the regions df
        """

        dl_regions = dl.RegionsDL()
        dl_regions.load_from_path(self.dl_path)

        assert dl_regions.get_dl_as_dict() == {
            "domestic": ["France"],
            "import": ["Austria", "Slovakia", "Portugal"],
        }

    def test_get_regions_list(self):
        """
        Test functions `get_domestic_regions_list` and `get_import_regions_list`
        and `get_regions_list`

        Expected results:
            - domestic regions list shall contain the regions associated with a
              value set to "domestic" in the origin column
            - import regions list shall contain the regions associated with a
              value set to "import" in the origin column
            - the list of regions shall contain the list of values in the
              "region" column
        """
        dl_regions = dl.RegionsDL()
        dl_regions.load_from_path(self.dl_path)
        assert (
            dl_regions.get_domestic_regions_list()
            == dl_regions.df.loc[
                dl_regions.df[cst.IDX_ORIGIN] == cst.IDX_DOMESTIC
            ][cst.IDX_REGION].to_list()
        )
        assert (
            dl_regions.get_import_regions_list()
            == dl_regions.df.loc[
                dl_regions.df[cst.IDX_ORIGIN] == cst.IDX_IMPORT
            ][cst.IDX_REGION].to_list()
        )
        assert (
            dl_regions.get_regions_list()
            == dl_regions.df[cst.IDX_REGION].squeeze().to_list()
        )
