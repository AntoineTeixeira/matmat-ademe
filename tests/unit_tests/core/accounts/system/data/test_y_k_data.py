import numpy as np

from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestYKData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_y_k().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_y_k().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate_from_k_and_x(self):
        """
        Test function `calculate` with parameters K and x
        Expected results:
            - Check that Y_k = K * x_dom
        """
        yk = builders.build_test_y_k()
        x = builders.build_test_x()
        k = builders.build_test_k()
        builders.randomize(x.df)
        builders.randomize(k.df)
        yk.calculate(x=x, K=k)

        yk_ref_df = k.df * x.get_domestic_origin().squeeze()
        assert np.allclose(yk.df, yk_ref_df)
