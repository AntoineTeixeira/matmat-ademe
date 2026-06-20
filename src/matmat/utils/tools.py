"""
Presentation
************
This module contains functions to perform various operations to be reused
throughout MatMat model.

Content
*******
- Functions:
    - :meth:`find_most_recent_input_file`
    - :meth:`clean_dataframe`
    - :meth:`sum_on_sectors`
    - :meth:`inject_data`
"""

__all__ = [
    "find_most_recent_input_file",
    "clean_dataframe",
    "sum_on_sectors",
    "inject_data",
]

import os
import copy
import functools
import time
import hashlib

import pandas as pd
import numpy as np
from scipy import sparse as sp

from matmat.utils import constants as cst, logging as log, config
from matmat.utils.errors import MEIncorrectArguments


def clean_dataframe(df: pd.DataFrame | pd.Series):
    """
    Clean the dataframe inplace from NaN, INF, -INF. Replace them by 0.0.

    Parameters:
        df (pd.DataFrame):
            The dataframe to clean
    """
    df.replace(np.nan, 0.0, inplace=True)
    df.replace(np.inf, 0.0, inplace=True)
    df.replace(-np.inf, 0.0, inplace=True)


def sum_on_sectors(df: pd.DataFrame, axis: int, sectors_levels: list[str] = None) -> pd.DataFrame:
    """
    Sum the dataframe relatively to the levels
    ["category", "sub_category", "sector"], along the given axis

    Parameters:
        df (pd.DataFrame):
            The dataframe to sum
        axis (int):
            0 or 1. The axis along which the sum shall be performed
        sectors_levels (list[str]):
            The list of levels to group by
    Returns:
        pd.DataFrame : the dataframe containing the results of the sum
    """
    if sectors_levels is None:
        sectors_levels = [
            cst.IDX_CATEGORY,
            cst.IDX_SUB_CATEGORY,
            cst.IDX_SECTOR,
        ]

    if axis == 0:
        return df.groupby(
            level=sectors_levels,
            sort=False,
        ).sum()

    if axis == 1:
        return (
            df.T.groupby(
                level=sectors_levels,
                sort=False,
            )
            .sum()
            .T
        )

    log.error("Axis must be 0 or 1")
    raise MEIncorrectArguments(msg="axis = 0 or 1")


def inject_data(
    df_ref: pd.DataFrame, df_new: pd.DataFrame, inject_zeros: bool = False
):
    """
    Inject the values of df_new into df_ref

    If inject_zeros is True, inject the 0.0 as well, otherwise replace them
    by NaN before injection

    Parameters:
        df_ref (pd.DataFrame):
            The dataframe to update
        df_new (pd.DataFrame):
            The dataframe containing the new values
        inject_zeros:
            True if the 0.0 shall be injected
    """
    if inject_zeros:
        df_ref.update(df_new)
    else:
        df_ref.update(df_new.replace(to_replace=0.0, value=np.nan))


def find_most_recent_input_file(path: str, file_name_suffix: str) -> str:
    """
    Find the most recent file w.r.t. the name of the file

    The file names shall follow the standard *YYMMDD-file_name_suffix*

    The function will return the path to the file with the most recent YYMMDD.

    Parameters:
        path (str):
            The path where to search for the file
        file_name_suffix (str):
            The extension of the file (.xlsx, .csv, ...)
    Returns:
        str : the path to the most recent file
    """
    dates = []
    files = {}
    for file_name in os.listdir(path):
        if file_name.endswith(file_name_suffix):
            file_date = file_name.split("-")[0]
            dates.append(file_date)
            files[file_date] = file_name
    dates.sort()
    if len(dates) == 0:
        log.error(f"No {file_name_suffix} input file found")
        raise FileNotFoundError
    log.info(f"Most recent file found is {files[dates[-1]]}")
    return os.path.join(path, files[dates[-1]])

def retrieve_data_list_from_path(path: str, data_list: list) -> list[str]:
    """
    This function builds the list of data files found in path
    among the elements of data_list.

    Parameters:
        path (str):
            The path to the directory containing the files
        data_list (list):
            The list of data to search (i.e. the names of the files
            without extension). The files not matching these names will
            be ignored.
    Returns:
        list[str] : a list of the data names found in path
    """
    list_of_found_data = []
    for elt in os.listdir(path):
        elt_path = os.path.join(path, elt)
        if not os.path.isdir(elt_path):
            elt_name = elt.split(".")[0]
            if elt_name in data_list:
                list_of_found_data.append(elt_name)
    return list_of_found_data


def cast_index_to_multiindex(idx: pd.Index) -> pd.MultiIndex:
    """
    Cast an Index to a MultiIndex.

    If the input is not a MultiIndex, converts it to a single-level MultiIndex.

    Parameters:
        idx (pd.Index): Index to convert.

    Returns:
        pd.MultiIndex: Resulting MultiIndex.
    """
    if not isinstance(idx, pd.MultiIndex):
        return pd.MultiIndex.from_arrays([idx], names=[idx.name])
    return idx


def convert_single_level_multi_index_to_regular_index(df: pd.DataFrame | pd.Series,
                                                      inplace: bool = True) -> None | pd.DataFrame | pd.Series:
    """
    Convert single-level multi-index to regular index.
    Applied to both index and columns (columns only for DataFrame).

    In case of multi-level multi-index, do nothing.

    Parameters:
        df (pd.DataFrame | pd.Series):
            DataFrame or Series to convert.
        inplace (bool):
            If True, modifies in place.
            If False, returns a modified deep copy.
            (default is True)
    Returns:
        None | pd.DataFrame | pd.Series
    """

    def cast_to_index(idx: pd.MultiIndex) -> pd.Index:
        return pd.Index(
            data=idx.get_level_values(0),
            name=idx.names[0],
        )

    if inplace:
        new_df = df
    else:
        new_df = copy.deepcopy(df)

    if isinstance(new_df.index, pd.MultiIndex) and len(new_df.index.names) == 1:
        new_df.index = cast_to_index(new_df.index)

    if isinstance(new_df, pd.DataFrame) and (
        isinstance(new_df.columns, pd.MultiIndex)
        and len(new_df.columns.names) == 1
    ):
        new_df.columns = cast_to_index(new_df.columns)

    if not inplace:
        return new_df


def convert_regular_index_to_single_level_multi_index(df: pd.DataFrame | pd.Series,
                                                      inplace: bool = True) -> None | pd.DataFrame | pd.Series:
    """
    Convert regular index to single-level multi-index.
    Applied to both index and columns (columns only for DataFrame).

    In case already multi-index, do nothing.

    Parameters:
        df (pd.DataFrame | pd.Series):
            DataFrame or Series to convert.
        inplace (bool):
            If True, modifies in place.
            If False, returns a modified deep copy.
            (default is True)
    Returns:
        None | pd.DataFrame | pd.Series : None if inplace is True, otherwise
            the converted DataFrame or Series.
    """

    if inplace:
        new_df = df
    else:
        new_df = copy.deepcopy(df)

    if not isinstance(new_df.index, pd.MultiIndex):
        new_df.index = cast_index_to_multiindex(new_df.index)

    if isinstance(new_df, pd.DataFrame) and not isinstance(new_df.columns, pd.MultiIndex):
        new_df.columns = cast_index_to_multiindex(new_df.columns)

    if not inplace:
        return new_df


def timeit(func):
    """
    Decorator to measure and log the execution time of a function.

    Parameters:
        func (callable): The function to be timed.

    Returns:
        callable: The wrapped function that measures execution time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not config.ENABLE_PERFORMANCE_MEASUREMENTS:
            return func(*args, **kwargs)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"Execution time measured for function '{func.__name__}': {elapsed:.3f}s")
        return result
    return wrapper


def hash_df(df: pd.DataFrame) -> str:
    """
    Compute a MD5 hash of a pandas DataFrame.

    Parameters:
        df (pd.DataFrame):
            The DataFrame to hash.

    Returns:
        str:
            The MD5 hash as a hexadecimal string.
    """
    return hashlib.md5(
        pd.util.hash_pandas_object(df).values
    ).hexdigest()


def hash_csr_array(array: sp.csr_array) -> str:
    """
    Compute MD5 hash of a CSR array.

    Parameters:
        array (sp.csr_array):
            Compressed Sparse Row array to hash
    Returns:
        str: MD5 hexadecimal digest of the array data
    """
    h = hashlib.md5()
    h.update(array.data.tobytes())
    h.update(array.indices.tobytes())
    h.update(array.indptr.tobytes())
    return h.hexdigest()


