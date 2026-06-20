import os
import shutil
import pytest

from matmat.core.detail_level import core as dl
from matmat.core.shocks.system.core import SystemShock
from matmat.core.shocks.extension.core import ExtensionShock
import matmat.core.shocks.builder as s_builder
import matmat.core.shocks.system.builder as ss_builder
import matmat.core.shocks.extension.builder as se_builder
import matmat.utils.constants as cst
from matmat.utils.errors import MEExtensionNotFound, MEInconsistentDetailLevels

from tests.utils import builders, constants as tests_cst


class TestAccountsShock:
    """
    Test class to test the class AccountsShock
    """

    EXT_1 = "test_extension_1"
    EXT_2 = "test_extension_2"
    EXT_3 = "test_extension_3"

    PATH_TO_INIT_DIR = f"./{cst.DIR_SHOCKS}"
    PATH_TO_INIT_DIR_SYSTEM = f"{PATH_TO_INIT_DIR}/{cst.DIR_SYSTEM}"
    PATH_TO_INIT_DIR_EXTENSIONS = f"{PATH_TO_INIT_DIR}/{cst.DIR_EXTENSIONS}"

    # Entities
    # --------
    system_shock: SystemShock = None
    extension_shocks: dict[str, ExtensionShock] = None

    # Shock directors
    # ---------------
    s_dir = s_builder.get_director()
    ss_dir = ss_builder.get_director()
    se_dir = se_builder.get_director()

    @classmethod
    def setup_class(cls):

        os.makedirs(cls.PATH_TO_INIT_DIR, exist_ok=True)
        os.makedirs(cls.PATH_TO_INIT_DIR_SYSTEM, exist_ok=True)
        os.makedirs(cls.PATH_TO_INIT_DIR_EXTENSIONS, exist_ok=True)
        os.makedirs(
            f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}/{cls.EXT_1}", exist_ok=True
        )
        os.makedirs(
            f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}/{cls.EXT_2}", exist_ok=True
        )
        os.makedirs(
            f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}/{cls.EXT_3}", exist_ok=True
        )

        for director in [cls.s_dir, cls.ss_dir, cls.se_dir]:
            director.set_regions(tests_cst.DEFAULT_REGIONS)
            director.set_sectors(builders.get_test_sectors())
            director.set_final_demand_categories(
                tests_cst.DEFAULT_Y_CATEGORIES
            )

        cls.set_up_system()
        cls.set_up_extensions()

    @classmethod
    def set_up_system(cls):

        cls.ss_dir._id.base_year = 2000
        cls.system_shock = cls.ss_dir.make_shock_exo()
        builders.randomize_dataset(cls.system_shock.dataset)
        cls.system_shock.save_to_path(
            path=f"{cls.PATH_TO_INIT_DIR_SYSTEM}",
            export_format="pickle",
        )

    @classmethod
    def set_up_extensions(cls):

        cls.extension_shocks = {}
        cls.se_dir.set_extension_categories(
            dl.ExtensionCategoriesDL(
                extension_name=cls.EXT_1,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES.df,
            )
        )
        cls.extension_shocks[cls.EXT_1] = cls.se_dir.make_shock_from_data_list(
            data_list=[cst.D_S_Y, cst.D_S_Z],
            name=cls.EXT_1,
        )

        cls.se_dir.set_extension_categories(
            dl.ExtensionCategoriesDL(
                extension_name=cls.EXT_2,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES.df,
            )
        )
        cls.extension_shocks[cls.EXT_2] = cls.se_dir.make_shock_from_data_list(
            data_list=[cst.D_S_Y, cst.D_S_Z],
            name=cls.EXT_2,
        )

        cls.se_dir.set_extension_categories(
            dl.ExtensionCategoriesDL(
                extension_name=cls.EXT_3,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES.df,
            )
        )
        cls.extension_shocks[cls.EXT_3] = cls.se_dir.make_shock_from_data_list(
            data_list=[cst.D_S_Y, cst.D_S_Z],
            name=cls.EXT_3,
        )

        for key, value in cls.extension_shocks.items():
            builders.randomize_dataset(value.dataset)
            value.save_to_path(
                path=f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}",
                export_format="pickle",
            )

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.PATH_TO_INIT_DIR)

    def test_load_from_path(self):
        """
        Test function `load_from_path` and `get_extension_shock`

        Expected results:
            - Test that the data composing the shock are the same as the data
              exported
        """
        shock = self.s_dir.make_from_path(
            path=self.PATH_TO_INIT_DIR, load_data=False
        )
        shock.load_from_path(path=self.PATH_TO_INIT_DIR)

        # Check system shock
        assert shock.system_shock.dataset.equals(self.system_shock.dataset)
        for ext_name in [self.EXT_1, self.EXT_2, self.EXT_3]:
            assert shock.get_extension_shock(ext_name).dataset.equals(
                self.extension_shocks[ext_name].dataset
            )

    def test_save_to_path(self):
        """
        Test function `save_to_path`

        Expected results:
            - Check that the saved shock equals the loaded shock
        """
        ref_shock = self.s_dir.make_from_path(
            path=self.PATH_TO_INIT_DIR, load_data=False
        )
        ref_shock.load_from_path(path=self.PATH_TO_INIT_DIR)

        # Call function under test
        tmp_dir = "./tmp_dir"
        ref_shock.save_to_path(path=tmp_dir, export_format="pickle")

        test_shock = self.s_dir.make_from_path(path=tmp_dir, load_data=True)

        shutil.rmtree(tmp_dir)
        assert test_shock.equals(ref_shock)

    def test_add_extension_shock_with_inconsistent_regions(self):
        """
        Test methods `add_extension_shock` with regions detail levels
        different from the system shock regions detail levels
        """
        alternate_extension_name = "alternate_extension"

        # Build alternate regions DL
        dl_regions = dl.RegionsDL()
        dl_regions.load_from_path(
            path=os.path.join(self.PATH_TO_INIT_DIR_EXTENSIONS, self.EXT_1),
        )
        dl_regions_alternate = dl_regions.copy()
        dl_regions_alternate.df.iloc[
            0, len(dl_regions_alternate.df.columns) - 1
        ] = "an_alternate_region"
        # Build extensions categories for alternate extension
        dl_ext_cats = dl.ExtensionCategoriesDL(
            extension_name=alternate_extension_name,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES.df,
        )

        # Build and export alternate extension
        ext_director = se_builder.get_director(reset=True)
        ext_director.set_sectors(builders.get_test_sectors())
        ext_director.set_final_demand_categories(
            tests_cst.DEFAULT_Y_CATEGORIES
        )
        ext_director.set_regions(dl_regions_alternate)
        ext_director.set_extension_categories(dl_ext_cats)
        alternate_ext_shock = ext_director.make_shock_complete(
            name=alternate_extension_name
        )

        accounts = self.s_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )
        with pytest.raises(MEInconsistentDetailLevels):
            accounts.add_extension_shock(alternate_ext_shock)

    def test_add_extension_shock_with_inconsistent_sectors(self):
        """
        Test methods `add_extension_shock` with sectors detail levels
        different from the system shock sectors detail levels
        """
        alternate_extension_name = "alternate_extension"

        # Build alternate sectors DL
        dl_sectors = dl.SectorsDL()
        dl_sectors.load_from_path(
            path=os.path.join(self.PATH_TO_INIT_DIR_EXTENSIONS, self.EXT_1),
        )
        dl_sectors_alternate = dl_sectors.copy()
        dl_sectors_alternate.df.iloc[
            0, len(dl_sectors_alternate.df.columns) - 1
        ] = "an_alternate_sector"
        # Build extensions categories for alternate extension
        dl_ext_cats = dl.ExtensionCategoriesDL(
            extension_name=alternate_extension_name,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES.df,
        )

        # Build and export alternate extension
        ext_director = se_builder.get_director(reset=True)
        ext_director.set_regions(tests_cst.DEFAULT_REGIONS)
        ext_director.set_final_demand_categories(
            tests_cst.DEFAULT_Y_CATEGORIES
        )
        ext_director.set_sectors(dl_sectors_alternate)
        ext_director.set_extension_categories(dl_ext_cats)
        alternate_ext_shock = ext_director.make_shock_complete(
            name=alternate_extension_name
        )

        accounts = self.s_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )
        with pytest.raises(MEInconsistentDetailLevels):
            accounts.add_extension_shock(alternate_ext_shock)

    def test_add_extension_shock_with_inconsistent_final_demand_categories(
        self,
    ):
        """
        Test methods `add_extension_shock` with final demand categories detail levels
        different from the system shock final demand categories detail levels
        """
        alternate_extension_name = "alternate_extension"

        # Build alternate sectors DL
        dl_fdc = dl.FinalDemandCategoriesDL()
        dl_fdc.load_from_path(
            path=os.path.join(self.PATH_TO_INIT_DIR_EXTENSIONS, self.EXT_1),
        )
        dl_fdc_alternate = dl_fdc.copy()
        dl_fdc_alternate.df.iloc[
            0, len(dl_fdc_alternate.df.columns) - 1
        ] = "an_alternate_category"
        # Build extensions categories for alternate extension
        dl_ext_cats = dl.ExtensionCategoriesDL(
            extension_name=alternate_extension_name,
            df=tests_cst.DEFAULT_EXTENSION_CATEGORIES.df,
        )

        # Build and export alternate extension
        ext_director = se_builder.get_director(reset=True)
        ext_director.set_regions(tests_cst.DEFAULT_REGIONS)
        ext_director.set_sectors(builders.get_test_sectors())
        ext_director.set_final_demand_categories(dl_fdc_alternate)
        ext_director.set_extension_categories(dl_ext_cats)
        alternate_ext_shock = ext_director.make_shock_complete(
            name=alternate_extension_name
        )

        accounts = self.s_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )
        with pytest.raises(MEInconsistentDetailLevels):
            accounts.add_extension_shock(alternate_ext_shock)

    def test_get_extension_shock_error(self):
        """
        Test function `get_extension_shock` when the extension does not exist

        Expected results:
            - Check that an exception MEExtensionNotFound is raised
        """
        shock = self.s_dir.make_from_path(
            path=self.PATH_TO_INIT_DIR, load_data=False
        )

        with pytest.raises(MEExtensionNotFound):
            shock.get_extension_shock("wrong_extension")
