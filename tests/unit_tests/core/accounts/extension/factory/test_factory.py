import pytest

import matmat.core.accounts.extension.data.factory as factory
import matmat.utils.constants as cst
import matmat.core.accounts.extension.data.core as extension_data
import matmat.utils.errors as errors

import tests.utils.constants as tests_cst
from tests.utils import builders


class TestFactory:

    def test_make_data_nominal(self, mocker):
        """
        Test function `make_data` with a data name allowed

        Expected results:
            - Check that the instantiated data match the data name
              given as parameter
        """
        dict_of_extension_data = {
            cst.S_X_DOM: extension_data.SxDomData,
            cst.S_Y: extension_data.SyData,
            cst.S_Z: extension_data.SzData,
            cst.F_X_DOM: extension_data.FxDomData,
            cst.F_Y: extension_data.FyData,
            cst.F_Z: extension_data.FzData,
            cst.M_ROW: extension_data.MRoWData,
            cst.M: extension_data.MData,
            cst.M_K: extension_data.MKData,
            cst.D_CBA: extension_data.DCbaData,
            cst.D_CBA_K: extension_data.DCbaKData,
            cst.UNIT: extension_data.UnitExtensionData,
        }
        for key, value in dict_of_extension_data.items():

            spy_constructor = mocker.spy(value, "__init__")

            data = factory.make_data(
                name=key,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                extension_name="test_extension",
                extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
                strategy=cst.STRATEGY_USE_BASED,
            )
            assert type(data) is value

            spy_constructor.assert_called_once_with(
                data,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                extension_name="test_extension",
                extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
                strategy=cst.STRATEGY_USE_BASED,
            )

            mocker.stop(spy_constructor)

    def test_make_data_not_allowed(self):
        """
        Test function `make_data` with a data name not allowed
        as an extension data

        Expected results:
            - Check that the function raises an exception MEDataNotAllowed
        """
        with pytest.raises(errors.MEDataNotAllowed):
            factory.make_data(
                name=cst.A,
                regions=tests_cst.DEFAULT_REGIONS,
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                extension_name="test_extension",
                extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
            )
