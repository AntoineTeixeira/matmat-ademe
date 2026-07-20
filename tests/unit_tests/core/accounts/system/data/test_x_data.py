import numpy as np
import pandas as pd

from matmat.core.data.strategies import structure, nature
from matmat.utils import constants as cst

from tests.utils import builders, constants as tests_cst


class TestXData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_x().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_x().get_structure_type()
            is structure.StructureX
        )

    def test_calculate_from_interindustry_matrix(self):
        """
        Test function `calculate_from_interindustry_matrix`
        Expected results:
            - Check that x = Z.sum(axis=1) + Y.sum(axis=1)
        """
        x = builders.build_test_x()
        y = builders.build_test_y()
        z = builders.build_test_z()
        builders.randomize(y.df)
        builders.randomize(z.df)
        x.calculate_from_interindustry_matrix(Z=z, Y=y)

        x_ref_df = pd.DataFrame(z.df.sum(axis=1) + y.df.sum(axis=1))
        assert np.allclose(x.df, x_ref_df)

    def test_calculate_from_leontief_matrix(self):
        """
        Test function `calculate_from_leontief_matrix`
        Expected results:
            - Check that x_dom = L_dom.(Y_dom.sum(axis=1))
            - Check that x_imp = 0.0
        """
        x = builders.build_test_system_data(
            name=cst.X, regions=tests_cst.REGIONS_W_IMPORT
        )
        y = builders.build_test_system_data(
            name=cst.Y, regions=tests_cst.REGIONS_W_IMPORT
        )
        l = builders.build_test_system_data(
            name=cst.L, regions=tests_cst.REGIONS_W_IMPORT
        )
        builders.randomize(y.df)
        builders.randomize(l.df)
        x.calculate_from_leontief_matrix(L=l, Y=y)

        x_ref_df_dom = pd.DataFrame(
            l.get_domestic_origin().dot(y.get_domestic_origin().sum(axis=1))
        )
        x_ref_df_imp = pd.DataFrame(
            index=x_ref_df_dom.index, columns=x_ref_df_dom.columns, data=0.0
        )
        x_ref_df = pd.concat([x_ref_df_dom, x_ref_df_imp])
        assert np.allclose(x.df, x_ref_df)

    def test_calculate_from_leontief_matrix_wo_import_regions(self):
        """
        Test function `calculate_from_leontief_matrix`, without import
        regions.

        Expected results:
            - Check that x = L_dom.(Y_dom.sum(axis=1))
        """
        x = builders.build_test_system_data(
            name=cst.X, regions=tests_cst.REGIONS_WO_IMPORT
        )
        y = builders.build_test_system_data(
            name=cst.Y, regions=tests_cst.REGIONS_WO_IMPORT
        )
        l = builders.build_test_system_data(
            name=cst.L, regions=tests_cst.REGIONS_WO_IMPORT
        )
        builders.randomize(y.df)
        builders.randomize(l.df)
        x.calculate_from_leontief_matrix(L=l, Y=y)

        x_ref_df = pd.DataFrame(
            l.get_domestic_origin().dot(y.get_domestic_origin().sum(axis=1))
        )

        assert np.allclose(x.df, x_ref_df)
