import os
import shutil

from matmat.core.accounts.extension import builder as ext_builder
from matmat.core.accounts.extension.identity import ExtensionIdentity
import matmat.utils.constants as cst
from matmat.core.accounts.extension.strategies import calcul
import matmat.core.accounts.extension.data.core as data

import tests.utils.constants as tests_cst
from tests.utils import builders


class TestExtensionDirector:
    """
    Unit tests for class `ExtensionDirector`.
    The class `SEBuilder` is tested through these test cases.
    """

    def test_constructor(self):
        """
        Test function `__init__`
        """
        se_dir = ext_builder.get_director(reset=True)
        assert se_dir.regions is None
        assert se_dir.sectors is None
        assert se_dir.final_demand_categories is None
        assert se_dir.extension_categories is None

    def test_setters_and_reset(self):
        """
        Test setters and function `reset`
        """
        se_dir = ext_builder.get_director(reset=True)
        se_dir.set_regions(regions=tests_cst.REGIONS_W_IMPORT_INV)
        se_dir.set_sectors(sectors=builders.get_test_sectors())
        se_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)

        assert se_dir._sectors.equals(builders.get_test_sectors())
        assert se_dir._regions.equals(tests_cst.REGIONS_W_IMPORT_INV)
        assert se_dir._final_demand_categories.equals(
            tests_cst.DEFAULT_Y_CATEGORIES
        )

        se_dir.reset()

        assert se_dir._regions is None
        assert se_dir._sectors is None
        assert se_dir._final_demand_categories is None

    def test_make_use_based_extension(self):
        """
        Test function `make_use_based_extension`
        """
        se_dir = ext_builder.get_director(reset=True)

        se_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        se_dir.set_sectors(builders.get_test_sectors())
        se_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        se_dir.set_extension_categories(
            builders.get_test_extension_categories_equivalent_to_sectors(
                extension_name="test_extension"
            )
        )

        # Regular extension
        extension = se_dir.make_use_based_extension(name="test_extension")

        # Check strategy
        assert isinstance(extension.calcul, calcul.UseBased)
        # Check data
        # Not null data
        list_of_not_null_data = [
            cst.S_Y,
            cst.F_Y,
            cst.S_Z,
            cst.F_Z,
            cst.UNIT,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
        ]
        assert isinstance(extension.dataset.S_Y, data.SyData)
        assert isinstance(extension.dataset.S_Z, data.SzData)
        assert isinstance(extension.dataset.F_Y, data.FyData)
        assert isinstance(extension.dataset.F_Z, data.FzData)
        assert isinstance(extension.dataset.unit, data.UnitExtensionData)
        assert isinstance(extension.dataset.M, data.MData)
        assert isinstance(extension.dataset.M_k, data.MKData)
        assert isinstance(extension.dataset.d_cba, data.DCbaData)
        assert isinstance(extension.dataset.d_cba_k, data.DCbaKData)

        # Null data
        for data_ in extension.dataset.data:
            if data_.name not in list_of_not_null_data:
                assert isinstance(data_, data.NullExtensionData)

        for data_name in cst.LIST_OF_EXTENSION_DATA:
            ext_data = extension.dataset.__getattribute__(f"_{data_name}")
            if not ext_data.is_null():
                # Check regions
                assert ext_data.structure._regions.equals(
                    tests_cst.DEFAULT_MULTI_REGIONS
                )
                # Check sectors
                assert ext_data.structure._sectors.equals(
                    builders.get_test_sectors()
                )
                # Check final demand categories
                assert ext_data.structure._final_demand_categories.equals(
                    tests_cst.DEFAULT_Y_CATEGORIES
                )
                # Check extension categories
                assert ext_data.structure._extension_categories.equals(
                    builders.get_test_extension_categories_equivalent_to_sectors(
                        extension_name="test_extension"
                    )
                )

    def test_make_gross_output_based_extension(self):
        """
        Test function `make_gross_output_based_extension`
        """
        se_dir = ext_builder.get_director(reset=True)

        se_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        se_dir.set_sectors(sectors=builders.get_test_sectors())
        se_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        se_dir.set_extension_categories(
            categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )
        extension = se_dir.make_gross_output_based_extension(
            name=tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name
        )

        # Check strategy
        assert isinstance(extension.calcul, calcul.GrossOutputBased)
        # Check data
        # Not null data
        list_of_not_null_data = [
            cst.S_X_DOM,
            cst.F_X_DOM,
            cst.UNIT,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
            cst.MAPPING,
            cst.MAPPING_K,
        ]
        assert isinstance(extension.dataset.S_x_dom, data.SxDomData)
        assert isinstance(extension.dataset.F_x_dom, data.FxDomData)
        assert isinstance(extension.dataset.unit, data.UnitExtensionData)
        assert isinstance(extension.dataset.M, data.MData)
        assert isinstance(extension.dataset.M_k, data.MKData)
        assert isinstance(extension.dataset.d_cba, data.DCbaData)
        assert isinstance(extension.dataset.d_cba_k, data.DCbaKData)
        assert isinstance(extension.dataset.mapping, data.MappingData)
        assert isinstance(extension.dataset.mapping_k, data.MappingKData)

        # Null data
        for data_ in extension.dataset.data:
            if data_.name not in list_of_not_null_data:
                assert isinstance(data_, data.NullExtensionData)

        for data_name in cst.LIST_OF_EXTENSION_DATA:
            ext_data = extension.dataset.__getattribute__(f"_{data_name}")
            if not ext_data.is_null():
                # Check regions
                assert ext_data.structure._regions.equals(
                    tests_cst.DEFAULT_MULTI_REGIONS
                )
                # Check sectors
                assert ext_data.structure._sectors.equals(
                    builders.get_test_sectors()
                )
                # Check final demand categories
                assert ext_data.structure._final_demand_categories.equals(
                    tests_cst.DEFAULT_Y_CATEGORIES
                )
                # Check extension categories
                assert ext_data.structure._extension_categories.equals(
                    tests_cst.DEFAULT_EXTENSION_CATEGORIES
                )

    def test_make_embodied_in_import_extension(self):
        """
        Test function `make_embodied_in_import_extension`
        """
        se_dir = ext_builder.get_director(reset=True)

        se_dir.set_regions(tests_cst.DEFAULT_MULTI_REGIONS)
        se_dir.set_sectors(sectors=builders.get_test_sectors())
        se_dir.set_final_demand_categories(tests_cst.DEFAULT_Y_CATEGORIES)
        se_dir.set_extension_categories(
            categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )
        extension = se_dir.make_embodied_in_import_extension(
            name=tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name
        )

        # Check strategy
        assert isinstance(extension.calcul, calcul.EmbodiedInImport)
        # Check data
        # Not null data
        list_of_not_null_data = [
            cst.M_ROW,
            cst.D_IMP,
            cst.UNIT,
            cst.M,
            cst.M_K,
            cst.D_CBA,
            cst.D_CBA_K,
            cst.MAPPING,
            cst.MAPPING_K,
        ]
        assert isinstance(extension.dataset.M_RoW, data.MRoWData)
        assert isinstance(extension.dataset.d_imp, data.DImpData)
        assert isinstance(extension.dataset.unit, data.UnitExtensionData)
        assert isinstance(extension.dataset.M, data.MData)
        assert isinstance(extension.dataset.M_k, data.MKData)
        assert isinstance(extension.dataset.d_cba, data.DCbaData)
        assert isinstance(extension.dataset.d_cba_k, data.DCbaKData)
        assert isinstance(extension.dataset.mapping, data.MappingData)
        assert isinstance(extension.dataset.mapping_k, data.MappingKData)

        # Null data
        for data_ in extension.dataset.data:
            if data_.name not in list_of_not_null_data:
                assert isinstance(data_, data.NullExtensionData)

        for data_name in cst.LIST_OF_EXTENSION_DATA:
            ext_data = extension.dataset.__getattribute__(f"_{data_name}")
            if not ext_data.is_null():
                # Check regions
                assert ext_data.structure._regions.equals(
                    tests_cst.DEFAULT_MULTI_REGIONS
                )
                # Check sectors
                assert ext_data.structure._sectors.equals(
                    builders.get_test_sectors()
                )
                # Check final demand categories
                assert ext_data.structure._final_demand_categories.equals(
                    tests_cst.DEFAULT_Y_CATEGORIES
                )
                # Check extension categories
                assert ext_data.structure._extension_categories.equals(
                    tests_cst.DEFAULT_EXTENSION_CATEGORIES
                )

    def test_make_from_path_files_all_files(self):
        """
        Test functions `make_from_path`

        Expected results:
            - The extension exported and the extension made from files
              are equal
        """
        se_dir = ext_builder.get_director(reset=True)
        se_dir.set_regions(regions=tests_cst.DEFAULT_MULTI_REGIONS)
        se_dir.set_sectors(sectors=builders.get_test_sectors())
        se_dir.set_final_demand_categories(
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES
        )
        se_dir.set_extension_categories(
            categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        # Generate extension files
        export_dir = "tmp_export_dir"
        ref_extension = se_dir.make_use_based_extension(
            name="test_extension"
        )
        builders.randomize_extension(ref_extension)
        ref_extension.save_to_path(path=export_dir, export_format="pickle")

        # Instantiate extension from these files
        se_dir.reset()
        test_extension = se_dir.make_from_path(
            path=f"{export_dir}/{ref_extension.name}", load_data=True
        )

        shutil.rmtree(export_dir)

        assert test_extension.equals(ref_extension)

    def test_make_from_path_ignored_files(self):
        """
        Test functions `make_from_path`

        Expected results:
            - The files not related to 'use_based'
              strategy shall be ignored
        """
        se_dir = ext_builder.get_director(reset=True)
        se_dir.set_regions(regions=tests_cst.DEFAULT_MULTI_REGIONS)
        se_dir.set_sectors(sectors=builders.get_test_sectors())
        se_dir.set_final_demand_categories(
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES
        )
        se_dir.set_extension_categories(
            categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        # Generate system files
        export_dir = "tmp_export_dir"
        ref_extension = se_dir.make_use_based_extension(
            name=tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name
        )

        builders.randomize_extension(ref_extension)

        # Generate files for gross output based extension
        gross_output_extension = se_dir.make_gross_output_based_extension(
            name=tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name
        )
        builders.randomize_extension(gross_output_extension)
        gross_output_extension.save_to_path(
            path=export_dir, export_format="pickle"
        )

        # Generate files for use based extension
        ref_extension.save_to_path(path=export_dir, export_format="pickle")

        se_dir.reset()
        test_extension = se_dir.make_from_path(
            path=f"{export_dir}/{ref_extension.name}", load_data=True
        )

        shutil.rmtree(export_dir)

        assert test_extension.dataset.equals(ref_extension.dataset)

    def test_make_from_path_missing_files(self):
        """
        Test functions `make_from_path`

        Expected results:
            - The extension is 'gross_output_based' and made from only
              one file.
              Check that the file is read properly, and that the extension data
              are instantiated w.r.t. 'gross_output_based' strategy.
        """
        se_dir = ext_builder.get_director(reset=True)
        se_dir.set_regions(regions=tests_cst.DEFAULT_MULTI_REGIONS)
        se_dir.set_sectors(sectors=builders.get_test_sectors())
        se_dir.set_final_demand_categories(
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES
        )
        se_dir.set_extension_categories(
            categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        # Generate extension files
        export_dir = "tmp_export_dir"
        s_x = builders.build_test_extension_data(
            name=cst.S_X_DOM,
            regions=se_dir.regions,
            sectors=se_dir.sectors,
            final_demand_categories=se_dir.final_demand_categories,
            extension_categories=se_dir.extension_categories,
        )
        builders.randomize(s_x.df)

        os.makedirs(export_dir, exist_ok=True)
        s_x.save_to_path(path=export_dir, export_format="excel")

        # Generate detail levels files
        for dl_ in se_dir.detail_levels:
            dl_.save_to_path(path=export_dir)

        id_ = ExtensionIdentity(
            extension_name=tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name,
            base_year=2023,
            strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
        )
        id_.to_json_file(
            folder_path=export_dir,
            file_name=cst.FILE_INFO,
        )

        # Instantiate extension from these files
        se_dir.reset()
        extension = se_dir.make_from_path(path=export_dir, load_data=True)

        shutil.rmtree(export_dir)

        # Check that S_x_dom is correctly instantiated and initialized
        assert extension.dataset.S_x_dom.equals(s_x)
        # Check that other data are instantiated
        assert isinstance(extension.dataset.F_x_dom, data.FxDomData)
        assert isinstance(extension.dataset.M, data.MData)
        assert isinstance(extension.dataset.M_k, data.MKData)
        assert isinstance(extension.dataset.d_cba, data.DCbaData)
        assert isinstance(extension.dataset.d_cba_k, data.DCbaKData)
        # S_Y, F_Y, S_Z, F_Z, M_RoW shall be null for a gross_output_based
        # extension
        assert isinstance(extension.dataset.S_Y, data.NullExtensionData)
        assert isinstance(extension.dataset.F_Y, data.NullExtensionData)
        assert isinstance(extension.dataset.S_Z, data.NullExtensionData)
        assert isinstance(extension.dataset.F_Z, data.NullExtensionData)
        assert isinstance(extension.dataset.M_RoW, data.NullExtensionData)
        # Check strategy
        assert isinstance(extension.calcul, calcul.GrossOutputBased)
