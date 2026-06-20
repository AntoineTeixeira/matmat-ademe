from matmat.core.base.filter import FilterRemoveRows


LEVEL_NAME = "origin"
LEVEL_VALUE = "domestic"

class TestFilterRemoveRows:

    class TestApplyToDetailLevel:
        """Test suite for `FilterRemoveRows.apply_to_detail_level`."""

        def test_removes_matching_rows(self, dl_regions_3):
            """
            Test function `FilterRemoveRows.apply_to_detail_level`

            Test that rows matching the specified level value are removed.
            """
            filter_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value=LEVEL_VALUE)
            result = filter_.apply_to_detail_level(dl_regions_3.df)
            assert (result[LEVEL_NAME] != LEVEL_VALUE).all()
            assert len(result) == 5

        def test_returns_intact_if_no_match(self, dl_regions_3):
            """
            Test function `FilterRemoveRows.apply_to_detail_level`

            Test that the DataFrame remains unchanged when no rows match
            the specified level value.
            """
            filter_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value="nonexistent")
            result = filter_.apply_to_detail_level(dl_regions_3.df)
            assert len(result) == len(dl_regions_3.df)

        def test_returns_empty_if_all_match(self, dl_regions_3):
            """
            Test function `FilterRemoveRows.apply_to_detail_level`

            Test that an empty DataFrame is returned when all rows match
            the specified level value.
            """
            df = dl_regions_3.df[dl_regions_3.df[LEVEL_NAME] == LEVEL_VALUE]
            filter_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value=LEVEL_VALUE)
            result = filter_.apply_to_detail_level(df)
            assert result.empty

        def test_does_not_modify_columns(self, dl_regions_3):
            """
            Test function `FilterRemoveRows.apply_to_detail_level`

            Test that the column structure remains unchanged after filtering.
            """
            filter_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value=LEVEL_VALUE)
            result = filter_.apply_to_detail_level(dl_regions_3.df)
            assert list(result.columns) == list(dl_regions_3.df.columns)

    class TestApplyToBridge:
        """Test suite for `FilterRemoveRows.apply_to_bridge`."""

        def test_removes_matching_rows_and_columns(self, bridge_regions_from_3_to_1):
            """
            Test function `FilterRemoveRows.apply_to_bridge`

            Test that matching rows and columns are removed from a bridge
            DataFrame.
            """
            filter_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value=LEVEL_VALUE)
            result = filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
            assert (result.index.get_level_values(LEVEL_NAME) != LEVEL_VALUE).all()
            assert (result.columns.get_level_values(LEVEL_NAME) != LEVEL_VALUE).all()
            assert result.shape == (5, 1)

        def test_returns_intact_if_no_match(self, bridge_regions_from_3_to_1):
            """
            Test function `FilterRemoveRows.apply_to_bridge`

            Test that the DataFrame remains unchanged when no rows or
            columns match the specified level value.
            """
            filter_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value="nonexistent")
            result = filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
            assert result.shape == bridge_regions_from_3_to_1.df.shape

        def test_returns_empty_if_all_match(self, bridge_regions_from_3_to_1):
            """
            Test function `FilterRemoveRows.apply_to_bridge`

            Test that an empty DataFrame is returned when all rows and
            columns match the specified level values.
            """
            filter_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value="domestic")
            intermediate = filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
            filter2_ = FilterRemoveRows(level_name=LEVEL_NAME, level_value="import")
            result = filter2_.apply_to_bridge(intermediate)
            assert result.to_dataframe().empty

