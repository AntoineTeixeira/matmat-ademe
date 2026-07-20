import numpy as np

from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestZData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_z().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_z().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate_from_a_and_x(self):
        """
        Test function `calculate` with parameters A and x
        Expected results:
            - Check that Z = A * x_dom
        """
        z = builders.build_test_z()
        a = builders.build_test_a()
        x = builders.build_test_x()
        builders.randomize(a.df)
        builders.randomize(x.df)
        z.calculate(A=a, x=x)

        z_ref_df = a.df * x.get_domestic_origin().squeeze()
        assert np.allclose(z.df, z_ref_df)
