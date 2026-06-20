from matmat.utils import constants as cst
from matmat.core.shocks.system.dataset.core import SystemShockDataSet
from matmat.core.shocks.system.data import factory, core as system_shock_data

from tests.utils import builders, constants as tests_cst, spy as spy_utils


class TestSystemShockDataSet:

    # Dataset to be used throughout the tests
    dataset: SystemShockDataSet = None

    def set_up_dataset(self):
        self.dataset = builders.build_test_system_shock_dataset()

    def test_set_data(self, mocker):
        """
        Test function 'set_data'

        Expected results:
            Check that the method 'set_data' uses correctly the system shock
            data factory method, and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(factory, "make_data")

        # Call function under test
        self.dataset.set_data(name=cst.D_A)

        # Check results
        spy_utils.check_specific_call_with_args(
            function_spy=spy,
            call_number=1,
            args=[],
            kwargs={
                "name": cst.D_A,
                "regions": tests_cst.DEFAULT_REGIONS,
                "final_demand_categories": tests_cst.DEFAULT_Y_CATEGORIES,
                "sectors": builders.get_test_sectors(),
            },
        )
        assert self.dataset.dA is spy.spy_return

    def test_set_null_data(self, mocker):
        """
        Test function 'set_null_data'

        Expected results:
            Check that the method 'set_null_data' uses the null system shock
            data class and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(system_shock_data.NullSystemShockData, "__init__")

        # Call function under test
        self.dataset.set_null_data(name=cst.D_A)

        # Check results
        spy.assert_called_once()
        assert isinstance(
            self.dataset.dA, system_shock_data.NullSystemShockData
        )
