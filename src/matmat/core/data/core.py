__all__ = [
    "AbstractData",
]

from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

from matmat.core.base.identity import AbstractBaseIdentity
from matmat.core.bridge import core as bridge
from matmat.core.data.strategies import structure, nature

from matmat.utils import (
    logging as log,
    constants as cst,
    config,
    checks,
    tools,
)
from matmat.utils.mixins import CopyMixin
from matmat.utils.errors import (
    MEIncorrectDataFrameStructure,
)
import matmat.utils.formats.factory as formats_factory


class AbstractData(ABC, CopyMixin):
    """
    Abstract class representing a data

    It defines a set of attributes and methods common to all its subclasses
    (accounts, shock, system and extension data classes).

    Attributes
    ----------
    _TYPE : str
        The type of the data composing the matrix (class constant)
    _NAME : str
        The name of the data (class constant)
    _IS_LAZY : bool
        True if the dataframe shall only be built when used (default to False)
        This permits to avoid memory problems when dealing with large
        dataframes
    _id : AbstractBaseIdentity
        The identity card of the data
    _df : pd.DataFrame
        The dataframe of this data which contains all the values
    """

    # Class constants
    _TYPE: str = cst.DTYPE_FLOAT
    _NAME: str
    _IS_LAZY: bool = False

    # Attributes
    # Identity
    _id: AbstractBaseIdentity
    # Data
    _df: pd.DataFrame
    # Strategies
    _nature: nature.AbstractDataNature
    _structure: structure.AbstractDataStructure

    @abstractmethod
    def get_nature_type(self, **kwargs) -> type:
        """
        Returns the type of data nature for this data.
        """

    @abstractmethod
    def get_structure_type(self, **kwargs) -> type:
        """
        Returns the type of data structure for this data. It may vary depending
        on the parameters.
        """

    @abstractmethod
    def get_origin_description(self) -> str:
        """
        Returns a brief description about the data owner.
        Shall start with "from "

        Example: "from extension 'ghg_other'"
        """

    @property
    def id(self):
        return self._id

    @property
    def df(self) -> pd.DataFrame:
        # Build dataframe if not yet built (lazy init)
        if not self.is_df_initialized():
            self.build_df(force_build=True)
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame):
        """
        Set the attribute '_df' with 'value' if the rows and columns index
        of value match the expected index of the data structure, otherwise
        raise an exception.

        Raises:
            MEIncorrectDataFrameStructure
        """
        if not value.index.equals(self.structure.df_rows):
            log.error(
                f"Can't set {self.name}. Input dataframe does not match "
                f"the expected rows index"
            )
            raise MEIncorrectDataFrameStructure(
                erroneous_index=value.index,
                expected_index=self.structure.df_rows,
            )
        if not value.columns.equals(self.structure.df_columns):
            log.error(
                f"Can't set {self.name}. Input dataframe does not match "
                f"the expected columns index"
            )
            raise MEIncorrectDataFrameStructure(
                erroneous_index=value.columns,
                expected_index=self.structure.df_columns,
            )
        self._df = value

    @property
    def name(self) -> str:
        return self._NAME

    @property
    def type(self) -> str:
        return self._TYPE

    @property
    def is_lazy(self) -> bool:
        return self._IS_LAZY

    @property
    def nature(self) -> nature.AbstractDataNature:
        return self._nature

    @property
    def structure(self) -> structure.AbstractDataStructure:
        return self._structure

    @property
    def df_columns(self) -> pd.Index:
        return self._structure.df_columns

    @property
    def df_rows(self) -> pd.Index:
        return self._structure.df_rows

    @property
    def values(self):
        return self.df.values

    @property
    def index(self) -> pd.Index:
        return self._df.index

    @property
    def columns(self) -> pd.Index:
        return self._df.columns

    @property
    def regions(self):
        """
        Returns the regions detail levels from the structure
        """
        return self._structure.regions

    @property
    def sectors(self):
        """
        Returns the sectors detail levels from the structure
        """
        return self._structure.sectors

    @property
    def final_demand_categories(self):
        """
        Returns the final demand categories detail levels from the structure
        """
        return self._structure.final_demand_categories

    @property
    def extension_categories(self):
        """
        Returns the extension categories detail levels from the structure
        """
        return self._structure.extension_categories

    def build_df(self, force_build: bool = False):
        """
        Build the dataframe w.r.t. its structure.

        Notes:
            The dataframe is not built in case of lazy data initialization,
            it is set to None instead.

        Parameters:
            force_build (bool):
                Force the dataframe building even if lazy initialization is enabled.
        """
        if force_build or not self.is_lazy:
            self._df = pd.DataFrame(
                index=self._structure.df_rows,
                columns=self._structure.df_columns,
                dtype=self._TYPE,
            )
        else:
            self._df = None

    @staticmethod
    def is_null() -> bool:
        """
        Tells if this data is *null*. Returns *False* by default.
        Shall be overridden by *null* data subclasses
        """
        return False

    def is_coefficient(self) -> bool:
        """
        True if this data is a coefficient, False otherwise
        """
        return isinstance(self._nature, nature.Coefficient)

    def is_flux(self) -> bool:
        """
        True if this data is a flux, False otherwise
        """
        return isinstance(self._nature, nature.Flux)

    def is_unit(self) -> bool:
        """
        True if this data is a unit, False otherwise
        """
        return isinstance(self._nature, nature.Unit)

    def is_df_initialized(self) -> bool:
        """
        Checks if the DataFrame is initialized.

        Returns:
            bool: True if the DataFrame is initialized, False otherwise.
        """
        return self._df is not None

    def is_df_empty(self) -> bool:
        """
        Returns True if the dataframe is filled only with NaN
        """
        if self.is_df_initialized():
            return self._df.isna().all().all()
        return True

    def is_domestic_region_empty(self) -> bool:
        """
        Returns True if the domestic part of the dataframe is filled only
        with NaN
        """
        return self.get_domestic_origin().isna().all().all()

    def is_import_region_empty(self) -> bool:
        """
        Returns True if the import part of the dataframe is filled only
        with NaN
        """
        return self.get_import_origin().isna().all().all()

    def equals(self, other: "AbstractData") -> bool:
        """
        Tell if this data equals other

        Returns True if data are both null and of same type or if the
        following attributes are identical:
                - df_rows
                - df_columns
                - _df (equality with tolerance is the dataframe is composed
                  by floats)
        """
        if (self.is_null() and other.is_null()) and (
            type(self) is type(other)
        ):
            are_equal = True
        else:

            are_index_eq = self.df_rows.equals(other.df_rows)
            if not are_index_eq:
                log.verbose(f"Data {self.name} have different rows index")

            are_columns_eq = self.df_columns.equals(other.df_columns)
            if not are_columns_eq:
                log.verbose(f"Data {self.name} have different columns index")

            if self.is_df_initialized() and other.is_df_initialized():

                if self._TYPE == cst.DTYPE_FLOAT:
                    are_df_eq = checks.are_df_equal_with_tolerance(
                        tested_df=other.df,
                        ref_df=self._df,
                        with_index=True,
                    )
                elif self._TYPE == cst.DTYPE_STRING:
                    try:
                        are_df_eq = bool(
                            (self._df.values == other.df.values).all().all()
                        )
                    except TypeError:
                        # Replace <NA> with "missing" to avoid TypeError
                        are_df_eq = bool(
                            (
                                self._df.fillna("missing").values
                                == other.df.fillna("missing").values
                            )
                            .all()
                            .all()
                        )
                else:
                    log.error(
                        f"'equals' function not implemented for type {self._TYPE}"
                    )
                    raise NotImplementedError

            elif self.is_df_initialized() is not other.is_df_initialized():
                log.error(
                    "One of the dataframes is not initialized, "
                    "can't compare"
                )
                are_df_eq = False

            else:
                are_df_eq = True

            if not are_df_eq:
                log.verbose(
                    f"Data {self.name} have different dataframe values"
                )

                if self.is_df_initialized() and other.is_df_initialized():
                    # Display more info to help debugging
                    if are_index_eq and are_columns_eq:
                        df_diff = self._df.compare(other.df)
                        log.verbose(
                            f"This dataframe shows the difference(s):"
                            f"{df_diff}"
                        )

            are_equal = are_index_eq and are_columns_eq and are_df_eq

            if are_equal:
                log.verbose(f"Data '{self.name}' are identical")

        return are_equal

    def get_regions_list(self) -> list[str]:
        """
        Returns the concatenated list of domestic and import regions
        represented in this data
        """
        return (
            self.get_domestic_regions_list() + self.get_import_regions_list()
        )

    def get_domestic_regions_list(self) -> list[str]:
        """
        Returns the list of domestic regions currently represented in this data
        """
        return self._structure.get_domestic_regions_list()

    def get_domestic_origin(self, keep_origin: bool = False) -> pd.DataFrame:
        """
        Returns the domestic part of this data

        Parameters:
            keep_origin (bool):
                If True, then the row *origin* will be kept in the returned
                dataframe
        Returns:
            pd.DataFrame : the dataframe corresponding to the domestic part
            of this data
        """
        if keep_origin:
            return self.df.loc[[cst.IDX_DOMESTIC]]
        return self.df.loc[cst.IDX_DOMESTIC]

    def set_values(self, values: float | str | np.ndarray):
        """
        Set the values of the dataframe.

        Parameters:
            values (float | str | np.ndarray):
                - If a float or str is provided, all elements of the dataframe are set to that value.
                - If a numpy array is provided, its values are assigned to the dataframe.
        """
        if np.isscalar(values):
            self.df.loc[:, :] = values
        elif isinstance(values, np.ndarray):
            self.df.loc[:] = values
        else:
            raise TypeError(
                f"Expected scalar or np.ndarray, got {type(values).__name__}"
            )

    def set_domestic_values(self, values: float | str | np.ndarray):
        """
        Set the domestic values of the dataframe.

        Parameters:
            values (float | str | np.ndarray):
                - If a scalar (float/int/str) is provided, all elements of the domestic part
                  of the dataframe are set to that value.
                - If a numpy array is provided, its values are assigned to the domestic rows.
                  The shape must match the domestic part of the dataframe.

        Raises:
            ValueError: If a numpy array is provided and its shape does not match the expected shape.
            TypeError: If the provided value type is unsupported.
        """
        domestic_shape = self.get_domestic_origin().shape

        if isinstance(values, np.ndarray):
            if values.shape == domestic_shape:
                self.df.loc[cst.IDX_DOMESTIC] = values
            else:
                log.error(
                    f"Input values shape is {values.shape}. "
                    f"Expected {domestic_shape}"
                )
                raise ValueError(
                    f"Shape mismatch: got {values.shape}, expected {domestic_shape}"
                )
        elif np.isscalar(values):
            self.df.loc[cst.IDX_DOMESTIC, :] = values
        else:
            raise TypeError(
                f"Expected scalar or np.ndarray, got {type(values).__name__}"
            )

    def set_import_values(self, values: float | str | np.ndarray):
        """
        Set the import values of the dataframe, if it has an import part.

        Parameters:
            values (float | int | np.ndarray):
                - If a scalar is provided, all elements of the import part of
                  the dataframe are set to that value.
                - If a numpy array is provided, its values are assigned to the
                  import rows. The shape must match the import part of the dataframe.

        Raises:
            ValueError: If a numpy array is provided and its shape does not match
                        the expected import shape.
            TypeError: If the provided value type is unsupported.
        """
        if not self.structure.has_import_regions():
            log.error(
                f"Can't set import values for {self.name}. "
                "Dataframe has no import regions."
            )
            return

        import_shape = self.get_import_origin().shape

        if isinstance(values, np.ndarray):
            if values.shape == import_shape:
                self.df.loc[cst.IDX_IMPORT] = values
            else:
                log.error(
                    f"Input values shape is {values.shape}. "
                    f"Expected {import_shape}"
                )
                raise ValueError(
                    f"Shape mismatch: got {values.shape}, expected {import_shape}"
                )
        elif np.isscalar(values):
            self.df.loc[cst.IDX_IMPORT, :] = values
        else:
            raise TypeError(
                f"Expected scalar or np.ndarray, got {type(values).__name__}"
            )

    def get_import_regions_list(self) -> list[str]:
        """
        Returns the list of import regions currently represented in this data
        """
        return self._structure.get_import_regions_list()

    def get_import_origin(self, keep_origin: bool = False) -> pd.DataFrame:
        """
        Returns the import part of this data

        Parameters:
            keep_origin (bool):
                If True, then the row *origin* will be kept in the returned
                dataframe
        Returns:
            pd.DataFrame : the dataframe corresponding to the import part of
            this data
        """
        if keep_origin:
            return self.df.loc[[cst.IDX_IMPORT]]
        return self.df.loc[cst.IDX_IMPORT]

    def set_value_at(
        self,
        value: float | str,
        rows_filters: dict[str, list[str]] | None,
        columns_filters: dict[str, list[str]] | None,
    ):
        """
        Set value(s) in the DataFrame based on row and column level filters.

        Parameters:
            value (float | str):
                Value to set in the DataFrame.
            rows_filters (dict[str, list[str]] | None):
                Dict of {level_name: level_values} to filter rows.
                If None, all rows are selected.
            columns_filters (dict[str, list[str]] | None):
                Dict of {level_name: level_values} to filter columns.
                If None, all columns are selected.

        """
        if rows_filters:
            mask_rows = np.ones(len(self.df.index), dtype=bool)
            for level_name, level_values in rows_filters.items():
                mask_rows &= self.df.index.get_level_values(level_name).isin(
                    level_values
                )
        else:
            mask_rows = slice(None)

        if columns_filters:
            mask_columns = np.ones(len(self.df.columns), dtype=bool)
            for level_name, level_values in columns_filters.items():
                mask_columns &= self.df.columns.get_level_values(
                    level_name
                ).isin(level_values)
        else:
            mask_columns = slice(None)

        self.df.loc[mask_rows, mask_columns] = value

    def set_manual_value(
        self,
        *,
        value: float,
        row: tuple[str, str, str],
        col: tuple[str, str, str],
    ):
        """
        Inject a specific value at a specific place in the dataframe.

        Parameters:
            value (float):
                The value to inject
            row (tuple[str, str, str]):
                The (row region, row level, row name) where the value shall be
                injected.
                If ':', then the value in injected in the whole column.
                If 'domestic' or 'import', then the value is injected in
                all the cells matching this origin
                Example: ("FR", "sector", "Clothing Industry")
            col (tuple[str, str, str]):
                The (col region, col level, col name) where the value shall be
                injected.
                If ':', then the value is injected in the whole row.
                Example: ("FR", "category", "Households")
        """
        # Constants
        sign_for_full_fill = ":"
        level_region = cst.IDX_REGION
        level_origin = cst.IDX_ORIGIN

        log.verbose(
            f"Set manual value {value} to '{self.name}' "
            f"at row {row} / column {col}"
        )

        # Check that the level names given exist in rows & columns index
        if row[1] != sign_for_full_fill and row[1] not in self.df.index.names:
            log.error(
                f"Level '{row[1]}' not found in rows index of {self.name}. "
                f"Only {self.df.index.names} are available."
            )
            return
        if (
            col[1] != sign_for_full_fill
            and col[1] not in self.df.columns.names
        ):
            log.error(
                f"Level '{col[1]}' not found in columns index of {self.name}. "
                f"Only {self.df.columns.names} are available."
            )
            return

        def compute_index_boolean_array(
            index: pd.Index, criteria: tuple[str, str, str]
        ):
            """
            Compute a boolean array based on specified criteria for a given
            pandas Index.

            This function generates a boolean series by evaluating an index
            against given criteria.
            The criteria can specify conditions at different levels such as
            'origin' or 'region'.
            The resulting boolean series indicates whether each element in
            the index meets the criteria.

            Parameters
            ----------
            index : pd.Index
                The pandas Index to evaluate against the criteria.
            criteria : tuple of str
                A tuple of three strings representing the criteria to apply.
                The first element specifies the origin or the region
                (e.g., 'domestic', 'import', or a region).
                The second element specifies the level to check.
                The third element specifies the value to match.
                A ':' can be used as a wildcard to match all values
                at a particular level.

            Returns
            -------
            pd.Series
                A boolean pandas Series with the same index as the input,
                indicating whether each element meets the specified criteria.
            """

            # Build a dataframe from the index
            index_df = index.to_frame()

            # Case when both criteria are specific (and not ':')
            if (
                criteria[0] != sign_for_full_fill
                and criteria[2] != sign_for_full_fill
            ):
                # Case 'domestic' or 'import', we check at 'origin' level
                if criteria[0] in [cst.IDX_DOMESTIC, cst.IDX_IMPORT]:
                    boolean_series = (
                        index_df[level_origin] == criteria[0]
                    ) & (index_df[criteria[1]] == criteria[2])
                # Normal case, we check at 'region' level
                else:
                    try:
                        boolean_series = (
                            index_df[level_region] == criteria[0]
                        ) & (index_df[criteria[1]] == criteria[2])
                    except KeyError:
                        # If no region level, then applicable on the whole
                        # column / row
                        boolean_series = index_df[criteria[1]] == criteria[2]
            # Case when region is ':' => applicable on all regions
            elif criteria[0] != sign_for_full_fill:
                boolean_series = index_df[level_region] == criteria[0]
            # Case when name is ':' => applicable on the whole column / row
            elif criteria[2] != sign_for_full_fill:
                boolean_series = index_df[criteria[1]] == criteria[2]
            # Otherwise, applicable everywhere
            else:
                boolean_series = pd.Series(True, index=index_df)

            # Re-instantiate with the MultiIndex to avoid losing information
            return pd.Series(boolean_series.values, index=index)

        # Compute rows index w.r.t. row criteria
        rows_index = compute_index_boolean_array(
            index=self.df.index,
            criteria=row,
        )

        if not rows_index.any():
            log.error(
                f"Can't set to '{self.name}' "
                f"at row {row} / column {col}. Cell does not exist."
            )
            return

        # Reset indices to numbers for performance
        rows_index_copy = rows_index.reset_index(drop=True)
        self.df.reset_index(drop=True, inplace=True)

        # Set values to the right spot
        if len(self.df.shape) > 1:
            if self.df.shape[1] > 1:
                # Compute columns index w.r.t. column criteria
                columns_index = compute_index_boolean_array(
                    index=self.df.columns,
                    criteria=col,
                )
                if not columns_index.any():
                    log.error(
                        f"Can't set to '{self.name}' "
                        f"at row {row} / column {col}. Cell does not exist."
                    )
                else:
                    if (
                        self.df.loc[rows_index_copy, columns_index]
                        .notna()
                        .any()
                        .any()
                    ):
                        log.warning(
                            f"In {self.name}: values at row {row} / column {col} are not only "
                            f"NaN. They will be overridden."
                        )
                    self.df.loc[rows_index_copy, columns_index] = value
            else:
                if self.df.loc[rows_index_copy].notna().any():
                    log.warning(
                        f"In {self.name}: values at row {row} are not only "
                        f"NaN. They will be overridden."
                    )
                self.df.loc[rows_index_copy] = value
        else:
            if self.df.loc[rows_index_copy].notna().any():
                log.warning(
                    f"In {self.name}: values at row {row} are not only "
                    f"NaN. They will be overridden."
                )
            self.df.loc[rows_index_copy] = value

        # reset index of df
        self.df.index = rows_index.index

    def inject_dataframe(self, df: pd.DataFrame, inject_zeros: bool = False):
        """
        Inject the values of df into this data

        If inject_zeros is True, inject the 0.0 as well, otherwise replace them
        by NaN before injection

        Parameters:
            df (pd.DataFrame):
                The dataframe containing the values to inject
            inject_zeros:
                True if the 0.0 shall be injected
        """
        if not self.df.columns.equals(df.columns):
            log.warning(
                f"Injection of {self.name}: columns of injected "
                f"dataframe are different. Update may not work"
            )
        if not self.df.index.equals(df.index):
            log.warning(
                f"Injection of {self.name}: rows of injected "
                f"dataframe are different. Update may not work"
            )

        if inject_zeros:
            self.df.update(df)
        else:
            self.df.update(df.replace(to_replace=0.0, value=np.nan))

    def update_values(
        self,
        values: pd.DataFrame,
        join: str = "left",
        overwrite: bool = True,
        filter_func=None,
        errors: str = "ignore",
    ):
        """
        Update the internal DataFrame using another DataFrame.

        This method behaves like :meth:`pd.DataFrame.update`, aligning
        on both index and columns, and updating existing values with non-NA
        values from the provided DataFrame.

        Parameters:
            values (pd.DataFrame):
                DataFrame containing the new values to apply. Index and columns
                are aligned with the current data before updating.
            join ({'left', 'right', 'outer', 'inner'}):
                Type of join used to align the DataFrames before updating (Default is 'left')
            overwrite (bool):
                Whether to overwrite existing values in the current data.
                If False, only NaN values are updated. (Default is True)
            filter_func (callable, optional):
                Function to filter values before updating. Must return a boolean
                mask with the same shape as the DataFrame. (Default is None)
            errors ({'ignore', 'raise'}):
                If 'raise', errors during the update process will raise a
                ValueError. If 'ignore', errors are suppressed. (Default is 'ignore')

        Raises:
            TypeError : If `values` is not a pandas DataFrame.

        Notes:
            The alignment and update rules follow exactly
            those of :meth:`pd.DataFrame.update`.

        See also:
            :meth:`pd.DataDataFrame.update`
        """
        if not isinstance(values, pd.DataFrame):
            raise TypeError(
                "The 'values' argument must be a pandas DataFrame."
            )

        if not self.df.index.equals(values.index):
            log.warning(
                f"The index of 'values' does not fully match the index of {self.name}."
                "Update may not behave as expected."
            )
        if not self.df.columns.equals(values.columns):
            log.warning(
                f"The columns of 'values' does not fully match the columns of {self.name}."
                "Update may not behave as expected."
            )

        self.df.update(
            values,
            join=join,
            overwrite=overwrite,
            filter_func=filter_func,
            errors=errors,
        )

    def update_domestic_values(
        self,
        values: pd.DataFrame,
        join: str = "left",
        overwrite: bool = True,
        filter_func=None,
        errors: str = "ignore",
    ):
        """
        Update the domestic values of the dataframe where the rows and
        columns index match.

        Notes:
            The dataframe given may or may not have an "origin" level.

        See also:
            :meth:`AbstractData.update_values`
        """
        if cst.IDX_ORIGIN not in values.index.names:
            input_df = pd.concat(
                {cst.IDX_DOMESTIC: values},
                axis=0,
                names=[cst.IDX_ORIGIN],
            )
        else:
            input_df = values
        self.update_values(
            values=input_df,
            join=join,
            overwrite=overwrite,
            filter_func=filter_func,
            errors=errors,
        )

    def update_import_values(
        self,
        values: pd.DataFrame,
        join: str = "left",
        overwrite: bool = True,
        filter_func=None,
        errors: str = "ignore",
    ):
        """
        Update the import values of the dataframe where the rows and
        columns index match.

        Notes:
            The dataframe given may or may not have an "origin" level.

        See also:
            :meth:`AbstractData.update_values`
        """
        if cst.IDX_ORIGIN not in values.index.names:
            input_df = pd.concat(
                {cst.IDX_IMPORT: values},
                axis=0,
                names=[cst.IDX_ORIGIN],
            )
        else:
            input_df = values
        self.update_values(
            values=input_df,
            join=join,
            overwrite=overwrite,
            filter_func=filter_func,
            errors=errors,
        )

    def inject(
        self,
        data_: "AbstractData",
        inject_zeros: bool = False,
    ):
        """
        Inject the values of data_ into this data

        If inject_zeros is True, inject the 0.0 as well, otherwise replace them
        by NaN before injection

        Parameters:
            data_ (pd.DataFrame):
                The data to inject
            inject_zeros:
                True if the 0.0 shall be injected
        """
        if inject_zeros:
            self.update_values(data_.df)
        else:
            self.update_values(data_.df.replace(to_replace=0.0, value=np.nan))

    def load_from_path(self, path: str, format_: str = None):
        """
        This method loads the dataframe w.r.t. the following steps:
            - Depending on config.CHECK_INPUT_DATA_STRUCTURE,
              check that the index and columns of the dataframe to read
              are the ones expected by the data
            - update the structure of data with the verified index and columns
            - load the values into the dataframe
            - Depending on config.CLEAN_RESIDUAL_NAN_AND_INF,
              clean the dataframes from NaN and INF values

        Parameters:
            path (str):
                The path to the directory containing the file
            format_ (str):
                The input format of the data file (default to None). If None,
                automatically detect the format from the files in path.
        """
        if format_ is None:
            format_in = formats_factory.build_format_from_path(
                path=path, data_name=self.name
            )
        else:
            format_in = formats_factory.build_format_from_name(format_)

        if not format_in.is_null():

            nb_levels_rows = len(self.df_rows.names)
            nb_levels_columns = len(self.df_columns.names)

            # Read input file
            df_read = format_in.read(
                path=path,
                file_name=self._NAME,
                data_name=self._NAME,
                nb_levels_rows=nb_levels_rows,
                nb_levels_columns=nb_levels_columns,
            )

            # Check rows and columns index
            if config.CHECK_INPUT_DATA_STRUCTURE:
                self._structure.check_df_index(df_index=df_read.index)
                self._structure.check_df_columns(df_columns=df_read.columns)

            # Assign rows and columns index
            self._structure.df_rows = df_read.index
            self._structure.df_columns = df_read.columns

            # Update dataframe
            self._df = df_read.astype(dtype=self._TYPE)

            # Clean dataframe
            if config.CLEAN_RESIDUAL_NAN_AND_INF:
                self.clean_residual_nan()

    def clean_residual_nan(self):
        """
        Replace all NaN, INF, -INF by 0.0 in the dataframe. Does nothing if
        the dataframe contains only NaN
        """
        if self.is_df_initialized():
            if self._TYPE == cst.DTYPE_FLOAT:
                if (
                    not self._df.isna().all().all()
                    and (self._df.isna() | np.isinf(self._df)).any().any()
                ):
                    log.warning(
                        f"Data {self._NAME} {self.get_origin_description()} "
                        "contains residual NaN or INF values. "
                        "Replacing them by 0.0"
                    )
                    tools.clean_dataframe(self._df)

    def save_to_path(
        self, path: str, export_format: str | list = cst.FORMAT_EXCEL
    ):
        """
        If the dataframe is not empty, save the dataframe into a file

        Parameters:
            path (str):
                The path of the directory in which the exported file
                shall be saved
            export_format (str | list):
                The format(s) of the exported file, default is *excel*
        """
        if not self.is_df_empty():
            if isinstance(export_format, str):
                export_format = [export_format]
            for format_ in export_format:
                log.verbose(
                    f"Save data {self._NAME} to path {path} "
                    f"with format {format_}"
                )
                writer = formats_factory.build_format_from_name(format_)
                writer.export(df=self.df, path=path, file_name=self._NAME)

    def reset(self):
        """
        Resets the state of the object to its default configuration.

        Depending on the lazy-loading setting, recreates an empty
        DataFrame or sets its reference to None.
        """
        log.verbose(f"Reset {self._NAME}")
        if not self.is_lazy:
            self.df = pd.DataFrame(
                index=self.df_rows,
                columns=self.df_columns,
                dtype=self._TYPE,
            )
        else:
            self._df = None

    def reset_domestic_region(self):
        """
        Reset the domestic part of this data by setting all the values to NaN
        """
        if self.is_df_initialized():
            log.verbose(f"Reset domestic part of {self._NAME}")
            self.set_domestic_values(np.nan)

    def reset_import_region(self):
        """
        Reset the import part of this data by setting all the values to NaN
        """
        if self.is_df_initialized():
            log.verbose(f"Reset import part of {self._NAME}")
            self.set_import_values(np.nan)

    def aggregate(self, bridge_: bridge.Bridge, reset: bool):
        bridge_.validate_dimensions_for_aggregation()
        if reset or self.is_df_empty():
            self.structure.build_rows(bridge_.columns_dl)
            self.structure.build_columns(bridge_.columns_dl)
            self.reset()
        else:
            log.verbose(
                f"Aggregate data {self._NAME} over {bridge_.kind.value}"
            )
            self._df = self.nature.aggregate(
                df=self.df,
                structure=self.structure,
                bridge_=bridge_,
            )
            self.structure.df_rows = self.df.index
            self.structure.df_columns = self.df.columns
            self.structure.set_detail_level(bridge_.columns_dl)

    def disaggregate(self, bridge_: bridge.Bridge, reset: bool):
        bridge_.validate_dimensions_for_disaggregation()
        if reset or self.is_df_empty():
            self.structure.build_rows(bridge_.columns_dl)
            self.structure.build_columns(bridge_.columns_dl)
            self.reset()
        else:
            log.verbose(
                f"Disaggregate data {self._NAME} over {bridge_.kind.value}"
            )
            self._df = self.nature.disaggregate(
                df=self.df,
                structure=self.structure,
                bridge_=bridge_,
            )
            self.structure.df_rows = self.df.index
            self.structure.df_columns = self.df.columns
            self.structure.set_detail_level(bridge_.columns_dl)

    def reformat(self, bridge_: bridge.Bridge):
        """
        Reformat this data through the bridge given

        Parameters:
            bridge_ (bridge.Bridge):
                The bridge to apply

        Raises:
            NotImplementedError:
                Raised if the bridge type is unknown
        """
        log.verbose(f"Reformat data {self._NAME} over {bridge_.kind.value}")
        if self.is_df_empty():
            self.structure.build_rows(bridge_.columns_dl)
            self.structure.build_columns(bridge_.columns_dl)
            self.reset()
        else:
            self._df = self.structure.apply_bridge_to_df(
                df=self.df,
                bridge_=bridge_,
            )
            self.structure.df_rows = self.df.index
            self.structure.df_columns = self.df.columns
            self.structure.set_detail_level(bridge_.columns_dl)

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in this data object:
            - Values below the threshold are set to zero
            - Operation can be applied in place or return a filtered copy
            - Non-numeric data are left unchanged

        Parameters:
            threshold (float):
                Values lower than this threshold are considered near zero
            inplace (bool):
                Whether to apply the filtering directly to this object or
                return the filtered result

        Returns:
            AbstractData:
                The filtered data when ``inplace`` is False
        """

        if self.is_df_initialized():
            try:
                result = self._df.where(self._df >= threshold, 0.0)
            except TypeError:
                result = self._df
        else:
            result = None

        if inplace:
            self._df = result
        else:
            data_ = self.copy()
            data_._df = result
            return data_

    def __sub__(self, other):
        """
        Compute the difference between two data objects:
            - Only objects of the same type can be subtracted
            - Subtraction is performed element-wise on the underlying data

        Parameters:
            other (AbstractData):
                The data object to subtract from this one

        Returns:
            AbstractData:
                A new data object containing the element-wise difference
                between this object and the other
        """

        if isinstance(other, type(self)):
            result = self.copy()
            result.df = self.df - other.df
            return result
        else:
            raise TypeError(
                f"Operand shall be a {type(self)}, not a {type(other)}"
            )

    def __add__(self, other):
        """
        Compute the sum of two data objects:
            - Only objects of the same type can be added
            - Addition is performed element-wise on the underlying data

        Parameters:
            other (AbstractData):
                The data object to add to this one

        Returns:
            AbstractData:
                A new data object containing the element-wise sum
                of this object and the other
        """

        if isinstance(other, type(self)):
            result = self.copy()
            result.df = self.df + other.df
            return result
        else:
            raise TypeError(
                f"Operand shall be a {type(self)}, not a {type(other)}"
            )

    def __abs__(self):
        """
        Compute the absolute value this data

        Returns:
            AbstractData:
                A new data with the absolute value of the dataframe
        """
        result = self.copy()
        result.df = abs(self.df)
        return result

    def _build_nature(self, **kwargs):
        """
        Build the nature object of this data.

        It may be overridden by subclasses to perform specific operations
        when building the nature object.
        """
        self._nature = self.get_nature_type(**kwargs)(**kwargs)

    def _build_structure(self, **kwargs):
        """
        Build the structure object of this data.

        It may be overridden by subclasses to perform specific operations
        when building the structure object.
        """
        self._structure = self.get_structure_type(**kwargs)(**kwargs)
