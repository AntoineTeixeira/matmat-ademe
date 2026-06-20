import shutil
import os

import matmat.core.accounts.builder as a_builder
import matmat.core.shocks.builder as as_builder
import matmat.core.accounts.system.builder as s_builder
import matmat.core.shocks.system.builder as ss_builder
import matmat.core.accounts.extension.builder as e_builder
import matmat.core.shocks.extension.builder as se_builder
from matmat.core.detail_level import core as dl
from matmat.utils import constants as cst

from tests.utils import builders, constants as tests_cst


class TestAccounts:
    PATH_ACCOUNTS = "tmp_accounts"
    PATH_ACCOUNTS_SHOCK = "tmp_accounts_shock"

    @classmethod
    def setup_method(cls):
        os.makedirs(cls.PATH_ACCOUNTS, exist_ok=True)
        os.makedirs(cls.PATH_ACCOUNTS_SHOCK, exist_ok=True)

    @classmethod
    def teardown_method(cls):
        shutil.rmtree(cls.PATH_ACCOUNTS)
        shutil.rmtree(cls.PATH_ACCOUNTS_SHOCK)

    def test_tc_int_acc_001(self):
        """
        TC-INT-ACC-001

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
        a_dir = a_builder.get_director()
        s_dir = s_builder.get_director()
        e_dir = e_builder.get_director()

        # Set detail levels
        for director in [a_dir, s_dir, e_dir]:
            director.set_regions(dl_regions)
            director.set_sectors(dl_sectors)
            director.set_final_demand_categories(dl_fd)

        # Build system
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_dataset(ref_system.dataset)

        # Build extensions
        # 1. use_based
        e_dir.set_extension_categories(dl_ext_1)
        ext_use_based = e_dir.make_use_based_extension(name_ext_use_based)

        # 2. gross_output_based
        e_dir.set_extension_categories(dl_ext_2)
        ext_gross_output_based = e_dir.make_gross_output_based_extension(
            name_ext_gross_output_based
        )

        # 3. embodied_in_import
        e_dir.set_extension_categories(dl_ext_3)
        ext_embodied_in_import = e_dir.make_embodied_in_import_extension(
            name=name_ext_embodied_in_import
        )

        for ext_ in [
            ext_use_based,
            ext_gross_output_based,
            ext_embodied_in_import,
        ]:
            builders.randomize_dataset(ext_.dataset)

        # Build accounts
        ref_accounts = a_dir.make_from_system_and_extensions(
            system=ref_system,
            extensions={
                ext_use_based.name: ext_use_based,
                ext_gross_output_based.name: ext_gross_output_based,
                ext_embodied_in_import: ext_embodied_in_import,
            },
        )

        # Export accounts with coefficients reset
        ref_accounts.reset_coefficients()
        truncated_accounts = ref_accounts.copy()
        truncated_accounts.save_to_path(
            path=self.PATH_ACCOUNTS, export_format=cst.FORMAT_PICKLE
        )

        # Load accounts and compare
        # -------------------------
        a_dir.reset()
        test_accounts = a_dir.make_from_path(
            path=self.PATH_ACCOUNTS, load_data=True
        )

        # Calculate reference & test accounts
        ref_accounts.calculate()
        test_accounts.calculate()

        # Check equality
        assert test_accounts.equals(ref_accounts)

    def test_tc_int_acc_002(self):
        """
        TC-INT-ACC-002

        No import regions
        """
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"

        a_dir = a_builder.get_director()

        s_dir = a_dir.system_director
        e_dir = a_dir.extension_director

        for director in [s_dir, e_dir]:
            director.set_sectors(sectors=builders.get_test_sectors())
            director.set_regions(regions=tests_cst.REGIONS_WO_IMPORT)
            director.set_final_demand_categories(
                tests_cst.DEFAULT_Y_CATEGORIES
            )

        # Build system
        # ------------
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_dataset(ref_system.dataset)

        # Build extensions
        # ----------------
        # 1. use_based
        ext_cats_dl = (
            builders.get_test_sectors().get_as_extension_categories_dl(
                extension_name=name_ext_use_based
            )
        )
        ext_cats_dl.prefix_level_names_if_duplicates(
            prefix=cst.IDX_PREFIX_EXT, other_dl=builders.get_test_sectors()
        )
        e_dir.set_extension_categories(ext_cats_dl)
        ext_use_based = e_dir.make_use_based_extension(name_ext_use_based)

        # 2. use_based
        e_dir.set_extension_categories(
            dl.ExtensionCategoriesDL(
                extension_name=name_ext_gross_output_based,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.df,
            )
        )
        ext_gross_output_based = e_dir.make_gross_output_based_extension(
            name_ext_gross_output_based
        )

        # 3. embodied_in_import
        # No embodied_in_import extension as there are no import regions

        for ext_ in [
            ext_use_based,
            ext_gross_output_based,
        ]:
            builders.randomize_dataset(ext_.dataset)

        # Build accounts
        # --------------
        ref_accounts = a_dir.make_from_system_and_extensions(
            system=ref_system,
            extensions={
                name_ext_use_based: ext_use_based,
                name_ext_gross_output_based: ext_gross_output_based,
            },
        )

        ref_accounts.reset_coefficients()
        truncated_accounts = ref_accounts.copy()

        truncated_accounts.save_to_path(
            path=self.PATH_ACCOUNTS, export_format=cst.FORMAT_PICKLE
        )

        # Load accounts and compare
        # -------------------------
        a_dir.reset()
        test_accounts = a_dir.make_from_path(
            path=self.PATH_ACCOUNTS, load_data=True
        )

        ref_accounts.calculate()
        test_accounts.calculate()

        assert test_accounts.equals(ref_accounts)

    def test_tc_int_acc_003(self):
        """
        TC-INT-ACC-003

        Test accounts and accounts shocks interface
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
        a_dir = a_builder.get_director()
        as_dir = as_builder.get_director()
        s_dir = s_builder.get_director()
        ss_dir = ss_builder.get_director()
        e_dir = e_builder.get_director()
        es_dir = se_builder.get_director()

        # Set detail levels
        for director in [a_dir, as_dir, s_dir, ss_dir, e_dir, es_dir]:
            director.set_regions(dl_regions)
            director.set_sectors(dl_sectors)
            director.set_final_demand_categories(dl_fd)

        # Build system & related shock
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_dataset(ref_system.dataset)
        ref_system.reset_coefficients()
        ref_system.calculate()
        ref_system_shock = ss_dir.make_shock_exo()
        builders.randomize_dataset(ref_system_shock.dataset)

        # Build extensions & related shocks
        # 1. use_based
        e_dir.set_extension_categories(dl_ext_1)
        es_dir.set_extension_categories(dl_ext_1)
        ext_use_based = e_dir.make_use_based_extension(name_ext_use_based)
        ext_shock_use_based = es_dir.make_shock_s_z(name_ext_use_based)

        # 2. gross_output_based
        e_dir.set_extension_categories(dl_ext_2)
        es_dir.set_extension_categories(dl_ext_2)
        ext_gross_output_based = e_dir.make_gross_output_based_extension(
            name_ext_gross_output_based
        )
        ext_shock_gross_output_based = es_dir.make_shock_s_x(
            name_ext_gross_output_based
        )

        # 3. embodied_in_import
        e_dir.set_extension_categories(dl_ext_3)
        es_dir.set_extension_categories(dl_ext_3)
        ext_embodied_in_import = e_dir.make_embodied_in_import_extension(
            name_ext_embodied_in_import
        )
        ext_shock_embodied_in_import = es_dir.make_shock_m_row(
            name_ext_embodied_in_import
        )

        for ext_ in [
            ext_use_based,
            ext_gross_output_based,
            ext_embodied_in_import,
        ]:
            builders.randomize_dataset(ext_.dataset)
            ext_.reset_fluxes()
            ext_.calculate(ref_system)

        for ext_shock in [
            ext_shock_use_based,
            ext_shock_gross_output_based,
            ext_shock_embodied_in_import,
        ]:
            builders.randomize_dataset(ext_shock.dataset)

        # Build accounts & related shock
        ref_accounts = a_dir.make_from_system_and_extensions(
            system=ref_system,
            extensions={
                ext_use_based.name: ext_use_based,
                ext_gross_output_based.name: ext_gross_output_based,
                ext_embodied_in_import: ext_embodied_in_import,
            },
        )
        ref_accounts_shock = as_dir.make_from_system_and_extensions_shocks(
            system_shock=ref_system_shock,
            extensions_shocks={
                ext_shock_use_based.name: ext_shock_use_based,
                ext_shock_gross_output_based.name: ext_shock_gross_output_based,
                ext_shock_embodied_in_import.name: ext_shock_embodied_in_import,
            }
        )

        # Export accounts & related shock
        ref_accounts.save_to_path(
            path=self.PATH_ACCOUNTS, export_format=cst.FORMAT_PICKLE
        )
        ref_accounts_shock.save_to_path(
            path=self.PATH_ACCOUNTS_SHOCK, export_format=cst.FORMAT_PICKLE
        )

        # Compute reference accounts shocked
        ref_accounts.reset_for_shock()
        ref_accounts.shock(ref_accounts_shock)
        ref_accounts.calculate()

        # Compute loaded accounts shocked
        a_dir.reset()
        loaded_accounts = a_dir.make_from_path(
            path=self.PATH_ACCOUNTS,
            load_data=True,
        )
        as_dir.reset()
        loaded_shock = as_dir.make_from_path(
            path=self.PATH_ACCOUNTS_SHOCK,
            load_data=True,
        )
        loaded_accounts.reset_for_shock()
        loaded_accounts.shock(loaded_shock)
        loaded_accounts.calculate()

        # Check equality
        assert loaded_accounts.equals(ref_accounts)
