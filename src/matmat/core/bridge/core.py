"""
Overview
********
This module defines the bridge classes.
These classes gather functionalities to deal with bridge matrices
defining relations between various detail level instances.

Contents
********
- Classes:
  - :class:`AbstractBridge`
  - :class:`Bridge`
  - :class:`MultiBridge`
  - :class:`DirectBridge`
  - :class:`CombinedBridge`
"""

__all__ = [
    "AbstractBridge",
    "Bridge",
    "MultiBridge",
    "DirectBridge",
    "CombinedBridge",
]

import os.path
from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd
import numpy as np
from scipy import sparse as sp

from matmat.core.base.matrix import SparseMatrix
from matmat.core.base import filter
from matmat.core.detail_level import (
    factory as dl_factory,
    tools as dl_tools,
)
from matmat.core.detail_level.core import (
    AbstractDetailLevel,
    DetailLevelKind,
)
from matmat.utils import logging as log, constants as cst, mixins, tools
from matmat.utils.errors import (
    MEIncompatibleDetailLevelKind,
    MEUndefinedAggregationLevel,
    MEIncorrectLevelNames,
    MEAggMatrixDimensionsInconsistent,
)
from matmat.utils.formats import core as formats


class AbstractBridge(ABC, mixins.CopyMixin):
    """Abstract base class for bridge structures linking detail levels.

    Attributes
    ----------
    _kind : DetailLevelKind
        The kind of detail level associated with the bridge.
    _rows_level_names : list[str]
        The names of the levels represented in the rows of the bridge.
    _columns_level_names : list[str]
        The names of the levels represented in the columns of the bridge.
    _columns_dl : AbstractDetailLevel
        The detail level associated with the columns of the bridge.
    _sheet_name: str
        The name of the sheet in the Excel file where the bridge data is stored.
        Set to _kind.value by default, but can be passed as parameter if
        necessary (for example for extension categories)
    _matrix : SparseMatrix
        The underlying matrix representing the bridge, stored as a
        SparseMatrix object.
    """

    INDEX_CHECK_LINE = "Check"

    def __init__(
        self,
        kind: DetailLevelKind,
        rows_level_names: list[str] = None,
        columns_level_names: list[str] = None,
        sheet_name: str | None = None,
    ):
        self._kind = kind
        self._rows_level_names = rows_level_names
        self._columns_level_names = columns_level_names
        self._columns_dl: AbstractDetailLevel = None

        # Save optional sheet name
        self._sheet_name = (
            sheet_name if sheet_name is not None else self._kind.value
        )

        self._matrix: SparseMatrix = SparseMatrix()

    @classmethod
    def init_from_df(
        cls,
        kind: DetailLevelKind,
        df: pd.DataFrame,
        sheet_name: str = None,
    ):
        """
        Build a Bridge instance directly from a bridge dataframe

        Parameters:
            kind (DetailLevelKind):
                The kind of bridge
            df (pd.DataFrame):
                The dataframe defining the bridge between detail levels
            sheet_name (str):
                The name of the sheet containing the bridge

        Returns:
            AbstractBridge:
                A bridge built from the provided dataframe
        """
        bridge = cls(kind=kind, sheet_name=sheet_name)
        bridge.df = df
        return bridge

    @classmethod
    def init_from_matrix(
        cls,
        kind: DetailLevelKind,
        matrix: SparseMatrix,
        sheet_name: str = None,
    ):
        """
        Build a Bridge instance directly from a sparse matrix

        Parameters:
            kind (DetailLevelKind):
                The kind of bridge
            matrix (SparseMatrix):
                The sparse matrix defining the bridge between detail levels
            sheet_name (str):
                The name of the sheet containing the bridge

        Returns:
            AbstractBridge:
                A bridge built from the provided sparse matrix
        """
        bridge = cls(kind=kind, sheet_name=sheet_name)
        bridge.matrix = matrix
        return bridge

    @abstractmethod
    def _build_rows_dl(self):
        raise NotImplementedError

    @property
    def kind(self):
        return self._kind

    @property
    def df(self):
        """
        Returns a representation (copy) of this bridge as a dataframe
        """
        return pd.DataFrame(
            self._matrix.array.toarray(),
            index=self._matrix.rows,
            columns=self._matrix.columns,
        )

    @df.setter
    def df(self, value: pd.DataFrame):
        """
        Set the internal bridge matrix from the given dataframe and
        build the corresponding row and column detail levels.

        Parameters:
            value (pd.DataFrame):
                The dataframe defining the bridge
        """
        tools.clean_dataframe(value)
        self._matrix = SparseMatrix.init_from_df(df=value)
        self._build_columns_dl()
        self._build_rows_dl()
        self.__hook_post_matrix_update()

    @property
    def matrix(self) -> SparseMatrix:
        """
        Returns the sparse matrix representing this bridge
        """
        return self._matrix

    @matrix.setter
    def matrix(self, value: SparseMatrix):
        """
        Set the internal bridge matrix from the given sparse matrix and
        build the corresponding row and column detail levels.

        Parameters:
            value (pd.DataFrame):
                The sparse matrix defining the bridge
        """
        self._matrix = value
        self._build_columns_dl()
        self._build_rows_dl()
        self.__hook_post_matrix_update()

    @property
    def sheet_name(self):
        return self._sheet_name

    @sheet_name.setter
    def sheet_name(self, value: str):
        self._sheet_name = value

    @property
    def extension_name(self):
        if self.is_extension_categories_bridge():
            return self._sheet_name
        log.error(
            f"This bridge is a {self.kind} bridge. "
            f"Can't return extension name"
        )
        return None

    @property
    def columns_dl(self):
        return self._columns_dl

    def equals(self, other: "AbstractBridge") -> bool:
        """
        Compare this bridge to other.
        Returns True if they have:
            - the same type
            - the same kind
            - the same sparse array
            - the same rows index
            - the same columns index
        False otherwise.
        """
        if type(self) is not type(other):
            return False
        if self.kind != other.kind:
            return False
        return self._matrix.equals(other.matrix)

    def is_regions_bridge(self) -> bool:
        return self._kind is DetailLevelKind.REGIONS

    def is_sectors_bridge(self) -> bool:
        return self._kind is DetailLevelKind.SECTORS

    def is_final_demand_categories_bridge(self) -> bool:
        return self._kind is DetailLevelKind.FINAL_DEMAND_CATEGORIES

    def is_extension_categories_bridge(self) -> bool:
        return self._kind is DetailLevelKind.EXTENSION_CATEGORIES

    def load_from_path(self, path: str, file_name: str = cst.BRIDGES_FILE):
        """
        Load the bridge dataframe from an Excel file and build the corresponding
        detail levels.

        Parameters:
            path (str):
                Path to the Excel file containing the bridge dataframe
            file_name (str):
                The name of the file to read (default to cst.BRIDGES_FILE)

        Raises:
            FileNotFoundError: when the file at `path` does not exist.
            ValueError: when the sheet does not exist in the Excel file.
        """

        def process_list_length(list_: list):
            if list_ is None:
                return None
            elif len(list_) == 0:
                return 1
            return len(list_)

        file_path = os.path.join(path, file_name)
        if not file_name.endswith(".xlsx"):
            log.error("Bridge file shall be an Excel file.")
            log.error(f"Can't read file {file_name}")
            raise NotImplementedError

        format_ = formats.ExcelFormat()

        try:
            # Call setter to trigger detail level attributes builds
            self.df = format_.read(
                path=path,
                file_name=file_name.split(".")[0],
                data_name=file_name.split(".")[0],
                sheet_name=self._sheet_name,
                nb_levels_rows=process_list_length(self._rows_level_names),
                nb_levels_columns=process_list_length(
                    self._columns_level_names
                ),
            )

        except FileNotFoundError as e:
            log.error(f"File '{file_path}' does not exist")
            raise FileNotFoundError from e
        except ValueError as e:
            log.error(
                f"Sheet '{self._sheet_name}' does not exist in file {file_path}"
            )
            raise ValueError from e

    def save_to_path(
        self,
        path: str,
        file_name: str = cst.BRIDGES_FILE,
        sheet_name: str = None,
        write_index: bool = True,
    ):
        """
        Save the bridge dataframe to an Excel file at the specified path.

        If the file at `path` already exists, the method appends the dataframe to it,
        replacing any existing sheet with the same name. If the file does not exist,
        a new Excel file is created.

        Parameters:
            path (str):
                Path to the directory in which the bridge shall be saved.
            file_name (str):
                The name of the bridge file (default to cst.BRIDGES_FILE)
            sheet_name (str):
                The sheet to write to (default set w.r.t. to the bridge kind)
            write_index (bool):
                Whether to write the index in the generated file. Default to True.

        Notes:
            - Uses the `openpyxl` engine for Excel writing.
            - The sheet name used is stored in `self._sheet_name`.
            - Overwrites any existing sheet with the same name in the target file.
        """
        self._save_to_path(
            df=self.df,
            path=path,
            file_name=file_name,
            sheet_name=(
                sheet_name if sheet_name is not None else self._sheet_name
            ),
            write_index=write_index,
        )

    @staticmethod
    def _save_to_path(
        df: pd.DataFrame,
        path: str,
        file_name: str,
        sheet_name: str,
        write_index: bool,
    ):
        """
        Save the dataframe given to an Excel file at the specified path.

        If the file at `path` already exists, the method appends the dataframe to it,
        replacing any existing sheet with the same name. If the file does not exist,
        a new Excel file is created.

        Parameters:
            df (pd.DataFrame):
                The dataframe to be saved
            path (str):
                Destination path for the exported bridge dataframe, including the filename
                and .xlsx extension.
            file_name (str):
                The name of the bridge file (default to cst.BRIDGES_FILE)
            sheet_name (str):
                The sheet to write to (default set w.r.t. to the bridge kind)
            write_index (bool):
                Whether to write the index in the generated file. Default to True.

        Notes:
            - Uses the `openpyxl` engine for Excel writing.
            - The sheet name used is stored in `self._sheet_name`.
            - Overwrites any existing sheet with the same name in the target file.
        """
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, file_name)
        if os.path.exists(file_path):
            with pd.ExcelWriter(
                file_path,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="replace",
            ) as writer:
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=write_index,
                )

        else:
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=write_index,
                )

    def _build_columns_dl(self):
        """
        Build the columns detail level associated to this bridge.
        Update the attributes _columns_dl / _columns_level_names
        """
        self._columns_dl = dl_factory.make_dl_from_kind(
            kind=self._kind,
            df=self._drop_check_lines_from_index(self.matrix.columns).to_frame(
                index=False
            ),
            extension_name=(
                self._sheet_name
                if self._kind is DetailLevelKind.EXTENSION_CATEGORIES
                else None
            ),
        )
        if not self._columns_level_names:
            self._columns_level_names = self._columns_dl.get_level_names()

    def _validate_level_names(self):
        """
        Compare bridge rows / columns level names w.r.t. pre-defined level
        names stored in _rows_level_names / _columns_level_names.

        Raises:
            MEIncorrectLevelNames
        """
        if self._rows_level_names != list(self._matrix.rows.names):
            # Exclude case when self._rows_level_names is empty, and index.names is [None]
            if not self._rows_level_names and list(
                self._matrix.rows.names
            ) == [None]:
                pass
            else:
                log.error("Incorrect level names in bridge dataframe rows")
                raise MEIncorrectLevelNames(
                    expected_level_names=self._rows_level_names,
                    found_level_names=list(self._matrix.rows.names),
                )
        if self._columns_level_names != list(self._matrix.columns.names):
            # Exclude case when self._column_level_names is empty, and columns.names is [None]
            if not self._columns_level_names and list(
                self._matrix.columns.names
            ) == [None]:
                pass
            else:
                log.error("Incorrect level names in bridge dataframe columns")
                raise MEIncorrectLevelNames(
                    expected_level_names=self._columns_level_names,
                    found_level_names=list(self._matrix.columns.names),
                )

    def _drop_check_lines_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove any rows or columns labeled as a "Check" line from the DataFrame.

        This method creates a deep copy of the input DataFrame and removes any
        occurrences of the label specified by `self.INDEX_CHECK_LINE` from both
        rows and columns. It supports both regular and MultiIndex DataFrames.

        Parameters:
            df (pd.DataFrame):
                The input DataFrame from which "Check" rows or columns should be removed.

        Returns:
            pd.DataFrame:
                A new DataFrame with all "Check" lines removed, preserving the original
                DataFrame.

        Notes:
            - The method checks both the first level of MultiIndex (if present) or
              standard index/columns for the label `self.INDEX_CHECK_LINE`.
            - The original DataFrame is not modified; a cleaned copy is returned.
        """
        cleaned_df = df.copy(deep=True)
        for axis in [0, 1]:
            values = (
                cleaned_df.index.get_level_values(0)
                if axis == 0
                else cleaned_df.columns.get_level_values(0)
            )
            if self.INDEX_CHECK_LINE in values:
                if isinstance(cleaned_df.index, pd.MultiIndex):
                    cleaned_df = cleaned_df.drop(
                        labels=self.INDEX_CHECK_LINE,
                        axis=axis,
                        level=0,
                        inplace=False,
                    )
                else:
                    cleaned_df = cleaned_df.drop(
                        labels=self.INDEX_CHECK_LINE,
                        axis=axis,
                        inplace=False,
                    )

        return cleaned_df

    def _drop_check_lines_from_index(
        self, idx: pd.MultiIndex
    ) -> pd.MultiIndex:
        """
        Returns an index without the entries "Check" at level 0.
        """
        mask = idx.get_level_values(0) != self.INDEX_CHECK_LINE
        return idx[mask]

    def __hook_post_matrix_update(self):
        """
        Hook to perform specific operations after updating the bridge matrix
        """
        pass


class Bridge(AbstractBridge):
    """Concrete bridge class linking two detail levels (rows and columns).

    Attributes
    ----------
    _rows_dl : AbstractDetailLevel
        The detail level associated with the rows of the bridge.
    _agg_matrix : pd.DataFrame
        The aggregation matrix associated to this bridge, used to store
        the dataframe to avoid computing each at each call of get_agg_matrix().
    """

    def __init__(
        self,
        kind: DetailLevelKind,
        columns_level_names: list[str] = None,
        rows_level_names: list[str] = None,
        sheet_name: str | None = None,
    ):
        super().__init__(
            kind=kind,
            rows_level_names=rows_level_names,
            columns_level_names=columns_level_names,
            sheet_name=sheet_name,
        )
        self._rows_dl: AbstractDetailLevel = None
        self._agg_matrix: SparseMatrix = None

    @classmethod
    def init_from_dls(
        cls, rows_dl: AbstractDetailLevel, columns_dl: AbstractDetailLevel
    ):
        """
        Build a Bridge instance directly from two detail-level objects.

        Parameters:
            rows_dl (AbstractDetailLevel):
                Detail level used for the rows.
            columns_dl (AbstractDetailLevel):
                Detail level used for the columns.

        Returns:
            Bridge:
                A bridge linking the two provided detail levels
        """
        if rows_dl.kind != columns_dl.kind:
            log.error(
                f"Can't create a bridge between different detail level kinds: "
                f"'{rows_dl.kind}' and '{columns_dl.kind}'"
            )
            raise MEIncompatibleDetailLevelKind(
                rows_kind=rows_dl.kind.value,
                columns_kind=columns_dl.kind.value,
            )

        return cls.init_from_matrix(
            kind=rows_dl.kind,
            matrix=SparseMatrix(
                rows=rows_dl.get_dl_as_multi_index(),
                columns=columns_dl.get_dl_as_multi_index(),
            ),
        )

    @property
    def rows_dl(self) -> AbstractDetailLevel:
        return self._rows_dl

    def get_filtered_bridge(
        self, *filters_: filter.AbstractFilter
    ) -> "Bridge":
        """
        Get a bridge filtered through the provided filters.

        Parameters:
            *filters_ (filter.AbstractFilter):
                Variable number of filter objects to apply sequentially.

        Returns:
            Bridge:
                A new Bridge instance with the filtered data.
        """

        filtered_matrix = self.matrix.copy()
        for filter_ in filters_:
            filtered_matrix = filter_.apply_to_bridge(matrix=filtered_matrix)

        filtered_matrix.rows = tools.cast_index_to_multiindex(
            filtered_matrix.rows
        )
        filtered_matrix.columns = tools.cast_index_to_multiindex(
            filtered_matrix.columns
        )

        return Bridge.init_from_matrix(kind=self._kind, matrix=filtered_matrix)

    def get_agg_matrix(self) -> SparseMatrix:
        """
        Return the aggregated matrix with the optional removal of the
        ``INDEX_CHECK_LINE`` row and column.

        This method checks whether the special index label defined by
        ``self.INDEX_CHECK_LINE`` exists in the first level of the matrix
        rows and columns index.
        If present, the corresponding row / column is removed. The behavior is
        consistent for both simple ``Index`` and ``MultiIndex`` objects.

        The purpose of this removal is typically to discard validation or
        consistency-check rows / columns that should not appear in the final
        bridge matrix.

        Returns:
            SparseMatrix : A SparseMatrix identical to ``self._matrix``
                           except that the ``INDEX_CHECK_LINE`` row / column
                           is removed when present.
        """
        if self._agg_matrix is None:

            agg_matrix = self._matrix.copy()
            agg_matrix.drop(labels=self.INDEX_CHECK_LINE, level=0, axis=0)
            agg_matrix.drop(labels=self.INDEX_CHECK_LINE, level=0, axis=1)

            self._agg_matrix = agg_matrix

        return self._agg_matrix

    def project_agg_matrix(
        self,
        detail_levels: AbstractDetailLevel | list[AbstractDetailLevel],
    ) -> SparseMatrix:
        """
        Return the aggregation matrix projected to the given detail levels.

        The aggregation matrix is expanded so that its rows and columns match
        the provided detail levels by propagating multi-index structures.
        Aggregation values are preserved and returned as a new sparse matrix.

        Parameters:
            detail_levels (AbstractDetailLevel | list[AbstractDetailLevel]):
                Detail levels to propagate the aggregation matrix to.
                It may be only one detail level object or a list of detail
                level objects.
                The order in the list is relevant. The most granular detail
                level shall be the first in the list.

        Returns:
            SparseMatrix : Aggregation matrix aligned with the
                           specified detail levels.
        """
        if isinstance(detail_levels, AbstractDetailLevel):
            list_of_detail_levels = [detail_levels]
        else:
            list_of_detail_levels = detail_levels

        # Build detail levels dataframe
        dl_dataframe = list_of_detail_levels[0].df
        dl_levels_names = list_of_detail_levels[0].get_level_names()
        if len(list_of_detail_levels) > 1:
            for detail_level in list_of_detail_levels[1:]:
                dl_dataframe = dl_tools.propagate_columns(
                    df_from=dl_dataframe,
                    df_to=detail_level.df,
                )
                dl_levels_names = (
                    detail_level.get_level_names() + dl_levels_names
                )

        # Build rows and columns index for propagated aggregation matrix
        agg_matrix_propagated_index = pd.MultiIndex.from_frame(
            dl_tools.propagate_columns(
                df_from=dl_dataframe,
                df_to=self.rows_dl.df,
            )
        )
        agg_matrix_propagated_columns = pd.MultiIndex.from_frame(
            dl_tools.propagate_columns(
                df_from=dl_dataframe,
                df_to=self.columns_dl.df,
            )
        )
        # Propagate aggregation matrix values
        agg_matrix_propagated = self.get_agg_matrix().loc[
            agg_matrix_propagated_index, agg_matrix_propagated_columns
        ]

        # At this stage we have block matrices; we need to filter them to enforce
        # consistency at the chosen detail-level granularity.
        row_detail = agg_matrix_propagated.rows.to_frame()[dl_levels_names]
        col_detail = agg_matrix_propagated.columns.to_frame()[dl_levels_names]

        # Build a boolean mask enforcing diagonal propagation across detail levels.
        # A (row, col) entry is True only if all detail-level components match exactly.
        # This avoids Cartesian duplication and preserves identity-like behavior
        # within each aggregation block.

        # Optimized approach:
        # Factorize multi-level keys into 1D integer codes shared between rows and columns.
        # This removes the need for a 3D comparison and reduces memory footprint.
        combined = pd.concat([row_detail, col_detail], axis=0)

        # Each unique tuple of detail levels gets a unique integer code
        codes, _ = pd.factorize(pd.MultiIndex.from_frame(combined))

        n_rows = len(row_detail)

        # Split back into row and column codes
        row_codes = codes[:n_rows]
        col_codes = codes[n_rows:]

        # Final mask: equality of factorized codes (vectorized, 2D only)
        mask = row_codes[:, None] == col_codes[None, :]

        # Apply mask to propagated aggregation matrix
        agg_matrix_propagated.array = agg_matrix_propagated.array.multiply(
            mask
        )

        return agg_matrix_propagated

    def extend_agg_matrix(
        self,
        detail_levels: AbstractDetailLevel | list[AbstractDetailLevel],
    ) -> SparseMatrix:
        """
        Build the extended aggregation matrix:

            A_extended = I ⊗ A_base

        where I is the identity matrix over the provided detail levels
        (e.g., regions) and A_base is the base aggregation matrix.

        The resulting matrix operates on data indexed as:

            detail_levels × base_index

        Parameters:
            detail_levels (AbstractDetailLevel | list[AbstractDetailLevel]):
                Additional levels to replicate the base
                aggregation structure over.
                The order in the list is relevant. The most granular detail
                level shall be the first in the list.

        Returns:
            SparseMatrix : Extended aggregation matrix with MultiIndex on both
                           rows and columns corresponding to:
                                - detail_levels × base_rows
                                - detail_levels × base_columns
        """
        if isinstance(detail_levels, list):
            list_of_dls = detail_levels
        else:
            list_of_dls = [detail_levels]

        full_df = list_of_dls[0].df
        if len(list_of_dls) > 1:
            for dl in list_of_dls[1:]:
                full_df = dl_tools.propagate_columns(
                    df_from=full_df,
                    df_to=dl.df,
                )

        n_blocks = len(full_df)

        # --- Kronecker product: I ⊗ A_base ---
        agg_matrix_extended = sp.kron(
            sp.csr_matrix(np.eye(n_blocks)),
            self.get_agg_matrix().array,
        )

        # --- Build extended MultiIndex for rows and columns ---
        # Propagates base detail levels over the additional detail levels
        extended_row_index = pd.MultiIndex.from_frame(
            dl_tools.propagate_columns(
                df_from=self._rows_dl.df,
                df_to=full_df,
            )
        )
        extended_col_index = pd.MultiIndex.from_frame(
            dl_tools.propagate_columns(
                df_from=self._columns_dl.df,
                df_to=full_df,
            )
        )

        return SparseMatrix(
            array=agg_matrix_extended,
            rows=extended_row_index,
            columns=extended_col_index,
        )

    def validate_dimensions_for_aggregation(self):
        """
        Raises an exception if this bridge's dimensions are not fit for
        aggregation. Do nothing otherwise.

        Raises:
            MEAggMatrixDimensionsInconsistent
        """
        agg_matrix = self.get_agg_matrix()
        if len(agg_matrix.rows) < len(agg_matrix.columns):
            log.error(
                f"{self._kind} bridge dimensions are not consistent "
                "with an aggregation"
            )
            raise MEAggMatrixDimensionsInconsistent(
                agg_matrix_index=agg_matrix.rows,
                agg_matrix_columns=agg_matrix.columns,
            )

    def validate_dimensions_for_disaggregation(self):
        """
        Raises an exception if this bridge's dimensions are not fit for
        disaggregation. Do nothing otherwise.

        Raises:
            MEAggMatrixDimensionsInconsistent
        """
        agg_matrix = self.get_agg_matrix()
        if len(agg_matrix.rows) > len(agg_matrix.columns):
            log.error(
                f"{self._kind} bridge dimensions are not consistent "
                "with a disaggregation"
            )
            raise MEAggMatrixDimensionsInconsistent(
                agg_matrix_index=agg_matrix.rows,
                agg_matrix_columns=agg_matrix.columns,
            )

    def _build_rows_dl(self):
        """
        Build a row detail level for each aggregation key present
        in the matrix index.
        """
        self._rows_dl = dl_factory.make_dl_from_kind(
            kind=self._kind,
            df=self._drop_check_lines_from_index(self.matrix.rows).to_frame(
                index=False
            ),
            extension_name=(
                self._sheet_name
                if self._kind is DetailLevelKind.EXTENSION_CATEGORIES
                else None
            ),
        )
        if not self._rows_level_names:
            self._rows_level_names = self._rows_dl.get_level_names()

    def __hook_post_matrix_update(self):
        """
        Reset the saved aggregation matrix so that it is computed again
        if accessed.
        """
        self._agg_matrix = None


class MultiBridge(AbstractBridge):
    """Bridge supporting multiple row detail levels distinguished by an aggregation key.

    Attributes
    ----------
    _filter_level : str
        The name of the level permitting to select a specific bridge.
        Default to 'agg_level'
    _value_to_ignore_level : str
        The value used in the matrix to tell that a level shall be excluded
        from the MultiIndex for a specific bridge.
        Default to '-'
    _rows_dls : dict[str, AbstractDetailLevel]
        Mapping from aggregation keys to their corresponding row detail levels.
    _map_bridges : dict[str, Bridge]
        Mapping between aggregation keys to their corresponding bridge.
        It is filled each time a Bridge object is needed.
        Used to avoid re-instantiating several times the same bridge.
    """

    DEFAULT_FILTER_LEVEL = "agg_level"
    DEFAULT_VALUE_TO_IGNORE_LEVEL = "-"

    def __init__(
        self,
        kind: DetailLevelKind,
        filter_level: str = DEFAULT_FILTER_LEVEL,
        value_to_ignore_level: str = DEFAULT_VALUE_TO_IGNORE_LEVEL,
        columns_level_names: list[str] = None,
        rows_level_names: list[str] = None,
        sheet_name: str | None = None,
    ):
        if filter_level is None:
            filter_level = self.DEFAULT_FILTER_LEVEL

        super().__init__(
            kind=kind,
            columns_level_names=(
                [filter_level] + columns_level_names
                if columns_level_names is not None
                else None
            ),
            rows_level_names=(
                [filter_level] + rows_level_names
                if rows_level_names is not None
                else None
            ),
            sheet_name=sheet_name,
        )
        self._filter_level = filter_level
        self._value_to_ignore_level = value_to_ignore_level
        self._rows_dls: Dict[str, AbstractDetailLevel] = {}
        self._map_bridges: Dict[str, Bridge] = {}

    @classmethod
    def init_from_df(
        cls,
        kind: DetailLevelKind,
        df: pd.DataFrame,
        sheet_name: str = None,
    ):
        """
        Build a MultiBridge instance directly from a dataframe.
        The filter level is retrieved from the index first level name.

        Parameters:
            kind (DetailLevelKind):
                The kind of bridge
            df (pd.DataFrame):
                The dataframe defining the bridge between detail levels
            sheet_name (str):
                The name of the sheet containing the dataframe

        Returns:
            AbstractBridge:
                A bridge built from the provided dataframe
        """
        bridge = cls(
            kind=kind,
            sheet_name=sheet_name,
            filter_level=df.index.names[0],
        )
        bridge.df = df
        return bridge

    @classmethod
    def init_from_matrix(
        cls,
        kind: DetailLevelKind,
        matrix: SparseMatrix,
        sheet_name: str = None,
    ):
        """
        Build a MultiBridge instance directly from a sparse matrix.
        The filter level is retrieved from the index first level name.

        Parameters:
            kind (DetailLevelKind):
                The kind of bridge
            matrix (SparseMatrix):
                The sparse matrix defining the bridge between detail levels
            sheet_name (str):
                The name of the sheet containing the bridge

        Returns:
            AbstractBridge:
                A bridge built from the provided sparse matrix
        """
        bridge = cls(
            kind=kind,
            sheet_name=sheet_name,
            filter_level=matrix.rows.names[0],
        )
        bridge.matrix = matrix
        return bridge

    @classmethod
    def init_from_bridges(
        cls,
        kind: DetailLevelKind,
        bridges: dict[str, Bridge],
        filter_level: str = DEFAULT_FILTER_LEVEL,
        value_to_ignore_level: str = DEFAULT_VALUE_TO_IGNORE_LEVEL,
        sheet_name: str = None,
    ):
        """
        Build a MultiBridge instance from a dictionary of Bridge instances.
        """

        def build_multi_bridge_df(
            dfs: dict[str, pd.DataFrame],
        ) -> pd.DataFrame:
            all_level_names = []
            for df in dfs.values():
                for name in df.index.names:
                    if name not in all_level_names:
                        all_level_names.append(name)

            def reindex_to_full_levels(
                key: str, df: pd.DataFrame
            ) -> pd.DataFrame:
                index = df.index.to_frame(index=False)
                for name in all_level_names:
                    if name not in index.columns:
                        index[name] = value_to_ignore_level
                index.insert(0, filter_level, key)
                index = index[[filter_level] + all_level_names]
                df = df.copy()
                df.index = pd.MultiIndex.from_frame(index)
                return df

            reindexed = [
                reindex_to_full_levels(key, df) for key, df in dfs.items()
            ]
            return pd.concat(reindexed, axis=0)

        return cls.init_from_df(
            kind=kind,
            df=build_multi_bridge_df(
                {key: bridge.df for key, bridge in bridges.items()}
            ),
            sheet_name=sheet_name,
        )

    def get_rows_dl(self, key: str) -> AbstractDetailLevel:
        """
        Return the row detail level corresponding to an aggregation key.

        Parameters:
            key (str):
                Aggregation level identifier.

        Returns:
            AbstractDetailLevel:
                Detail level for the given key.

        Raises:
            MEUndefinedAggregationLevel
                If the key does not match any known aggregation level.
        """
        try:
            return self._rows_dls[key]
        except KeyError:
            log.error(f"Can't find row detail level for '{key}'")
            raise MEUndefinedAggregationLevel(
                agg_level=key,
                kind="detail level",
                known_levels=list(self._rows_dls.keys()),
            )

    def get_agg_matrix(self, key: str) -> SparseMatrix:
        """
         Return the matrix associated with an aggregation key, with the filter
         level removed and any “Check” row or column dropped.

         Parameters:
             key (str):
                 Aggregation level identifier.

         Returns:
             SparseMatrix:
                 Cleaned matrix corresponding to the requested
                 aggregation level.

        Raises:
            MEUndefinedAggregationLevel
                If the key is not present in the matrix index.
        """
        # Retrieve the correct matrix corresponding to input key
        try:
            raw_agg_matrix: pd.DataFrame = self._drop_filter_level_from_df(
                self.df.loc[key]
            )
        except KeyError:
            raise MEUndefinedAggregationLevel(
                agg_level=key,
                kind="detail level",
                known_levels=self._matrix.rows.get_level_values(
                    self._filter_level
                )
                .unique()
                .tolist(),
            )

        cleaned_agg_matrix = self._drop_ignored_levels(
            self._drop_check_lines_from_df(df=raw_agg_matrix)
        )

        # Return cleaned agg matrix
        return SparseMatrix.init_from_df(df=cleaned_agg_matrix)

    def get_bridge(self, key: str) -> Bridge:
        """
        Returns the bridge corresponding to the requested aggregation level.
        """
        try:
            bridge_ = self._map_bridges[key]
        except KeyError:
            bridge_ = Bridge.init_from_matrix(
                kind=self.kind, matrix=self.get_agg_matrix(key=key)
            )
            self._map_bridges[key] = bridge_
        return bridge_

    def _build_columns_dl(self):
        """
        Build the column detail level excluding the filter level.
        """
        try:
            columns_agg_levels = (
                self._matrix.columns.get_level_values(level=self._filter_level)
                .unique()
                .tolist()
            )
            if len(columns_agg_levels) > 1:
                log.error(
                    "Found 2 different agg_level in columns. It should be just 1."
                )
                raise NotImplementedError
            else:
                matrix_for_columns_dl = self.df[columns_agg_levels[0]]
        except KeyError:
            matrix_for_columns_dl = self.df

        self._columns_dl = dl_factory.make_dl_from_kind(
            kind=self._kind,
            df=self._drop_check_lines_from_df(
                matrix_for_columns_dl
            ).columns.to_frame(index=False),
            extension_name=(
                self._sheet_name
                if self._kind is DetailLevelKind.EXTENSION_CATEGORIES
                else None
            ),
        )

    def _drop_ignored_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop the levels to be ignored from df

        The levels to be ignored are identified by the attribute
        '_value_to_ignore_level', defined at instantiation.
        """
        levels_to_drop = [
            level
            for level in range(df.index.nlevels)
            if (
                df.index.get_level_values(level) == self._value_to_ignore_level
            ).all()
        ]
        return df.droplevel(levels_to_drop)

    def _build_rows_dl(self):
        """
        Build row detail levels for each aggregation key found in the index.
        """
        for rows_agg_level in (
            self._matrix.rows.get_level_values(self._filter_level)
            .unique()
            .tolist()
        ):
            self._rows_dls[rows_agg_level] = dl_factory.make_dl_from_kind(
                kind=self._kind,
                df=self._drop_ignored_levels(
                    self._drop_check_lines_from_df(self.df.loc[rows_agg_level])
                ).index.to_frame(index=False),
                extension_name=(
                    self._sheet_name
                    if self._kind is DetailLevelKind.EXTENSION_CATEGORIES
                    else None
                ),
            )

            if not self._rows_level_names:
                self._rows_level_names = self._rows_dls[
                    rows_agg_level
                ].get_level_names()

    def _drop_filter_level_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove the aggregation filter level from the index and columns of a
        DataFrame slice.

        Parameters:
            df (pd.DataFrame):
                A dataframe slice associated with one aggregation key.

        Returns:
            pd.DataFrame:
                Matrix without the aggregation filter level.
        """

        filtered_df: pd.DataFrame = df.copy(deep=True)
        if (
            isinstance(filtered_df.index, pd.MultiIndex)
            and self._filter_level in df.index.names
        ):
            filtered_df = filtered_df.droplevel(self._filter_level, axis=0)
        if (
            isinstance(filtered_df.columns, pd.MultiIndex)
            and self._filter_level in filtered_df.columns.names
        ):
            filtered_df = filtered_df.droplevel(self._filter_level, axis=1)
        return filtered_df

    def __hook_post_matrix_update(self):
        """
        Reset the bridges map
        """
        self._map_bridges = {}


class DirectBridge(Bridge):
    """Direct bridge class for simplified data linkage."""

    def __init__(
        self,
        kind: DetailLevelKind,
        columns_level_names: list[str] = None,
        rows_level_names: list[str] = None,
        sheet_name: str | None = None,
    ):
        super().__init__(
            kind=kind,
            columns_level_names=columns_level_names,
            rows_level_names=rows_level_names,
            sheet_name=sheet_name,
        )
        self._direct_matrix: pd.DataFrame = None

    @property
    def direct_matrix(self) -> pd.DataFrame:
        return self._direct_matrix

    def load_from_path(self, path: str, file_name: str = cst.BRIDGES_FILE):
        """
        Load the direct bridge table from an Excel sheet and convert it to the
        full binary bridge matrix.

        Parameters:
            path (str):
                Path to the Excel file containing the direct bridge table
            file_name (str):
                The name of the file to read (default to cst.BRIDGES_FILE)
        """
        file_path = os.path.join(path, file_name)
        if not file_name.endswith(".xlsx"):
            log.error("Bridge file shall be an Excel file.")
            log.error(f"Can't read file {file_name}")
            raise NotImplementedError

        self._direct_matrix = pd.read_excel(
            file_path,
            sheet_name=self._sheet_name,
        )
        self._process_direct_matrix(
            source_level_name=self._retrieve_source_level_name(),
            destination_level_name=self._retrieve_destination_level_name(),
        )

    def save_to_path(
        self,
        path: str,
        file_name: str = cst.BRIDGES_FILE,
        sheet_name: str = None,
        write_index: bool = True,
        direct: bool = False,
    ):
        """
        Save the bridge matrix to an Excel file at the specified path, with an option
        to save the direct matrix instead.

        Parameters:
            path (str):
                Path to the directory in which the bridge shall be saved.
            file_name (str):
                The name of the bridge file (default to cst.BRIDGES_FILE)
            sheet_name (str):
                The sheet to write to (default set w.r.t. to the bridge kind)
            write_index (bool):
                Whether to write the index in the generated file. Default to True.
            direct (bool, optional (default=False)):
                If True, saves `self._direct_matrix` instead of the standard `_matrix`.
                If False, saves the standard `_matrix`.

        Notes:
            - The actual writing logic is handled by the superclass method.
        """
        if direct:
            super()._save_to_path(
                df=self._direct_matrix,
                path=path,
                file_name=file_name,
                sheet_name=(
                    sheet_name if sheet_name is not None else self._sheet_name
                ),
                write_index=False,
            )
        else:
            super().save_to_path(path=path)

    def _process_direct_matrix(
        self, source_level_name: str, destination_level_name: str
    ) -> None:
        """
        Build the complete binary bridge matrix from the direct bridge stored
        in ``self._direct_matrix``.

        The direct bridge table contains the source and destination columns
        given as parameters, plus optional extra level columns.
        Each row represents exactly one correspondence between these levels.
        Extra levels must *not* be expanded: they must be kept exactly as
        specified in each row.

        Parameters:
            source_level_name (str):
                Name of the source level column in the direct bridge table.
            destination_level_name (str):
                Name of the destination level column in the direct bridge table.
        """
        # -------------------------
        # 1. Validate inputs
        # -------------------------
        required = {source_level_name, destination_level_name}
        missing = required - set(self._direct_matrix.columns)
        if missing:
            raise ValueError(f"Missing required columns {missing}")

        if self._direct_matrix.empty:
            raise ValueError("Direct bridge table is empty.")

        # -------------------------
        # 2. Identify extra levels
        # -------------------------
        extra_levels = [
            c
            for c in self._direct_matrix.columns
            if c not in (source_level_name, destination_level_name)
        ]

        # -------------------------
        # 3. Build row and column MultiIndexes directly from the DF
        #    WITHOUT generating a cartesian product.
        # -------------------------
        if extra_levels:
            # Row index columns = extra levels + source
            row_levels = extra_levels + [source_level_name]
            # Column index columns = extra levels + destination
            col_levels = extra_levels + [destination_level_name]
        else:
            row_levels = [source_level_name]
            col_levels = [destination_level_name]

        row_index = pd.MultiIndex.from_frame(
            self._direct_matrix[row_levels].drop_duplicates(),
            names=row_levels,
        )
        col_index = pd.MultiIndex.from_frame(
            self._direct_matrix[col_levels].drop_duplicates(),
            names=col_levels,
        )

        # -------------------------
        # 4. Initialize empty matrix
        # -------------------------
        matrix = pd.DataFrame(
            0, index=row_index, columns=col_index, dtype=cst.DTYPE_FLOAT
        )

        # -------------------------
        # 5. Populate matrix
        # -------------------------
        # One row of self._direct_matrix = one mapping source → destination
        for _, row in self._direct_matrix.iterrows():

            row_key = tuple(row[level] for level in row_levels)
            col_key = tuple(row[level] for level in col_levels)

            matrix.loc[row_key, col_key] = 1

        # ---------------------------
        # 6. Sort w.r.t. higher level
        # ---------------------------
        if len(matrix.index.names) > 1:
            matrix.sort_index(
                level=0, sort_remaining=False, axis=0, inplace=True
            )
        if len(matrix.columns.names) > 1:
            matrix.sort_index(
                level=0, sort_remaining=False, axis=1, inplace=True
            )

        # -------------------------
        # 7. Save back to self
        # -------------------------
        self.df = matrix

    def _retrieve_source_level_name(self) -> str:
        """
        Retrieve the source level name:
            - If rows_level_names is given, then use the last element of the list
            - Else use the penultimate column name
        """
        if not self._rows_level_names:
            try:
                return self._direct_matrix.columns[-2]
            except IndexError as e:
                log.error(
                    "There should be at least 2 columns in the direct bridge matrice. "
                    f"Found only {len(self._direct_matrix.columns)} columns."
                )
                raise IndexError from e
        return self._rows_level_names[-1]

    def _retrieve_destination_level_name(self) -> str:
        """
        Retrieve the destination level name:
            - If columns_level_names is given, then use the last element of the list
            - Else use the last column name
        """
        if not self._columns_level_names:
            try:
                return self._direct_matrix.columns[-1]
            except IndexError as e:
                log.error(
                    "There should be at least 2 columns in the direct bridge matrice. "
                    f"Found only {len(self._direct_matrix.columns)} columns."
                )
                raise IndexError from e
        return self._columns_level_names[-1]


class CombinedBridge(Bridge):
    """
    Combined bridge class
    """

    @classmethod
    def init_from_bridge(
        cls,
        bridge_: Bridge,
        left_dls: list[AbstractDetailLevel],
        right_dls: list[AbstractDetailLevel],
    ):
        """
        Initialize a combined detail level bridge from an existing bridge and
        detail levels.

        Parameters:
            bridge_ (Bridge):
                The base bridge to extend or project.
            left_dls (list[AbstractDetailLevel]):
                List of left detail levels to extend the bridge with.
            right_dls (list[AbstractDetailLevel]):
                List of right detail levels to project the bridge with.
        Returns:
            A new instance initialized from the combined bridge data.
        """

        combined_bridge = bridge_
        if len(right_dls) > 0:
            combined_bridge = Bridge.init_from_matrix(
                matrix=combined_bridge.project_agg_matrix(right_dls[::-1]),
                kind=DetailLevelKind.COMBINED,
            )
        if len(left_dls) > 0:
            combined_bridge = Bridge.init_from_matrix(
                matrix=combined_bridge.extend_agg_matrix(left_dls[::-1]),
                kind=DetailLevelKind.COMBINED,
            )
        return cls.init_from_matrix(
            kind=DetailLevelKind.COMBINED,
            matrix=combined_bridge.matrix,
        )
