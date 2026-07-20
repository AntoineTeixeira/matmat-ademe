import numpy as np
import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.data.strategies import structure, nature
from matmat.core.accounts.extension.data.core import SxDomData, FxDomData
from matmat.core.shocks.mixins import ShockableMixin
import matmat.utils.constants as cst
from tests.utils import builders, constants as tests_cst


class TestSxDomData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert (
            builders.build_test_s_x_dom().get_nature_type()
            is nature.Coefficient
        )

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        # Case 1
        assert (
            builders.build_test_s_x_dom().get_structure_type()
            is structure.StructureSx
        )

    def test_calculate_from_f_x_dom_and_x(self):
        """
        Test function `calculate` with parameters F_x_dom and x

        Expected results:
            - Check that S_x_dom = F_x_dom / x_dom
              x contains some zeros => we check that there are no
              remaining np.inf / -np.inf in the computed dataframe
        """
        s_x_dom: SxDomData = builders.build_test_extension_data(
            name=cst.S_X_DOM,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
        )
        x = builders.build_test_x()
        f_x_dom: FxDomData = builders.build_test_extension_data(
            name=cst.F_X_DOM,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
        )

        builders.randomize(x.df, with_zeros=True)
        builders.randomize(f_x_dom.df)

        s_x_dom.calculate(F_x_dom=f_x_dom, x=x)
        s_x_ref = pd.DataFrame(
            f_x_dom.df.div(x.get_domestic_origin().squeeze(), axis=1)
        )
        s_x_ref.replace(np.inf, 0.0, inplace=True)
        s_x_ref.replace(-np.inf, 0.0, inplace=True)

        assert np.allclose(s_x_dom.df, s_x_ref)
        assert not s_x_dom.df.isin([np.inf, -np.inf]).any().any()

    def test_shock_1(self):
        """
        Test method 'shock'.
        In this test case, the shock data has only one row.

        Expected results:
            - Each row of S_x_dom is multiplied by (1 + the row
              of dS_x_dom)
        """
        ds_x_dom = builders.build_test_extension_shock_data(
            name=cst.D_S_X_DOM,
            extension_categories=dl.ExtensionCategoriesDL(
                extension_name="test_extension",
                df=pd.DataFrame({cst.IDX_PERIMETER: ["ghg_emissions"]}),
            ),
        )

        builders.randomize(df=ds_x_dom.df)

        s_x_dom = builders.build_test_extension_data(name=cst.S_X_DOM)
        builders.randomize(df=s_x_dom.df)

        s_x_ref = s_x_dom.df.mul(1 + ds_x_dom.df.squeeze(), axis=1)
        s_x_dom.shock(shock_data=ds_x_dom)

        assert np.allclose(s_x_dom.df, s_x_ref)

    def test_shock_2(self, mocker):
        """
        Test method 'shock'.
        In this test case, the shock data has the same rows index than
        the data to shock

        Expected results:
            - The 'shock' method of ShockableMixin shall be called with the
              correct arguments
        """
        ds_x_dom = builders.build_test_extension_shock_data(
            name=cst.D_S_X_DOM,
        )
        builders.randomize(df=ds_x_dom.df)

        s_x_dom = builders.build_test_extension_data(name=cst.S_X_DOM)
        builders.randomize(df=s_x_dom.df)

        spy_shock = mocker.spy(ShockableMixin, "shock")

        s_x_dom.shock(shock_data=ds_x_dom)

        spy_shock.assert_called_once_with(self=s_x_dom, shock_data=ds_x_dom)
