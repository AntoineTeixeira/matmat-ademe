"""
Presentation
************
Defines filter classes to apply on DetailLevel dataframes and Bridge dataframes.

Content
*******
- Classes:
    - AbstractFilter
    - FilterKeepRows
    - FilterRemoveRows
    - FilterRemoveColumn
- Functions:
    - get_filter_keep_domestic_regions
    - get_filter_keep_import_regions
    - get_filter_remove_investment
    - get_filter_remove_origin_level
"""

from abc import ABC, abstractmethod

import pandas as pd

from matmat.core.base.matrix import SparseMatrix
from matmat.utils import constants as cst, logging as log

# Filters singletons
filter_keep_domestic_regions = None
filter_keep_import_regions = None
filter_remove_investment = None
filter_remove_origin_level = None


class AbstractFilter(ABC):
    """
    Abstract base class for filters applicable to DetailLevel and Bridge objects.
    """

    @abstractmethod
    def apply_to_detail_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the filter to a DetailLevel dataframe.

        ...

        Parameters:
            df (pd.DataFrame):
                The DetailLevel dataframe to filter.
        Returns:
            pd.DataFrame : Filtered dataframe.

        """
        pass

    @abstractmethod
    def apply_to_bridge(self, matrix: SparseMatrix) -> SparseMatrix:
        """
        Apply the filter to a Bridge matrix (acts on index and columns).

        ...

        Parameters:
            matrix (pd.DataFrame):
                The Bridge matrix to filter.
        Returns:
            SparseMatrix : Filtered matrix.

        """
        pass


class FilterKeepRows(AbstractFilter):
    """
    Filter that keeps only rows matching a given level value.

    ...

    Attributes
    ----------
    _level_name : str
        Name of the level to filter on.
    _level_value : str
        Value to keep.

    """

    def __init__(self, level_name: str, level_value: str):
        """
        Initialize FilterKeepRows.

        ...

        Parameters:
            level_name (str):
                Name of the level to filter on.
            level_value (str):
                Value to keep.

        """
        self._level_name = level_name
        self._level_value = level_value

    def __str__(self):
        return (
            f"{self.__class__.__name__} | level '{self._level_name}' "
            f"| value '{self._level_value}'"
        )

    def apply_to_detail_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Keep only rows where level_name == level_value.

        ...

        Parameters:
            df (pd.DataFrame):
                The DetailLevel dataframe to filter.
        Returns:
            pd.DataFrame : Filtered dataframe.

        """
        try:
            mask = df[self._level_name] == self._level_value
            return df[mask]
        except KeyError:
            log.error(f"Error when applying filter {self}")
        return df

    def apply_to_bridge(self, matrix: SparseMatrix) -> SparseMatrix:
        """
        Keep only rows and columns where level_name == level_value.

        Parameters:
            matrix (SparseMatrix):
                The Bridge matrix to filter.
        Returns:
            SparseMatrix : Filtered matrix.

        """
        try:
            row_mask = (
                matrix.rows.get_level_values(level=self._level_name)
                == self._level_value
            )
            col_mask = (
                matrix.columns.get_level_values(level=self._level_name)
                == self._level_value
            )
            filtered_array = matrix.array[row_mask, :][:, col_mask]
            filtered_rows = matrix.rows[row_mask]
            filtered_cols = matrix.columns[col_mask]
            return SparseMatrix(filtered_array, filtered_rows, filtered_cols)
        except KeyError:
            log.error(f"Error when applying filter {self}")
        return matrix


class FilterRemoveRows(AbstractFilter):
    """
    Filter that removes rows matching a given level value.

    ...

    Attributes
    ----------
    _level_name : str
        Name of the level to filter on.
    _level_value : str
        Value to remove.

    """

    def __init__(self, level_name: str, level_value: str):
        """
        Initialize FilterRemoveRows.

        ...

        Parameters:
            level_name (str):
                Name of the level to filter on.
            level_value (str):
                Value to remove.

        """
        self._level_name = level_name
        self._level_value = level_value

    def __str__(self):
        return (
            f"{self.__class__.__name__} | level '{self._level_name}' "
            f"| value '{self._level_value}'"
        )

    def apply_to_detail_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows where level_name == level_value.

        ...

        Parameters:
            df (pd.DataFrame):
                The DetailLevel dataframe to filter.
        Returns:
            pd.DataFrame : Filtered dataframe.

        """
        try:
            mask = df[self._level_name] != self._level_value
            return df[mask]
        except KeyError:
            log.error(f"Error when applying filter {self}")
        return df

    def apply_to_bridge(self, matrix: SparseMatrix) -> SparseMatrix:
        """
        Remove rows and columns where level_name == level_value.

        Parameters:
            matrix (SparseMatrix):
                The Bridge matrix to filter.
        Returns:
            SparseMatrix : Filtered matrix.

        """
        try:
            row_mask = (
                matrix.rows.get_level_values(level=self._level_name)
                != self._level_value
            )
            col_mask = (
                matrix.columns.get_level_values(level=self._level_name)
                != self._level_value
            )
            filtered_array = matrix.array[row_mask, :][:, col_mask]
            filtered_rows = matrix.rows[row_mask]
            filtered_cols = matrix.columns[col_mask]
            return SparseMatrix(filtered_array, filtered_rows, filtered_cols)
        except KeyError:
            log.error(f"Error when applying filter {self}")
        return matrix


class FilterRemoveColumn(AbstractFilter):
    """
    Filter that removes a level from the dataframe columns and index.

    ...

    Attributes
    ----------
    _level_name : str
        Name of the level to remove.

    """

    def __init__(self, level_name: str):
        """
        Initialize FilterRemoveColumn.

        ...

        Parameters:
            level_name (str):
                Name of the level to remove.

        """
        self._level_name = level_name

    def __str__(self):
        return f"{self.__class__.__name__} | level '{self._level_name}'"

    def apply_to_detail_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop the column corresponding to level_name.

        ...

        Parameters:
            df (pd.DataFrame):
                The DetailLevel dataframe to filter.
        Returns:
            pd.DataFrame : Filtered dataframe.

        """
        try:
            return df.drop(columns=self._level_name)
        except KeyError:
            log.error(f"Error when applying filter {self}")
        return df

    def apply_to_bridge(self, matrix: SparseMatrix) -> SparseMatrix:
        """
        Drop the level corresponding to level_name from index and columns.

        Parameters:
            matrix (SparseMatrix):
                The Bridge matrix to filter.
        Returns:
            SparseMatrix : Filtered matrix.
        """
        try:
            filtered_rows = matrix.rows.droplevel(level=self._level_name)
            filtered_cols = matrix.columns.droplevel(level=self._level_name)
            return SparseMatrix(matrix.array, filtered_rows, filtered_cols)
        except KeyError:
            log.error(f"Error when applying filter {self}")
        return matrix


# Getters for filters singletons
def get_filter_keep_domestic_regions() -> FilterKeepRows:
    """
    Return the singleton filter that keeps domestic region rows.

    ...

    Returns:
        FilterKeepRows : Singleton instance.

    """
    global filter_keep_domestic_regions
    if filter_keep_domestic_regions is None:
        filter_keep_domestic_regions = FilterKeepRows(
            level_name=cst.IDX_ORIGIN,
            level_value=cst.IDX_DOMESTIC,
        )
    return filter_keep_domestic_regions


def get_filter_keep_import_regions() -> FilterKeepRows:
    """
    Return the singleton filter that keeps import region rows.

    ...

    Returns:
        FilterKeepRows : Singleton instance.

    """
    global filter_keep_import_regions
    if filter_keep_import_regions is None:
        filter_keep_import_regions = FilterKeepRows(
            level_name=cst.IDX_ORIGIN,
            level_value=cst.IDX_IMPORT,
        )
    return filter_keep_import_regions


def get_filter_remove_investment() -> FilterRemoveRows:
    """
    Return the singleton filter that removes investment rows.

    ...

    Returns:
        FilterRemoveRows : Singleton instance.

    """
    global filter_remove_investment
    if filter_remove_investment is None:
        filter_remove_investment = FilterRemoveRows(
            level_name=cst.IDX_Y_CATEGORY,
            level_value=cst.IDX_INVESTMENT,
        )
    return filter_remove_investment


def get_filter_remove_origin_level() -> FilterRemoveColumn:
    """
    Return the singleton filter that removes the origin level.

    ...

    Returns:
        FilterRemoveColumn : Singleton instance.

    """
    global filter_remove_origin_level
    if filter_remove_origin_level is None:
        filter_remove_origin_level = FilterRemoveColumn(
            level_name=cst.IDX_ORIGIN
        )
    return filter_remove_origin_level
