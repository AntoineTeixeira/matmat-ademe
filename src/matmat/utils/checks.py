"""
Presentation
************
This module contains classes and functions to perform common verification
operations

Content
*******
- Functions:
    - :meth:`check_dict_key`
    - :meth:`are_df_equal_with_tolerance`
"""

import pandas as pd
import numpy as np

from matmat.utils.errors import MEMissingKey


def check_dict_key(json_dict: dict, key: str):
    """
    Check that key is included in json_dict keys

    Raises:
        MEMissingKey
    """
    if key not in json_dict.keys():
        raise MEMissingKey(key=key, given_keys=json_dict.keys())


def are_df_equal_with_tolerance(
    tested_df: pd.DataFrame,
    ref_df: pd.DataFrame,
    with_index: bool = False,
) -> bool:
    """
    Check the equality between two dataframes (with tolerance)

    The relative tolerance is set to **1e-05**

    The absolute tolerance is set to **1e-06**

    Parameters:
        tested_df (pd.DataFrame):
            The dataframe to compare with the reference dataframe
        ref_df (pd.DataFrame):
            The reference dataframe
        with_index (bool):
            True if the rows / columns index shall be compared. If False,
            only the values are compared.

    Returns:
        True if the dataframes are equal, False otherwise
    """
    # Tolerance configuration constants
    R_TOL_INITIAL = 1e-05
    R_TOL_MAX = 1e-05
    A_TOL = 1e-06

    are_index_equal = tested_df.index.equals(
        ref_df.index
    ) and tested_df.columns.equals(ref_df.columns)

    # result_r_tol = "no matching r_tol"
    are_values_equal = False

    if tested_df.shape == ref_df.shape:
        # If both dataframes contains only NaN, we consider them equal
        if tested_df.isna().all().all() and ref_df.isna().all().all():
            are_values_equal = True
        else:
            current_r_tol = R_TOL_INITIAL
            while current_r_tol <= R_TOL_MAX:
                are_values_equal = np.allclose(
                    tested_df.values,
                    ref_df.values,
                    atol=A_TOL,
                    rtol=current_r_tol,
                    equal_nan=True,
                )
                if are_values_equal:
                    # result_r_tol = current_r_tol
                    break
                current_r_tol *= 10
    else:
        are_values_equal = False

    if with_index:
        are_equal = are_index_equal and are_values_equal
    else:
        are_equal = are_values_equal

    return are_equal


def compare_dataframes(
    df_ref: pd.DataFrame,
    df_test: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """
    Compare two pandas DataFrames and return the cells whose absolute difference
    is greater than a given threshold or where only one of the two values is NaN.

    Adds a relative difference column expressed as a percentage.

    Parameters
    ----------
    df_ref : pd.DataFrame
        Reference DataFrame.
    df_test : pd.DataFrame
        Test DataFrame.
    threshold : float
        Absolute difference threshold.

    Returns
    -------
    pd.DataFrame
        Output DataFrame with one row per differing cell and the following columns:
        - row_index
        - column_index
        - ref_value
        - test_value
        - abs_diff
        - relative_diff_pct
    """

    # --- Index validation ---
    if not df_ref.index.equals(df_test.index):
        raise ValueError("Row indexes of the two DataFrames are not identical.")

    if not df_ref.columns.equals(df_test.columns):
        raise ValueError("Column indexes of the two DataFrames are not identical.")

    # --- Absolute difference ---
    abs_diff = (df_ref - df_test).abs()

    # True when exactly one of the two values is NaN
    nan_mismatch = df_ref.isna() ^ df_test.isna()

    # For NaN mismatches, abs_diff is the non-NaN value
    abs_diff = abs_diff.where(~nan_mismatch, df_ref.fillna(df_test).abs())

    # --- Selection condition ---
    mask = (abs_diff > threshold) | nan_mismatch

    # Exclude cells where both values are NaN
    mask &= ~(df_ref.isna() & df_test.isna())

    # --- Relative difference (percentage) ---
    ref_values = df_ref.to_numpy()
    test_values = df_test.to_numpy()
    abs_diff_values = abs_diff.to_numpy()

    with np.errstate(divide="ignore", invalid="ignore"):
        relative_diff = abs_diff_values / np.abs(ref_values)

    # ref == 0 and test != 0 → +inf
    relative_diff = np.where(
        (ref_values == 0.0) & (test_values != 0.0),
        np.inf,
        relative_diff,
        )

    # ref == 0 and test == 0 → 0
    relative_diff = np.where(
        (ref_values == 0.0) & (test_values == 0.0),
        0.0,
        relative_diff,
        )

    # NaN mismatch → NaN
    nan_mismatch_values = nan_mismatch.to_numpy()
    relative_diff = np.where(
        nan_mismatch_values,
        np.nan,
        relative_diff,
    )

    # Convert to percentage
    relative_diff_pct = relative_diff * 100.0

    # --- Output DataFrame construction ---
    if not mask.any().any():
        return pd.DataFrame(
            columns=[
                "row_index",
                "column_index",
                "ref_value",
                "test_value",
                "abs_diff",
                "relative_diff_pct",
            ]
        )

    rows, cols = np.where(mask.to_numpy())

    result = pd.DataFrame(
        {
            "row_index": [df_ref.index[i] for i in rows],
            "column_index": [df_ref.columns[j] for j in cols],
            "ref_value": df_ref.to_numpy()[rows, cols],
            "test_value": df_test.to_numpy()[rows, cols],
            "abs_diff": abs_diff.to_numpy()[rows, cols],
            "relative_diff_pct": relative_diff_pct[rows, cols],
        }
    )

    # Add information about total if the diff is not empty
    if not result.empty:
        total_ref = np.nansum(df_ref.to_numpy())
        total_test = np.nansum(df_test.to_numpy())
        total_abs_diff = abs(total_ref - total_test)

        if total_ref == 0.0:
            total_relative_diff_pct = 0.0 if total_test == 0.0 else np.inf
        else:
            total_relative_diff_pct = (
                total_abs_diff / abs(total_ref)
            ) * 100.0

        total_row = pd.DataFrame(
            {
                "row_index": ["Total"],
                "column_index": ["Total"],
                "ref_value": [total_ref],
                "test_value": [total_test],
                "abs_diff": [total_abs_diff],
                "relative_diff_pct": [total_relative_diff_pct],
            }
        )

        result = pd.concat([total_row, result], ignore_index=True)


    return result


def compare_zero_reference(
    df_ref: pd.DataFrame,
    df_test: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare two pandas DataFrames and return the cells where the reference value
    is exactly 0.0 and the test value is non-zero.

    Parameters
    ----------
    df_ref : pd.DataFrame
        Reference DataFrame.
    df_test : pd.DataFrame
        Test DataFrame.

    Returns
    -------
    pd.DataFrame
        Output DataFrame with one row per matching cell and the following columns:
        - row_index
        - column_index
        - ref_value
        - test_value
        - abs_diff
    """

    # --- Index validation ---
    if not df_ref.index.equals(df_test.index):
        raise ValueError("Row indexes of the two DataFrames are not identical.")

    if not df_ref.columns.equals(df_test.columns):
        raise ValueError("Column indexes of the two DataFrames are not identical.")

    # --- Selection condition ---
    # Cell is selected if:
    # - reference value is exactly 0.0
    # - test value is not 0.0
    # NaN values are naturally excluded
    mask = (df_ref == 0.0) & (df_test != 0.0)

    # --- Absolute difference ---
    # Here this is equivalent to abs(test_value),
    # but we keep the same semantic as the previous function
    abs_diff = (df_ref - df_test).abs()

    # --- Output DataFrame construction ---
    if not mask.any().any():
        return pd.DataFrame(
            columns=[
                "row_index",
                "column_index",
                "ref_value",
                "test_value",
                "abs_diff",
            ]
        )

    rows, cols = np.where(mask.to_numpy())

    result = pd.DataFrame(
        {
            "row_index": [df_ref.index[i] for i in rows],
            "column_index": [df_ref.columns[j] for j in cols],
            "ref_value": df_ref.to_numpy()[rows, cols],
            "test_value": df_test.to_numpy()[rows, cols],
            "abs_diff": abs_diff.to_numpy()[rows, cols],
        }
    )

    return result

