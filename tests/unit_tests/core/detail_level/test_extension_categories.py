from matmat.core.detail_level import core as dl

from tests.unit_tests.core.detail_level.base import TestDetailLevel


class TestExtensionCategories(TestDetailLevel):

    def test_extension_raw_materials_load_from_path(self):
        """
        Test function `load_from_path` for extension categories detail level
        for an extension named "raw_materials"

        Expected results:
            - The read matrix in the "raw_materials" sheet
              matches the one exported in the Excel file
        """

        dl_rm = dl.ExtensionCategoriesDL(extension_name="raw_materials")
        dl_rm.load_from_path(self.dl_path)

        assert dl_rm.df.equals(self.dl_raw_materials)

    def test_extension_ghg_emissions_load_from_path(self):
        """
        Test function `load_from_path` for extension categories detail level
        for an extension named "ghg_emissions"

        Expected results:
            - The read matrix in the "ghg_emissions" sheet
              matches the one exported in the Excel file
        """

        dl_ghg_emissions = dl.ExtensionCategoriesDL(extension_name="ghg_emissions")
        dl_ghg_emissions.load_from_path(self.dl_path)

        assert dl_ghg_emissions.df.equals(self.dl_ghg_emissions)

    def test_get_dl_as_list(self):
        """
        Test function `get_dl_as_list` for ghg_emissions detail level

        Expected results:
            - The list is built correctly from the ghg_emissions categories df
        """

        dl_ghg_emissions = dl.ExtensionCategoriesDL(extension_name="ghg_emissions")
        dl_ghg_emissions.load_from_path(self.dl_path)

        assert dl_ghg_emissions.get_dl_as_list() == self.ghg_emission_categories

    def test_get_dl_as_dict_or_list(self):
        """
        Test function `get_dl_as_dict_or_list` for extension categories detail level

        Expected results:
            - The list is built correctly from the ghg_emissions categories df
        """

        dl_fdc = dl.ExtensionCategoriesDL(extension_name="ghg_emissions")
        dl_fdc.load_from_path(self.dl_path)

        assert dl_fdc.get_dl_as_dict_or_list() == dl_fdc.get_dl_as_list()
