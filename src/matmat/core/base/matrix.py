"""
Overview
********
This module defines the matrix classes.
This class gather functionalities to work with:
    - sparse matrices and their associated index.

Contents
********
- Classes:
  - :class:`SparseMatrix`
"""

__all__ = ["SparseMatrix"]

import pandas as pd
import numpy as np
import scipy.sparse as sp

from matmat.utils import constants as cst
from matmat.utils.mixins import CopyMixin


class _LocIndexer:
    """
    Indexer class for SparseMatrix object to handle .loc access
    """

    def __init__(self, matrix):
        self._matrix = matrix

    def __getitem__(self, key):
        """
        Retrieve a sub-matrix using row and column labels.

        Parameters:
            key (tuple): Tuple containing (row_labels, col_labels)
        Returns:
            SparseMatrix: Sub-matrix matching the specified labels
        """
        row_labels, col_labels = key
        return self._matrix._loc(row_labels, col_labels)


class SparseMatrix(CopyMixin):
    """
    This class represents a matrix stored as a sparse array to optimize
    memory performances. The rows and columns index of the matrix are
    also included, to be able to rebuild the complete dense matrix.

    Attributes:
        _array : sp.csr_array
            The sparse array representing the matrix non-zero values
        _rows : pd.MultiIndex
            The rows index of the matrix
        _columns : pd.MultiIndex
            The columns index of the matrix
    """

    TYPE = np.float64

    def __init__(
        self,
        array: sp.csr_array = None,
        rows: pd.MultiIndex = None,
        columns: pd.MultiIndex = None,
    ):
        """
        Initialize a SparseMatrix instance.

        Parameters:
            array (sp.csr_array, optional):
                Sparse CSR array. Defaults to None.
            rows (pd.MultiIndex, optional):
                Row index labels. Defaults to None.
            columns (pd.MultiIndex, optional):
                Column index labels. Defaults to None.
        """
        self._rows: pd.MultiIndex = rows
        self._columns: pd.MultiIndex = columns
        if array is None and not (rows is None or columns is None):
            self._array = sp.csr_array(
                (len(rows), len(columns)), dtype=self.TYPE
            )
        else:
            self._array: sp.csr_array = array

    @classmethod
    def init_from_df(cls, df: pd.DataFrame):
        """
        Create a SparseMatrix instance from a pandas DataFrame.

        Parameters:
            df (pd.DataFrame): Input DataFrame to convert
        Returns:
            SparseMatrix: New SparseMatrix instance initialized with DataFrame data
        """
        matrix = cls()
        matrix._array = sp.csr_array(df.values, dtype=cls.TYPE)
        matrix._rows = df.index
        matrix._columns = df.columns
        return matrix

    @property
    def array(self) -> sp.csr_array:
        return self._array

    @array.setter
    def array(self, value: sp.csr_array):
        self._array = value

    @property
    def rows(self) -> pd.MultiIndex:
        return self._rows

    @rows.setter
    def rows(self, value: pd.MultiIndex):
        self._rows = value

    @property
    def index(self) -> pd.MultiIndex:
        return self.rows

    @property
    def columns(self) -> pd.MultiIndex:
        return self._columns

    @columns.setter
    def columns(self, value: pd.MultiIndex):
        self._columns = value

    @property
    def shape(self):
        return self._array.shape

    @property
    def loc(self):
        return _LocIndexer(self)

    def equals(self, other: "SparseMatrix") -> bool:
        """
        Check if this matrix is equal to another matrix.

        Parameters:
            other (SparseMatrix): SparseMatrix to compare with
        Returns:
            bool: True if matrices are equal, False otherwise
        """
        return (self.array != other.array).nnz == 0 and (
            self.rows.equals(other.rows) and self.columns.equals(other.columns)
        )

    def to_dataframe(self) -> pd.DataFrame:
        """
        Returns this matrix as a Pandas dataframe.
        """
        return pd.DataFrame(
            self.array.toarray(),
            index=self.rows,
            columns=self.columns,
            dtype=cst.DTYPE_FLOAT,
        )

    def drop(self, labels, axis=0, level=None):
        """
        Drop specified labels from rows or columns.

        Parameters:
            labels (str or list):
                Label(s) to drop. If str, converts to list.
            axis (int):
                Axis along which to drop labels (0 for rows, 1 for columns).
            level (int, optional):
                Level in MultiIndex to drop from. Defaults to None.
        """
        if isinstance(labels, str):
            labels = [labels]

        index = self._rows if axis == 0 else self._columns

        if level is not None:
            existing = [
                l for l in labels if l in index.get_level_values(level)
            ]
        else:
            existing = [l for l in labels if l in index]

        if not existing:
            return

        if axis == 0:
            if level is not None:
                mask = ~self._rows.get_level_values(level).isin(labels)
            else:
                mask = ~self._rows.isin(labels)
            self._array = self._array[mask.nonzero()[0], :]
            self._rows = self._rows[mask]
        else:
            if level is not None:
                mask = ~self._columns.get_level_values(level).isin(labels)
            else:
                mask = ~self._columns.isin(labels)
            self._array = self._array[:, mask.nonzero()[0]]
            self._columns = self._columns[mask]

    def _loc(self, row_labels: pd.MultiIndex, col_labels: pd.MultiIndex):
        """
        Select a sub-matrix using row and column labels.

        Parameters:
            row_labels (pd.MultiIndex):
                Row labels for selection
            col_labels (pd.MultiIndex):
                Column labels for selection
        Returns:
            SparseMatrix: New SparseMatrix instance containing the selected sub-matrix
        """
        n_row_levels = self._rows.nlevels
        n_col_levels = self._columns.nlevels

        row_keys = row_labels.droplevel(
            list(range(n_row_levels, row_labels.nlevels))
        )
        if not isinstance(row_keys, pd.MultiIndex):
            row_keys = pd.MultiIndex.from_frame(row_keys.to_frame())
        col_keys = col_labels.droplevel(
            list(range(n_col_levels, col_labels.nlevels))
        )
        if not isinstance(col_keys, pd.MultiIndex):
            col_keys = pd.MultiIndex.from_frame(col_keys.to_frame())

        row_idx = self._rows.get_indexer(row_keys)
        col_idx = self._columns.get_indexer(col_keys)

        sub = self._array[row_idx][:, col_idx]
        return SparseMatrix(sub, row_labels, col_labels)
