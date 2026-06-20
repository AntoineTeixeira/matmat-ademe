import os
import shutil

import matmat.core.shocks.extension.builder as se_builder
from tests.utils import builders, constants as tests_cst


class TestExtensionShock:
    PATH_EXTENSION = "tmp_extension_shocks"

    @classmethod
    def setup_method(cls):
        os.makedirs(cls.PATH_EXTENSION, exist_ok=True)

    @classmethod
    def teardown_method(cls):
        shutil.rmtree(cls.PATH_EXTENSION)

    def test_tc_int_ase_001(self):
        """
        TC-INT-ASE-001

        Domestic and import regions
        """
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"
        name_ext_embodied_in_import = "ext_embodied_in_import"

        se_dir = se_builder.get_director()

        se_dir.set_regions(tests_cst.REGIONS_W_IMPORT)
        se_dir.set_sectors(builders.get_test_sectors())
        se_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        # Build extension shocks
        # ----------------------
        se_dir.set_extension_categories(
            builders.get_test_extension_categories_with_2_levels(
                name_ext_use_based
            )
        )
        ref_extension_shock_use_based = se_dir.make_shock_s_x(
            name=name_ext_use_based
        )
        se_dir.set_extension_categories(
            builders.get_test_extension_categories_with_1_level(
                name_ext_gross_output_based
            )
        )
        ref_extension_shock_gross_output_based = se_dir.make_shock_s_z(
            name=name_ext_gross_output_based
        )
        se_dir.set_extension_categories(
            builders.get_test_extension_categories_with_1_level(
                name_ext_embodied_in_import
            )
        )
        ref_extension_shock_embodied_in_import = se_dir.make_shock_m_row(
            name=name_ext_embodied_in_import
        )

        for ref_ext_shock in [
            ref_extension_shock_use_based,
            ref_extension_shock_gross_output_based,
            ref_extension_shock_embodied_in_import,
        ]:
            builders.randomize_dataset(ref_ext_shock.dataset)
            ref_ext_shock.save_to_path(
                path=self.PATH_EXTENSION, export_format="pickle"
            )

            se_dir.reset()
            test_ref_ext_shock = se_dir.make_from_path(
                path=os.path.join(self.PATH_EXTENSION, ref_ext_shock.name),
                load_data=True,
            )
            assert test_ref_ext_shock.equals(ref_ext_shock)

    def test_tc_int_ase_002(self):
        """
        TC-INT-ASE-002

        No import regions
        """
        name_ext_use_based = "ext_use_based"
        name_ext_gross_output_based = "ext_gross_output_based"

        se_dir = se_builder.get_director()

        se_dir.set_regions(tests_cst.REGIONS_WO_IMPORT)
        se_dir.set_sectors(builders.get_test_sectors())
        se_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        # Build extension shocks
        # ----------------------
        se_dir.set_extension_categories(
            builders.get_test_extension_categories_with_2_levels(
                name_ext_use_based
            )
        )
        ref_extension_shock_use_based = se_dir.make_shock_s_x(
            name=name_ext_use_based
        )
        se_dir.set_extension_categories(
            builders.get_test_extension_categories_with_1_level(
                name_ext_gross_output_based
            )
        )
        ref_extension_shock_gross_output_based = se_dir.make_shock_s_z(
            name=name_ext_gross_output_based
        )

        for ref_ext_shock in [
            ref_extension_shock_use_based,
            ref_extension_shock_gross_output_based,
        ]:
            builders.randomize_dataset(ref_ext_shock.dataset)
            ref_ext_shock.save_to_path(
                path=self.PATH_EXTENSION, export_format="pickle"
            )

            se_dir.reset()
            test_ref_ext_shock = se_dir.make_from_path(
                path=os.path.join(self.PATH_EXTENSION, ref_ext_shock.name),
                load_data=True,
            )
            assert test_ref_ext_shock.equals(ref_ext_shock)
