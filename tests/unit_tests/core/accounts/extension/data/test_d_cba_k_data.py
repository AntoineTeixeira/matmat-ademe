import numpy as np

import matmat.utils.constants as cst
from matmat.core.data.strategies import structure, nature
from matmat.core.accounts.extension.data.core import DCbaKData

import tests.utils.builders as builders
import tests.utils.constants as tests_cst


class TestDCbaKData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_d_cba_k().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_d_cba_k().get_structure_type()
            is structure.StructureDCbaKBySector
        )
        assert (
            builders.build_test_d_cba_k().get_structure_type(
                strategy=cst.STRATEGY_USE_BASED
            )
            is structure.StructureDCbaKBySector
        )
        assert (
            builders.build_test_d_cba_k().get_structure_type(
                strategy=cst.STRATEGY_GROSS_OUTPUT_BASED
            )
            is structure.StructureDCbaKByExtensionCategory
        )
        assert (
            builders.build_test_d_cba_k().get_structure_type(
                strategy=cst.STRATEGY_EMBODIED_IN_IMPORT
            )
            is structure.StructureDCbaKByExtensionCategory
        )

    def test_calculate_from_m_and_y_and_f_y(self):
        """
        Test function `calculate` with parameters M, Y, F_Y

        (used in case of use_based extension)

        Expected_results:
            - d_cba_k = M.dot(Y\k_diag_dom) + F_Y\k_diag
        """
        # Define inputs
        test_regions = tests_cst.REGIONS_W_IMPORT
        test_strategy = cst.STRATEGY_USE_BASED
        d_cba_k: DCbaKData = builders.build_test_extension_data(
            name=cst.D_CBA_K,
            regions=test_regions,
            strategy=test_strategy,
        )
        m_k = builders.build_test_extension_data(
            name=cst.M_K,
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
        builders.randomize(m_k.df)
        builders.randomize(f_y.df)

        # Call function under test
        d_cba_k.calculate(M=m_k, Y=y, F_Y=f_y)

        # Compute reference data
        y_diag = y.structure.diagonalize(df=y.df)
        y_diag_wo_k = y_diag.drop(columns=cst.IDX_INVESTMENT, level=1)
        y_diag_wo_k_dom = y_diag_wo_k.loc[cst.IDX_DOMESTIC]
        f_y_diag = f_y.structure.diagonalize(df=f_y.df)
        f_y_diag_wo_k = f_y_diag.drop(columns=cst.IDX_INVESTMENT, level=1)
        d_cba_ref = m_k.df.dot(y_diag_wo_k_dom) + f_y_diag_wo_k

        # Compare results
        assert np.allclose(d_cba_k.df, d_cba_ref)
