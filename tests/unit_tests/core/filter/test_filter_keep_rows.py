import pytest

from matmat.core.base.filter import FilterKeepRows


LEVEL_NAME = "origin"
LEVEL_VALUE = "domestic"


@pytest.fixture
def filter_keep_rows():
    return FilterKeepRows(level_name=LEVEL_NAME, level_value=LEVEL_VALUE)


class TestApplyToDetailLevel:

    def test_keeps_matching_rows(self, filter_keep_rows, dl_regions_3):
        """
        Test function `FilterKeepRows.apply_to_detail_level`

        Test that only rows matching the specified level value are kept.
        """
        result = filter_keep_rows.apply_to_detail_level(dl_regions_3.df)
        assert (result[LEVEL_NAME] == LEVEL_VALUE).all()
        assert len(result) == 4

    def test_returns_empty_if_no_match(self, dl_regions_3):
        """
        Test function `FilterKeepRows.apply_to_detail_level`

        Test that an empty DataFrame is returned when no rows match
        the specified level value.
        """
        filter_ = FilterKeepRows(
            level_name=LEVEL_NAME, level_value="nonexistent"
        )
        result = filter_.apply_to_detail_level(dl_regions_3.df)
        assert result.empty

    def test_returns_all_rows_if_all_match(self, dl_regions_3):
        """
        Test function `FilterKeepRows.apply_to_detail_level`

        Test that all rows are returned when all match the specified
        level value.
        """
        filter_ = FilterKeepRows(level_name="region", level_value="France")
        df = dl_regions_3.df[dl_regions_3.df["region"] == "France"]
        result = filter_.apply_to_detail_level(df)
        assert len(result) == len(df)

    def test_does_not_modify_columns(self, filter_keep_rows, dl_regions_3):
        """
        Test function `FilterKeepRows.apply_to_detail_level`

        Test that the column structure remains unchanged after filtering.
        """
        result = filter_keep_rows.apply_to_detail_level(dl_regions_3.df)
        assert list(result.columns) == list(dl_regions_3.df.columns)


class TestApplyToBridge:
    """Test suite for `FilterKeepRows.apply_to_bridge`."""

    def test_keeps_matching_rows_and_columns(
        self, filter_keep_rows, bridge_regions_from_3_to_1
    ):
        """
        Test function `FilterKeepRows.apply_to_bridge`

        Test that only matching rows and columns are kept in a bridge
        DataFrame.
        """
        result = filter_keep_rows.apply_to_bridge(
            bridge_regions_from_3_to_1.matrix
        )
        assert (result.index.get_level_values(LEVEL_NAME) == LEVEL_VALUE).all()
        assert (
            result.columns.get_level_values(LEVEL_NAME) == LEVEL_VALUE
        ).all()
        assert result.shape == (4, 1)

    def test_returns_empty_if_no_match(self, bridge_regions_from_3_to_1):
        """
        Test function `FilterKeepRows.apply_to_bridge`

        Test that an empty DataFrame is returned when no rows or
        columns match the specified level value.
        """
        filter_ = FilterKeepRows(
            level_name=LEVEL_NAME, level_value="nonexistent"
        )
        result = filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
        assert result.to_dataframe().empty

    def test_returns_all_if_all_match(
        self, filter_keep_rows, bridge_regions_from_3_to_1
    ):
        """
        Test function `FilterKeepRows.apply_to_bridge`

        Test that the entire DataFrame is returned when all rows and
        columns match the specified level value.
        """
        filter_ = FilterKeepRows(level_name=LEVEL_NAME, level_value="import")
        result = filter_.apply_to_bridge(bridge_regions_from_3_to_1.matrix)
        assert result.shape == (5, 1)
