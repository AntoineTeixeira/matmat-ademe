import numpy as np

from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestFzData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_f_z().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_f_z().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate(self):
        """
        Test function calculate with parameters S_Z and Z

        Expected results:
            - Check that F_Z = S_Z * Z
        """
        f_z = builders.build_test_f_z()
        z = builders.build_test_z()
        s_z = builders.build_test_s_z()

        builders.randomize(z.df)
        builders.randomize(s_z.df)

        f_z.calculate(S_Z=s_z, Z=z)
        f_z_ref = s_z.df.mul(z.df)

        assert np.allclose(f_z.df, f_z_ref)
