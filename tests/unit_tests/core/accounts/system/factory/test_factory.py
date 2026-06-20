import pytest

import matmat.core.accounts.system.data.factory as factory
import matmat.utils.constants as cst
import matmat.core.accounts.system.data.core as system_data
import matmat.utils.errors as errors

import tests.utils.constants as tests_cst
import tests.utils.builders as builders


class TestFactory:

    def test_make_data_nominal(self, mocker):
        """
        Test function `make_data` with a data name allowed

        Expected results:
            - Check that the instantiated data match the data name given
              as parameter
        """
        dict_of_system_data = {
            cst.A: system_data.AData,
            cst.K: system_data.KData,
            cst.L: system_data.LData,
            cst.L_K: system_data.LKData,
            cst.X: system_data.XData,
            cst.Y: system_data.YData,
            cst.Y_K: system_data.YKData,
            cst.Z: system_data.ZData,
            cst.UNIT: system_data.UnitSystemData,
        }
        for key, value in dict_of_system_data.items():

            spy_constructor = mocker.spy(value, "__init__")

            data = factory.make_data(
                name=key,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
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

    def test_make_data_not_allowed(self):
        """
        Test function `make_data` with a data name not allowed as a system data

        Expected results:
            - Check that the function raises an exception MEDataNotAllowed
        """
        with pytest.raises(errors.MEDataNotAllowed):
            factory.make_data(
                name=cst.S_Y,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            )
