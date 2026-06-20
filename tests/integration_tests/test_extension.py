import os
import shutil

from matmat.core.detail_level import core as dl
import matmat.core.accounts.extension.builder as e_builder
import matmat.core.accounts.system.builder as s_builder
import matmat.core.shocks.system.builder as ss_builder
import matmat.core.shocks.extension.builder as se_builder
from matmat.utils import constants as cst

from tests.utils import builders, constants as tests_cst


class TestExtension:
    PATH_SYSTEM = "tmp_system"
    PATH_EXTENSION = "tmp_extensions"
    PATH_EXTENSION_SHOCK = "tmp_extension_shocks"

    @classmethod
    def setup_method(cls):
        os.makedirs(cls.PATH_SYSTEM, exist_ok=True)
        os.makedirs(cls.PATH_EXTENSION, exist_ok=True)
        os.makedirs(cls.PATH_EXTENSION_SHOCK, exist_ok=True)

    @classmethod
    def teardown_method(cls):
        shutil.rmtree(cls.PATH_SYSTEM)
        shutil.rmtree(cls.PATH_EXTENSION)
        shutil.rmtree(cls.PATH_EXTENSION_SHOCK)

    def test_tc_int_ext_001(self):
        """
        TC-INT-EXT-001

        Domestic and import regions
        """
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"
        name_ext_embodied_in_import = "ext_embodied_in_import"

        e_dir = e_builder.get_director()
        s_dir = s_builder.get_director()

        for director in [s_dir, e_dir]:
            director.set_sectors(sectors=builders.get_test_sectors())
            director.set_regions(regions=tests_cst.REGIONS_W_IMPORT)
            director.set_final_demand_categories(
                tests_cst.DEFAULT_Y_CATEGORIES
            )

        # Build system
        # ------------
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_dataset(ref_system.dataset)
        ref_system.reset_coefficients()
        ref_system.calculate()

        # Build extensions
        # ----------------
        # 1. use based
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

        # 2. gross output based
        e_dir.set_extension_categories(
            dl.ExtensionCategoriesDL(
                extension_name=name_ext_gross_output_based,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.df,
            )
        )
        ext_gross_output_based = e_dir.make_gross_output_based_extension(
            name_ext_gross_output_based
        )

        # 3. embodied in import
        e_dir.set_extension_categories(
            dl.ExtensionCategoriesDL(
                extension_name=name_ext_embodied_in_import,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS.df,
            )
        )
        ext_embodied_in_import = e_dir.make_embodied_in_import_extension(
            name_ext_embodied_in_import
        )

        for ext_ in [
            ext_use_based,
            ext_gross_output_based,
            ext_embodied_in_import,
        ]:
            ext_.tune_dataset(system=ref_system)
            builders.randomize_dataset(ext_.dataset)
            ext_.reset_fluxes()
            truncated_ext = ext_.copy()
            ext_.calculate(system=ref_system)

            truncated_ext.save_to_path(
                path=self.PATH_EXTENSION, export_format="pickle"
            )

            # Load extension and compare
            # --------------------------
            e_dir.reset()
            test_ext = e_dir.make_from_path(
                path=f"{self.PATH_EXTENSION}/{ext_.name}", load_data=True
            )
            test_ext.calculate(system=ref_system)

            assert test_ext.equals(ext_)

    def test_tc_int_ext_002(self):
        """
        TC-INT-EXT-002

        No import regions
        """
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"

        e_dir = e_builder.get_director()
        s_dir = s_builder.get_director()

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
        ref_system.reset_coefficients()
        ref_system.calculate()

        # Build extensions
        # ----------------
        # 1. use based
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

        # 2. gross output based
        e_dir.set_extension_categories(
            dl.ExtensionCategoriesDL(
                extension_name=name_ext_gross_output_based,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL.df,
            )
        )
        ext_gross_output_based = e_dir.make_gross_output_based_extension(
            name_ext_gross_output_based
        )

        # 3. embodied in import
        # No embodied in import extension as there are no import regions

        for ext_ in [ext_use_based, ext_gross_output_based]:
            builders.randomize_dataset(ext_.dataset)
            ext_.reset_coefficients()
            truncated_ext = ext_.copy()
            ext_.calculate(system=ref_system)

            truncated_ext.save_to_path(
                path=self.PATH_EXTENSION, export_format=cst.FORMAT_PICKLE
            )

            # Load extension and compare
            # --------------------------
            e_dir.reset()
            test_ext = e_dir.make_from_path(
                path=f"{self.PATH_EXTENSION}/{ext_.name}", load_data=True
            )
            test_ext.calculate(system=ref_system)

            assert test_ext.equals(ext_)

    def test_tc_int_ext_003(self):
        """
        TC-INT-EXT-003

        Test extension and extension shocks interface
        """
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"
        name_ext_embodied_in_import = "ext_embodied_in_import"

        e_dir = e_builder.get_director()
        s_dir = s_builder.get_director()
        se_dir = se_builder.get_director()
        ss_dir = ss_builder.get_director()

        for director in [s_dir, e_dir, ss_dir, se_dir]:
            director.set_sectors(sectors=builders.get_test_sectors())
            director.set_regions(regions=tests_cst.REGIONS_W_IMPORT)
            director.set_final_demand_categories(
                tests_cst.DEFAULT_Y_CATEGORIES
            )

        # Build system
        # ------------
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_dataset(ref_system.dataset)
        ref_system.reset_coefficients()
        ref_system.calculate()
        ref_system.save_to_path(
            path=self.PATH_SYSTEM,
            export_format=cst.FORMAT_PICKLE,
        )

        # Build extensions
        # ----------------
        # 1. use based
        for director in [e_dir, se_dir]:
            director.set_extension_categories(
                builders.get_test_extension_categories_equivalent_to_sectors(
                    name_ext_use_based
                )
            )
        ext_use_based = e_dir.make_use_based_extension(name_ext_use_based)
        ext_shock_use_based = se_dir.make_shock_s_z(name_ext_use_based)

        # 2. gross output based
        for director in [e_dir, se_dir]:
            director.set_extension_categories(
                builders.get_test_extension_categories_with_1_level(
                    name_ext_gross_output_based
                )
            )
        ext_gross_output_based = e_dir.make_gross_output_based_extension(
            name_ext_gross_output_based
        )
        ext_shock_gross_output_based = se_dir.make_shock_s_x(
            name_ext_gross_output_based
        )

        # 3. embodied in import
        for director in [e_dir, se_dir]:
            director.set_extension_categories(
                builders.get_test_extension_categories_with_2_levels(
                    name_ext_embodied_in_import
                )
            )
        ext_embodied_in_import = e_dir.make_gross_output_based_extension(
            name_ext_embodied_in_import
        )
        ext_shock_embodied_in_import = se_dir.make_shock_m_row(
            name_ext_embodied_in_import
        )

        # Calculate and save extensions
        for ext_ in [
            ext_use_based,
            ext_gross_output_based,
            ext_embodied_in_import,
        ]:
            builders.randomize_dataset(ext_.dataset)
            ext_.reset_coefficients()
            ext_.calculate(system=ref_system)

            ext_.save_to_path(
                path=self.PATH_EXTENSION, export_format=cst.FORMAT_PICKLE
            )

        # Save extensions shocks
        for ext_shock in [
            ext_shock_use_based,
            ext_shock_gross_output_based,
            ext_shock_embodied_in_import,
        ]:
            builders.randomize_dataset(ext_shock.dataset)
            ext_shock.save_to_path(
                path=self.PATH_EXTENSION_SHOCK, export_format=cst.FORMAT_PICKLE
            )

        # Compute reference projected extensions
        ext_use_based.reset_for_shock()
        ext_use_based.shock(ext_shock_use_based)
        ext_use_based.calculate(ref_system)

        ext_gross_output_based.reset_for_shock()
        ext_gross_output_based.shock(ext_shock_gross_output_based)
        ext_gross_output_based.calculate(ref_system)

        ext_embodied_in_import.reset_for_shock()
        ext_embodied_in_import.shock(ext_shock_embodied_in_import)
        ext_embodied_in_import.calculate(ref_system)
        # ---

        for name, ref_extension in {
            name_ext_use_based: ext_use_based,
            name_ext_gross_output_based: ext_gross_output_based,
            name_ext_embodied_in_import: ext_embodied_in_import,
        }.items():
            e_dir.reset()
            se_dir.reset()

            # Compute loaded projected extension
            loaded_ext = e_dir.make_from_path(
                path=os.path.join(self.PATH_EXTENSION, name), load_data=True
            )
            loaded_ext_shock = se_dir.make_from_path(
                path=os.path.join(self.PATH_EXTENSION_SHOCK, name),
                load_data=True,
            )
            loaded_ext.reset_for_shock()
            loaded_ext.shock(loaded_ext_shock)
            loaded_ext.calculate(system=ref_system)

            # Compare with reference extension
            assert loaded_ext.equals(ref_extension)
