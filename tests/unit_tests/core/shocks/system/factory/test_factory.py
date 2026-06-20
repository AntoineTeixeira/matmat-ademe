import pytest

import matmat.core.shocks.system.data.factory as factory
import matmat.utils.constants as cst
import matmat.core.shocks.system.data.core as sys_shock_data
import matmat.utils.errors as errors

import tests.utils.constants as tests_cst
from tests.utils import builders


class TestFactory:

    def test_build_system_shock_data_nominal(self, mocker):
        """
        Test function `build_system_shock_data` with a data name allowed

        Expected results:
            - Check that the instantiated data match the data name given as
              parameter
        """
        dict_of_shock_data = {
            cst.D_A: sys_shock_data.AShockData,
            cst.D_K: sys_shock_data.KShockData,
            cst.D_Y: sys_shock_data.YShockData,
            cst.D_Y_K: sys_shock_data.YkShockData,
            cst.D_Z: sys_shock_data.ZShockData,
        }
        for key, value in dict_of_shock_data.items():

            spy_constructor = mocker.spy(value, "__init__")

            data = factory.make_data(
                name=key,
                sectors=builders.get_test_sectors(),
                regions=tests_cst.DEFAULT_REGIONS,
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            )
            assert type(data) is value

            spy_constructor.assert_called_once_with(
                data,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            )

            mocker.stop(spy_constructor)

    def test_build_system_shock_data_disallowed_data(self):
        """
        Test function `build_system_shock_data` with a data not allowed as a
        shock data

        Expected results:
            - Check that the function raises an exception MEDataNotAllowed
        """
        with pytest.raises(errors.MEDataNotAllowed):
            factory.make_data(
                name=cst.D_S_X_DOM,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            )
