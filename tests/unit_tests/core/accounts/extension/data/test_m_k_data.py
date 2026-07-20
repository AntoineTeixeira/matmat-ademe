import numpy as np

from matmat.core.accounts.extension.data.core import MKData

from tests.utils import builders
import matmat.utils.constants as cst


class TestMkData:

    def test_calculate_domestic_from_f_z_and_x_and_s_y_and_y_k(self):
        """
        Test function `calculate` from F_Z, x, S_Y, Y_k, and leontief

        (used in case of use_based extension)

        Expected results:
            - Check that M = ((F_Z + S_Y_GFCF*Y_k) / x_dom).L_dom
        """
        # Define inputs
        m_k: MKData = builders.build_test_extension_data(name=cst.M_K)
        f_z = builders.build_test_extension_data(name=cst.F_Z)
        s_y = builders.build_test_extension_data(name=cst.S_Y)
        l_k = builders.build_test_l_k()
        x = builders.build_test_x()
        y_k = builders.build_test_y_k()

        builders.randomize(f_z.df)
        builders.randomize(s_y.df)
        builders.randomize(l_k.df)
        builders.randomize(x.df)
        builders.randomize(y_k.df)

        # Call function under test
        m_k.calculate(L=l_k, x=x, F_Z=f_z, S_Y=s_y, Y_k=y_k)

        # Compute reference data
        s_y_gfcf = s_y.df.xs(
            key=cst.IDX_INVESTMENT,
            level=s_y.final_demand_categories.get_main_level_name(),
            axis=1,
        ).squeeze()
        m_k_ref = (
            (f_z.df + y_k.df.mul(s_y_gfcf, axis=0)).divide(
                x.get_domestic_origin().squeeze(), axis=1
            )
        ).dot(l_k.get_domestic_origin())

        # Compare results
        assert np.allclose(m_k.df, m_k_ref)

    def test_calculate_domestic_from_m_row_and_a_and_k(self):
        """
        Test function `calculate` from M_RoW, A, K and leontief

        (used in case of embodied_in_import extension)

        Expected results:
            - Check that M = M_RoW.A_imp.L_dom
        """
        # Define inputs
        m_k: MKData = builders.build_test_extension_data(name=cst.M_K)
        m_row = builders.build_test_extension_data(name=cst.M_ROW)
        l = builders.build_test_l()
        a = builders.build_test_a()
        k = builders.build_test_k()

        builders.randomize(m_row.df)
        builders.randomize(a.df)
        builders.randomize(l.df)
        builders.randomize(k.df)

        # Call function under test
        m_k.calculate(L=l, A=a, K=k, M_RoW=m_row)

        # Compute reference data
        m_k_ref = m_row.df.dot(
            a.get_import_origin() + k.get_import_origin()
        ).dot(l.get_domestic_origin())

        # Compare results
        assert np.allclose(m_k.df, m_k_ref)
