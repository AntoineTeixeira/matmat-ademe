import pandas as pd
import numpy as np

from matmat.core.data.strategies import structure, nature
from matmat.core.accounts.extension.data.core import FxDomData, SxDomData

from tests.utils import builders


class TestFxDomData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_f_x_dom().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_f_x_dom().get_structure_type()
            is structure.StructureSx
        )

    def test_calculate_from_s_x_dom_and_x(self):
        """
        Test function `calculate` with parameters S_x_dom and x

        Expected results:
            - Check that F_x_dom = S_x_dom * x_dom
        """
        s_x_dom: SxDomData = builders.build_test_s_x_dom()
        x = builders.build_test_x()
        f_x_dom: FxDomData = builders.build_test_f_x_dom()

        builders.randomize(x.df)
        builders.randomize(s_x_dom.df)

        f_x_dom.calculate(S_x_dom=s_x_dom, x=x)
        f_x_ref = pd.DataFrame(
            s_x_dom.df.mul(x.get_domestic_origin().squeeze(), axis=1)
        )

        assert np.allclose(f_x_dom.df, f_x_ref)
