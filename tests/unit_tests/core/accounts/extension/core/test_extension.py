import os
import shutil

import pytest

import matmat.utils.constants as cst
from matmat.utils.errors import MEShockExtensionInconsistency
import matmat.core.accounts.extension.data.core as data
from matmat.core.accounts.extension.core import Extension
from matmat.core.accounts.extension.dataset.core import ExtensionDataSet
from matmat.core.accounts.extension import builder as e_builder

from tests.utils import constants as tests_cst
import tests.utils.builders as builders
import tests.utils.spy as spy


class TestExtension:
    """
    Test class to test the methods of the class `Extension`
    """

    EXTENSION_NAME = "test_extension"
    PATH_TO_INIT_DIR = os.path.join(".", cst.DIR_EXTENSIONS)
    PATH_TO_TMP_DIR = os.path.join(".", "tmp_export_dir")
    # system
    system = builders.build_exo_invest_matrix_system(random=True)
    # Extension dataset
    extension_dataset: ExtensionDataSet = None

    @classmethod
    def setup_class(
        cls,
        extension_name: str = EXTENSION_NAME,
        extension_strategy: str = cst.STRATEGY_USE_BASED,
    ):
        os.makedirs(cls.PATH_TO_INIT_DIR, exist_ok=True)
        os.makedirs(cls.PATH_TO_TMP_DIR, exist_ok=True)
        if not os.path.isdir(f"{cls.PATH_TO_INIT_DIR}/{extension_name}"):
            os.mkdir(f"{cls.PATH_TO_INIT_DIR}/{extension_name}")

        cls.extension_dataset = builders.build_test_extension_dataset(
            extension_name=cls.EXTENSION_NAME,
            system_calcul_strategy=cls.system.calcul.name,
            extension_calcul_strategy=extension_strategy,
        )
        builders.randomize_dataset(cls.extension_dataset)
        cls.extension_dataset.save_to_path(
            path=f"{cls.PATH_TO_INIT_DIR}/{extension_name}",
            export_format="pickle",
        )

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.PATH_TO_INIT_DIR)
        shutil.rmtree(cls.PATH_TO_TMP_DIR)

    def test_load_from_path(self):
        """
        Test function `load_from_path`

        Expected results:
            - Check that the extension attributes are correctly initialized
        """

        extension = builders.build_use_based_extension(
            name=self.EXTENSION_NAME
        )

        # Call function under test
        extension.load_from_path(
            path=f"{self.PATH_TO_INIT_DIR}/{self.EXTENSION_NAME}"
        )

        assert extension.dataset.S_x_dom.is_null()
        assert extension.dataset.F_x_dom.is_null()
        assert extension.dataset.M_RoW.is_null()

        assert extension.dataset.S_Y.equals(self.extension_dataset.S_Y)
        assert extension.dataset.S_Z.equals(self.extension_dataset.S_Z)
        assert extension.dataset.F_Y.equals(self.extension_dataset.F_Y)
        assert extension.dataset.F_Z.equals(self.extension_dataset.F_Z)

    def test_save_to_path(self):
        """
        Test function `save_to_path`

        Expected results:
            - Check that the exported data match the exported extension
            - Also checks that computed data (M, M_k, d_cba, d_cba_k)
              are properly exported
        """

        extension_ref = builders.build_use_based_extension(
            name=self.EXTENSION_NAME
        )
        extension_ref.load_from_path(
            path=f"{self.PATH_TO_INIT_DIR}/{self.EXTENSION_NAME}"
        )

        extension_ref.calculate(system=self.system)

        if not os.path.isdir(self.PATH_TO_TMP_DIR):
            os.mkdir(self.PATH_TO_TMP_DIR)

        # Call function under test
        extension_ref.save_to_path(
            path=self.PATH_TO_TMP_DIR, export_format=cst.FORMAT_PICKLE
        )

        # Make extension from exported files
        extension_test = e_builder.get_director(reset=True).make_from_path(
            path=os.path.join(self.PATH_TO_TMP_DIR, extension_ref.name),
            load_data=True,
        )

        assert extension_test.dataset.equals(extension_ref.dataset)

    def test_reset_for_shock(self, mocker):
        """
        Test function `reset_for_shock`

        Expected results:
            - Check that the method `reset_for_shock` of the extension strategy
              is called with the correct parameters
            - Check that the multipliers and d_cba are reset
        """
        extension = builders.build_use_based_extension(
            name=self.EXTENSION_NAME
        )

        spy_strategy = mocker.spy(type(extension.calcul), "reset_for_shock")

        builders.randomize(extension.dataset.M.df)
        builders.randomize(extension.dataset.M_k.df)
        builders.randomize(extension.dataset.d_cba.df)
        builders.randomize(extension.dataset.d_cba_k.df)

        # Call function under test
        extension.reset_for_shock()

        spy_strategy.assert_called_once_with(
            extension.calcul,
            extension_dataset=extension.dataset,
        )
        assert extension.dataset.M.is_df_empty()
        assert extension.dataset.M_k.is_df_empty()
        assert extension.dataset.d_cba.is_df_empty()
        assert extension.dataset.d_cba_k.is_df_empty()

    def test_reset_fluxes(self):
        """
        Test function `reset_fluxes`

        Expected results:
            - F_x, F_xk, F_Y, F_Z shall be empty
            - M, M_k, d_cba, d_cba_k shall be empty
        """

        def check_extension(
            extension: Extension,
            list_of_data_to_check: list,
            before_reset: bool,
        ):
            for data_name in list_of_data_to_check:
                data_ = getattr(extension, data_name)
                if before_reset:
                    assert not data_.is_df_empty()
                else:
                    assert data_.is_df_empty()

        # Use based extension
        extension_use_based = builders.build_use_based_extension(
            name=self.EXTENSION_NAME, random=True
        )
        data_list = [cst.F_Y, cst.F_Z, cst.M, cst.M_K, cst.D_CBA, cst.D_CBA_K]
        check_extension(
            extension=extension_use_based,
            list_of_data_to_check=data_list,
            before_reset=True,
        )
        # Call function under test
        extension_use_based.reset_fluxes()
        check_extension(
            extension=extension_use_based,
            list_of_data_to_check=data_list,
            before_reset=False,
        )
        del extension_use_based

        # Gross output based extension
        extension_gross_output = builders.build_gross_output_based_extension(
            name=self.EXTENSION_NAME, random=True
        )
        data_list = [
            cst.F_X_DOM,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
        ]
        check_extension(
            extension=extension_gross_output,
            list_of_data_to_check=data_list,
            before_reset=True,
        )
        # Call function under test
        extension_gross_output.reset_fluxes()
        check_extension(
            extension=extension_gross_output,
            list_of_data_to_check=data_list,
            before_reset=False,
        )

    def test_reset_coefficients(self):
        """
        Test function `reset_coefficients`

        Expected results:
            - S_x, S_Y, S_Z shall be empty
            - M, M_k, d_cba, d_cba_k shall be empty
        """

        def check_extension(
            extension: Extension,
            list_of_data_to_check: list,
            before_reset: bool,
        ):
            for data_name in list_of_data_to_check:
                data_ = getattr(extension, data_name)
                if before_reset:
                    assert not data_.is_df_empty()
                else:
                    assert data_.is_df_empty()

        # Use based extension
        extension_use_based = builders.build_use_based_extension(
            name=self.EXTENSION_NAME, random=True
        )
        data_list = [cst.S_Y, cst.S_Z, cst.M, cst.M_K, cst.D_CBA, cst.D_CBA_K]
        check_extension(
            extension=extension_use_based,
            list_of_data_to_check=data_list,
            before_reset=True,
        )
        # Call function under test
        extension_use_based.reset_coefficients()
        check_extension(
            extension=extension_use_based,
            list_of_data_to_check=data_list,
            before_reset=False,
        )
        del extension_use_based

        # Gross output based extension
        extension_gross_output = builders.build_gross_output_based_extension(
            name=self.EXTENSION_NAME, random=True
        )
        data_list = [
            cst.S_X_DOM,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
        ]
        check_extension(
            extension=extension_gross_output,
            list_of_data_to_check=data_list,
            before_reset=True,
        )
        # Call function under test
        extension_gross_output.reset_coefficients()
        check_extension(
            extension=extension_gross_output,
            list_of_data_to_check=data_list,
            before_reset=False,
        )

    def test_calculate(self, mocker):
        """
        Test function `calculate`

        Expected results:
            - The method `calculate` is called with the correct arguments
            - The method `calculate_m` is called with the correct arguments
            - The method `calculate_mk` is called with the correct arguments
            - The method `calculate_d_cba` is called with the correct arguments
            - The method `calculate_d_cba_k` is called with the correct
              arguments
        """

        def execute_test(extension: Extension, strategy_class):
            spy_calculate = mocker.spy(strategy_class, "calculate")
            spy_calculate_m = mocker.spy(strategy_class, "calculate_m")
            spy_calculate_mk = mocker.spy(strategy_class, "calculate_mk")
            spy_calculate_d_cba = mocker.spy(strategy_class, "calculate_d_cba")
            spy_calculate_d_cba_k = mocker.spy(
                strategy_class, "calculate_d_cba_k"
            )

            # Call function under test
            extension.calculate(system=self.system)

            spy_calculate.assert_called_once_with(
                extension.calcul,
                system_dataset=self.system.dataset,
                extension_dataset=extension.dataset,
            )
            spy_calculate_m.assert_called_once_with(
                extension.calcul,
                system_dataset=self.system.dataset,
                extension_dataset=extension.dataset,
            )
            spy_calculate_mk.assert_called_once_with(
                extension.calcul,
                system_dataset=self.system.dataset,
                extension_dataset=extension.dataset,
            )
            spy_calculate_d_cba.assert_called_once_with(
                extension.calcul,
                system_dataset=self.system.dataset,
                extension_dataset=extension.dataset,
            )
            spy_calculate_d_cba_k.assert_called_once_with(
                extension.calcul,
                system_dataset=self.system.dataset,
                extension_dataset=extension.dataset,
            )

            mocker.stop(spy_calculate)
            mocker.stop(spy_calculate_m)
            mocker.stop(spy_calculate_mk)
            mocker.stop(spy_calculate_d_cba)
            mocker.stop(spy_calculate_d_cba_k)

        # Execute test
        my_extension = builders.build_use_based_extension(
            name=self.EXTENSION_NAME,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )
        my_extension.load_from_path(
            path=f"{self.PATH_TO_INIT_DIR}/{my_extension.name}"
        )
        execute_test(my_extension, type(my_extension.calcul))

    def test_shock_s_x(self, mocker):
        """
        Test function `shock` with shock data dS_x

        Expected results:
            - The `shock` method of SxDomData is called with the correct arguments
        """
        spy_s_x_shock = mocker.spy(data.SxDomData, "shock")

        extension = builders.build_gross_output_based_extension(
            name=self.EXTENSION_NAME
        )
        extension_shock = builders.build_extension_shock_only_s_x(
            extension=extension
        )
        builders.randomize_dataset(extension_shock.dataset)

        extension.reset_for_shock()
        extension.shock(shock=extension_shock)

        spy.check_specific_call_with_args(
            function_spy=spy_s_x_shock,
            call_number=1,
            args=[extension.dataset.S_x_dom],
            kwargs={"shock_data": extension_shock.dS_x_dom},
        )

    def test_shock_s_y(self, mocker):
        """
        Test function `shock` with shock data dS_Y

        Expected results:
            - The `shock` method of SyData is called with the correct
              arguments
        """
        spy_s_y_shock = mocker.spy(data.SyData, "shock")

        extension = builders.build_use_based_extension(
            name=self.EXTENSION_NAME
        )
        extension_shock = builders.build_extension_shock_only_s_y(
            extension=extension
        )
        builders.randomize_dataset(extension_shock.dataset)

        extension.reset_for_shock()
        extension.shock(shock=extension_shock)

        spy_s_y_shock.assert_called_once_with(
            extension.dataset.S_Y, shock_data=extension_shock.dataset.dS_Y
        )

    def test_shock_s_z(self, mocker):
        """
        Test function `shock` with shock data dS_Z

        Expected results:
            - The `shock` method of SzData is called with the correct
              arguments
        """
        spy_s_z_shock = mocker.spy(data.SzData, "shock")

        extension = builders.build_use_based_extension(
            name=self.EXTENSION_NAME
        )
        extension_shock = builders.build_extension_shock_only_s_z(
            extension=extension
        )
        builders.randomize_dataset(extension_shock.dataset)

        extension.reset_for_shock()
        extension.shock(shock=extension_shock)

        spy_s_z_shock.assert_called_once_with(
            extension.dataset.S_Z, shock_data=extension_shock.dataset.dS_Z
        )

    def test_shock_inconsistent_extension_names(self):
        """
        Test function `shock` with a shock wrongly named

        Expected results:
            - Raises an exception MEShockExtensionInconsistency
        """
        extension = builders.build_use_based_extension(self.EXTENSION_NAME)
        extension_shock = builders.build_extension_shock(extension)
        extension_test = builders.build_use_based_extension(
            "other_test_extension"
        )

        with pytest.raises(MEShockExtensionInconsistency):
            extension_test.shock(extension_shock)

    def test_aggregate(
        self,
        mocker,
        extension_use_based_3,
        bridge_sectors_from_3_to_1,
        bridge_regions_from_3_to_1,
        bridge_fdc_from_3_to_1,
        bridge_ext_cats_from_3_to_1,
    ):
        """
        Test function `aggregate` with various bridges

        Expected results:
            - Check that the methods `aggregate` of data classes are
              called with the proper arguments
        """
        extension = extension_use_based_3.copy()

        # Set uniform unit to avoid error raised when checking aggregation
        # consistency with unit vector
        extension.dataset.unit.set_values("kT")

        # Set up spies
        spy_dataset = mocker.spy(ExtensionDataSet, "aggregate")

        # Call method under test
        extension.aggregate(
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_fdc_from_3_to_1,
            bridge_ext_cats_from_3_to_1,
            match_extension_name=False,
        )

        # Check calls
        spy_dataset.assert_called_once_with(
            extension.dataset,
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_fdc_from_3_to_1,
            bridge_ext_cats_from_3_to_1,
        )

    def test_aggregate_wrt_extension_name(
        self,
        mocker,
        extension_use_based_3,
        bridge_sectors_from_3_to_1,
        bridge_regions_from_3_to_1,
        bridge_fdc_from_3_to_1,
        bridge_ext_cats_from_3_to_1,
    ):
        """
        Test function `aggregate`

        Expected results:
            - If match_extension_name is True:
                - Nothing happens if the bridge extension name does not match
                - The extension is aggregated if the bridge extension name
                  match
            - Else the extension name does not matter
        """
        extension = extension_use_based_3.copy()

        # Prepare extension categories bridges
        bridge_ext_cats_valid = bridge_ext_cats_from_3_to_1.copy()
        bridge_ext_cats_valid.sheet_name = extension.name
        bridge_ext_cats_invalid = bridge_ext_cats_from_3_to_1.copy()

        # Set uniform unit to avoid error raised when checking aggregation
        # consistency with unit vector
        extension.dataset.unit.set_values("kT")

        # Set up spies
        spy_dataset = mocker.spy(ExtensionDataSet, "aggregate")

        # Call method under test
        extension.aggregate(
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_fdc_from_3_to_1,
            bridge_ext_cats_valid,
            bridge_ext_cats_invalid,
            match_extension_name=True,
        )

        # Check calls
        spy_dataset.assert_called_once_with(
            extension.dataset,
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_fdc_from_3_to_1,
            bridge_ext_cats_valid,
        )

    def test_disaggregate(
        self,
        extension_use_based_3,
        bridge_sectors_from_3_to_1,
    ):
        """
        Test function `disaggregate`

        Expected results:
            - Check that the method returns an exception as it is not
              implemented yet
        """
        extension = extension_use_based_3.copy()

        with pytest.raises(NotImplementedError):
            extension.disaggregate(bridge_sectors_from_3_to_1)
