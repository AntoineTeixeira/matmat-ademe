import pytest

import matmat.core.shocks.extension.data.factory as factory
import matmat.utils.constants as cst
import matmat.core.shocks.extension.data.core as ext_shock_data
import matmat.utils.errors as errors

import tests.utils.constants as tests_cst
from tests.utils import builders


class TestFactory:

    def test_build_extension_shock_data_nominal(self, mocker):
        """
        Test function `build_extensions_shock_data`

        Expected results:
            - Check that the instantiated data match the data name given
              as parameter
        """
        dict_of_shock_data = {
            cst.D_S_X_DOM: ext_shock_data.SxDomShockData,
            cst.D_S_Y: ext_shock_data.SyShockData,
            cst.D_S_Z: ext_shock_data.SzShockData,
            cst.D_M_ROW: ext_shock_data.MRoWShockData,
        }
        for key, value in dict_of_shock_data.items():

            # Spy __init__ method of data class
            spy_constructor = mocker.spy(value, "__init__")

            data = factory.make_data(
                name=key,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
                extension_name="test_extension",
            )
            assert type(data) is value

            spy_constructor.assert_called_once_with(
                data,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                extension_name="test_extension",
                extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
            )

            mocker.stop(spy_constructor)

    def test_build_extension_shock_data_disallowed_data(self):
        """
        Test function `build_extension_shock_data` with a data not allowed as a shock data

        Expected results:
            - Check that the function raises an exception MEDataNotAllowed
        """
        with pytest.raises(errors.MEDataNotAllowed):
            factory.make_data(
                name=cst.D_A,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                extension_name="test_extension",
                extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
            )
