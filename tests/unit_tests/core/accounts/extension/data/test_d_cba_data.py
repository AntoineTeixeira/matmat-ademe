import numpy as np

import matmat.utils.constants as cst
from matmat.core.data.strategies import structure, nature
from matmat.core.accounts.extension.data.core import DCbaData, MData

import tests.utils.builders as builders
import tests.utils.constants as tests_cst


class TestDCbaData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_d_cba().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_d_cba().get_structure_type()
            is structure.StructureDCbaBySector
        )
        assert (
            builders.build_test_d_cba().get_structure_type(
                strategy=cst.STRATEGY_USE_BASED
            )
            is structure.StructureDCbaBySector
        )
        assert (
            builders.build_test_d_cba().get_structure_type(
                strategy=cst.STRATEGY_GROSS_OUTPUT_BASED
            )
            is structure.StructureDCbaByExtensionCategory
        )
        assert (
            builders.build_test_d_cba().get_structure_type(
                strategy=cst.STRATEGY_EMBODIED_IN_IMPORT
            )
            is structure.StructureDCbaByExtensionCategory
        )

    def test_get_domestic_exports(self):
        # Define inputs
        test_regions = tests_cst.REGIONS_W_IMPORT
        test_strategy = cst.STRATEGY_GROSS_OUTPUT_BASED
        d_cba: DCbaData = builders.build_test_extension_data(
            name=cst.D_CBA,
            regions=test_regions,
            strategy=test_strategy,
        )
        builders.randomize(df=d_cba.df)

        # Call function under test
        d_cba_exports = d_cba.get_domestic_exports()

        # Compute reference data
        ref_d_cba_exports = d_cba.df.xs(
            key=cst.IDX_EXPORTS,
            level=d_cba.final_demand_categories.get_main_level_name(),
            axis=1,
        )

        # Compare results
        assert np.allclose(d_cba_exports.values, ref_d_cba_exports.values)

    def test_calculate_from_m_and_y(self):
        """
        Test function `calculate` with parameters M, Y

        (used in case of gross_output_based extension)

        Expected_results:
            - d_cba = M.dot(Y_diag_dom)
        """
        # Define inputs
        test_regions = tests_cst.REGIONS_W_IMPORT
        test_strategy = cst.STRATEGY_GROSS_OUTPUT_BASED
        d_cba: DCbaData = builders.build_test_extension_data(
            name=cst.D_CBA,
            regions=test_regions,
            strategy=test_strategy,
        )
        m = builders.build_test_extension_data(
            name=cst.M,
            regions=test_regions,
            strategy=test_strategy,
        )
        y = builders.build_test_system_data(
            name=cst.Y,
            regions=test_regions,
        )

        builders.randomize(y.df)
        builders.randomize(m.df)

        # Call function under test
        d_cba.calculate(M=m, Y=y)

        # Compute reference data
        y_diag = y.structure.diagonalize(df=y.df)
        y_diag_dom = y_diag.loc[cst.IDX_DOMESTIC]
        d_cba_ref = m.df.dot(y_diag_dom)

        # Compare results
        assert np.allclose(d_cba.df, d_cba_ref)

    def test_calculate_from_m_and_y_and_f_y(self):
        """
        Test function `calculate` with parameters M, Y, F_Y

        (used in case of use_based extension)

        Expected_results:
            - d_cba = M.dot(Y_diag_dom) + F_Y_diag
        """
        # Define inputs
        test_regions = tests_cst.REGIONS_W_IMPORT
        test_strategy = cst.STRATEGY_USE_BASED
        d_cba: DCbaData = builders.build_test_extension_data(
            name=cst.D_CBA,
            regions=test_regions,
            strategy=test_strategy,
        )
        m = builders.build_test_extension_data(
            name=cst.M,
            regions=test_regions,
            strategy=test_strategy,
        )
        y = builders.build_test_system_data(
            name=cst.Y,
            regions=test_regions,
        )
        f_y = builders.build_test_extension_data(
            name=cst.F_Y, regions=test_regions
        )

        builders.randomize(y.df)
        builders.randomize(m.df)
        builders.randomize(f_y.df)

        # Call function under test
        d_cba.calculate(M=m, Y=y, F_Y=f_y)

        # Compute reference data
        y_diag = y.structure.diagonalize(df=y.df)
        y_diag_dom = y_diag.loc[cst.IDX_DOMESTIC]
        f_y_diag = f_y.structure.diagonalize(df=f_y.df)
        d_cba_ref = m.df.dot(y_diag_dom) + f_y_diag

        # Compare results
        assert np.allclose(d_cba.df, d_cba_ref)

    def test_calculate_from_m_and_y_and_m_row(self):
        """
        Test function `calculate` with parameters M, Y, M_RoW

        (used in case of embodied_in_import extension)

        Expected_results:
            - d_cba = M.dot(Y_diag_dom) + M_RoW.dot(Y_diag_imp)
        """
        # Define inputs
        test_regions = tests_cst.REGIONS_W_IMPORT
        test_strategy = cst.STRATEGY_EMBODIED_IN_IMPORT
        d_cba: DCbaData = builders.build_test_extension_data(
            name=cst.D_CBA,
            regions=test_regions,
            strategy=test_strategy,
        )
        m: MData = builders.build_test_extension_data(
            name=cst.M,
            regions=test_regions,
            strategy=test_strategy,
        )
        y = builders.build_test_system_data(
            name=cst.Y,
            regions=test_regions,
        )
        m_row = builders.build_test_extension_data(
            name=cst.M_ROW, regions=test_regions
        )

        builders.randomize(y.df)
        builders.randomize(m.df)
        builders.randomize(m_row.df)

        # Call function under test
        d_cba.calculate(M=m, Y=y, M_RoW=m_row)

        # Compute reference data
        y_diag = y.structure.diagonalize(df=y.df)
        y_diag_dom = y_diag.loc[cst.IDX_DOMESTIC]
        y_diag_imp = y_diag.loc[cst.IDX_IMPORT]
        d_cba_ref = m.df.dot(y_diag_dom) + m_row.df.dot(y_diag_imp)

        # Compare results
        assert np.allclose(d_cba.df, d_cba_ref)
