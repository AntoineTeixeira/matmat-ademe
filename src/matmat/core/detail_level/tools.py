__all__ = [
    "propagate_columns",
]

import pandas as pd


def propagate_columns(
    df_from: pd.DataFrame, df_to: pd.DataFrame
) -> pd.DataFrame:
    """
    Propagates the values of each row in `df_to` to all rows of `df_from`,
    creating a Cartesian product.

    The resulting DataFrame contains all columns from both `df_to` and `df_from`,
    with `df_from` columns repeated for each row of `df_to`.
    """
    merge_key = "__merge_key__"
    df_from = df_from.assign(__merge_key__=1)
    df_to = df_to.assign(__merge_key__=1)
    result = df_to.merge(df_from, on=merge_key).drop(columns=merge_key)
    return result
