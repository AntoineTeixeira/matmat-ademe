import numpy as np
from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestLKData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_l_k().get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_l_k().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate_from_a_and_k(self):
        """
        Test function `calculate` with parameters A and K
        Expected results:
            - Check that L = inv(I-(A+K))
        """
        lk = builders.build_test_l_k()
        a = builders.build_test_a()
        k = builders.build_test_k()
        builders.randomize(a.df)
        builders.randomize(k.df)
        lk.calculate(A=a, K=k)

        i = np.eye(a.get_domestic_origin().shape[0])

        lk_ref_df_dom = np.linalg.inv(
            i - (a.get_domestic_origin() + k.get_domestic_origin()).values
        )
        assert np.allclose(lk.get_domestic_origin(), lk_ref_df_dom)

        assert np.isin(lk.get_import_origin(), 0.0).all().all()
