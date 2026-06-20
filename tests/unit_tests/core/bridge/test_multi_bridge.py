import os

import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from tests.utils import builders


class TestMultiBridge:

    bridge_type = "Int64"
    bridge_file = "test_multi_bridge.xlsx"
    bridge_path = os.path.dirname(__file__)
    bridge_file_path = os.path.join(bridge_path, bridge_file)
    bridge_filter_level = "agg_level"

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

    @staticmethod
    def add_check_line(df: pd.DataFrame):
        if isinstance(df.index, pd.MultiIndex):
            df.loc[
                (bridge.AbstractBridge.INDEX_CHECK_LINE,)
                * len(df.index.names),
                :,
            ] = 1
        else:
            df.loc[bridge.AbstractBridge.INDEX_CHECK_LINE, :] = 1

    def execute_test_on_specific_multi_bridge(
        self,
        bridge_ref_df: pd.DataFrame,
        bridge_kind: dl.DetailLevelKind,
    ):

        self.add_check_line(bridge_ref_df)

        # Build multibridge dataframe
        multi_bridge_ref_df = pd.concat(
            {
                "columns_agg_level_1": pd.concat(
                    {
                        "rows_agg_level_1": bridge_ref_df,
                        "rows_agg_level_2": bridge_ref_df,
                    },
                    axis=0,
                    names=[self.bridge_filter_level],
                )
            },
            axis=1,
            names=[self.bridge_filter_level],
        )

        # Add random 1 to make it as close to a functional bridge as possible
        builders.add_random_number(multi_bridge_ref_df, 1)

        # Export to an Excel file
        multi_bridge_ref_df.to_excel(
            self.bridge_file_path,
            sheet_name=bridge_kind.value,
        )

        # Load bridge from Excel file
        bridge_test = bridge.MultiBridge(
            kind=bridge_kind,
            filter_level=self.bridge_filter_level,
        )
        bridge_test.load_from_path(
            path=self.bridge_path, file_name=self.bridge_file
        )

        # Check that the loaded bridge is equal to the reference dataframe
        assert bridge_test.df.astype(self.bridge_type).equals(
            multi_bridge_ref_df
        )

        # Check that, for each aggregation level,
        # the aggregation matrix is equal to the reference dataframe without the "Check" line
        # Loop on row aggregation levels
        for row_key in bridge_test.df.index.get_level_values(
            self.bridge_filter_level
        ).unique():
            # Loop on column aggregation levels
            for col_key in bridge_test.df.columns.get_level_values(
                self.bridge_filter_level
            ).unique():

                sub_df = multi_bridge_ref_df.loc[row_key][col_key]
                if isinstance(sub_df.index, pd.MultiIndex):
                    bridge_ref_df_without_check = sub_df.drop(
                        (bridge.AbstractBridge.INDEX_CHECK_LINE,)
                        * len(sub_df.index.names)
                    )
                else:
                    bridge_ref_df_without_check = sub_df.drop(
                        bridge.AbstractBridge.INDEX_CHECK_LINE
                    )

                assert (
                    bridge_test.get_agg_matrix(key=row_key)
                    .to_dataframe()
                    .astype(self.bridge_type)
                    .equals(bridge_ref_df_without_check)
                )

    def test_bridge_rows_3_columns_3(self):

        # Generate bridge dataframes
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
        self.execute_test_on_specific_multi_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_2_columns_3(self):

        # Generate bridge dataframes
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
        self.execute_test_on_specific_multi_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_2_columns_2(self):

        # Generate bridge dataframes
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
        self.execute_test_on_specific_multi_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_1_columns_3(self):

        # Generate bridge dataframes
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=[],
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
        self.execute_test_on_specific_multi_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_1_columns_2(self):

        # Generate bridge dataframes
        bridge_ref_df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(
                builders.generate_sectors(
                    categories=[],
                    sub_categories=[],
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
        self.execute_test_on_specific_multi_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )

    def test_bridge_rows_3_columns_2(self):

        # Generate bridge dataframes
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
        self.execute_test_on_specific_multi_bridge(
            bridge_ref_df, dl.DetailLevelKind.SECTORS
        )
