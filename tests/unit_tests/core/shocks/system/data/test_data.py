from matmat.core.shocks.system.data.core import AShockData

from tests.utils import constants as tests_cst, builders


class TestSystemShockData:
    """
    This class contains test cases to test methods of `AbstractSystemShockData`
    """

    def test_constructor(self, mocker):
        """
        Test function `__init__`

        Expected results:
            - Instantiate an object AShockData and check that:
                - Check that the structure and nature are properly set
                - Check that the dataframe index and columns match the
                  attributes df_index & df_columns of the associated structure
                - Check that the dataframe index and columns match
                  the attributes df_index & df_columns
                - Check that the dataframe values are all NaN
        """
        spy_nature = mocker.spy(AShockData, "get_nature_type")
        spy_structure = mocker.spy(AShockData, "get_structure_type")

        da = AShockData(
            regions=tests_cst.DEFAULT_REGIONS,
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )
        # Nature
        assert spy_nature.spy_return is da.nature.__class__
        # Structure
        assert spy_structure.spy_return is da.structure.__class__
        # Dataframe
        assert da.df.index.equals(da.df_rows)
        assert da.df.columns.equals(da.df_columns)
        assert da.df.isna().all().all()
