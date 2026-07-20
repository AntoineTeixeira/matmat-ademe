import numpy as np

from matmat.core.data.strategies import structure, nature
from tests.utils import builders


class TestDImpData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_d_imp().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_d_imp().get_structure_type()
            is structure.StructureMRoW
        )

    def test_calculate(self):
        """
        Test function calculate with parameters M_RoW and x

        Expected results:
            - Check that d_imp = M_RoW * x_imp
        """
        d_imp = builders.build_test_d_imp()
        m_row = builders.build_test_m_row()
        x = builders.build_test_x()

        builders.randomize(m_row.df)
        builders.randomize(x.df)

        # Compute reference d_imp
        d_imp_ref = m_row.df.mul(x.get_import_origin().squeeze())

        # Execute function under test
        d_imp.calculate(M_RoW=m_row, x=x)

        # Check consistency
        assert np.allclose(d_imp.df, d_imp_ref)
