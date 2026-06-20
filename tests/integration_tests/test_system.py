import os
import shutil

import matmat.core.accounts.system.builder as s_builder
import matmat.core.shocks.system.builder as ss_builder
from tests.utils import builders, constants as tests_cst


class TestSystem:
    PATH_SYSTEM = "tmp_system"
    PATH_SYSTEM_SHOCK = "tmp_system_shock"

    @classmethod
    def setup_method(cls):
        os.makedirs(cls.PATH_SYSTEM, exist_ok=True)
        os.makedirs(cls.PATH_SYSTEM_SHOCK, exist_ok=True)

    @classmethod
    def teardown_method(cls):
        shutil.rmtree(cls.PATH_SYSTEM)
        shutil.rmtree(cls.PATH_SYSTEM_SHOCK)

    def test_tc_int_sys_001(self):
        """
        TC-INT-SYS-001

        Domestic and import regions
        """
        s_dir = s_builder.get_director()

        s_dir.set_regions(tests_cst.REGIONS_W_IMPORT)
        s_dir.set_sectors(builders.get_test_sectors())
        s_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        # Build system
        # ------------
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_system(ref_system)
        ref_system.reset_coefficients()
        truncated_system = ref_system.copy()
        ref_system.calculate()

        truncated_system.save_to_path(
            path=self.PATH_SYSTEM, export_format="pickle"
        )

        # Load system and compare
        # -----------------------
        s_dir.reset()
        test_system = s_dir.make_from_path(
            path=self.PATH_SYSTEM, load_data=True
        )
        test_system.calculate()
        assert test_system.equals(ref_system)

    def test_tc_int_sys_002(self):
        """
        TC-INT-SYS-002

        No import regions
        """
        s_dir = s_builder.get_director()

        s_dir.set_regions(regions=tests_cst.REGIONS_WO_IMPORT)
        s_dir.set_sectors(sectors=builders.get_test_sectors())
        s_dir.set_final_demand_categories(
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES
        )

        # Build system
        # ------------
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_system(ref_system)
        ref_system.reset_coefficients()
        truncated_system = ref_system.copy()
        ref_system.calculate()

        truncated_system.save_to_path(
            path=self.PATH_SYSTEM, export_format="pickle"
        )

        # Load system and compare
        # -----------------------
        s_dir.reset()
        test_system = s_dir.make_from_path(
            path=self.PATH_SYSTEM, load_data=True
        )
        test_system.calculate()

        assert test_system.equals(ref_system)

    def test_tc_int_sys_003(self):
        """
        TC-INT-SYS-003

        Test system and system shocks interface
        """
        s_dir = s_builder.get_director()
        ss_dir = ss_builder.get_director()

        for director in [s_dir, ss_dir]:
            director.set_regions(tests_cst.REGIONS_W_IMPORT)
            director.set_sectors(builders.get_test_sectors())
            director.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        # Build system
        # ------------
        ref_system = s_dir.make_exo_invest_matrix_system()
        builders.randomize_dataset(ref_system.dataset)
        ref_system.reset_coefficients()
        ref_system.calculate()
        ref_system.save_to_path(
            path=self.PATH_SYSTEM, export_format="pickle"
        )

        # Build system shock
        # ------------------
        ref_system_shock = ss_dir.make_shock_exo()
        builders.randomize_dataset(ref_system_shock.dataset)
        ref_system_shock.save_to_path(
            path=self.PATH_SYSTEM_SHOCK, export_format="pickle"
        )

        # Compute reference projected system
        # ----------------------------------
        ref_shocked_system = ref_system.copy()
        ref_shocked_system.reset_for_shock()
        ref_shocked_system.shock(ref_system_shock)
        ref_shocked_system.calculate()

        # Compute loaded projected system
        # -------------------------------
        s_dir.reset()
        ss_dir.reset()
        loaded_shocked_system = s_dir.make_from_path(
            path=self.PATH_SYSTEM, load_data=True
        )
        loaded_shocked_system.reset_for_shock()
        loaded_shocked_system.shock(
            shock=ss_dir.make_from_path(
                path=self.PATH_SYSTEM_SHOCK, load_data=True
            )
        )
        loaded_shocked_system.calculate()

        assert loaded_shocked_system.equals(ref_shocked_system)
