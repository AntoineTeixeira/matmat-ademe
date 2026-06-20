import os
import shutil
import copy

import pytest

from matmat.core.detail_level import core as dl
import matmat.core.accounts.builder as a_builder
import matmat.core.accounts.system.builder as s_builder
import matmat.core.accounts.extension.builder as e_builder
import matmat.core.shocks.builder as as_builder
import matmat.core.shocks.system.builder as ss_builder
import matmat.core.shocks.extension.builder as es_builder
import matmat.core.accounts.system.core as system_core
import matmat.core.accounts.extension.core as extension_core
import matmat.utils.constants as cst
import matmat.utils.errors as errors

import tests.utils.builders as builders
import tests.utils.constants as tests_cst
import tests.utils.spy as spy
from tests.utils import tools


class TestAccounts:
    """
    Test class to test the methods of the class `Accounts`
    """

    EXT_1 = "test_extension_1"
    EXT_2 = "test_extension_2"
    EXT_3 = "test_extension_3"
    STANDARD_SYSTEM = {
        cst.KEY_STRATEGY: "standard",
        cst.KEY_BASE_YEAR: "2019",
    }
    EXO_INVEST_MATRIX_SYSTEM = {
        cst.KEY_STRATEGY: "exo_invest_matrix",
        cst.KEY_BASE_YEAR: "2019",
    }
    EXTENSION_USE_BASED = {
        cst.KEY_EXTENSION_NAME: EXT_1,
        cst.KEY_STRATEGY: cst.STRATEGY_USE_BASED,
    }
    EXTENSION_GROSS_OUTPUT_BASED = {
        cst.KEY_EXTENSION_NAME: EXT_2,
        cst.KEY_STRATEGY: cst.STRATEGY_GROSS_OUTPUT_BASED,
    }
    EXTENSION_EMBODIED_IN_IMPORT = {
        cst.KEY_EXTENSION_NAME: EXT_3,
        cst.KEY_STRATEGY: cst.STRATEGY_EMBODIED_IN_IMPORT,
    }
    PATH_TO_INIT_DIR = "./tmp_accounts"
    PATH_TO_INIT_DIR_SYSTEM = f"{PATH_TO_INIT_DIR}/{cst.DIR_SYSTEM}"
    PATH_TO_INIT_DIR_EXTENSIONS = f"{PATH_TO_INIT_DIR}/{cst.DIR_EXTENSIONS}"
    # Data objects defined as class variables to be reused easily throughout
    # the tests
    # System
    a_data = builders.build_test_a()
    l_data = builders.build_test_l()
    x_data = builders.build_test_x()
    y_data = builders.build_test_y()
    z_data = builders.build_test_z()
    k_data = builders.build_test_k()
    l_k_data = builders.build_test_l_k()
    y_k_data = builders.build_test_y_k()
    sys_unit_data = builders.build_test_system_unit()
    # Extensions
    ext_1_unit_data = builders.build_test_extension_data(
        name=cst.UNIT,
        extension_name=EXT_1,
        strategy=cst.STRATEGY_USE_BASED,
    )
    ext_1_s_y_data = builders.build_test_s_y()
    ext_1_s_z_data = builders.build_test_s_z()
    ext_1_f_y_data = builders.build_test_f_y()
    ext_1_f_z_data = builders.build_test_f_z()

    ext_2_unit_data = builders.build_test_extension_data(
        name=cst.UNIT,
        extension_name=EXT_2,
        strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
    )
    ext_2_s_x_dom_data = builders.build_test_s_x_dom()
    ext_2_f_x_dom_data = builders.build_test_f_x_dom()

    ext_3_unit_data = builders.build_test_extension_data(
        name=cst.UNIT,
        extension_name=EXT_3,
        strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
    )
    ext_3_m_row_data = builders.build_test_m_row()

    # Accounts director
    acc_dir = a_builder.get_director()
    # Detail levels
    dl_regions = tests_cst.DEFAULT_REGIONS
    dl_sectors = builders.get_test_sectors()
    dl_fd = tests_cst.DEFAULT_Y_CATEGORIES

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

        cls.set_up_system()
        cls.set_up_extensions()

    @classmethod
    def set_up_system(cls):
        list_of_system_data = [
            cls.a_data,
            cls.l_data,
            cls.x_data,
            cls.y_data,
            cls.z_data,
            cls.k_data,
            cls.l_k_data,
            cls.y_k_data,
        ]

        for sys_data in list_of_system_data:
            if sys_data.is_df_empty():
                builders.randomize(sys_data.df)
            sys_data.df.to_pickle(
                f"{cls.PATH_TO_INIT_DIR_SYSTEM}/{sys_data.name}.pkl"
            )

        if cls.sys_unit_data.is_df_empty():
            builders.randomize_string_df(cls.sys_unit_data.df)
            cls.sys_unit_data.df.to_pickle(
                f"{cls.PATH_TO_INIT_DIR_SYSTEM}/{cst.UNIT}.pkl"
            )

        for dl_ in [cls.dl_regions, cls.dl_sectors, cls.dl_fd]:
            dl_.save_to_path(path=cls.PATH_TO_INIT_DIR_SYSTEM)

    @classmethod
    def set_up_extensions(cls):
        dict_of_ext_data = {
            cls.EXT_1: [
                cls.ext_1_s_y_data,
                cls.ext_1_s_z_data,
                cls.ext_1_f_y_data,
                cls.ext_1_f_z_data,
            ],
            cls.EXT_2: [
                cls.ext_2_s_x_dom_data,
                cls.ext_2_f_x_dom_data,
            ],
            cls.EXT_3: [
                cls.ext_3_m_row_data,
            ],
        }
        dict_of_unit_data = {
            cls.EXT_1: cls.ext_1_unit_data,
            cls.EXT_2: cls.ext_2_unit_data,
            cls.EXT_3: cls.ext_3_unit_data,
        }

        for key, value in dict_of_ext_data.items():
            for dl_ in [cls.dl_regions, cls.dl_sectors, cls.dl_fd]:
                dl_.save_to_path(
                    path=os.path.join(cls.PATH_TO_INIT_DIR_EXTENSIONS, key)
                )
            dl_ext_cats = dl.ExtensionCategoriesDL(
                extension_name=key,
                df=tests_cst.DEFAULT_EXTENSION_CATEGORIES.df,
            )
            dl_ext_cats.save_to_path(
                path=os.path.join(cls.PATH_TO_INIT_DIR_EXTENSIONS, key)
            )
            for ext_data in value:
                if ext_data.is_df_empty():
                    builders.randomize(ext_data.df)
                ext_data.df.to_pickle(
                    f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}/{key}/{ext_data.name}.pkl"
                )
        for key, value in dict_of_unit_data.items():
            builders.randomize_string_df(value.df)
            value.df.to_pickle(
                f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}/{key}/{cst.UNIT}.pkl"
            )

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.PATH_TO_INIT_DIR)

    def dump_system(self, kind: str):
        if kind == "standard":
            tools.dump_dict(
                dict_=self.STANDARD_SYSTEM, path=self.PATH_TO_INIT_DIR_SYSTEM
            )
        else:
            tools.dump_dict(
                dict_=self.EXO_INVEST_MATRIX_SYSTEM,
                path=self.PATH_TO_INIT_DIR_SYSTEM,
            )

    def dump_extensions(self):
        tools.dump_dict(
            dict_=self.EXTENSION_USE_BASED,
            path=f"{self.PATH_TO_INIT_DIR_EXTENSIONS}/{self.EXT_1}",
        )
        tools.dump_dict(
            dict_=self.EXTENSION_GROSS_OUTPUT_BASED,
            path=f"{self.PATH_TO_INIT_DIR_EXTENSIONS}/{self.EXT_2}",
        )
        tools.dump_dict(
            dict_=self.EXTENSION_EMBODIED_IN_IMPORT,
            path=f"{self.PATH_TO_INIT_DIR_EXTENSIONS}/{self.EXT_3}",
        )

    def test_load_from_path(self):
        """
        Test function `load_from_path`

        Expected results:
            - Test that the data composing the accounts are the same as the
              data exported
        """

        self.dump_system("standard")
        self.dump_extensions()

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )
        accounts.load_from_path(path=self.PATH_TO_INIT_DIR)

        # Check system
        assert accounts.system.dataset.A.equals(self.a_data)
        assert accounts.system.dataset.L.equals(self.l_data)
        assert accounts.system.dataset.x.equals(self.x_data)
        assert accounts.system.dataset.Y.equals(self.y_data)
        assert accounts.system.dataset.Z.equals(self.z_data)
        assert accounts.system.dataset.K.is_null()
        assert accounts.system.dataset.L_k.is_null()
        assert accounts.system.dataset.Y_k.is_null()
        # Check extension 1
        assert accounts.get_extension(self.EXT_1).dataset.S_Y.equals(
            self.ext_1_s_y_data
        )
        assert accounts.get_extension(self.EXT_1).dataset.S_Z.equals(
            self.ext_1_s_z_data
        )
        assert accounts.get_extension(self.EXT_1).dataset.F_Y.equals(
            self.ext_1_f_y_data
        )
        assert accounts.get_extension(self.EXT_1).dataset.F_Z.equals(
            self.ext_1_f_z_data
        )
        # Check extension 2
        assert accounts.get_extension(self.EXT_2).dataset.S_x_dom.equals(
            self.ext_2_s_x_dom_data
        )
        assert accounts.get_extension(self.EXT_2).dataset.F_x_dom.equals(
            self.ext_2_f_x_dom_data
        )

    def test_save_to_path(self):
        """
        Test function `save_to_path`

        Expected results:
            - Read the exported files and check that they match the exported
              reference accounts
        """

        self.dump_system("standard")
        self.dump_extensions()

        accounts_ref = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )
        accounts_ref.load_from_path(self.PATH_TO_INIT_DIR)

        export_path = "./tmp_exports"
        if not os.path.isdir(export_path):
            os.mkdir(export_path)

        accounts_ref.save_to_path(
            path=export_path, export_format=cst.FORMAT_PICKLE
        )

        accounts_test = self.acc_dir.make_from_path(export_path)
        accounts_test.load_from_path(export_path)

        shutil.rmtree(export_path)

        # Check system
        assert accounts_test.system.dataset.A.equals(
            accounts_ref.system.dataset.A
        )
        assert accounts_test.system.dataset.L.equals(
            accounts_ref.system.dataset.L
        )
        assert accounts_test.system.dataset.x.equals(
            accounts_ref.system.dataset.x
        )
        assert accounts_test.system.dataset.Y.equals(
            accounts_ref.system.dataset.Y
        )
        assert accounts_test.system.dataset.Z.equals(
            accounts_ref.system.dataset.Z
        )
        # Check extension 1
        test_extension_1 = accounts_test.get_extension(self.EXT_1)
        ref_extension_1 = accounts_ref.get_extension(self.EXT_1)
        assert test_extension_1.dataset.S_Y.equals(ref_extension_1.dataset.S_Y)
        assert test_extension_1.dataset.S_Z.equals(ref_extension_1.dataset.S_Z)
        assert test_extension_1.dataset.F_Y.equals(ref_extension_1.dataset.F_Y)
        assert test_extension_1.dataset.F_Z.equals(ref_extension_1.dataset.F_Z)
        # Check extension 2
        test_extension_2 = accounts_test.get_extension(self.EXT_2)
        ref_extension_2 = accounts_ref.get_extension(self.EXT_2)
        assert test_extension_2.dataset.S_x_dom.equals(
            ref_extension_2.dataset.S_x_dom
        )
        assert test_extension_2.dataset.F_x_dom.equals(
            ref_extension_2.dataset.F_x_dom
        )
        # Check extension 3
        test_extension_3 = accounts_test.get_extension(self.EXT_3)
        ref_extension_3 = accounts_ref.get_extension(self.EXT_3)
        assert test_extension_3.dataset.M_RoW.equals(
            ref_extension_3.dataset.M_RoW
        )

    def test_calculate(self, mocker):
        """
        Test function `calculate`

        Expected results:
            - Check that the `calculate` method of System is called with the
              correct arguments
            - For each extension, check that the `calculate` method is called
              with the correct arguments
        """
        self.dump_system("exo")
        self.dump_extensions()

        spy_system = mocker.spy(system_core.System, "calculate")
        spy_extensions = mocker.spy(extension_core.Extension, "calculate")

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )

        accounts.calculate()

        spy_system.assert_called_once_with(accounts.system)
        for index, extension in enumerate(accounts.list_extensions()):
            spy.check_specific_call_with_args(
                spy_extensions,
                call_number=index + 1,
                args=[accounts.list_extensions()[index]],
                kwargs={"system": accounts.system},
            )

    def test_calculate_system(self, mocker):
        """
        Test function `calculate_system`

        Expected results:
            - Check that the `calculate` method of System is called with the
              correct arguments
            - Check that the `calculate` method of Extension is never called
        """
        self.dump_system("exo")
        self.dump_extensions()

        spy_system = mocker.spy(system_core.System, "calculate")
        spy_extensions = mocker.spy(extension_core.Extension, "calculate")

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )

        accounts.calculate_system()

        spy_system.assert_called_once_with(accounts.system)
        spy_extensions.assert_not_called()

    def test_calculate_extensions(self, mocker):
        """
        Test function `calculate_extensions`

        Expected results:
            - Check that the `calculate` method of System is never called
            - For each extension, check that the `calculate` method is called
              with the correct arguments
        """
        self.dump_system("exo")
        self.dump_extensions()

        spy_system = mocker.spy(system_core.System, "calculate")
        spy_extensions = mocker.spy(extension_core.Extension, "calculate")

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )

        accounts.calculate_extensions()

        spy_system.assert_not_called()
        for index, extension in enumerate(accounts.list_extensions()):
            spy.check_specific_call_with_args(
                spy_extensions,
                call_number=index + 1,
                args=[accounts.list_extensions()[index]],
                kwargs={"system": accounts.system},
            )

    def test_shock(self, mocker):
        """
        Test function `shock`

        In this test case, the shock is composed with:
            - a system shock with dA and imp_dom_ratio matrices
            - an extension shock for the first extension with dS_x matrix

        Expected results:
            - Check that the `shock` method of `System` is called with
              the correct arguments
            - Check that the `shock` method of `Extension` for
              the first extension, and never called for the second
        """
        self.dump_system("standard")
        self.dump_extensions()

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )

        sys_shock_dir = ss_builder.get_director()
        ext_shock_dir = es_builder.get_director()

        for director in sys_shock_dir, ext_shock_dir:
            director.set_regions(self.acc_dir.system_director.regions)
            director.set_sectors(self.acc_dir.system_director.sectors)
            director.set_final_demand_categories(
                self.acc_dir.system_director.final_demand_categories
            )
            director.id.base_year = 2000
        ext_shock_dir.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        sys_shock = sys_shock_dir.make_shock_a()
        ext_shock = ext_shock_dir.make_shock_s_x(name=self.EXT_1)

        shock = (
            as_builder.get_director().make_from_system_and_extensions_shocks(
                system_shock=sys_shock,
                extensions_shocks={ext_shock.name: ext_shock},
            )
        )

        # Randomize shock data so that it is not empty
        builders.randomize(
            shock.system_shock.dataset.dA.df, full_randomization=False
        )
        builders.randomize(
            shock.get_extension_shock(self.EXT_1).dataset.dS_x_dom.df,
            full_randomization=False,
        )

        # Initialize spies
        spy_system = mocker.spy(system_core.System, "shock")
        spy_extensions = mocker.spy(extension_core.Extension, "shock")

        accounts.reset_for_shock()
        accounts.shock(shock=shock)

        spy_system.assert_called_once_with(
            accounts.system, shock=shock.system_shock
        )
        spy_extensions.assert_called_once_with(
            accounts.get_extension(self.EXT_1),
            shock=shock.get_extension_shock(self.EXT_1),
        )

    def test_reset_for_shock(self, mocker):
        """
        Test function `reset_for_shock`

        Expected results:
            - Check that the method `reset_for_shock` is called for the system
              and the extensions classes
        """
        self.dump_system("standard")
        self.dump_extensions()

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )

        spy_system = mocker.spy(system_core.System, "reset_for_shock")
        spy_extensions = mocker.spy(
            extension_core.Extension, "reset_for_shock"
        )

        accounts.reset_for_shock()

        spy_system.assert_called_once()

        for index, extension in enumerate(accounts.list_extensions()):
            spy.check_specific_call_with_args(
                spy_extensions,
                call_number=index + 1,
                args=[accounts.list_extensions()[index]],
                kwargs={},
            )

    def test_reset_coefficients(self, mocker):
        """
        Test function `reset_coefficients`

        Expected results:
            - Check that the method `reset_coefficients` is called for the
              system and the extensions classes
        """
        self.dump_system("standard")
        self.dump_extensions()

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )

        spy_system = mocker.spy(system_core.System, "reset_coefficients")
        spy_extensions = mocker.spy(
            extension_core.Extension, "reset_coefficients"
        )

        accounts.reset_coefficients()

        spy_system.assert_called_once()

        for index, extension in enumerate(accounts.list_extensions()):
            spy.check_specific_call_with_args(
                spy_extensions,
                call_number=index + 1,
                args=[accounts.list_extensions()[index]],
                kwargs={},
            )

    def test_reset_fluxes(self, mocker):
        """
        Test function `reset_fluxes`

        Expected results:
            - Check that the method `reset_fluxes` is called for the system and the extensions classes
        """
        self.dump_system("standard")
        self.dump_extensions()

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )

        spy_system = mocker.spy(system_core.System, "reset_fluxes")
        spy_extensions = mocker.spy(extension_core.Extension, "reset_fluxes")

        accounts.reset_fluxes()

        spy_system.assert_called_once()

        for index, extension in enumerate(accounts.list_extensions()):
            spy.check_specific_call_with_args(
                spy_extensions,
                call_number=index + 1,
                args=[accounts.list_extensions()[index]],
                kwargs={},
            )

    def test_make_system_and_extensions_consistent(self, mocker):
        """
        Test function `make_system_and_extensions_consistent` called through
        `make_from_path`

        Expected results:
            - The system is standard. Check that the method
              `tune_dataset` is called for each extension
        """
        spy_extensions = mocker.spy(extension_core.Extension, "tune_dataset")

        self.dump_system("standard")
        self.dump_extensions()

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )

        for index, extension in enumerate(accounts.list_extensions()):
            spy.check_specific_call_with_args(
                spy_extensions,
                call_number=index + 1,
                args=[accounts.list_extensions()[index]],
                kwargs={"system": accounts.system},
            )

    def test_aggregate_sectors(self, mocker):
        """
        Test function `aggregate` with sectors bridge

        Expected results:
            - Check that the method `aggregate` of System and Extension
              are called with the proper arguments
        """
        sys_id = copy.deepcopy(self.STANDARD_SYSTEM)
        tools.dump_dict(sys_id, path=self.PATH_TO_INIT_DIR_SYSTEM)

        for extension in [
            self.EXTENSION_USE_BASED,
            self.EXTENSION_GROSS_OUTPUT_BASED,
            self.EXTENSION_EMBODIED_IN_IMPORT,
        ]:
            ext_id = copy.deepcopy(extension)
            tools.dump_dict(
                ext_id,
                path=f"{self.PATH_TO_INIT_DIR_EXTENSIONS}/{ext_id[cst.KEY_EXTENSION_NAME]}",
            )

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )
        # Remove extensions "gross_output_based" and "embodied_in_import"
        # as they are not compatible with aggregation matrix
        accounts.remove_extension(self.EXT_2)
        accounts.remove_extension(self.EXT_3)

        bridge_ = builders.get_test_sectors_bridge()

        # Initialize accounts
        builders.randomize_system(accounts.system)
        # Set uniform unit to avoid error raised when checking aggregation
        # consistency with unit vector
        accounts.system.dataset.unit.set_values("kT")
        for extension in accounts.list_extensions():
            builders.randomize_extension(extension)
            # Set uniform unit to avoid error raised when checking aggregation
            # consistency with unit vector
            extension.dataset.unit.set_values("kT")

        # Set up spies
        spy_system = mocker.spy(system_core.System, "aggregate")
        spy_extensions = mocker.spy(extension_core.Extension, "aggregate")

        accounts.aggregate(bridge_)

        spy_system.assert_called_once_with(accounts.system, bridge_)
        for index in range(0, len(accounts.extensions)):
            spy.check_specific_call_with_args(
                function_spy=spy_extensions,
                call_number=index + 1,
                args=[accounts.list_extensions()[index], bridge_],
                kwargs={},
            )

    def test_aggregate_with_multiple_bridges(self, mocker):
        """
        Test method `aggregate` with multiple bridges
        """
        s_director = s_builder.get_director(reset=True)
        e_director = e_builder.get_director(reset=True)
        for director in s_director, e_director:
            director.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
            director.set_sectors(builders.get_test_sectors())
            director.set_final_demand_categories(tests_cst.Y_CATEGORIES_DISAGG)

        system = s_director.make_standard_system()
        e_director.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_2_LEVELS
        )
        ext_1 = e_director.make_use_based_extension(name=self.EXT_1)
        ext_2 = e_director.make_gross_output_based_extension(name=self.EXT_2)
        ext_3 = e_director.make_embodied_in_import_extension(name=self.EXT_3)
        accounts = self.acc_dir.make_from_system_and_extensions(
            system=system,
            extensions={
                self.EXT_1: ext_1,
                self.EXT_2: ext_2,
                self.EXT_3: ext_3,
            },
        )

        regions_bridge = builders.get_test_regions_bridge()
        sectors_bridge = builders.get_test_sectors_bridge()
        ec_bridge = builders.get_test_extension_categories_bridge()
        fdc_bridge = builders.get_test_final_demand_categories_bridge()

        # Set up spies
        spy_system = mocker.spy(system_core.System, "aggregate")
        spy_extensions = mocker.spy(extension_core.Extension, "aggregate")

        # Set bridge extension name
        # This means the bridge shall apply to ext_2
        ext_2_ec_bridge = ec_bridge.copy()
        ext_2_ec_bridge.sheet_name = ext_2.name

        # Build bridge list
        bridges = [regions_bridge, sectors_bridge, fdc_bridge, ext_2_ec_bridge]
        filtered_bridges = [regions_bridge, sectors_bridge, fdc_bridge]

        # Call function under test
        accounts.aggregate(*bridges)

        # Check correct call of system aggregate method
        spy_system.assert_called_once_with(accounts.system, *bridges)
        for index, extension in enumerate(accounts.list_extensions()):
            if extension is ext_2:
                spy.check_specific_call_with_args(
                    function_spy=spy_extensions,
                    call_number=index + 1,
                    args=[extension, *bridges],
                    kwargs={},
                )
            else:
                spy.check_specific_call_with_args(
                    function_spy=spy_extensions,
                    call_number=index + 1,
                    args=[extension, *filtered_bridges],
                    kwargs={},
                )

    def test_add_and_remove_extension(self):
        """
        Test methods `add_extension` and `remove_extension`
        """
        self.dump_system("standard")
        self.dump_extensions()

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=False
        )

        ext = self.acc_dir.extension_director.make_by_output_extension(
            "new_extension"
        )

        assert ext not in accounts.list_extensions()
        accounts.add_extension(new_extension=ext)
        assert ext in accounts.list_extensions()

        with pytest.raises(errors.MEExtensionAlreadyExisting):
            accounts.add_extension(new_extension=ext)

        accounts.remove_extension(extension_name="new_extension")
        assert ext not in accounts.list_extensions()

    def test_add_extension_with_inconsistent_regions(self):
        """
        Test methods `add_extension` with regions detail levels
        different from the system regions detail levels
        """
        self.dump_system("standard")
        self.dump_extensions()

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
        ext_director = e_builder.get_director(reset=True)
        ext_director.set_sectors(builders.get_test_sectors())
        ext_director.set_final_demand_categories(
            tests_cst.DEFAULT_Y_CATEGORIES
        )
        ext_director.set_regions(dl_regions_alternate)
        ext_director.set_extension_categories(dl_ext_cats)
        alternate_extension = ext_director.make_use_based_extension(
            name=alternate_extension_name
        )

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )
        with pytest.raises(errors.MEInconsistentDetailLevels):
            accounts.add_extension(alternate_extension)

    def test_add_extension_with_inconsistent_sectors(self):
        """
        Test methods `add_extension` with sectors detail levels
        different from the system sectors detail levels
        """
        self.dump_system("standard")
        self.dump_extensions()

        alternate_extension_name = "alternate_extension"

        # Build alternate final demand categories DL
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
        ext_director = e_builder.get_director(reset=True)
        ext_director.set_sectors(dl_sectors_alternate)
        ext_director.set_regions(tests_cst.DEFAULT_REGIONS)
        ext_director.set_final_demand_categories(
            tests_cst.DEFAULT_Y_CATEGORIES
        )
        ext_director.set_extension_categories(dl_ext_cats)
        alternate_extension = ext_director.make_use_based_extension(
            name=alternate_extension_name
        )

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )
        with pytest.raises(errors.MEInconsistentDetailLevels):
            accounts.add_extension(alternate_extension)

    def test_add_extension_with_inconsistent_final_demand_categories(self):
        """
        Test methods `add_extension` with final demand categories detail levels
        different from the system final demand categories detail levels
        """
        self.dump_system("standard")
        self.dump_extensions()

        alternate_extension_name = "alternate_extension"

        # Build alternate final demand categories DL
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
        ext_director = e_builder.get_director(reset=True)
        ext_director.set_sectors(builders.get_test_sectors())
        ext_director.set_regions(tests_cst.DEFAULT_REGIONS)
        ext_director.set_final_demand_categories(dl_fdc_alternate)
        ext_director.set_extension_categories(dl_ext_cats)
        alternate_extension = ext_director.make_use_based_extension(
            name=alternate_extension_name
        )

        accounts = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )
        with pytest.raises(errors.MEInconsistentDetailLevels):
            accounts.add_extension(alternate_extension)

    def test_equals(self):
        """
        Test method 'equals'
        """
        self.dump_system("standard")
        self.dump_extensions()

        accounts_1 = self.acc_dir.make_from_path(
            self.PATH_TO_INIT_DIR, load_data=True
        )

        accounts_2 = copy.deepcopy(accounts_1)

        assert accounts_1.equals(accounts_2)

        accounts_1.system.dataset.x.set_values(1.0)
        accounts_2.system.dataset.x.set_values(0.0)

        assert not accounts_1.equals(accounts_2)
