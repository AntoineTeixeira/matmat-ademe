from matmat.core.base.filter import FilterRemoveColumn

LEVEL_NAME = "origin"
LEVEL_VALUE = "domestic"

class TestFilterRemoveColumn:

    class TestApplyToDetailLevel:

        def test_removes_column(self, dl_regions_3):
            """
            Test function `FilterRemoveColumn.apply_to_detail_level`

            Test that the column specified by `level_name` is removed from the
            DataFrame.
            """
            filter_ = FilterRemoveColumn(level_name=LEVEL_NAME)
            result = filter_.apply_to_detail_level(dl_regions_3.df)
            assert LEVEL_NAME not in result.columns

        def test_other_columns_unchanged(self, dl_regions_3):
            """
            Test function FilterRemoveColumn.apply_to_detail_level

            Test that all columns except the one specified by level_name remain
            unchanged in the DataFrame.
            """
            filter_ = FilterRemoveColumn(level_name=LEVEL_NAME)
            result = filter_.apply_to_detail_level(dl_regions_3.df)
            expected_columns = [c for c in dl_regions_3.df.columns if c != LEVEL_NAME]
            assert list(result.columns) == expected_columns

    class TestApplyToBridge:

        def test_removes_level_from_index_and_columns(self, bridge_regions_from_3_to_1):
            """
            Test function `FilterRemoveColumn.apply_to_bridge`

            Test that the specified level is removed from both index and columns
            of a MultiIndex DataFrame.
            """
            filter_ = FilterRemoveColumn(level_name=LEVEL_NAME)
            result = filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
            assert LEVEL_NAME not in result.index.names
            assert LEVEL_NAME not in result.columns.names

        def test_rest_of_multiindex_intact(self, bridge_regions_from_3_to_1):
            """
            Test function `FilterRemoveColumn.apply_to_bridge`

            Test that all remaining levels in the MultiIndex remain intact after
            removing the specified level.
            """
            filter_ = FilterRemoveColumn(level_name=LEVEL_NAME)
            result = filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
            remaining_names = [n for n in bridge_regions_from_3_to_1.df.index.names if n != LEVEL_NAME]
            assert list(result.index.names) == remaining_names

        def test_does_not_mutate_original(self, bridge_regions_from_3_to_1):
            """
            Test function `FilterRemoveColumn.apply_to_bridge`

            Test that the original DataFrame is not mutated after applying the
            filter.
            """
            original_names = list(bridge_regions_from_3_to_1.df.index.names)
            filter_ = FilterRemoveColumn(level_name=LEVEL_NAME)
            filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
            assert list(bridge_regions_from_3_to_1.df.index.names) == original_names
