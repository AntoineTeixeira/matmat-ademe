import numpy as np

from matmat.core.data.strategies import structure, nature

import tests.utils.builders as builders


class TestFyData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_f_y().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_f_y().get_structure_type()
            is structure.StructureY
        )

    def test_calculate(self):
        """
        Test function calculate with parameters S_Y and Y

        Expected results:
            - Check that F_Y = S_Y * Y
        """
        f_y = builders.build_test_f_y()
        y = builders.build_test_y()
        s_y = builders.build_test_s_y()

        builders.randomize(y.df)
        builders.randomize(s_y.df)

        f_y.calculate(S_Y=s_y, Y=y)
        f_y_ref = s_y.df.mul(y.df)

        assert np.allclose(f_y.df, f_y_ref)
