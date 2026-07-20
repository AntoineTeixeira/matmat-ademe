import pandas as pd
import numpy as np

from matmat.core.data.strategies import structure, nature
import matmat.utils.constants as cst

from tests.utils import builders


class TestYShockData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`

        Expected results:
            - Check that the nature type is properly returned
        """
        data_ = builders.build_test_system_shock_data(name=cst.D_Y)
        assert data_.get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`

        Expected results:
            - Check that the structure type is properly returned
        """
        data_ = builders.build_test_system_shock_data(name=cst.D_Y)
        assert data_.get_structure_type() is structure.StructureY

    def test_set_exports(self):
        """
        Test function `set_exports`

        Expected results:
            - Check that the exports column(s) is properly set
        """
        dy = builders.build_test_dy()
        exports_df = pd.DataFrame(
            index=dy.df_rows,
            columns=pd.Index([cst.IDX_EXPORTS]),
            dtype=cst.DTYPE_FLOAT,
        )
        builders.randomize(exports_df)
        dy.set_exports(exports=exports_df)

        assert np.allclose(
            dy.df.xs(key=cst.IDX_EXPORTS, axis=1, level=1), exports_df
        )
