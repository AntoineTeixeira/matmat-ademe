import os

import numpy as np

from matmat.core.accounts.extension.data.core import SxDomData
import matmat.utils.constants as cst
import matmat.utils.config as config

import tests.utils.builders as builders
import tests.utils.constants as tests_cst


class TestExtensionData:

    def test_constructor(self, mocker):
        """
        Test function `__init__`

        Expected results:
            - Instantiate an object S_x data, and check that:
                - Check that the structure and nature are properly set
                - Check that the dataframe index and columns match the
                  attributes df_index & df_columns of the associated structure
                - Check that the dataframe values are all NaN
                - Check that the detail levels attributes are properly set
        """
        spy_nature = mocker.spy(SxDomData, "get_nature_type")
        spy_structure = mocker.spy(SxDomData, "get_structure_type")

        data_ = SxDomData(
            extension_name="test_extension",
            sectors=builders.get_test_sectors(),
            regions=tests_cst.DEFAULT_REGIONS,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )
        # ID
        assert data_.id.extension_name == "test_extension"
        # Nature
        assert spy_nature.spy_return is data_.nature.__class__
        # Structure
        assert spy_structure.spy_return is data_.structure.__class__
        # Dataframe
        assert data_.df.index.equals(data_.df_rows)
        assert data_.df.columns.equals(data_.df_columns)
        assert np.isnan(data_.df).all().all()
        # Detail levels
        assert data_.sectors.equals(builders.get_test_sectors())
        assert data_.regions.equals(tests_cst.DEFAULT_REGIONS)
        assert data_.final_demand_categories.equals(tests_cst.DEFAULT_Y_CATEGORIES)
        assert data_.extension_categories.equals(tests_cst.DEFAULT_EXTENSION_CATEGORIES)

    def test_constructor_no_import_regions(self):
        """
        Test function `__init__`

        In this test case, the list of "import" regions is empty.

        Expected results:
        - Check that the regions are properly set in the data structure
          and the identity card
        """
        test_regions = tests_cst.REGIONS_WO_IMPORT
        data_ = SxDomData(
            regions=test_regions,
            extension_name="test_extension",
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )

        assert data_.structure.df_columns.get_level_values(
            "region"
        ).unique().tolist() == ["France"]
        assert len(data_.structure.get_import_regions_list()) == 0
        assert not data_.structure.has_import_regions()

    def test_load_no_nan(self):
        """
        Test function `load_from_path` from a dataframe containing no NaN / INF

        Expected results:
            - Create an initialization file from a dataframe (df_ref) and:
                - Check that the df columns match the ones of df_ref
                - Check that the df values match the ones of df_ref
        """
        path_to_init_dir = "./"
        extension_name = "test_extension"

        os.makedirs(f"{path_to_init_dir}/{extension_name}", exist_ok=True)

        s_x_ref = builders.build_test_extension_data(
            name=cst.S_X_DOM,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )
        path_to_init_file = (
            f"{path_to_init_dir}/{extension_name}/{s_x_ref.name}.pkl"
        )
        builders.randomize(s_x_ref.df)
        s_x_ref.save_to_path(
            path=f"{path_to_init_dir}/{extension_name}", export_format="pickle"
        )

        s_x_test = builders.build_test_extension_data(
            name=cst.S_X_DOM,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )
        s_x_test.load_from_path(path=f"{path_to_init_dir}/{extension_name}")

        os.remove(path_to_init_file)
        os.rmdir(f"{path_to_init_dir}/{extension_name}")

        assert s_x_test.df_columns.equals(s_x_ref.df.columns)
        assert np.allclose(s_x_test.df, s_x_ref.df)

    def test_load_with_nan(self):
        """
        Test function `load_from_path` from a dataframe containing NaN / INF

        Expected results:
            - Create an initialization file from a dataframe (df_ref) and:
                - Check that the df columns match the ones of df_ref
                - Check that the df values match the ones of df_ref
                - Check that the residual NaN / INF are cleaned (or not, depending on the configuration)
        """
        path_to_init_dir = "./"
        extension_name = "test_extension"

        os.makedirs(f"{path_to_init_dir}/{extension_name}", exist_ok=True)

        s_x_ref = builders.build_test_extension_data(
            name=cst.S_X_DOM,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )
        path_to_init_file = (
            f"{path_to_init_dir}/{extension_name}/{s_x_ref.name}.pkl"
        )

        builders.randomize(s_x_ref.df)
        builders.add_random_number(df=s_x_ref.df, number=np.nan, occurrences=5)
        builders.add_random_number(df=s_x_ref.df, number=np.inf, occurrences=4)
        builders.add_random_number(
            df=s_x_ref.df, number=-np.inf, occurrences=3
        )

        s_x_ref.save_to_path(
            path=f"{path_to_init_dir}/{extension_name}", export_format="pickle"
        )

        s_x_test = builders.build_test_extension_data(
            name=cst.S_X_DOM,
            extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES,
        )

        s_x_test.load_from_path(path=f"{path_to_init_dir}/{extension_name}")

        os.remove(path_to_init_file)
        os.rmdir(f"{path_to_init_dir}/{extension_name}")

        if config.CLEAN_RESIDUAL_NAN_AND_INF:
            s_x_ref.df.replace(np.nan, 0.0, inplace=True)
            s_x_ref.df.replace(np.inf, 0.0, inplace=True)
            s_x_ref.df.replace(-np.inf, 0.0, inplace=True)
            assert not s_x_test.df.isin([np.nan, np.inf, -np.inf]).any().any()
        assert s_x_test.df_columns.equals(s_x_ref.df.columns)
        assert np.allclose(s_x_test.df, s_x_ref.df)
