from matmat.utils import constants as cst
from matmat.core.accounts.system.dataset.core import SystemDataSet
from matmat.core.accounts.system.data import factory, core as system_data

from tests.utils import builders, constants as tests_cst, spy as spy_utils


class TestSystemDataSet:

    # Dataset to be used throughout the tests
    dataset: SystemDataSet = None

    def set_up_dataset(self):
        self.dataset = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_STANDARD,
        )

    def test_set_data(self, mocker):
        """
        Test function 'set_data'

        Expected results:
            Check that the method 'set_data' uses correctly the system
            data factory method, and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(factory, "make_data")

        # Call function under test
        self.dataset.set_data(name=cst.A)

        # Check results
        spy_utils.check_specific_call_with_args(
            function_spy=spy,
            call_number=1,
            args=[],
            kwargs={
                "name": cst.A,
                "regions": tests_cst.DEFAULT_REGIONS,
                "final_demand_categories": tests_cst.DEFAULT_Y_CATEGORIES,
                "sectors": builders.get_test_sectors(),
            },
        )
        assert self.dataset.A is spy.spy_return

    def test_set_null_data(self, mocker):
        """
        Test function 'set_null_data'

        Expected results:
            Check that the method 'set_null_data' uses the null system data
            class and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(system_data.NullSystemData, "__init__")

        # Call function under test
        self.dataset.set_null_data(name=cst.A)

        # Check results
        spy.assert_called_once()
        assert isinstance(self.dataset.A, system_data.NullSystemData)

    def test_tune_from_standard(self):
        """
        Test function 'tune'

        Expected results:
            When switching configuration, the dataset data are properly
            tuned:
                - Case 1: from STANDARD to EXO_INVEST_MATRIX
                - Case 2: from STANDARD to ENDO_INVEST_MATRIX
        """
        dataset_ref_exo_invest_matrix = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
        )
        dataset_ref_endo_invest_matrix = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_STANDARD,
        )
        # Change configuration
        dataset_test.set_config(
            name="system_calcul_strategy",
            value=cst.STRATEGY_EXO_INVEST_MATRIX,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_exo_invest_matrix)

        # CASE 2

        # Init dataset
        dataset_test = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_STANDARD,
        )
        # Change configuration
        dataset_test.set_config(
            name="system_calcul_strategy",
            value=cst.STRATEGY_ENDO_INVEST_MATRIX,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_endo_invest_matrix)

    def test_tune_from_exo_invest_matrix(self):
        """
        Test function 'tune'

        Expected results:
            When switching configuration, the dataset data are properly
            tuned:
                - Case 1: from EXO_INVEST_MATRIX to STANDARD
                - Case 2: from EXO_INVEST_MATRIX to ENDO_INVEST_MATRIX
        """
        dataset_ref_standard = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_STANDARD,
        )
        dataset_ref_endo_invest_matrix = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
        )
        # Change configuration
        dataset_test.set_config(
            name="system_calcul_strategy",
            value=cst.STRATEGY_STANDARD,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_standard)

        # CASE 2

        # Init dataset
        dataset_test = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
        )
        # Change configuration
        dataset_test.set_config(
            name="system_calcul_strategy",
            value=cst.STRATEGY_ENDO_INVEST_MATRIX,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_endo_invest_matrix)

    def test_tune_from_endo_invest_matrix(self):
        """
        Test function 'tune'

        Expected results:
            When switching configuration, the dataset data are properly
            tuned:
                - Case 1: from ENDO_INVEST_MATRIX to STANDARD
                - Case 2: from ENDO_INVEST_MATRIX to EXO_INVEST_MATRIX
        """
        dataset_ref_standard = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_STANDARD,
        )
        dataset_ref_exo_invest_matrix = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
        )
        # Change configuration
        dataset_test.set_config(
            name="system_calcul_strategy",
            value=cst.STRATEGY_STANDARD,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_standard)

        # CASE 2

        # Init dataset
        dataset_test = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
        )
        # Change configuration
        dataset_test.set_config(
            name="system_calcul_strategy",
            value=cst.STRATEGY_EXO_INVEST_MATRIX,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_exo_invest_matrix)
