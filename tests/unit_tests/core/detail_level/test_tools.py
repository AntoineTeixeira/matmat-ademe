import pytest
import pandas as pd
import numpy as np

from matmat.core.detail_level import tools as dl_tools


class TestPropagateColumns:

    @pytest.fixture
    def df_from(self):
        return pd.DataFrame({"x": ["x1", "x2"], "y": ["y1", "y2"]})

    @pytest.fixture
    def df_to(self):
        return pd.DataFrame({"a": ["a", "a", "b"], "b": ["a1", "a2", "b1"], "c": ["c1", "c2", "c3"]})

    def test_propagate_columns_row_count(self, df_from, df_to):
        """
        Test function `propagate_columns`

        Checks that the result contains N×M rows.
        """
        result = dl_tools.propagate_columns(df_from, df_to)
        assert len(result) == len(df_from) * len(df_to)

    def test_propagate_columns_column_order(self, df_from, df_to):
        """
        Test function `propagate_columns`

        Checks that df_to columns appear before df_from columns.
        """
        result = dl_tools.propagate_columns(df_from, df_to)
        assert list(result.columns) == list(df_to.columns) + list(df_from.columns)

    def test_propagate_columns_df_to_values_propagated(self, df_from, df_to):
        """
        Test function `propagate_columns`

        Checks that each value from df_to is repeated len(df_from) times in the result.
        """
        result = dl_tools.propagate_columns(df_from, df_to)
        for i, (_, row) in enumerate(df_to.iterrows()):
            block = result.iloc[i * len(df_from) : (i + 1) * len(df_from)]
            for col, val in row.items():
                assert (block[col] == val).all()

    def test_propagate_columns_df_from_values_preserved(self, df_from, df_to):
        """
        Test function `propagate_columns`

        Checks that df_from values are correctly copied into each block.
        """
        result = dl_tools.propagate_columns(df_from, df_to)
        for i in range(len(df_to)):
            block = result.iloc[i * len(df_from) : (i + 1) * len(df_from)]
            for col in df_from.columns:
                np.testing.assert_array_equal(block[col].values, df_from[col].values)

    def test_propagate_columns_single_row_df_to(self, df_from):
        """
        Test function `propagate_columns`

        Checks the behaviour when df_to contains a single row.
        """
        df_to_single = pd.DataFrame({"a": ["a"], "b": ["a1"], "c": ["c1"]})
        result = dl_tools.propagate_columns(df_from, df_to_single)
        assert len(result) == len(df_from)
        assert (result["a"] == "a").all()
        assert (result["b"] == "a1").all()
        assert (result["c"] == "c1").all()

    def test_propagate_columns_single_row_df_from(self, df_to):
        """
        Test function `propagate_columns`

        Checks the behaviour when df_from contains a single row.
        """
        df_from_single = pd.DataFrame({"x": ["x1"], "y": ["y1"]})
        result = dl_tools.propagate_columns(df_from_single, df_to)
        assert len(result) == len(df_to)
        assert (result["x"] == "x1").all()
        assert (result["y"] == "y1").all()

    def test_propagate_columns_reset_index(self, df_from, df_to):
        """
        Test function `propagate_columns`

        Checks that the result index is a plain RangeIndex 0..N×M-1.
        """
        result = dl_tools.propagate_columns(df_from, df_to)
        expected_index = pd.RangeIndex(len(df_from) * len(df_to))
        pd.testing.assert_index_equal(result.index, expected_index)

