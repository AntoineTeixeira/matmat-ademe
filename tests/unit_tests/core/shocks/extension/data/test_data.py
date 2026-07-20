from matmat.core.shocks.extension.data.core import SxDomShockData

from tests.utils import constants as tests_cst, builders


class TestExtensionShockData:
    """
    This class contains test cases to test methods
    of `AbstractExtensionShockData`
    """

    def test_constructor(self, mocker):
        """
        Test function `__init__`

        Expected results:
            - Instantiate an object SxShockData and check that:
                - Check that the structure and nature are properly set
                - Check that the dataframe index and columns match the
                  attributes df_index & df_columns of the associated structure
                - Check that the dataframe values are all NaN
        """
        spy_nature = mocker.spy(SxDomShockData, "get_nature_type")
        spy_structure = mocker.spy(SxDomShockData, "get_structure_type")

        ds_x = SxDomShockData(
            sectors=builders.get_test_sectors(),
            regions=tests_cst.DEFAULT_REGIONS,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            extension_name="test_extension",
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )
        # ID
        assert ds_x.id.extension_name == "test_extension"
        # Nature
        assert spy_nature.spy_return is ds_x.nature.__class__
        # Structure
        assert spy_structure.spy_return is ds_x.structure.__class__
        # Dataframe
        assert ds_x.df.index.equals(ds_x.df_rows)
        assert ds_x.df.columns.equals(ds_x.df_columns)
        assert ds_x.df.isna().all().all()
