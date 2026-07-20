import numpy as np

from matmat.core.data.strategies import structure, nature
from matmat.core.accounts.extension.data.core import MData

from tests.utils import builders
import matmat.utils.constants as cst


class TestMData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_m().get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`

        Case 1:
            - no arguments provided, structure shall be `StructureZ`
        Case 2:
            - strategy is None, structure shall be `StructureZ`
        Case 3:
            - extension_categories is not None, and strategy is "use_based",
              structure shall be `StructureZ`
        Case 4:
            - extension_categories is None, and strategy is 'gross_output_based',
              structure shall be `StructureSx`
        Case 5:
            - extension_categories is not None, and strategy is 'embodied_in_import',
              structure shall be `StructureSx`
        """
        # Case 1
        assert (
            builders.build_test_m().get_structure_type()
            is structure.StructureZ
        )

        # Case 2
        assert (
            builders.build_test_m().get_structure_type(strategy=None)
            is structure.StructureZ
        )

        # Case 3
        assert (
            builders.build_test_m().get_structure_type(
                strategy=cst.STRATEGY_USE_BASED,
                extension_categories=["cat1", "cat2"],
            )
            is structure.StructureZ
        )

        # Case 4
        assert (
            builders.build_test_m().get_structure_type(
                strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
                extension_categories=None,
            )
            is structure.StructureSx
        )

        # Case 5
        assert (
            builders.build_test_m().get_structure_type(
                strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
                extension_categories=["C1", "C2"],
            )
            is structure.StructureSx
        )

    def test_calculate_domestic_from_f_z_and_x(self):
        """
        Test function `calculate` from F_Z, x and leontief

        (used in case of use_based extension)

        Expected results:
            - Check that M = (F_Z / x_dom).L_dom
        """
        # Define inputs
        m: MData = builders.build_test_extension_data(name=cst.M)
        f_z = builders.build_test_extension_data(name=cst.F_Z)
        l = builders.build_test_l()
        x = builders.build_test_x()

        builders.randomize(f_z.df)
        builders.randomize(l.df)
        builders.randomize(x.df)

        # Call function under test
        m.calculate(L=l, x=x, F_Z=f_z)

        # Compute reference data
        m_ref = (f_z.df.divide(x.get_domestic_origin().squeeze(), axis=1)).dot(l.get_domestic_origin())

        # Compare results
        assert np.allclose(m.df, m_ref)

    def test_calculate_domestic_from_s_x_dom(self):
        """
        Test function `calculate` from S_x_dom and leontief

        (used in case of gross_output_based extension)

        Expected results:
            - Check that M = S_x_dom.L_dom
        """
        # Define inputs
        m: MData = builders.build_test_extension_data(name=cst.M)
        s_x_dom = builders.build_test_extension_data(name=cst.S_X_DOM)
        l = builders.build_test_l()

        builders.randomize(s_x_dom.df)
        builders.randomize(l.df)

        # Call function under test
        m.calculate(L=l, S_x_dom=s_x_dom)

        # Compute reference data
        m_ref = s_x_dom.df.dot(l.get_domestic_origin())

        # Compare results
        assert np.allclose(m.df, m_ref)

    def test_calculate_domestic_from_m_row_and_a(self):
        """
        Test function `calculate` from M_RoW, A and leontief

        (used in case of embodied_in_import extension)

        Expected results:
            - Check that M = M_RoW.A_imp.L_dom
        """
        # Define inputs
        m: MData = builders.build_test_extension_data(name=cst.M)
        m_row = builders.build_test_extension_data(name=cst.M_ROW)
        l = builders.build_test_l()
        a = builders.build_test_a()

        builders.randomize(m_row.df)
        builders.randomize(a.df)
        builders.randomize(l.df)

        # Call function under test
        m.calculate(L=l, A=a, M_RoW=m_row)

        # Compute reference data
        m_ref = m_row.df.dot(a.get_import_origin()).dot(l.get_domestic_origin())

        # Compare results
        assert np.allclose(m.df, m_ref)
