import os
import shutil

from matmat.core.accounts.system import builder as sys_builder
import matmat.utils.constants as cst
from matmat.core.accounts.system.strategies import calcul
import matmat.core.accounts.system.data.core as data

import tests.utils.constants as tests_cst
import tests.utils.builders as builders
from tests.utils import tools


class TestSystemDirector:
    """
    Unit tests for class `SystemDirector`.
    The class `SSBuilder` is tested through these test cases.
    """

    def test_constructor(self):
        """
        Test function `__init__`
        """
        ss_dir = sys_builder.get_director(reset=True)
        assert ss_dir.regions is None
        assert ss_dir.sectors is None
        assert ss_dir.final_demand_categories is None
        assert ss_dir.extension_categories is None

    def test_setters_and_reset(self):
        """
        Test setters and function `reset`
        """
        ss_dir = sys_builder.get_director(reset=True)
        ss_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        ss_dir.id.base_year = 2000
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        assert ss_dir._regions.equals(tests_cst.DEFAULT_MULTI_REGIONS)
        assert ss_dir.id.base_year == 2000
        assert ss_dir._sectors.equals(builders.get_test_sectors())
        assert ss_dir._final_demand_categories.equals(
            tests_cst.DEFAULT_Y_CATEGORIES
        )

        ss_dir.reset()

        assert ss_dir._regions is None
        assert ss_dir.id.base_year == 0
        assert ss_dir._sectors is None
        assert ss_dir._final_demand_categories is None

    def test_make_standard(self):
        """
        Test function `make_standard_system`
        """
        ss_dir = sys_builder.get_director(reset=True)

        ss_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ss_dir.id.base_year = 2000
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        system = ss_dir.make_standard_system()

        # Check strategy
        assert isinstance(system.calcul, calcul.Standard)
        # Check data
        # Not null data
        list_of_not_null_data = [cst.A, cst.L, cst.X, cst.Y, cst.Z, cst.UNIT]
        assert isinstance(system.dataset.A, data.AData)
        assert isinstance(system.dataset.L, data.LData)
        assert isinstance(system.dataset.x, data.XData)
        assert isinstance(system.dataset.Y, data.YData)
        assert isinstance(system.dataset.Z, data.ZData)
        assert isinstance(system.dataset.unit, data.UnitSystemData)
        # Null data
        for data_ in system.dataset.data:
            if data_.name not in list_of_not_null_data:
                assert isinstance(data_, data.NullSystemData)

        # Check id
        assert system.id.base_year == 2000

        for data_name in cst.LIST_OF_SYSTEM_DATA:
            sys_data = system.dataset.__getattribute__(f"_{data_name}")
            if not sys_data.is_null() and sys_data._NAME != cst.UNIT:
                # Check sectors
                assert sys_data.structure._sectors.equals(
                    builders.get_test_sectors()
                )

    def test_make_exo(self):
        """
        Test function `make_exo_invest_matrix_system`
        """
        ss_dir = sys_builder.get_director(reset=True)

        ss_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ss_dir.id.base_year = 2000
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        system = ss_dir.make_exo_invest_matrix_system()

        # Check strategy
        assert isinstance(system.calcul, calcul.ExoInvestMatrix)
        # Check data
        # Not null data
        list_of_not_null_data = [
            cst.A,
            cst.L,
            cst.X,
            cst.Y,
            cst.Z,
            cst.UNIT,
            cst.L_K,
            cst.K,
            cst.Y_K,
        ]
        assert isinstance(system.dataset.A, data.AData)
        assert isinstance(system.dataset.L, data.LData)
        assert isinstance(system.dataset.x, data.XData)
        assert isinstance(system.dataset.Y, data.YData)
        assert isinstance(system.dataset.Z, data.ZData)
        assert isinstance(system.dataset.unit, data.UnitSystemData)
        assert isinstance(system.dataset.L_k, data.LKData)
        assert isinstance(system.dataset.K, data.KData)
        assert isinstance(system.dataset.Y_k, data.YKData)
        # Null data
        for data_ in system.dataset.data:
            if data_.name not in list_of_not_null_data:
                assert isinstance(data_, data.NullSystemData)
        # Check id
        assert system.id.base_year == 2000

        for data_name in cst.LIST_OF_SYSTEM_DATA:
            sys_data = system.dataset.__getattribute__(f"_{data_name}")
            if not sys_data.is_null() and sys_data._NAME != cst.UNIT:
                # Check sectors
                assert sys_data.structure._sectors.equals(
                    builders.get_test_sectors()
                )

    def test_make_endo(self):
        """
        Test function `make_endo_invest_matrix_system`
        """
        ss_dir = sys_builder.get_director(reset=True)

        ss_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ss_dir.id.base_year = 2000
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        system = ss_dir.make_endo_invest_matrix_system()

        # Check strategy
        assert isinstance(system.calcul, calcul.EndoInvestMatrix)
        # Check data
        # Not null data
        list_of_not_null_data = [
            cst.A,
            cst.L,
            cst.X,
            cst.Y,
            cst.Z,
            cst.UNIT,
            cst.L_K,
            cst.K,
            cst.Y_K,
        ]
        assert isinstance(system.dataset.A, data.AData)
        assert isinstance(system.dataset.L, data.LData)
        assert isinstance(system.dataset.x, data.XData)
        assert isinstance(system.dataset.Y, data.YData)
        assert isinstance(system.dataset.Z, data.ZData)
        assert isinstance(system.dataset.unit, data.UnitSystemData)
        assert isinstance(system.dataset.L_k, data.LKData)
        assert isinstance(system.dataset.K, data.KData)
        assert isinstance(system.dataset.Y_k, data.YKData)
        # Null data
        for data_ in system.dataset.data:
            if data_.name not in list_of_not_null_data:
                assert isinstance(data_, data.NullSystemData)
        # Check id
        assert system.id.base_year == 2000

        for data_name in cst.LIST_OF_SYSTEM_DATA:
            sys_data = system.dataset.__getattribute__(f"_{data_name}")
            if not sys_data.is_null() and sys_data._NAME != cst.UNIT:
                # Check sectors
                assert sys_data.structure._sectors.equals(
                    builders.get_test_sectors()
                )

    def test_make_from_path_all_files(self):
        """
        Test functions `make_from_path`

        Expected results:
            - The system exported and the system made from files are equal
        """
        ss_dir = sys_builder.get_director(reset=True)
        ss_dir.set_regions(regions=tests_cst.DEFAULT_MULTI_REGIONS)
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        # Generate system files
        export_dir = "tmp_export_dir"
        ref_system = ss_dir.make_exo_invest_matrix_system()
        builders.randomize_system(ref_system)
        ref_system.save_to_path(path=export_dir, export_format="pickle")

        # Instantiate system from these files
        test_system = ss_dir.make_from_path(path=export_dir, load_data=True)

        shutil.rmtree(export_dir)

        assert test_system.equals(ref_system)

    def test_make_from_path_ignored_files(self):
        """
        Test functions `make_from_path`

        Expected results:
            - The files not related to standard strategy shall be ignored
        """
        ss_dir = sys_builder.get_director(reset=True)
        ss_dir.set_regions(regions=tests_cst.DEFAULT_MULTI_REGIONS)
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        # Generate system files
        export_dir = "tmp_export_dir"
        ref_system = ss_dir.make_exo_invest_matrix_system()
        builders.randomize_system(ref_system)
        # Override strategy for test purpose
        ref_system.id.strategy = calcul.EnumSystemCalcul.STANDARD.value
        ref_system.save_to_path(path=export_dir, export_format="csv")

        ss_dir.reset()
        ss_dir.set_regions(regions=tests_cst.DEFAULT_MULTI_REGIONS)
        ss_dir.set_sectors(sectors=builders.get_test_sectors())
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        test_system = ss_dir.make_from_path(path=export_dir, load_data=True)

        shutil.rmtree(export_dir)

        assert test_system.dataset.A.equals(ref_system.dataset.A)
        assert test_system.dataset.L.equals(ref_system.dataset.L)
        assert test_system.dataset.x.equals(ref_system.dataset.x)
        assert test_system.dataset.Y.equals(ref_system.dataset.Y)
        assert test_system.dataset.Z.equals(ref_system.dataset.Z)
        # K, L_k, L shall be null for a standard system
        assert isinstance(test_system.dataset.K, data.NullSystemData)
        assert isinstance(test_system.dataset.L_k, data.NullSystemData)
        assert isinstance(test_system.dataset.Y_k, data.NullSystemData)
        # Check strategy
        assert isinstance(test_system.calcul, calcul.Standard)

    def test_make_from_path_missing_files(self):
        """
        Test functions `make_from_path`

        Expected results:
            - The system is standard and made from only one file. Check
              that the file is read properly, and that the system data
              are instantiated w.r.t. standard strategy.
        """
        ss_dir = sys_builder.get_director(reset=True)
        ss_dir.set_regions(regions=tests_cst.DEFAULT_REGIONS)
        ss_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        ss_dir.set_sectors(sectors=builders.get_test_sectors())

        # Generate system files
        export_dir = "tmp_export_dir"
        a = builders.build_test_a()
        builders.randomize(a.df)

        os.makedirs(export_dir, exist_ok=True)
        a.save_to_path(path=export_dir, export_format="excel")

        # Generate detail levels file
        for dl_ in ss_dir.detail_levels:
            dl_.save_to_path(path=export_dir)

        dict_settings = {
            cst.KEY_BASE_YEAR: 2012,
            cst.KEY_STRATEGY: calcul.EnumSystemCalcul.STANDARD.value,
        }
        tools.dump_dict(
            path=export_dir, json_file=cst.FILE_INFO, dict_=dict_settings
        )

        # Instantiate system from these files
        ss_dir.reset()
        system = ss_dir.make_from_path(path=export_dir, load_data=True)

        shutil.rmtree(export_dir)

        # Check that A is correctly instantiated and initialized
        assert system.dataset.A.equals(a)
        # Check that other data are instantiated
        assert isinstance(system.dataset.x, data.XData)
        assert isinstance(system.dataset.Y, data.YData)
        assert isinstance(system.dataset.Z, data.ZData)
        assert isinstance(system.dataset.L, data.LData)
        # K, L_k, L shall be null for a standard system
        assert isinstance(system.dataset.K, data.NullSystemData)
        assert isinstance(system.dataset.L_k, data.NullSystemData)
        assert isinstance(system.dataset.Y_k, data.NullSystemData)
        # Check strategy
        assert isinstance(system.calcul, calcul.Standard)
