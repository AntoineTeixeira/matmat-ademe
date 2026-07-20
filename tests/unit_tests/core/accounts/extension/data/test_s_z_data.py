import numpy as np
import pandas as pd

from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestSzData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_s_z().get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_s_z().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate(self):
        """
        Test function `calculate` with parameters F_Z and Z

        Expected results:
            - Check that S_Z = F_Z / Z
             Z contains some zeros => we check that there are no remaining np.inf / -np.inf in the computed dataframe
        """
        s_z = builders.build_test_s_z()
        z = builders.build_test_z()
        f_z = builders.build_test_f_z()

        builders.randomize(z.df, with_zeros=True)
        builders.randomize(f_z.df)

        s_z.calculate(F_Z=f_z, Z=z)
        s_z_ref = pd.DataFrame(f_z.df.div(z.df))
        s_z_ref.replace(np.inf, 0.0, inplace=True)
        s_z_ref.replace(-np.inf, 0.0, inplace=True)

        assert np.allclose(s_z.df, s_z_ref)
        assert not s_z.df.isin([np.inf, -np.inf]).any().any()
