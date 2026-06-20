from matmat.utils import constants as cst
from matmat.core.shocks.extension.dataset.core import ExtensionShockDataSet
from matmat.core.shocks.extension.data import factory, core as extension_data

from tests.utils import builders, constants as tests_cst, spy as spy_utils


class TestExtensionShockDataSet:

    # Dataset to be used throughout the tests
    dataset: ExtensionShockDataSet = None

    def set_up_dataset(self):
        self.dataset = builders.build_test_extension_shock_dataset(
            extension_name="test_extension",
        )

    def test_set_data(self, mocker):
        """
        Test function 'set_data'

        Expected results:
            Check that the method 'set_data' uses correctly the extension shock
            data factory method, and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(factory, "make_data")

        # Call function under test
        self.dataset.set_data(name=cst.D_S_Y)

        # Check results
        spy_utils.check_specific_call_with_args(
            function_spy=spy,
            call_number=1,
            args=[],
            kwargs={
                "name": cst.D_S_Y,
                "regions": tests_cst.DEFAULT_REGIONS,
                "final_demand_categories": tests_cst.DEFAULT_Y_CATEGORIES,
                "sectors": builders.get_test_sectors(),
                "extension_name": "test_extension",
                "extension_categories": tests_cst.DEFAULT_EXTENSION_CATEGORIES,
            },
        )
        assert self.dataset.dS_Y is spy.spy_return

    def test_set_null_data(self, mocker):
        """
        Test function 'set_null_data'

        Expected results:
            Check that the method 'set_null_data' uses the null extension shock
            data class and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(extension_data.NullExtensionShockData, "__init__")

        # Call function under test
        self.dataset.set_null_data(name=cst.D_S_Y)

        # Check results
        spy.assert_called_once()
        assert isinstance(
            self.dataset.dS_Y, extension_data.NullExtensionShockData
        )
