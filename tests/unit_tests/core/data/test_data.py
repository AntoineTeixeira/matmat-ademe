import os
import copy
import pytest

import numpy as np
import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.utils import constants as cst, errors

import tests.utils.builders as builders
import tests.utils.constants as tests_cst


class TestAbstractData:
    """
    This class contains test cases to check methods of `AbstractData`.

    `AbstractData` being an abstract class, it is not possible to instantiate
    it directly.
    To realize the tests, we instantiate some of its subclasses :
        - core.system.AData, core.system.XData,
        - core.shock.AShockData
    """

    def test_is_null(self):
        """
        Test function `is_null`

        Expected results:
            - Check that the function returns False
        """
        a = builders.build_test_a()
        assert a.is_null() is False

    def test_reset(self):
        """
        Test function `reset`

        Expected results:
            - Check that the dataframe contains no NaN before reset and only NaN after reset
        """
        a = builders.build_test_a()
        builders.randomize(a.df, full_randomization=False)
        assert not a.df.isin([np.nan]).any().any()
        a.reset()
        assert a.df.isin([np.nan]).all().all()

    def test_reset_domestic_region(self):
        """
        Test function `reset_domestic_region`

        Expected results:
            - Check that the domestic part of the dataframe contains no NaN before reset and only NaN after reset
            - Check that the import part remains unchanged
        """
        a = builders.build_test_a()
        builders.randomize(a.df, full_randomization=False)
        a_imp_ref = copy.deepcopy(a.get_import_origin())
        assert not a.df.isin([np.nan]).any().any()
        a.reset_domestic_region()
        assert a.get_domestic_origin().isin([np.nan]).all().all()
        assert np.allclose(a.get_import_origin(), a_imp_ref)

    def test_reset_import_region(self):
        """
        Test function `reset_import_region`

        Expected results:
            - Check that the import part of the dataframe contains no NaN before reset and only NaN after reset
            - Check that the domestic part remains unchanged
        """
        a = builders.build_test_a()
        builders.randomize(a.df, full_randomization=False)
        a_dom_ref = copy.deepcopy(a.get_domestic_origin())
        assert not a.df.isin([np.nan]).any().any()
        a.reset_import_region()
        assert a.get_import_origin().isin([np.nan]).all().all()
        assert np.allclose(a.get_domestic_origin(), a_dom_ref)

    def test_clean_residual_nan(self):
        """
        Test function `clean_residual_nan`

        Expected results:
            - (1) Checks that the function does nothing if the dataframe contains only NaN
            - (2) Checks that the function removes the several NaN, INF, -INF added randomly in the dataframe
        """
        a = builders.build_test_a()

        # (1)
        a.clean_residual_nan()
        assert a.df.isin([np.nan]).all().all()

        # (2)
        builders.randomize(a.df)
        builders.add_random_number(a.df, np.nan, 5)
        builders.add_random_number(a.df, np.inf, 4)
        builders.add_random_number(a.df, -np.inf, 3)
        assert a.df.isin([np.nan, np.inf, -np.inf]).any().any()
        a.clean_residual_nan()
        assert not a.df.isin([np.nan, np.inf, -np.inf]).all().all()

    def test_is_df_empty(self):
        """
        Test function `is_df_empty`

        Expected results:
            - (1) After initialization, check that is_df_empty returns True
            - (2) After randomization, check that is_df_empty returns False
        """
        a = builders.build_test_a()

        # (1)
        assert a.is_df_empty()

        # (2)
        builders.randomize(a.df)
        builders.add_random_number(a.df, np.nan)
        assert not a.is_df_empty()

    def test_is_domestic_region_empty(self):
        """
        Test function `is_domestic_region_empty`

        Expected results:
            - (1) After randomization, check that the function returns False
            - (2) After randomization, reset domestic region and check that the function returns True
            - (3) After randomization, reset import region and check that the function returns False
        """
        a = builders.build_test_a()

        # (1)
        builders.randomize(a.df)
        assert not a.is_domestic_region_empty()

        # (2)
        a.reset_domestic_region()
        assert a.is_domestic_region_empty()

        # (3)
        builders.randomize(a.df)
        a.reset_import_region()
        assert not a.is_domestic_region_empty()

    def test_is_import_region_empty(self):
        """
        Test function `test_is_import_region_empty`

        Expected results:
            - (1) After randomization, check that the function returns False
            - (2) After randomization, reset import region and check that the function returns True
            - (3) After randomization, reset domestic region and check that the function returns False
        """
        a = builders.build_test_a()

        # (1)
        builders.randomize(a.df)
        assert not a.is_import_region_empty()

        # (2)
        a.reset_import_region()
        assert a.is_import_region_empty()

        # (3)
        builders.randomize(a.df)
        a.reset_domestic_region()
        assert not a.is_import_region_empty()

    def test_set_values_with_ndarray(self):
        """
        Test function `set_values` with np.ndarray

        Expected results:
            - The dataframe values properly set
        """
        a = builders.build_test_a()
        a_ref = builders.build_test_a()
        builders.randomize(a_ref.df)
        a.set_values(a_ref.df.values)
        assert np.allclose(a.df, a_ref.df)

    def test_set_values_with_float(self):
        """
        Test function `set_values` with a float

        Expected results:
            - The dataframe values properly set to the one provided value
        """
        da = builders.build_test_da()
        test_value = 12.0
        da.set_values(values=test_value)
        assert da.df.isin([test_value]).all().all()

    def test_set_values_with_string(self):
        """
        Test function `set_values` with a string

        Expected results:
            - The dataframe values properly set to the one provided value
        """
        unit = builders.build_test_system_unit()
        test_value = "MT"
        unit.set_values(values=test_value)
        assert (unit.df == test_value).all().all()

    def test_update_values(self):
        """
        Test function `update_values`

        Expected results:
            - The dataframe values properly set
        """
        a = builders.build_test_a()
        a_ref = builders.build_test_a()
        builders.randomize(a_ref.df)
        a.update_values(a_ref.df)
        assert np.allclose(a.df, a_ref.df)

    def test_update_dom_values(self):
        """
        Test function `update_domestic_values`

        Expected results:
            - The domestic part of the dataframe is properly set to the values of the given dataframe
              (1) with origin level
              (2) without origin level
        """
        a = builders.build_test_a()
        a_ref = builders.build_test_a()
        builders.randomize(a_ref.df, full_randomization=True)

        # (1) With origin level
        a.update_domestic_values(a_ref.get_domestic_origin(keep_origin=True))
        assert a.get_domestic_origin(keep_origin=True).equals(
            a_ref.get_domestic_origin(keep_origin=True)
        )

        # (2) Without origin level
        a.reset()
        builders.randomize(a_ref.df, full_randomization=True)
        a.update_domestic_values(a_ref.get_domestic_origin(keep_origin=False))
        assert a.get_domestic_origin(keep_origin=True).equals(
            a_ref.get_domestic_origin(keep_origin=True)
        )

    def test_update_import_values(self):
        """
        Test function `update_import_values`

        Expected results:
            - The import part of the dataframe is properly set to the values of the given dataframe
              (1) with origin level
              (2) without origin level
        """
        a = builders.build_test_a()
        a_ref = builders.build_test_a()
        builders.randomize(a_ref.df)

        # (1) With origin level
        a.update_import_values(a_ref.get_import_origin(keep_origin=True))
        assert a.get_import_origin(keep_origin=True).equals(
            a_ref.get_import_origin(keep_origin=True)
        )

        # (2) Without origin level
        a.reset()
        builders.randomize(a_ref.df)
        a.update_import_values(a_ref.get_import_origin(keep_origin=False))
        assert a.get_import_origin(keep_origin=True).equals(
            a_ref.get_import_origin(keep_origin=True)
        )

    def test_set_domestic_import_values_with_ndarray(self):
        """
        Test functions `set_domestic_values` and `set_import_values`

        Expected results:
            - The domestic and import values of the dataframe properly set
        """
        a = builders.build_test_a()
        a_ref = builders.build_test_a()
        builders.randomize(a_ref.df, full_randomization=True)
        a.set_domestic_values(a_ref.get_domestic_origin().values)
        a.set_import_values(a_ref.get_import_origin().values)
        assert np.allclose(
            a.get_domestic_origin(), a_ref.get_domestic_origin()
        )
        assert np.allclose(a.get_import_origin(), a_ref.get_import_origin())

    def test_set_domestic_values_with_float(self):
        """
        Test function `set_domestic_values` with a float

        Expected_results:
            - The correct value is set to the domestic part of the dataframe
        """
        a = builders.build_test_a()
        builders.randomize(a.df)
        value = -1.11
        a.set_domestic_values(value)

        assert np.isin(a.get_domestic_origin(), value).all()
        assert not np.isin(a.get_import_origin(), value).any()

    def test_set_import_values_with_float(self):
        """
        Test function `set_import_values` with a float

        Expected_results:
            - The correct value is set to the import part of the dataframe
        """
        a = builders.build_test_a()
        builders.randomize(a.df)
        value = -999.999
        a.set_import_values(value)

        assert np.isin(a.get_import_origin(), value).all()
        assert not np.isin(a.get_domestic_origin(), value).any()

    def test_get_regions_list(self):
        """
        Test functions `get_domestic_regions_list` and `get_import_regions_list`

        Expected results:
            - After init, the regions shall match the constant DEFAULT_REGIONS
        """
        a = builders.build_test_a()
        assert (
            a.get_domestic_regions_list()
            == a.structure._regions.get_domestic_regions_list()
        )
        assert (
            a.get_import_regions_list()
            == a.structure._regions.get_import_regions_list()
        )

    def test_get_domestic_origin(self):
        """
        Test function `get_domestic_origin`

        Expected results:
            - (1) Check that the domestic part returned corresponds to the domestic rows (with origin level)
            - (2) Check that the domestic part returned corresponds to the domestic rows (without origin level)
        """
        a = builders.build_test_a()
        builders.randomize(a.df)
        a_dom_ref = a.df.xs(
            key=cst.IDX_DOMESTIC, axis=0, level=0, drop_level=False
        )
        # (1)
        assert a.get_domestic_origin(keep_origin=True).equals(a_dom_ref)
        # (2)
        assert a.get_domestic_origin(keep_origin=False).equals(
            a_dom_ref.droplevel(level=0, axis=0)
        )

    def test_get_import_origin(self):
        """
        Test function `get_import_origin`

        Expected results:
            - (1) Check that the import part returned corresponds to the import rows (with origin level)
            - (2) Check that the import part returned corresponds to the import rows (without origin level)
        """
        a = builders.build_test_a()
        builders.randomize(a.df)
        a_imp_ref = a.df.xs(
            key=cst.IDX_IMPORT, axis=0, level=0, drop_level=False
        )
        # (1)
        assert a.get_import_origin(keep_origin=True).equals(a_imp_ref)
        # (2)
        assert a.get_import_origin(keep_origin=False).equals(
            a_imp_ref.droplevel(level=0, axis=0)
        )

    def test_load_from_pickle(self):
        """
        Test function `load_from_path` for various structures / formats

        Expected results:
            - Create a pickle file from a dataframe (df_ref) and check
              that the function `load_from_path` applied
              to this file set the dataframe to the dataframe (df_ref)
        """
        path_to_init_dir = "./"

        def execute_load_data_test(data_ref):
            data_test = data_ref.copy()
            path_to_init_file = f"{path_to_init_dir}/{data_ref.name}.pkl"
            if data_ref.name == cst.UNIT:
                builders.randomize_string_df(data_ref.df)
            else:
                builders.randomize(data_ref.df)
            data_ref.df.to_pickle(path_to_init_file)
            data_test.load_from_path(path=path_to_init_dir, format_="pickle")
            os.remove(path_to_init_file)
            if data_ref.name == cst.UNIT:
                assert data_test.df.equals(data_ref.df)
            else:
                assert np.allclose(data_test.df, data_ref.df)

        for sys_data_name in cst.LIST_OF_SYSTEM_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_system_data(name=sys_data_name)
            )
        for ext_data_name in cst.LIST_OF_EXTENSION_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_extension_data(
                    name=ext_data_name,
                    extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
                )
            )
        for sys_shock_data_name in cst.LIST_OF_SYSTEM_SHOCK_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_system_shock_data(
                    name=sys_shock_data_name
                )
            )
        for ext_shock_data_name in cst.LIST_OF_EXTENSION_SHOCK_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_extension_shock_data(
                    name=ext_shock_data_name
                )
            )

    def test_load_from_excel(self):
        """
        Test function `load_from_path` for various structures / formats

        Expected results:
            - Create an excel file from a dataframe (df_ref) and check
              that the function `load_from_path` applied
              to this file set the dataframe to the dataframe (df_ref)
        """
        path_to_init_dir = "./"

        def execute_load_data_test(data_ref):
            data_test = data_ref.copy()
            path_to_init_file = f"{path_to_init_dir}/{data_ref.name}.xlsx"
            if data_ref.name == cst.UNIT:
                builders.randomize_string_df(data_ref.df)
            else:
                builders.randomize(data_ref.df)
            data_ref.df.to_excel(path_to_init_file)
            data_test.load_from_path(path=path_to_init_dir, format_="excel")
            os.remove(path_to_init_file)
            if data_ref.name == cst.UNIT:
                assert data_test.df.equals(data_ref.df)
            else:
                assert np.allclose(data_test.df, data_ref.df)

        for sys_data_name in cst.LIST_OF_SYSTEM_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_system_data(name=sys_data_name)
            )
        for ext_data_name in cst.LIST_OF_EXTENSION_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_extension_data(
                    name=ext_data_name,
                    extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
                )
            )
        for sys_shock_data_name in cst.LIST_OF_SYSTEM_SHOCK_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_system_shock_data(
                    name=sys_shock_data_name
                )
            )
        for ext_shock_data_name in cst.LIST_OF_EXTENSION_SHOCK_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_extension_shock_data(
                    name=ext_shock_data_name
                )
            )

    def test_load_from_csv(self):
        """
        Test function `load_from_path` for various structures / formats

        Expected results:
            - Create a csv file from a dataframe (df_ref) and check
              that the function `load_from_path` applied
              to this file set the dataframe to the dataframe (df_ref)
        """
        path_to_init_dir = "./"

        def execute_load_data_test(data_ref):
            data_test = data_ref.copy()
            path_to_init_file = f"{path_to_init_dir}/{data_ref.name}.csv"
            if data_ref.name == cst.UNIT:
                builders.randomize_string_df(data_ref.df)
            else:
                builders.randomize(data_ref.df)
            data_ref.df.to_csv(path_to_init_file)
            data_test.load_from_path(path=path_to_init_dir, format_="csv")
            os.remove(path_to_init_file)
            if data_ref.name == cst.UNIT:
                assert data_test.df.equals(data_ref.df)
            else:
                assert np.allclose(data_test.df, data_ref.df)

        for sys_data_name in cst.LIST_OF_SYSTEM_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_system_data(name=sys_data_name)
            )
        for ext_data_name in cst.LIST_OF_EXTENSION_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_extension_data(
                    name=ext_data_name,
                    extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
                )
            )
        for sys_shock_data_name in cst.LIST_OF_SYSTEM_SHOCK_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_system_shock_data(
                    name=sys_shock_data_name
                )
            )
        for ext_shock_data_name in cst.LIST_OF_EXTENSION_SHOCK_DATA:
            execute_load_data_test(
                data_ref=builders.build_test_extension_shock_data(
                    name=ext_shock_data_name
                )
            )

    def test_save_to_path(self):
        """
        Test function `save_to_path`

        Expected results:
            - Export a dataframe, then read this export file and checks that
            the read dataframe is the same as the original one
        """
        path_to_export_dir = "./"

        data_ = builders.build_test_a()
        builders.randomize(data_.df)

        for format_ in [
            (cst.FORMAT_PICKLE, ".pkl"),
            (cst.FORMAT_EXCEL, ".xlsx"),
            (cst.FORMAT_CSV, ".csv"),
        ]:
            data_test = data_.copy()
            data_.save_to_path(
                path=path_to_export_dir, export_format=format_[0]
            )

            data_test.reset()
            data_test.load_from_path(path=path_to_export_dir)
            os.remove(f"{path_to_export_dir}/{data_.name}{format_[1]}")
            assert np.allclose(data_test.df, data_.df)

    def test_equals_same_dataframe(self):
        """
        Test function `equals`

        Expected results:
            - The data are the same, the function shall return True
        """
        a_ref = builders.build_test_a()
        a_test = builders.build_test_a()
        builders.randomize(a_ref.df)
        a_test.set_values(a_ref.df.values)

        assert a_test.equals(a_ref)

    def test_equals_different_regions(self):
        """
        Test function `equals`

        Expected results:
            - The dataframe have same values but does not have the same index & columns
        """
        a_ref = builders.build_test_system_data(
            name=cst.A,
            regions=tests_cst.DEFAULT_REGIONS,
        )
        builders.randomize(a_ref.df)

        altered_regions = tests_cst.DEFAULT_REGIONS.copy()
        altered_regions.df.iloc[0, 1] = "new_region"

        a_test = builders.build_test_system_data(
            name=cst.A,
            regions=altered_regions,
        )
        a_test.set_values(a_ref.df.values)

        assert not a_test.equals(a_ref)

    def test_equals_different_values(self):
        """
        Test function `equals`

        Expected results:
            - The values are different, the function shall return False
        """
        a_ref = builders.build_test_a()
        a_ref.set_values(1.0)
        a_test = builders.build_test_a()
        a_ref.set_values(2.0)

        assert not a_test.equals(a_ref)

    def test_aggregate_sectors_with_reset(self):
        """
        Test function `aggregate` with sectors bridge

        Expected results:
            - Check that the index and columns are properly updated
            - Check that the df is properly reset
        """
        a = builders.build_test_system_data(
            name=cst.A,
            regions=tests_cst.REGIONS_W_IMPORT,
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )
        a.set_values(5.55)

        bridge_ = builders.get_test_sectors_bridge()

        # Call function under test
        a.aggregate(bridge_=bridge_, reset=True)

        reference_index = (
            bridge_.columns_dl.get_dl_as_multi_index_propagated_on(
                df_on=tests_cst.REGIONS_W_IMPORT.df,
            )
        )
        reference_columns = (
            bridge_.columns_dl.get_dl_as_multi_index_propagated_on(
                df_on=tests_cst.REGIONS_W_IMPORT.get_domestic_origin_df(
                    with_origin=False
                )
            )
        )

        assert a.df_rows.equals(reference_index)
        assert a.df.index.equals(reference_index)
        assert a.df_columns.equals(reference_columns)
        assert a.df.columns.equals(reference_columns)
        assert a.is_df_empty()

    def test_aggregate_sectors(self):
        """
        Test function `aggregate`

        Expected results:
            - The dataframe is properly aggregated. In this test, we consider
              that the function `_perform_aggregation_on_sectors` is
              correct.
        """
        data_ = builders.build_test_system_data(
            name=cst.Z, sectors=builders.get_test_sectors()
        )
        builders.randomize(data_.df)

        bridge_ = builders.get_test_sectors_bridge()

        # Use structure class to compute reference df
        a_df_ref = data_.structure.apply_bridge_to_df(
            df=data_.df, bridge_=bridge_
        )

        # Call function under test
        data_.aggregate(bridge_=bridge_, reset=False)

        assert data_.df.equals(a_df_ref)
        assert data_.df_rows.equals(a_df_ref.index)
        assert data_.df_columns.equals(a_df_ref.columns)

    def test_disaggregate_sectors(self):
        """
        Test function `disaggregate_sectors`

        Expected results:
            - The dataframe is properly disaggregated. In this test,
            we consider that the function `_perform_aggregation_on_sectors` is correct.
        """
        agg_matrix = (
            builders.get_test_sectors_bridge()
            .get_agg_matrix()
            .to_dataframe()
            .T
        )
        bridge_ = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=agg_matrix,
        )

        data_ = builders.build_test_system_data(
            name=cst.A, sectors=builders.get_test_agg_sectors()
        )
        # Configure A index
        data_.structure.sectors = dl.SectorsDL(agg_matrix.index.to_frame())
        data_.structure.build_rows()
        data_.structure.build_columns()
        data_.reset()
        builders.randomize(data_.df)

        # Use structure class to compute reference df
        a_df_ref = data_.structure.apply_bridge_to_df(
            df=data_.df, bridge_=bridge_
        )

        # Call function under test
        data_.disaggregate(bridge_=bridge_, reset=False)

        assert data_.df.equals(a_df_ref)
        assert data_.df_rows.equals(a_df_ref.index)
        assert data_.df_columns.equals(a_df_ref.columns)

    def test_aggregate_sectors_dimensions_error(self):
        """
        Test function `aggregate`

        Expected results:
            Aggregation matrix has more columns than rows.
            An exception MEAggMatrixDimensionsInconsistent shall be raised
        """
        data_ = builders.build_test_system_data(
            name=cst.Z,
            sectors=builders.get_test_sectors(),
        )

        disagg_matrix = (
            builders.get_test_sectors_bridge()
            .get_agg_matrix()
            .to_dataframe()
            .T
        )
        bridge_ = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=disagg_matrix,
        )

        with pytest.raises(errors.MEAggMatrixDimensionsInconsistent):
            data_.aggregate(bridge_=bridge_, reset=False)

    def test_disaggregate_sectors_dimensions_error(self):
        """
        Test function 'disaggregate'

        Expected results:
            Disaggregation matrix has more rows than columns.
            An exception MEAggMatrixDimensionsInconsistent shall be raised
        """
        data_ = builders.build_test_system_data(
            name=cst.A,
            sectors=builders.get_test_agg_sectors(),
        )

        bridge_ = builders.get_test_sectors_bridge()

        with pytest.raises(errors.MEAggMatrixDimensionsInconsistent):
            data_.disaggregate(bridge_=bridge_, reset=False)
