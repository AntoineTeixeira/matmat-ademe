import shutil
import os

import matmat.core.shocks.builder as as_builder
import matmat.core.shocks.system.builder as ss_builder
import matmat.core.shocks.extension.builder as se_builder
from matmat.core.detail_level import core as dl
from matmat.utils import constants as cst

from tests.utils import builders, constants as tests_cst


class TestAccountsShock:
    PATH_ACCOUNTS_SHOCK = "tmp_accounts_shock"

    @classmethod
    def setup_method(cls):
        os.makedirs(cls.PATH_ACCOUNTS_SHOCK, exist_ok=True)

    @classmethod
    def teardown_method(cls):
        shutil.rmtree(cls.PATH_ACCOUNTS_SHOCK)

    def test_tc_int_ash_001(self):
        """
        TC-INT-ASH-001

        Domestic and import regions
        """
        # Extension names
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"
        name_ext_embodied_in_import = "ext_embodied_in_import"

        # Detail levels
        dl_sectors = builders.get_test_sectors()
        dl_regions = tests_cst.REGIONS_W_IMPORT
        dl_fd = tests_cst.DEFAULT_Y_CATEGORIES
        dl_ext_1 = dl.ExtensionCategoriesDL(
            extension_name=name_ext_use_based,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS.df,
        )
        dl_ext_2 = dl.ExtensionCategoriesDL(
            extension_name=name_ext_gross_output_based,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.df,
        )
        dl_ext_3 = dl.ExtensionCategoriesDL(
            extension_name=name_ext_embodied_in_import,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.df,
        )

        # REFERENCE ACCOUNTS CONSTRUCTION
        # -------------------------------
        as_dir = as_builder.get_director()
        ss_dir = ss_builder.get_director()
        se_dir = se_builder.get_director()

        # Set detail levels
        for director in [as_dir, ss_dir, se_dir]:
            director.set_regions(dl_regions)
            director.set_sectors(dl_sectors)
            director.set_final_demand_categories(dl_fd)

        # Build system
        ref_system_shock = ss_dir.make_shock_exo()
        builders.randomize_dataset(ref_system_shock.dataset)

        # Build extensions
        # 1. use_based
        se_dir.set_extension_categories(dl_ext_1)
        ext_shock_use_based = se_dir.make_shock_s_z(name_ext_use_based)

        # 2. gross_output_based
        se_dir.set_extension_categories(dl_ext_2)
        ext_shock_gross_output_based = se_dir.make_shock_s_x(
            name_ext_gross_output_based
        )

        # 3. embodied_in_import
        se_dir.set_extension_categories(dl_ext_3)
        ext_shock_embodied_in_import = se_dir.make_shock_m_row(
            name=name_ext_embodied_in_import
        )

        for ext_ in [
            ext_shock_use_based,
            ext_shock_gross_output_based,
            ext_shock_embodied_in_import,
        ]:
            builders.randomize_dataset(ext_.dataset)

        # Build accounts
        ref_accounts = as_dir.make_from_system_and_extensions_shocks(
            system_shock=ref_system_shock,
            extensions_shocks={
                ext_shock_use_based.name: ext_shock_use_based,
                ext_shock_gross_output_based.name: ext_shock_gross_output_based,
                ext_shock_embodied_in_import: ext_shock_embodied_in_import,
            },
        )

        # Export accounts shock
        ref_accounts.save_to_path(
            path=self.PATH_ACCOUNTS_SHOCK, export_format=cst.FORMAT_PICKLE
        )

        # Load accounts and compare
        # -------------------------
        as_dir.reset()
        test_accounts = as_dir.make_from_path(
            path=self.PATH_ACCOUNTS_SHOCK, load_data=True
        )

        # Check equality
        assert test_accounts.equals(ref_accounts)

    def test_tc_int_ash_002(self):
        """
        TC-INT-ASH-002

        No import regions
        """
        # Extension names
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"

        # Detail levels
        dl_sectors = builders.get_test_sectors()
        dl_regions = tests_cst.REGIONS_WO_IMPORT
        dl_fd = tests_cst.DEFAULT_Y_CATEGORIES
        dl_ext_1 = dl.ExtensionCategoriesDL(
            extension_name=name_ext_use_based,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS.df,
        )
        dl_ext_2 = dl.ExtensionCategoriesDL(
            extension_name=name_ext_gross_output_based,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.df,
        )

        # REFERENCE ACCOUNTS CONSTRUCTION
        # -------------------------------
        as_dir = as_builder.get_director()
        ss_dir = ss_builder.get_director()
        se_dir = se_builder.get_director()

        # Set detail levels
        for director in [as_dir, ss_dir, se_dir]:
            director.set_regions(dl_regions)
            director.set_sectors(dl_sectors)
            director.set_final_demand_categories(dl_fd)

        # Build system
        ref_system_shock = ss_dir.make_shock_exo()
        builders.randomize_dataset(ref_system_shock.dataset)

        # Build extensions
        # 1. use_based
        se_dir.set_extension_categories(dl_ext_1)
        ext_shock_use_based = se_dir.make_shock_s_z(name_ext_use_based)

        # 2. gross_output_based
        se_dir.set_extension_categories(dl_ext_2)
        ext_shock_gross_output_based = se_dir.make_shock_s_x(
            name_ext_gross_output_based
        )

        for ext_ in [
            ext_shock_use_based,
            ext_shock_gross_output_based,
        ]:
            builders.randomize_dataset(ext_.dataset)

        # Build accounts
        ref_accounts = as_dir.make_from_system_and_extensions_shocks(
            system_shock=ref_system_shock,
            extensions_shocks={
                ext_shock_use_based.name: ext_shock_use_based,
                ext_shock_gross_output_based.name: ext_shock_gross_output_based,
            },
        )

        # Export accounts shock
        ref_accounts.save_to_path(
            path=self.PATH_ACCOUNTS_SHOCK, export_format=cst.FORMAT_PICKLE
        )

        # Load accounts and compare
        # -------------------------
        as_dir.reset()
        test_accounts = as_dir.make_from_path(
            path=self.PATH_ACCOUNTS_SHOCK, load_data=True
        )

        # Check equality
        assert test_accounts.equals(ref_accounts)
