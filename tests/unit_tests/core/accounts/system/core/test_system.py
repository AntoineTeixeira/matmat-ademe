import os.path
import shutil

import pytest

from matmat.core.accounts.system.core import System
from matmat.core.accounts.system.dataset.core import SystemDataSet
from matmat.core.accounts.system import builder as s_builder
import matmat.core.accounts.system.data.core as data
from matmat.core.accounts.system.strategies import calcul
import matmat.utils.constants as cst

import tests.utils.builders as builders
from tests.utils import constants as tests_cst


class TestSystem:
    """
    Test class to test the methods of the class `System`
    """

    PATH_TO_INIT_DIR = os.path.join(".", cst.DIR_SYSTEM)
    PATH_TO_TMP_DIR = os.path.join(".", "tmp_export_dir")
    system_dataset: SystemDataSet = None

    @classmethod
    def setup_class(cls):
        os.makedirs(cls.PATH_TO_INIT_DIR, exist_ok=True)
        os.makedirs(cls.PATH_TO_TMP_DIR, exist_ok=True)

        cls.system_dataset = builders.build_test_system_dataset(
            calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
        )
        builders.randomize_dataset(cls.system_dataset)
        cls.system_dataset.save_to_path(
            path=f"{cls.PATH_TO_INIT_DIR}",
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
            - Check that the system attributes are correctly initialized
        """

        system = builders.build_exo_invest_matrix_system()
        system.load_from_path(path=self.PATH_TO_INIT_DIR)

        assert system.dataset.A.df.equals(self.system_dataset.A.df)
        assert system.dataset.L.df.equals(self.system_dataset.L.df)
        assert system.dataset.x.df.equals(self.system_dataset.x.df)
        assert system.dataset.Y.df.equals(self.system_dataset.Y.df)
        assert system.dataset.Z.df.equals(self.system_dataset.Z.df)
        assert system.dataset.K.df.equals(self.system_dataset.K.df)
        assert system.dataset.L_k.df.equals(self.system_dataset.L_k.df)
        assert system.dataset.Y_k.df.equals(self.system_dataset.Y_k.df)

    def test_save_to_path(self):
        """
        Test function `save_to_path`

        Expected results:
            - Check that the exported data match the exported system
        """

        system_ref = builders.build_exo_invest_matrix_system()
        system_ref.load_from_path(path=self.PATH_TO_INIT_DIR)

        system_ref.calculate()

        # Call function under test
        system_ref.save_to_path(
            path=self.PATH_TO_TMP_DIR, export_format=cst.FORMAT_PICKLE
        )

        # Make system from exported files
        system_test = s_builder.get_director(reset=True).make_from_path(
            path=self.PATH_TO_TMP_DIR,
            load_data=True,
        )

        assert system_test.dataset.equals(system_ref.dataset)

    def test_export(self):
        """
        Test function `export`

        Expected results:
            - Check that the exported data match the exported system
        """

        system_ref = builders.build_exo_invest_matrix_system()
        system_ref.load_from_path(path=self.PATH_TO_INIT_DIR)

        test_export_dir = "./tmp_export_dir"
        if not os.path.isdir(test_export_dir):
            os.mkdir(test_export_dir)
        system_ref.save_to_path(
            path=test_export_dir, export_format=cst.FORMAT_PICKLE
        )

        system_test = builders.build_exo_invest_matrix_system()
        system_test.load_from_path(path=test_export_dir)

        assert system_test.dataset.A.equals(system_ref.dataset.A)
        assert system_test.dataset.L.equals(system_ref.dataset.L)
        assert system_test.dataset.x.equals(system_ref.dataset.x)
        assert system_test.dataset.Y.equals(system_ref.dataset.Y)
        assert system_test.dataset.Z.equals(system_ref.dataset.Z)
        assert system_test.dataset.K.equals(system_ref.dataset.K)
        assert system_test.dataset.L_k.equals(system_ref.dataset.L_k)
        assert system_test.dataset.Y_k.equals(system_ref.dataset.Y_k)

    def test_reset_for_shock(self):
        """
        Test function `reset_for_shock`

        Expected results:
            - x, Z, L, K, L_k empty
            - A, Y, Y_k not empty
        """

        system = builders.build_exo_invest_matrix_system()
        system.load_from_path(path=self.PATH_TO_INIT_DIR)
        system.reset_for_shock()

        assert system.dataset.x.is_df_empty()
        assert system.dataset.Z.is_df_empty()
        assert system.dataset.L.is_df_empty()
        assert system.dataset.K.is_df_empty()
        assert system.dataset.L_k.is_df_empty()

        assert not system.dataset.A.is_df_empty()
        assert not system.dataset.Y.is_df_empty()
        assert not system.dataset.Y_k.is_df_empty()

    def test_reset_fluxes(self):
        """
        Test function `reset_fluxes`

        Expected results:
            - x, Z, L, K, L_k empty
            - A, Y, Y_k not empty
        """

        system = builders.build_exo_invest_matrix_system()
        system.load_from_path(path=self.PATH_TO_INIT_DIR)
        system.reset_fluxes()

        assert system.dataset.x.is_df_empty()
        assert system.dataset.Z.is_df_empty()
        assert system.dataset.Y.is_df_empty()
        assert system.dataset.Y_k.is_df_empty()

        assert not system.dataset.L.is_df_empty()
        assert not system.dataset.K.is_df_empty()
        assert not system.dataset.L_k.is_df_empty()
        assert not system.dataset.A.is_df_empty()

    def test_reset_coefficients(self):
        """
        Test function `reset_coefficients`

        Expected results:
            - A, L, K, L_k empty
            - x, Z, Y, Y_k not empty
        """

        system = builders.build_exo_invest_matrix_system()
        system.load_from_path(path=self.PATH_TO_INIT_DIR)
        system.reset_coefficients()

        assert system.dataset.A.is_df_empty()
        assert system.dataset.L.is_df_empty()
        assert system.dataset.K.is_df_empty()
        assert system.dataset.L_k.is_df_empty()

        assert not system.dataset.x.is_df_empty()
        assert not system.dataset.Z.is_df_empty()
        assert not system.dataset.Y.is_df_empty()
        assert not system.dataset.Y_k.is_df_empty()

    def test_calculate(self, mocker):
        """
        Test functions `calculate`, `calculate_from_fluxes`, `calculate_from_leontief`

        Expected results:
            For each strategy:
                - (1) x, Y and Z are not empty.
                Check that the method `calculate_from_fluxes` of the strategy class is called with the correct arguments
                - (2) A and Y are not empty.
                Check that the method `calculate_from_leontief` of the strategy class is called with the correct arguments
        """

        def execute_test(system: System, strategy_class):
            spy_strategy_from_fluxes = mocker.spy(
                strategy_class, "calculate_from_fluxes"
            )
            spy_system_from_fluxes = mocker.spy(
                System, "calculate_from_fluxes"
            )
            spy_strategy_from_leontief = mocker.spy(
                strategy_class, "calculate_from_leontief"
            )
            spy_system_from_leontief = mocker.spy(
                System, "calculate_from_leontief"
            )

            # (1)
            builders.randomize(system.dataset.x.df, full_randomization=False)
            builders.randomize(system.dataset.Y.df, full_randomization=False)
            builders.randomize(system.dataset.Z.df, full_randomization=False)
            if not system.is_standard():
                builders.randomize(
                    system.dataset.Y_k.df, full_randomization=False
                )
            system.calculate()

            spy_system_from_fluxes.assert_called_once()
            spy_strategy_from_fluxes.assert_called_once_with(
                system.calcul,
                system_dataset=system.dataset,
            )

            # (2)
            system.dataset.x.reset()
            system.dataset.Z.reset()

            system.calculate()

            spy_system_from_leontief.assert_called_once()
            spy_strategy_from_leontief.assert_called_once_with(
                system.calcul,
                system_dataset=system.dataset,
            )

            mocker.stop(spy_system_from_fluxes)
            mocker.stop(spy_strategy_from_fluxes)
            mocker.stop(spy_system_from_leontief)
            mocker.stop(spy_strategy_from_leontief)

        execute_test(builders.build_standard_system(), calcul.Standard)
        execute_test(
            builders.build_exo_invest_matrix_system(),
            calcul.ExoInvestMatrix,
        )
        execute_test(
            builders.build_endo_invest_matrix_system(),
            calcul.EndoInvestMatrix,
        )

    def test_shock(self, mocker):
        """
        Test function `shock`

        Expected results:
            - The `shock` method of the shocked data are called with the correct arguments
        """
        system_shock = builders.build_system_shock()
        builders.randomize_dataset(system_shock.dataset)

        spy_a_shock = mocker.spy(data.AData, "shock")
        spy_k_shock = mocker.spy(data.KData, "shock")
        spy_y_shock = mocker.spy(data.YData, "shock")
        spy_yk_shock = mocker.spy(data.YKData, "shock")
        spy_z_shock = mocker.spy(data.ZData, "shock")

        system = builders.build_exo_invest_matrix_system()
        system.shock(shock=system_shock)

        spy_a_shock.assert_called_once_with(
            system.dataset.A,
            shock_data=system_shock.dataset.dA,
        )
        spy_k_shock.assert_called_once_with(
            system.dataset.K,
            shock_data=system_shock.dataset.dK,
        )
        spy_y_shock.assert_called_once_with(
            system.dataset.Y,
            shock_data=system_shock.dataset.dY,
            system_calcul_strategy=system.calcul.name,
        )
        spy_yk_shock.assert_called_once_with(
            system.dataset.Y_k,
            shock_data=system_shock.dataset.dY_k,
        )
        spy_z_shock.assert_called_once_with(
            system.dataset.Z,
            shock_data=system_shock.dataset.dZ,
        )

    def test_is_standard(self):
        """
        Test function `is_standard`

        Expected results:
            - (1) With a standard system, returns True
            - (2) With an exo_invest_matrix system, returns False
        """
        system = builders.build_standard_system()
        assert system.is_standard()

        system = builders.build_exo_invest_matrix_system()
        assert not system.is_standard()

    def test_aggregate(
        self,
        mocker,
        system_exo_3,
        bridge_sectors_from_3_to_1,
        bridge_regions_from_3_to_1,
        bridge_fdc_from_3_to_1,
    ):
        """
        Test function `aggregate` with various bridges

        Expected results:
            - Check that the methods `aggregate` of data classes are called
              with the proper arguments
        """
        system = system_exo_3.copy()

        # Set uniform unit to avoid error raised when checking aggregation
        # consistency with unit vector
        system.dataset.unit.set_values("kT")

        # Set up spies
        spy_dataset = mocker.spy(SystemDataSet, "aggregate")

        # Call method under test
        system.aggregate(
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_fdc_from_3_to_1,
        )

        # Check calls
        spy_dataset.assert_called_once_with(
            system.dataset,
            bridge_sectors_from_3_to_1,
            bridge_regions_from_3_to_1,
            bridge_fdc_from_3_to_1,
        )

    def test_disaggregate(
        self,
        system_exo_3,
        bridge_sectors_from_3_to_1,
    ):
        """
        Test function `disaggregate`

        Expected results:
            - Check that the method returns an exception as it is not
              implemented yet
        """
        system = system_exo_3.copy()

        with pytest.raises(NotImplementedError):
            system.disaggregate(bridge_sectors_from_3_to_1)
