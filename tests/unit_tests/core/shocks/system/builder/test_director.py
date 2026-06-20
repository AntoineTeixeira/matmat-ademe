import os
import shutil

from matmat.core.detail_level import core as dl
from matmat.core.shocks.system import builder as sys_shock_builder
from matmat.core.shocks.system.core import SystemShock
import matmat.core.shocks.system.data.core as data
import matmat.utils.constants as cst

import tests.utils.constants as tests_cst
from tests.utils import builders


class TestSystemShockDirector:
    """
    Unit tests for class `SystemShockDirector`.
    The class `SystemShockBuilder` is tested through these test cases.
    """

    TMP_FOLDER = "tmp_shocks"

    def test_constructor(self):
        """
        Test function `__init__`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)
        assert sss_dir.regions is None
        assert sss_dir.sectors is None
        assert sss_dir.final_demand_categories is None
        assert sss_dir.extension_categories is None

    def test_setters_and_reset(self):
        """
        Test setters and function `reset`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)
        sss_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        sss_dir.id.base_year = 2000
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        assert sss_dir._regions.equals(tests_cst.DEFAULT_MULTI_REGIONS)
        assert sss_dir.id.base_year == 2000
        assert sss_dir._sectors.equals(builders.get_test_sectors())
        assert sss_dir._final_demand_categories.equals(
            tests_cst.DEFAULT_Y_CATEGORIES
        )

        sss_dir.reset()

        assert sss_dir._regions is None
        assert sss_dir.id.base_year == 0
        assert sss_dir._sectors is None
        assert sss_dir._final_demand_categories is None

    @staticmethod
    def check_shock(
        shock: SystemShock,
        regions: dl.RegionsDL,
        base_year: int,
        data_list: list,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
    ):
        map_name_class = {
            cst.D_A: data.AShockData,
            cst.D_K: data.KShockData,
            cst.D_Y: data.YShockData,
            cst.D_Y_K: data.YkShockData,
            cst.D_Z: data.ZShockData,
        }
        # Check data types
        for data_name in data_list:
            assert isinstance(
                shock.dataset.__getattribute__(f"_{data_name}"),
                map_name_class[data_name],
            )
        for data_name in cst.LIST_OF_SYSTEM_SHOCK_DATA:
            if data_name not in data_list:
                assert isinstance(
                    shock.dataset.__getattribute__(f"_{data_name}"),
                    data.NullSystemShockData,
                )

        # Check IDs
        assert shock.id.base_year == base_year

        for data_name in data_list:
            shock_data = shock.dataset.__getattribute__(f"_{data_name}")
            assert shock_data.structure._sectors.equals(sectors)
            assert shock_data.structure._regions.equals(regions)
            assert shock_data.structure._final_demand_categories.equals(
                final_demand_categories
            )

    def test_make_shock_complete(self):
        """
        Test function `make_shock_complete`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)

        sss_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        sss_dir.id.base_year = 2222
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        shock = sss_dir.make_shock_complete()

        self.check_shock(
            shock=shock,
            regions=tests_cst.DEFAULT_REGIONS,
            base_year=2222,
            data_list=cst.LIST_OF_SYSTEM_SHOCK_DATA,
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_a(self):
        """
        Test function `make_shock_a`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)

        sss_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        sss_dir.id.base_year = 2222
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        shock = sss_dir.make_shock_a()

        self.check_shock(
            shock=shock,
            regions=tests_cst.DEFAULT_REGIONS,
            base_year=2222,
            data_list=[cst.D_A],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_k(self):
        """
        Test function `make_shock_k`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)

        sss_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        sss_dir.id.base_year = 2222
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        shock = sss_dir.make_shock_k()

        self.check_shock(
            shock=shock,
            regions=tests_cst.DEFAULT_REGIONS,
            base_year=2222,
            data_list=[cst.D_K],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_y(self):
        """
        Test function `make_shock_y`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)

        sss_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        sss_dir.id.base_year = 2222
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        shock = sss_dir.make_shock_y()

        self.check_shock(
            shock=shock,
            regions=tests_cst.DEFAULT_REGIONS,
            base_year=2222,
            data_list=[cst.D_Y],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_exo(self):
        """
        Test function `make_shock_exo`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)

        sss_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        sss_dir.id.base_year = 2222
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        shock = sss_dir.make_shock_exo()

        self.check_shock(
            shock=shock,
            regions=tests_cst.DEFAULT_REGIONS,
            base_year=2222,
            data_list=[cst.D_A, cst.D_Y, cst.D_Y_K],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_standard(self):
        """
        Test function `make_shock_standard`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)

        sss_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        sss_dir.id.base_year = 2222
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        shock = sss_dir.make_shock_standard()

        self.check_shock(
            shock=shock,
            regions=tests_cst.DEFAULT_REGIONS,
            base_year=2222,
            data_list=[cst.D_A, cst.D_Y],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_from_path(self):
        """
        Test function `make_from_path`
        """
        sss_dir = sys_shock_builder.get_director(reset=True)
        sss_dir.set_regions(regions=tests_cst.DEFAULT_REGIONS)
        sss_dir.set_sectors(sectors=builders.get_test_sectors())
        sss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        ref_shock = sss_dir.make_shock_complete()

        if os.path.isdir(self.TMP_FOLDER):
            shutil.rmtree(self.TMP_FOLDER)
        os.mkdir(self.TMP_FOLDER)

        builders.randomize_dataset(ref_shock.dataset)
        ref_shock.save_to_path(path=self.TMP_FOLDER, export_format=cst.FORMAT_PICKLE)

        sss_dir.reset()
        test_shock = sss_dir.make_from_path(path=self.TMP_FOLDER, load_data=True)

        shutil.rmtree(self.TMP_FOLDER)

        assert test_shock.equals(ref_shock)
