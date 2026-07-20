import numpy as np
from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestLData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_l().get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_l().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate_from_a(self):
        """
        Test function `calculate` with parameters A
        Expected results:
            - Check that L = inv(I-A)
        """
        l = builders.build_test_l()
        a = builders.build_test_a()
        builders.randomize(a.df)
        l.calculate(A=a)

        i = np.eye(a.get_domestic_origin().shape[0])

        l_ref_df_dom = np.linalg.inv(i - a.get_domestic_origin().values)
        assert np.allclose(l.get_domestic_origin(), l_ref_df_dom)

        if l.structure.has_import_regions():
            assert np.isin(l.get_import_origin(), 0.0).all().all()
