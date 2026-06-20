from matmat.core.detail_level import core as dl

from tests.unit_tests.core.detail_level.base import TestDetailLevel

class TestFinalDemandCategories(TestDetailLevel):

    def test_final_demand_categories_load_from_path(self):
        """
        Test function `load_from_path` for final demand categories detail level

        Expected results:
            - The read matrix in the "final_demand_categories" sheet
              matches the one exported in the Excel file
        """

        dl_fdc = dl.FinalDemandCategoriesDL()
        dl_fdc.load_from_path(self.dl_path)

        assert dl_fdc.df.equals(self.dl_final_demand)

    def test_get_dl_as_dict_or_list(self):
        """
        Test function `get_dl_as_dict_or_list` for final demand categories detail level

        Expected results:
            - The dictionary is built correctly from the final demand categories df
        """

        dl_fdc = dl.FinalDemandCategoriesDL()
        dl_fdc.load_from_path(self.dl_path)

        assert dl_fdc.get_dl_as_dict_or_list() == dl_fdc.get_dl_as_dict()
