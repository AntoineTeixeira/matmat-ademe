import os
import shutil

from matmat.core.detail_level import core as dl
from matmat.core.shocks.extension import builder as ext_shock_builder
from matmat.core.shocks.extension.core import ExtensionShock
import matmat.core.shocks.extension.data.core as data
import matmat.utils.constants as cst

import tests.utils.constants as tests_cst
from tests.utils import builders


class TestExtensionShockDirector:
    """
    Unit tests for class `ExtensionShockDirector`.
    The class `ExtensionBuilder` is tested through these test cases.
    """

    TMP_FOLDER = "tmp_shocks"

    def test_constructor(self):
        """
        Test function `__init__`
        """
        ses_dir = ext_shock_builder.get_director(reset=True)
        assert ses_dir.regions is None
        assert ses_dir.sectors is None
        assert ses_dir.final_demand_categories is None
        assert ses_dir.extension_categories is None
        assert ses_dir.id.name == "undefined"

    def test_setters_and_reset(self):
        """
        Test setters and function `reset`
        """
        ses_dir = ext_shock_builder.get_director(reset=True)

        ses_dir.id.extension_name = "test_extension"
        ses_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        ses_dir.set_sectors(builders.get_test_sectors())
        ses_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        assert ses_dir.id.name == "test_extension"
        assert ses_dir._regions.equals(tests_cst.DEFAULT_MULTI_REGIONS)
        assert ses_dir._sectors.equals(builders.get_test_sectors())
        assert ses_dir._final_demand_categories.equals(
            tests_cst.DEFAULT_Y_CATEGORIES
        )

        ses_dir.reset()

        assert ses_dir.id.name == "undefined"
        assert ses_dir._regions is None
        assert ses_dir._sectors is None
        assert ses_dir._final_demand_categories is None

    @staticmethod
    def check_shock(
        shock: ExtensionShock,
        name: str,
        regions: dl.RegionsDL,
        data_list: list,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
    ):
        map_name_class = {
            cst.D_S_X_DOM: data.SxDomShockData,
            cst.D_S_Y: data.SyShockData,
            cst.D_S_Z: data.SzShockData,
            cst.D_M_ROW: data.MRoWShockData,
        }
        # Check data types
        for data_name in data_list:
            assert isinstance(
                shock.dataset.__getattribute__(f"_{data_name}"),
                map_name_class[data_name],
            )
        for data_name in cst.LIST_OF_EXTENSION_SHOCK_DATA:
            if data_name not in data_list:
                assert isinstance(
                    shock.dataset.__getattribute__(f"_{data_name}"),
                    data.NullExtensionShockData,
                )

        # Check IDs
        assert shock.id.name == name

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
        ses_dir = ext_shock_builder.get_director(reset=True)

        ses_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        ses_dir.set_sectors(builders.get_test_sectors())
        ses_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ses_dir.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        shock = ses_dir.make_shock_complete(name="test_extension")

        self.check_shock(
            shock=shock,
            name="test_extension",
            regions=tests_cst.DEFAULT_REGIONS,
            data_list=cst.LIST_OF_EXTENSION_SHOCK_DATA,
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_s_x(self):
        """
        Test function `make_shock_s_x`
        """
        ses_dir = ext_shock_builder.get_director(reset=True)

        ses_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        ses_dir.set_sectors(builders.get_test_sectors())
        ses_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ses_dir.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        shock = ses_dir.make_shock_s_x(name="test_extension")

        self.check_shock(
            shock=shock,
            name="test_extension",
            regions=tests_cst.DEFAULT_REGIONS,
            data_list=[cst.D_S_X_DOM],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_s_y(self):
        """
        Test function `make_shock_s_y`
        """
        ses_dir = ext_shock_builder.get_director(reset=True)

        ses_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        ses_dir.set_sectors(builders.get_test_sectors())
        ses_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ses_dir.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        shock = ses_dir.make_shock_s_y(name="test_extension")

        self.check_shock(
            shock=shock,
            name="test_extension",
            regions=tests_cst.DEFAULT_REGIONS,
            data_list=[cst.D_S_Y],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_s_z(self):
        """
        Test function `make_shock_s_z`
        """
        ses_dir = ext_shock_builder.get_director(reset=True)

        ses_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        ses_dir.set_sectors(builders.get_test_sectors())
        ses_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ses_dir.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        shock = ses_dir.make_shock_s_z(name="test_extension")

        self.check_shock(
            shock=shock,
            name="test_extension",
            regions=tests_cst.DEFAULT_REGIONS,
            data_list=[cst.D_S_Z],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_shock_m_row(self):
        """
        Test function `make_shock_m_row`
        """
        ses_dir = ext_shock_builder.get_director(reset=True)

        ses_dir.set_regions(tests_cst.DEFAULT_REGIONS)
        ses_dir.set_sectors(builders.get_test_sectors())
        ses_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ses_dir.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        shock = ses_dir.make_shock_m_row(name="test_extension")

        self.check_shock(
            shock=shock,
            name="test_extension",
            regions=tests_cst.DEFAULT_REGIONS,
            data_list=[cst.D_M_ROW],
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

    def test_make_from_path(self):
        """
        Test function `make_from_path`
        """
        ses_dir = ext_shock_builder.get_director(reset=True)
        ses_dir.set_regions(regions=tests_cst.DEFAULT_REGIONS)
        ses_dir.set_sectors(sectors=builders.get_test_sectors())
        ses_dir.set_final_demand_categories(
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES
        )
        ses_dir.set_extension_categories(
            categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )
        ref_shock = ses_dir.make_shock_complete(
            name=tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name
        )
        builders.randomize_dataset(ref_shock.dataset)

        if os.path.isdir(self.TMP_FOLDER):
            shutil.rmtree(self.TMP_FOLDER)

        ref_shock.save_to_path(
            path=self.TMP_FOLDER, export_format=cst.FORMAT_PICKLE
        )

        ses_dir.reset()
        test_shock = ses_dir.make_from_path(
            path=os.path.join(self.TMP_FOLDER, ref_shock.name), load_data=True
        )

        shutil.rmtree(self.TMP_FOLDER)

        assert test_shock.equals(ref_shock)
