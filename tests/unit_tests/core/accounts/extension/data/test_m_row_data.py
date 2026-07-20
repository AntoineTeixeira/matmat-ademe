import pandas as pd
import numpy as np

from matmat.core.detail_level import core as dl
from matmat.core.data.strategies import structure, nature
from matmat.core.accounts.extension.data.core import DCbaData
import matmat.utils.constants as cst
from tests.utils import builders, constants as tests_cst


class TestMRoWData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert (
            builders.build_test_m_row().get_nature_type() is nature.Coefficient
        )

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_m_row().get_structure_type()
            is structure.StructureMRoW
        )

    def test_update_imports_from_world_format_m_row_disagg_d_cba_agg(self):
        """
        Test method `update_imports_from_world`

        Test with:
            - M_RoW with a disaggregated format
            - d_cba with an aggregated format

        Expected results: M_RoW = diag(d_cba_world.exports) / x_imp
        """
        # TODO: test the case when d_cba_world has several extensions
        #       categories
        d_cba_world: DCbaData = builders.build_test_extension_data(
            name=cst.D_CBA,
            regions=tests_cst.REGIONS_W_IMPORT_INV,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            extension_categories=dl.ExtensionCategoriesDL(
                extension_name="test_extension",
                df=pd.DataFrame({cst.IDX_PERIMETER: ["ghg_emissions"]}),
            ),
            strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
        )

        builders.randomize(d_cba_world.df)

        x = builders.build_test_system_data(
            name=cst.X, regions=tests_cst.REGIONS_W_IMPORT
        )
        builders.randomize(x.df)

        m_row = builders.build_test_extension_data(
            name=cst.M_ROW,
            extension_name="test_extension",
            regions=tests_cst.REGIONS_W_IMPORT,
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            extension_categories=builders.get_test_extension_categories_equivalent_to_sectors(
                "test_extension",
            ),
            strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
        )

        m_row.update_imports_from_world(d_cba_world=d_cba_world, x_domestic=x)

        # compute reference m_row (as done in old MatMat code)
        d_imp = d_cba_world.df[("RoW", "Exports", "E")]
        x_imp = x.df.loc[("import", "RoW")].squeeze()
        d_imp_diag = pd.DataFrame(
            index=m_row.index,
            columns=d_imp.columns,
            data=np.diag(d_imp.iloc[0]),
        )
        m_row_ref = (
            d_imp_diag.divide(x_imp).replace(np.nan, 0.0).replace(np.inf, 0.0)
        )

        assert np.allclose(m_row.df, m_row_ref)

    def test_update_imports_from_world_format_m_row_agg_d_cba_agg(self):
        """
        Test method `update_imports_from_world`

        Test with:
            - M_RoW with an aggregated format
            - d_cba with an aggregated format

        Expected results: S_x_imp = d_cba_world.exports / x_imp
        """
        d_cba_world = builders.build_test_extension_data(
            name=cst.D_CBA,
            regions=tests_cst.REGIONS_W_IMPORT_INV,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
            strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
        )

        builders.randomize(d_cba_world.df)

        x = builders.build_test_system_data(
            name=cst.X,
            regions=tests_cst.REGIONS_W_IMPORT,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )
        builders.randomize(x.df)

        m_row = builders.build_test_extension_data(
            name=cst.M_ROW,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
            regions=tests_cst.REGIONS_W_IMPORT,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
        )

        m_row.update_imports_from_world(d_cba_world=d_cba_world, x_domestic=x)

        # compute reference m_row (as done in old MatMat code)
        d_imp = d_cba_world.df[("RoW", "Exports", "E")]
        x_imp = x.df.loc[("import", "RoW")].squeeze()
        m_row_ref = (
            d_imp.divide(x_imp).replace(np.nan, 0.0).replace(np.inf, 0.0)
        )

        assert np.allclose(m_row.df, m_row_ref)

    def test_update_imports_from_world_format_m_row_disagg_d_cba_disagg(self):
        """
        Test method `update_imports_from_world`

        Test with:
            - M_RoW with a disaggregated format
            - d_cba with a disaggregated format

        Expected results: S_x_imp = d_cba_world.exports / x_imp
        """
        d_cba_world = builders.build_test_extension_data(
            name=cst.D_CBA,
            extension_name="test_extension",
            regions=tests_cst.REGIONS_W_IMPORT_INV,
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            extension_categories=builders.get_test_extension_categories_equivalent_to_sectors(
                "test_extension",
            ),
            strategy=cst.STRATEGY_USE_BASED,
        )

        builders.randomize(d_cba_world.df)

        x = builders.build_test_system_data(
            name=cst.X, regions=tests_cst.REGIONS_W_IMPORT
        )
        builders.randomize(x.df)

        m_row = builders.build_test_extension_data(
            name=cst.M_ROW,
            extension_name="test_extension",
            sectors=builders.get_test_sectors(),
            extension_categories=builders.get_test_extension_categories_equivalent_to_sectors(
                "test_extension",
            ),
            regions=tests_cst.REGIONS_W_IMPORT,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

        m_row.update_imports_from_world(d_cba_world=d_cba_world, x_domestic=x)

        # compute reference m_row (as done in old MatMat code)
        d_imp = d_cba_world.df.loc[("domestic", "RoW")][
            ("RoW", "Exports", "E")
        ]
        x_imp = x.df.loc[("import", "RoW")].squeeze()
        m_row_ref = (
            d_imp.divide(x_imp).replace(np.nan, 0.0).replace(np.inf, 0.0)
        )

        assert np.allclose(m_row.df, m_row_ref)
