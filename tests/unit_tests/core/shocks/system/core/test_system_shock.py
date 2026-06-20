import pytest
import os
import shutil
import numpy as np

from matmat.core.shocks.system.dataset.core import SystemShockDataSet
import matmat.utils.constants as cst

from tests.utils import builders, constants as tests_cst


class TestSystemShock:
    """
    Test class to test the class SystemShock
    """

    PATH_TO_INIT_DIR = f"./{cst.DIR_SHOCKS}"
    PATH_TO_INIT_DIR_SYSTEM = f"{PATH_TO_INIT_DIR}/{cst.DIR_SYSTEM}"

    system_shock_dataset = builders.build_test_system_shock_dataset()

    @classmethod
    def setup_class(cls):

        if not os.path.isdir(cls.PATH_TO_INIT_DIR):
            os.mkdir(cls.PATH_TO_INIT_DIR)
            os.mkdir(cls.PATH_TO_INIT_DIR_SYSTEM)

        builders.randomize_dataset(cls.system_shock_dataset)
        cls.system_shock_dataset.save_to_path(
            path=cls.PATH_TO_INIT_DIR_SYSTEM,
            export_format="pickle",
        )

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.PATH_TO_INIT_DIR)

    def test_load_from_path(self):
        """
        Test function `load_from_path`

        Expected results:
            - Test that the data composing the shock are the same as the data exported
        """
        system_shock = builders.build_system_shock()
        system_shock.load_from_path(path=f"{self.PATH_TO_INIT_DIR_SYSTEM}")

        assert system_shock.dataset.equals(self.system_shock_dataset)

    def test_init_from_exports_growth(self):
        """
        Test function `init_from_exports_growth`

        Expected results:
            - Check that domestic exports column of dY is computed correctly
            - Check that the other columns of dY are set to 0.0
            - Check that import part of dY is 0.0
        """
        system_shock = builders.build_system_y_shock()

        x_new = builders.build_test_x()
        builders.randomize(x_new.df)
        x_ref = builders.build_test_x()
        builders.randomize(x_ref.df, with_zeros=True)

        system_shock.init_from_exports_growth(
            x_new=x_new.get_domestic_origin(),
            x_ref=x_ref.get_domestic_origin(),
        )

        growth = (
            x_new.get_domestic_origin().div(x_ref.get_domestic_origin()) - 1
        )
        growth = growth.replace([np.nan, np.inf, -np.inf], 0.0)

        assert np.allclose(
            system_shock.dataset.dY.get_domestic_origin().xs(
                cst.IDX_EXPORTS, level=1, axis=1
            ),
            growth,
        )
        assert np.allclose(
            system_shock.dataset.dY.get_domestic_origin().drop(
                columns=[cst.IDX_EXPORTS], level=1
            ),
            0.0,
        )
        assert np.allclose(
            system_shock.dataset.dY.get_import_origin().values, 0.0
        )

    def test_inject_shock(self):
        """
        Test method `inject_shock`

        Expected results:
            - Check that the shock is injected properly
        """
        system_shock_1 = builders.build_system_shock()
        builders.randomize(system_shock_1.dataset.dY.df)
        builders.randomize(system_shock_1.dataset.dA.df)

        system_shock_2 = builders.build_system_shock()
        system_shock_2.dataset.dY.set_values(1.0)
        system_shock_2.dataset.dA.set_values(0.0)

        assert not system_shock_1.dataset.dY.equals(system_shock_2.dataset.dY)
        assert not system_shock_1.dataset.dA.equals(system_shock_2.dataset.dA)

        system_shock_1.inject_shock(shock=system_shock_2, inject_zeros=False)
        assert system_shock_1.dataset.dY.equals(system_shock_2.dataset.dY)
        assert not system_shock_1.dataset.dA.equals(system_shock_2.dataset.dA)

        system_shock_1.inject_shock(shock=system_shock_2, inject_zeros=True)
        assert system_shock_1.dataset.dY.equals(system_shock_2.dataset.dY)
        assert system_shock_1.dataset.dA.equals(system_shock_2.dataset.dA)

    def test_disaggregate(
        self,
        mocker,
        system_shock_standard_1,
        bridge_sectors_from_1_to_3,
        bridge_regions_from_1_to_3,
        bridge_fdc_from_1_to_3,
    ):
        """
        Test function `disaggregate` with various bridges

        Expected results:
            - Check that the methods `disaggregate` of dataset is called
              with the proper arguments
        """
        shock = system_shock_standard_1.copy()

        # Set up spies
        spy_dataset = mocker.spy(SystemShockDataSet, "disaggregate")

        # Call method under test
        shock.disaggregate(
            bridge_sectors_from_1_to_3,
            bridge_regions_from_1_to_3,
            bridge_fdc_from_1_to_3,
        )

        # Check calls
        spy_dataset.assert_called_once_with(
            shock.dataset,
            bridge_sectors_from_1_to_3,
            bridge_regions_from_1_to_3,
            bridge_fdc_from_1_to_3,
        )

    def test_aggregate(
        self,
        system_shock_standard_1,
        bridge_sectors_from_1_to_3,
        bridge_regions_from_1_to_3,
        bridge_fdc_from_1_to_3,
    ):
        """
        Test function `aggregate` with various bridges

        Expected results:
            - An exception is raised
        """
        shock = system_shock_standard_1.copy()

        # Call method under test
        with pytest.raises(NotImplementedError):
            shock.aggregate(
                bridge_sectors_from_1_to_3,
                bridge_regions_from_1_to_3,
                bridge_fdc_from_1_to_3,
            )
