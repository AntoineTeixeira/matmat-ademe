from matmat.utils import constants as cst
from matmat.core.accounts.extension.dataset.core import ExtensionDataSet
from matmat.core.accounts.extension.data import factory, core as extension_data

from tests.utils import builders, constants as tests_cst, spy as spy_utils


class TestExtensionDataSet:

    # Dataset to be used throughout the tests
    dataset: ExtensionDataSet = None

    def set_up_dataset(self):
        self.dataset = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )

    def test_set_data(self, mocker):
        """
        Test function 'set_data'

        Expected results:
            Check that the method 'set_data' uses correctly the extension
            data factory method, and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(factory, "make_data")

        # Call function under test
        self.dataset.set_data(name=cst.S_Y)

        # Check results
        spy_utils.check_specific_call_with_args(
            function_spy=spy,
            call_number=1,
            args=[],
            kwargs={
                "name": cst.S_Y,
                "regions": tests_cst.DEFAULT_REGIONS,
                "final_demand_categories": tests_cst.DEFAULT_Y_CATEGORIES,
                "sectors": builders.get_test_sectors(),
                "strategy": cst.STRATEGY_USE_BASED,
                "extension_name": "test_extension",
                "extension_categories": tests_cst.DEFAULT_EXTENSION_CATEGORIES,
            },
        )
        assert self.dataset.S_Y is spy.spy_return

    def test_set_null_data(self, mocker):
        """
        Test function 'set_null_data'

        Expected results:
            Check that the method 'set_null_data' uses the null extension data
            class and that the data is properly set
        """

        self.set_up_dataset()

        # Set up spy
        spy = mocker.spy(extension_data.NullExtensionData, "__init__")

        # Call function under test
        self.dataset.set_null_data(name=cst.S_Y)

        # Check results
        spy.assert_called_once()
        assert isinstance(self.dataset.S_Y, extension_data.NullExtensionData)

    def test_tune_from_use_based(self):
        """
        Test function 'tune'

        Expected results:
            When switching configuration, the dataset data are properly
            tuned:
                - Case 1: from USE_BASED to GROSS_OUTPUT_BASED
                - Case 2: from USE_BASED to EMBODIED_IN_IMPORT
        """
        dataset_ref_gross_output_based = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
            extension_name="test_extension",
            extension_categories=builders.get_test_extension_categories_equivalent_to_sectors(
                extension_name="test_extension",
            ),
        )
        dataset_ref_embodied_in_import = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
            extension_name="test_extension",
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
            extension_categories=builders.get_test_extension_categories_equivalent_to_sectors(
                extension_name="test_extension",
            ),
        )

        # Change configuration
        dataset_test.set_config(
            name="extension_calcul_strategy",
            value=cst.STRATEGY_GROSS_OUTPUT_BASED,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_gross_output_based)

        # CASE 2

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )
        # Change configuration
        dataset_test.set_config(
            name="extension_calcul_strategy",
            value=cst.STRATEGY_EMBODIED_IN_IMPORT,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_embodied_in_import)

    def test_tune_from_standard(self):
        """
        Test function 'tune'

        Expected results:
            When switching configuration, the dataset data are properly
            tuned:
                - Case 1: from STANDARD to EXO_INVEST_MATRIX
                - Case 2: from STANDARD to ENDO_INVEST_MATRIX
        """
        dataset_ref_exo_invest_matrix = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )
        dataset_ref_endo_invest_matrix = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
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
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
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
        dataset_ref_standard = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )
        dataset_ref_endo_invest_matrix = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
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
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
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
        dataset_ref_standard = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )
        dataset_ref_exo_invest_matrix = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
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
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )
        # Change configuration
        dataset_test.set_config(
            name="system_calcul_strategy",
            value=cst.STRATEGY_EXO_INVEST_MATRIX,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_exo_invest_matrix)

    def test_tune_from_gross_output_based(self):
        """
        Test function 'tune'

        Expected results:
            When switching configuration, the dataset data are properly
            tuned:
                - Case 1: from GROSS_OUTPUT_BASED to USE_BASED
                - Case 2: from GROSS_OUTPUT_BASED to EMBODIED_IN_IMPORT
        """
        dataset_ref_use_based = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )
        dataset_ref_embodied_in_import = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
            extension_name="test_extension",
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
            extension_name="test_extension",
        )
        # Change configuration
        dataset_test.set_config(
            name="extension_calcul_strategy",
            value=cst.STRATEGY_USE_BASED,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_use_based)

        # CASE 2

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
            extension_name="test_extension",
        )
        # Change configuration
        dataset_test.set_config(
            name="extension_calcul_strategy",
            value=cst.STRATEGY_EMBODIED_IN_IMPORT,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_embodied_in_import)

    def test_tune_from_embodied_in_import(self):
        """
        Test function 'tune'

        Expected results:
            When switching configuration, the dataset data are properly
            tuned:
                - Case 1: from EMBODIED_IN_IMPORT to USE_BASED
                - Case 2: from EMBODIED_IN_IMPORT to GROSS_OUTPUT_BASED
        """
        dataset_ref_use_based = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_USE_BASED,
            extension_name="test_extension",
        )
        dataset_ref_gross_output_based = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
            extension_name="test_extension",
        )

        # CASE 1

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
            extension_name="test_extension",
        )
        # Change configuration
        dataset_test.set_config(
            name="extension_calcul_strategy",
            value=cst.STRATEGY_USE_BASED,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_use_based)

        # CASE 2

        # Init dataset
        dataset_test = builders.build_test_extension_dataset(
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_calcul_strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
            extension_name="test_extension",
        )
        # Change configuration
        dataset_test.set_config(
            name="extension_calcul_strategy",
            value=cst.STRATEGY_GROSS_OUTPUT_BASED,
        )
        # Call function under test
        dataset_test.tune()

        assert dataset_test.equals(dataset_ref_gross_output_based)
