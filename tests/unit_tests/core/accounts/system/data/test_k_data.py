import numpy as np

from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestKData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_k().get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_k().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate_from_x_and_yk_no_zeros(self):
        """
        Test function `calculate` with parameters Y_k and x
        Expected results:
            - Check that K = Y_k / x_dom
        """
        k = builders.build_test_k()
        x = builders.build_test_x()
        yk = builders.build_test_y_k()
        builders.randomize(x.df, with_zeros=False)
        builders.randomize(yk.df)
        k.calculate(Y_k=yk, x=x)

        k_ref_df = yk.df / x.get_domestic_origin().squeeze()
        assert np.allclose(k.df, k_ref_df)

    def test_calculate_from_x_and_yk_with_zeros(self):
        """
        Test function `calculate` with parameters x and Y_k

        x contains some zeros => we check that there are no remaining np.inf / -np.inf in the computed dataframe

        Expected results:
            - Check that K = Y_k / x_dom
        """
        k = builders.build_test_k()
        x = builders.build_test_x()
        yk = builders.build_test_y_k()
        builders.randomize(x.df, with_zeros=True)
        builders.randomize(yk.df)
        k.calculate(Y_k=yk, x=x)

        k_ref_df = yk.df / x.get_domestic_origin().squeeze()
        k_ref_df.replace(np.inf, 0.0, inplace=True)
        k_ref_df.replace(-np.inf, 0.0, inplace=True)
        assert not k.df.isin((np.inf, -np.inf)).any().any()
        assert np.allclose(k.df, k_ref_df)
