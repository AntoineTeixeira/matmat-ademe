import numpy as np
import pandas as pd

from matmat.core.data.strategies import structure, nature
import matmat.utils.constants as cst
import tests.utils.builders as builders


class TestSyData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert (
            builders.build_test_s_y().get_nature_type() is nature.Coefficient
        )

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_s_y().get_structure_type()
            is structure.StructureY
        )

    def test_calculate(self):
        """
        Test function `calculate` with parameters F_Y and Y

        Expected results:
            - Check that S_Y = F_Y / Y
             Y contains some zeros => we check that there are no remaining np.inf / -np.inf in the computed dataframe
        """
        s_y = builders.build_test_s_y()
        y = builders.build_test_y()
        f_y = builders.build_test_f_y()

        builders.randomize(y.df, with_zeros=True)
        builders.randomize(f_y.df)

        s_y.calculate(F_Y=f_y, Y=y)
        s_y_ref = pd.DataFrame(f_y.df.div(y.df))
        s_y_ref.replace(np.inf, 0.0, inplace=True)
        s_y_ref.replace(-np.inf, 0.0, inplace=True)

        assert np.allclose(s_y.df, s_y_ref)
        assert not s_y.df.isin([np.inf, -np.inf]).any().any()

    def test_get_gfcf_column(self):
        """
        Test functions `get_gfcf_column`
        Expected results:
            - The column retrieved has the expected values
        """
        s_y = builders.build_test_s_y()
        y = builders.build_test_y()
        gfcf = pd.DataFrame(
            index=s_y.df.index,
            columns=[
                (
                    s_y.get_domestic_regions_list()[0],
                    cst.IDX_INVESTMENT,
                    cst.IDX_INVESTMENT_I,
                )
            ],
            dtype=cst.DTYPE_FLOAT,
        )
        builders.randomize(gfcf, full_randomization=True)
        s_y.df.update(gfcf)
        assert np.allclose(s_y.get_gfcf_column(), gfcf)
