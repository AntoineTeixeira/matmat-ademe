import os
import shutil

import matmat.core.shocks.system.builder as ss_builder
from tests.utils import builders, constants as tests_cst


class TestSystemShock:
    PATH_SYSTEM = "tmp_system_shock"

    @classmethod
    def setup_method(cls):
        os.makedirs(cls.PATH_SYSTEM, exist_ok=True)

    @classmethod
    def teardown_method(cls):
        shutil.rmtree(cls.PATH_SYSTEM)

    def test_tc_int_ass_001(self):
        """
        TC-INT-ASS-001

        Domestic and import regions
        """
        ss_dir = ss_builder.get_director()

        ss_dir.set_regions(tests_cst.REGIONS_W_IMPORT)
        ss_dir.set_sectors(builders.get_test_sectors())
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        # Build system shock
        # ------------------
        ref_system_shock = ss_dir.make_shock_exo()
        builders.randomize_dataset(ref_system_shock.dataset)

        ref_system_shock.save_to_path(
            path=self.PATH_SYSTEM, export_format="pickle"
        )

        # Load system shock and compare
        # -----------------------------
        ss_dir.reset()
        test_system_shock = ss_dir.make_from_path(
            path=self.PATH_SYSTEM, load_data=True
        )

        assert test_system_shock.equals(ref_system_shock)

    def test_tc_int_ass_002(self):
        """
        TC-INT-ASS-002

        No import regions
        """
        ss_dir = ss_builder.get_director()

        ss_dir.set_regions(regions=tests_cst.REGIONS_WO_IMPORT)
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        ss_dir.set_final_demand_categories(
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES
        )

        # Build system shock
        # ------------------
        ref_system_shock = ss_dir.make_shock_standard()
        builders.randomize_dataset(ref_system_shock.dataset)

        ref_system_shock.save_to_path(
            path=self.PATH_SYSTEM, export_format="pickle"
        )

        # Load system shock and compare
        # -----------------------------
        ss_dir.reset()
        test_system_shock = ss_dir.make_from_path(
            path=self.PATH_SYSTEM, load_data=True
        )

        assert test_system_shock.equals(ref_system_shock)
