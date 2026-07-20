import numpy as np

from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestAData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_a().get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_a().get_structure_type()
            is structure.StructureZ
        )

    def test_calculate_from_x_and_z_no_zeros(self):
        """
        Test function `calculate` with parameters x and Z
        Expected results:
            - Check that A = Z / x_dom
        """
        a = builders.build_test_a()
        x = builders.build_test_x()
        z = builders.build_test_z()
        builders.randomize(x.df, with_zeros=False)
        builders.randomize(z.df)
        a.calculate(Z=z, x=x)

        a_ref_df = z.df / x.get_domestic_origin().squeeze()
        assert np.allclose(a.df, a_ref_df)

    def test_calculate_from_x_and_z_with_zeros(self):
        """
        Test function `calculate` with parameters x and Z

        x contains some zeros => we check that there are no remaining np.inf / -np.inf in the computed dataframe

        Expected results:
            - Check that A = Z / x_dom
        """
        a = builders.build_test_a()
        x = builders.build_test_x()
        z = builders.build_test_z()
        builders.randomize(x.df, with_zeros=True)
        builders.randomize(z.df)
        a.calculate(Z=z, x=x)

        a_ref_df = z.df / x.get_domestic_origin().squeeze()
        a_ref_df.replace(np.inf, 0.0, inplace=True)
        a_ref_df.replace(-np.inf, 0.0, inplace=True)
        assert not a.df.isin((np.inf, -np.inf)).any().any()
        assert np.allclose(a.df, a_ref_df)
