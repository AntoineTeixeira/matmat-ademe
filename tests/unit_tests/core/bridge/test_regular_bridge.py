import os

import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.utils import constants as cst, tools

from tests.utils import builders, spy


class TestBridge:

    bridge_type = "Int64"
    bridge_file = "test_bridge.xlsx"
    bridge_path = os.path.dirname(__file__)
    bridge_file_path = os.path.join(bridge_path, bridge_file)

    categories = ["C1", "C1", "C2", "C2", "C2", "C3"]
    sub_categories = ["SC11", "SC11", "SC21", "SC22", "SC22", "SC3"]
    sectors = ["S11", "S12", "S21", "S22", "S23", "S31"]

    agg_categories = ["C1", "C2", "C2", "C3"]
    agg_sub_categories = ["SC11", "SC21", "SC22", "SC3"]
    agg_sectors = ["SC11_total", "S21", "SC22_total", "S31"]

    @classmethod
    def teardown_class(cls):
        try:
            os.remove(cls.bridge_file_path)
        except FileNotFoundError:
            pass

    def execute_test_on_specific_bridge(
        self,
        bridge_ref_df: pd.DataFrame,
        bridge_kind: dl.DetailLevelKind,
    ):

        # Add random 1 to make it as close to a functional bridge as possible
        builders.add_random_number(bridge_ref_df, 1)
        # Add check line
        if isinstance(bridge_ref_df.index, pd.MultiIndex):
            bridge_ref_df.loc[
                (bridge.AbstractBridge.INDEX_CHECK_LINE,)
                * len(bridge_ref_df.index.names),
                :,
            ] = 1
        else:
            bridge_ref_df.loc[bridge.AbstractBridge.INDEX_CHECK_LINE, :] = 1

        # Export to an Excel file
        bridge_ref_df.to_excel(
            self.bridge_file_path,
            sheet_name=bridge_kind.value,
        )

        # Transform Index to MultiIndex if applicable
        if not isinstance(bridge_ref_df.index, pd.MultiIndex):
            bridge_ref_df.index = pd.MultiIndex.from_arrays(
                [bridge_ref_df.index], names=bridge_ref_df.index.names
            )
        if not isinstance(bridge_ref_df.columns, pd.MultiIndex):
            bridge_ref_df.columns = pd.MultiIndex.from_arrays(
                [bridge_ref_df.columns], names=bridge_ref_df.columns.names
            )

        # Load bridge from Excel file
        bridge_test = bridge.Bridge(kind=bridge_kind)
        bridge_test.load_from_path(
            path=self.bridge_path, file_name=self.bridge_file
        )

        # Check that the loaded bridge is equal to the reference dataframe
        assert bridge_test.df.astype(self.bridge_type).equals(bridge_ref_df)

        # Check that the aggregation matrix is equal to the reference dataframe without the "Check" line
        if isinstance(bridge_ref_df.index, pd.MultiIndex):
            bridge_ref_df_without_check = bridge_ref_df.drop(
                (bridge.AbstractBridge.INDEX_CHECK_LINE,)
                * len(bridge_ref_df.index.names)
            )
        else:
            bridge_ref_df_without_check = bridge_ref_df.drop(
                bridge.AbstractBridge.INDEX_CHECK_LINE
            )

        assert (
            bridge_test.get_agg_matrix().to_dataframe()
            .astype(self.bridge_type)
            .equals(bridge_ref_df_without_check)
        )

    def test_bridge_rows_3_columns_3(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=self.categories,
                    sub_categories=self.sub_categories,
                    sectors=self.sectors,
                )
            ),
            columns=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=self.agg_categories,
                    sub_categories=self.agg_sub_categories,
                    sectors=self.agg_sectors,
                )
            ),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_2_columns_3(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=self.sub_categories,
                    sectors=self.sectors,
                )
            ),
            columns=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=self.agg_categories,
                    sub_categories=self.agg_sub_categories,
                    sectors=self.agg_sectors,
                )
            ),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.REGIONS
        )

    def test_bridge_rows_1_columns_3(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=[],
                    sectors=self.sectors,
                ),
            ),
            columns=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=self.agg_categories,
                    sub_categories=self.agg_sub_categories,
                    sectors=self.agg_sectors,
                )
            ),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_3_columns_2(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=self.categories,
                    sub_categories=self.sub_categories,
                    sectors=self.sectors,
                )
            ),
            columns=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=self.agg_sub_categories,
                    sectors=self.agg_sectors,
                )
            ),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_2_columns_2(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=self.sub_categories,
                    sectors=self.sectors,
                )
            ),
            columns=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=self.agg_sub_categories,
                    sectors=self.agg_sectors,
                )
            ),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES
        )

    def test_bridge_rows_3_columns_0(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=self.categories,
                    sub_categories=self.sub_categories,
                    sectors=self.sectors,
                )
            ),
            columns=pd.Index(["A", "B", "C"]),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.EXTENSION_CATEGORIES
        )

    def test_bridge_rows_2_columns_0(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=self.sub_categories,
                    sectors=self.sectors,
                )
            ),
            columns=pd.Index(["A", "B", "C"]),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.EXTENSION_CATEGORIES
        )

    def test_bridge_rows_1_columns_0(self):

        # Generate bridge dataframe
        bridge_ref_df = pd.DataFrame(
            index=pd.Index(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=[],
                    sectors=self.sectors,
                ).squeeze(),
                name="sector",
            ),
            columns=pd.Index(["A", "B", "C"]),
            data=0,
            dtype=self.bridge_type,
        )

        # Execute test on reference bridge
        self.execute_test_on_specific_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )


class TestGetFilteredBridge:

    def test_no_filters(self, mocker, bridge_sectors_from_2_to_1):
        """
        Test function `get_filtered_bridge`

        Pass no filters, verify apply_to_bridge is never called and
        Bridge.init_from_df is called with the original df.
        """
        mock_init = mocker.patch(
            "matmat.core.bridge.core.Bridge.init_from_matrix",
            return_value=mocker.Mock(),
        )
        mocker.patch(
            "matmat.utils.tools.convert_regular_index_to_single_level_multi_index",
            return_value=mocker.Mock(),
        )

        result = bridge_sectors_from_2_to_1.get_filtered_bridge()

        assert mock_init.call_count == 1
        spy.check_specific_call_with_args(
            function_spy=mock_init,
            call_number=1,
            args=[],
            kwargs={
                "kind": bridge_sectors_from_2_to_1.kind,
                "matrix": bridge_sectors_from_2_to_1.matrix,
            }
        )

        assert result == mock_init.return_value

    def test_single_filter(self, mocker, bridge_sectors_from_2_to_1):
        """
        Test function `get_filtered_bridge`

        Pass a single mocked filter, verify apply_to_bridge is called with
        the original df and Bridge.init_from_df receives the filtered df.
        """
        filtered_matrix = mocker.Mock()
        mock_filter = mocker.Mock()
        mock_filter.apply_to_bridge.return_value = filtered_matrix
        mock_init = mocker.patch(
            "matmat.core.bridge.core.Bridge.init_from_matrix",
            return_value=mocker.Mock(),
        )
        mocker.patch(
            "matmat.utils.tools.cast_index_to_multiindex",
            return_value=mocker.Mock(),
        )

        result = bridge_sectors_from_2_to_1.get_filtered_bridge(mock_filter)

        assert mock_init.call_count == 1
        spy.check_specific_call_with_args(
            function_spy=mock_init,
            call_number=1,
            args=[],
            kwargs={
                "kind": bridge_sectors_from_2_to_1.kind,
                "matrix": filtered_matrix,
            },
        )
        assert result == mock_init.return_value

    def test_multiple_filters_chained(
        self, mocker, bridge_sectors_from_2_to_1
    ):
        """
        Test function `get_filtered_bridge`

        Pass two mocked filters, verify they are applied in order, each
        receiving the output of the previous one.
        """
        matrix_after_first = mocker.Mock()
        matrix_after_second = mocker.Mock()
        filter_1 = mocker.Mock()
        filter_1.apply_to_bridge.return_value = matrix_after_first
        filter_2 = mocker.Mock()
        filter_2.apply_to_bridge.return_value = matrix_after_second
        mock_init = mocker.patch(
            "matmat.core.bridge.core.Bridge.init_from_matrix",
            return_value=mocker.Mock(),
        )
        mocker.patch(
            "matmat.utils.tools.cast_index_to_multiindex",
            return_value=mocker.Mock(),
        )

        bridge_sectors_from_2_to_1.get_filtered_bridge(filter_1, filter_2)

        spy.check_specific_call_with_args(
            function_spy=filter_1.apply_to_bridge,
            call_number=1,
            args=[],
            kwargs={
                "matrix": bridge_sectors_from_2_to_1.matrix,
            },
        )
        spy.check_specific_call_with_args(
            function_spy=filter_2.apply_to_bridge,
            call_number=1,
            args=[],
            kwargs={
                "matrix": matrix_after_first,
            },
        )

        assert mock_init.call_count == 1
        spy.check_specific_call_with_args(
            function_spy=mock_init,
            call_number=1,
            args=[],
            kwargs={
                "kind": bridge_sectors_from_2_to_1.kind,
                "matrix": matrix_after_second,
            },
        )

    def test_convert_index_called(self, mocker, bridge_sectors_from_2_to_1):
        """
        Test function `get_filtered_bridge`

        Verify cast_index_to_multiindex is called
        with the final filtered df before Bridge.init_from_matrix.
        """
        mocker.patch(
            "matmat.core.bridge.core.Bridge.init_from_matrix",
            return_value=mocker.Mock(),
        )
        mock_convert = mocker.patch(
            "matmat.utils.tools.cast_index_to_multiindex",
            return_value=mocker.Mock(),
        )

        rows_before_filter = bridge_sectors_from_2_to_1.matrix.rows
        columns_before_filter = bridge_sectors_from_2_to_1.matrix.columns
        bridge_sectors_from_2_to_1.get_filtered_bridge()

        spy.check_specific_call_with_args(
            function_spy=mock_convert,
            call_number=1,
            args=[rows_before_filter],
            kwargs={},
        )
        spy.check_specific_call_with_args(
            function_spy=mock_convert,
            call_number=2,
            args=[columns_before_filter],
            kwargs={},
        )


class TestProjectAggMatrix:

    def test_level_names_proj_with_1_dl(
        self, bridge_regions_from_1_to_2, dl_sectors_1
    ):
        """
        Test function `project_agg_matrix`

        Verify that the level names of the projected aggregation matrix match
        the expected concatenation of dimension level names when projecting
        with one detail level.
        """

        # Call function under test
        proj_agg_matrix = bridge_regions_from_1_to_2.project_agg_matrix(
            dl_sectors_1
        )
        assert (
            proj_agg_matrix.rows.names
            == bridge_regions_from_1_to_2.rows_dl.get_level_names()
            + dl_sectors_1.get_level_names()
        )
        assert (
            proj_agg_matrix.columns.names
            == bridge_regions_from_1_to_2.columns_dl.get_level_names()
            + dl_sectors_1.get_level_names()
        )

    def test_level_names_proj_with_2_dls(
        self,
        bridge_regions_from_1_to_2,
        dl_sectors_1,
        dl_final_demand_categories_1,
    ):
        """
        Test function `project_agg_matrix`

        Verify that the level names of the projected aggregation matrix match
        the expected concatenation of dimension level names when projecting
        with two detail levels.
        """

        # Call function under test
        proj_agg_matrix = bridge_regions_from_1_to_2.project_agg_matrix(
            [dl_final_demand_categories_1, dl_sectors_1],
        )
        assert (
            proj_agg_matrix.rows.names
            == bridge_regions_from_1_to_2.rows_dl.get_level_names()
            + dl_sectors_1.get_level_names()
            + dl_final_demand_categories_1.get_level_names()
        )
        assert (
            proj_agg_matrix.columns.names
            == bridge_regions_from_1_to_2.columns_dl.get_level_names()
            + dl_sectors_1.get_level_names()
            + dl_final_demand_categories_1.get_level_names()
        )

    def test_projected_values(self):
        """
        Test function `project_agg_matrix`

        Verify the projection of an aggregation matrix from sector detail level
        to final demand categories detail level using a bridge matrix.

        Especially checks that the mask is correctly applied after index
        broadcasting to retrieve only the relevant 1, the non-relevant
        ones being set to 0.
        """
        # Define levels
        level_category = "category"
        level_sector = "sector"
        level_fd_category = "Y_category"
        level_fd_sub_category = "Y_sub_category"

        bridge_df = pd.DataFrame(
            data=[[1, 0, 0], [0, 1, 1]],
            index=pd.MultiIndex.from_tuples(
                [("A",), ("B",)], names=[level_category]
            ),
            columns=pd.MultiIndex.from_tuples(
                [("A", "A1"), ("B", "B1"), ("B", "B2")],
                names=[level_category, level_sector],
            ),
            dtype=cst.DTYPE_FLOAT,
        )
        bridge_ = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=bridge_df,
        )

        fd_dl = dl.FinalDemandCategoriesDL(
            df=pd.DataFrame(
                {
                    level_fd_category: ["X", "X", "Y"],
                    level_fd_sub_category: ["X1", "X2", "Y1"],
                }
            )
        )

        projected_index = pd.MultiIndex.from_tuples(
            [
                ("A", "X", "X1"),
                ("A", "X", "X2"),
                ("A", "Y", "Y1"),
                ("B", "X", "X1"),
                ("B", "X", "X2"),
                ("B", "Y", "Y1"),
            ],
            names=[level_category, level_fd_category, level_fd_sub_category],
        )
        projected_columns = pd.MultiIndex.from_tuples(
            [
                ("A", "A1", "X", "X1"),
                ("A", "A1", "X", "X2"),
                ("A", "A1", "Y", "Y1"),
                ("B", "B1", "X", "X1"),
                ("B", "B1", "X", "X2"),
                ("B", "B1", "Y", "Y1"),
                ("B", "B2", "X", "X1"),
                ("B", "B2", "X", "X2"),
                ("B", "B2", "Y", "Y1"),
            ],
            names=[
                level_category,
                level_sector,
                level_fd_category,
                level_fd_sub_category,
            ],
        )

        expected_agg_matrix = pd.DataFrame(
            data=[
                [1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1, 0, 0, 1],
            ],
            index=projected_index,
            columns=projected_columns,
            dtype=cst.DTYPE_FLOAT,
        )

        # Call function under test
        tested_agg_matrix = bridge_.project_agg_matrix(fd_dl)

        # Check results
        assert tested_agg_matrix.to_dataframe().equals(expected_agg_matrix)


class TestExtendAggMatrix:

    def test_level_names_extended_with_1_dl(
        self, bridge_regions_from_1_to_2, dl_sectors_1
    ):
        """
        Test function `extend_agg_matrix`

        Verify that the level names of the extended aggregation matrix match
        the expected concatenation of dimension level names when projecting
        with one detail level.
        """

        # Call function under test
        extended_agg_matrix = bridge_regions_from_1_to_2.extend_agg_matrix(
            dl_sectors_1
        )
        assert (
            extended_agg_matrix.rows.names
            == dl_sectors_1.get_level_names()
            + bridge_regions_from_1_to_2.rows_dl.get_level_names()
        )
        assert (
            extended_agg_matrix.columns.names
            == dl_sectors_1.get_level_names()
            + bridge_regions_from_1_to_2.columns_dl.get_level_names()
        )

    def test_level_names_extended_with_2_dls(
        self,
        bridge_fdc_from_1_to_2,
        dl_regions_1,
        dl_sectors_1,
    ):
        """
        Test function `extend_agg_matrix`

        Verify that the level names of the extended aggregation matrix match
        the expected concatenation of dimension level names when projecting
        with two detail levels.
        """

        # Call function under test
        extended_agg_matrix = bridge_fdc_from_1_to_2.extend_agg_matrix(
            [dl_sectors_1, dl_regions_1],
        )
        assert (
            extended_agg_matrix.rows.names
            == dl_regions_1.get_level_names()
            + dl_sectors_1.get_level_names()
            + bridge_fdc_from_1_to_2.rows_dl.get_level_names()
        )
        assert (
            extended_agg_matrix.columns.names
            == dl_regions_1.get_level_names()
            + dl_sectors_1.get_level_names()
            + bridge_fdc_from_1_to_2.columns_dl.get_level_names()
        )

    def test_extended_values(self):
        """
        Test function `extend_agg_matrix`

        Test the extension of an aggregation matrix by final demand categories.
        Verifies correct projection of bridge data onto a multi-indexed matrix.
        """
        # Define levels
        level_category = "category"
        level_sector = "sector"
        level_fd_category = "Y_category"
        level_fd_sub_category = "Y_sub_category"

        bridge_df = pd.DataFrame(
            data=[[1, 0, 0], [0, 1, 1]],
            index=pd.MultiIndex.from_tuples(
                [("A",), ("B",)], names=[level_category]
            ),
            columns=pd.MultiIndex.from_tuples(
                [("A", "A1"), ("B", "B1"), ("B", "B2")],
                names=[level_category, level_sector],
            ),
            dtype=cst.DTYPE_FLOAT,
        )
        bridge_ = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=bridge_df,
        )

        fd_dl = dl.FinalDemandCategoriesDL(
            df=pd.DataFrame(
                {
                    level_fd_category: ["X", "X", "Y"],
                    level_fd_sub_category: ["X1", "X2", "Y1"],
                }
            )
        )

        projected_index = pd.MultiIndex.from_tuples(
            [
                ("X", "X1", "A"),
                ("X", "X1", "B"),
                ("X", "X2", "A"),
                ("X", "X2", "B"),
                ("Y", "Y1", "A"),
                ("Y", "Y1", "B"),
            ],
            names=[level_fd_category, level_fd_sub_category, level_category],
        )
        projected_columns = pd.MultiIndex.from_tuples(
            [
                ("X", "X1", "A", "A1"),
                ("X", "X1", "B", "B1"),
                ("X", "X1", "B", "B2"),
                ("X", "X2", "A", "A1"),
                ("X", "X2", "B", "B1"),
                ("X", "X2", "B", "B2"),
                ("Y", "Y1", "A", "A1"),
                ("Y", "Y1", "B", "B1"),
                ("Y", "Y1", "B", "B2"),
            ],
            names=[
                level_fd_category,
                level_fd_sub_category,
                level_category,
                level_sector,
            ],
        )

        expected_agg_matrix = pd.DataFrame(
            data=[
                [1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1, 1],
            ],
            index=projected_index,
            columns=projected_columns,
            dtype=cst.DTYPE_FLOAT,
        )

        # Call function under test
        tested_agg_matrix = bridge_.extend_agg_matrix(fd_dl)

        # Check results
        assert tested_agg_matrix.to_dataframe().equals(expected_agg_matrix)
