"""
Overview
********
This module defines the detail-level classes used to represent structured
inputs such as regions, sectors, final demand categories, and extension
categories. These classes provide utilities for loading, validating, and
converting detail-level definitions across multiple formats.

Contents
********
- Classes:
  - :class:`DetailLevelKind`
  - :class:`AbstractDetailLevel`
  - :class:`RegionsDL`
  - :class:`SectorsDL`
  - :class:`FinalDemandCategoryDL`
  - :class:`ExtensionCategoryDL`
  - :class:`CombinedDetailLevel`
"""

__all__ = [
    "DetailLevelKind",
    "AbstractDetailLevel",
    "RegionsDL",
    "SectorsDL",
    "FinalDemandCategoriesDL",
    "ExtensionCategoriesDL",
    "CombinedDetailLevel",
]

import os.path
from enum import Enum
from abc import ABC, abstractmethod
from typing import Literal

import pandas as pd

from matmat.core.base import filter
from matmat.core.detail_level import tools as dl_tools
from matmat.utils import logging as log, constants as cst
from matmat.utils.errors import (
    MEIncorrectSettings,
    MEIncorrectFinalDemandCategories,
    MEIncorrectLevelNames,
    MEMissingSheet,
)
from matmat.utils.mixins import CopyMixin


class DetailLevelKind(Enum):
    """Enumeration of detail level types."""

    SECTORS = "sectors"
    REGIONS = "regions"
    FINAL_DEMAND_CATEGORIES = "final_demand_categories"
    EXTENSION_CATEGORIES = "extension_categories"
    COMBINED = "combined"


class AbstractDetailLevel(ABC, CopyMixin):
    """Abstract base class for detail levels.

    Class constants
    ---------------
    _KIND : DetailLevelKind
        The kind of detail level.

    Attributes
    ----------
    _df : pd.DataFrame
        The dataFrame containing the detail level data.
    """

    _KIND: DetailLevelKind

    def __init__(
        self,
        df: pd.DataFrame = None,
    ):
        self._df: pd.DataFrame = df

        # Save optional sheet name
        self._sheet_name = self.kind.value

    @classmethod
    def init_from_index(cls, index: pd.Index | pd.MultiIndex):
        return cls(
            df=index.to_frame(index=False),
        )

    @classmethod
    def init_from_list(cls, list_: list[str], level_name: str):
        return cls(
            df=pd.MultiIndex.from_arrays([list_], names=[level_name]).to_frame(
                index=False
            ),
        )

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame):
        self._df = value
        self._validate_dataframe()

    @property
    def kind(self) -> DetailLevelKind:
        return self._KIND

    @property
    def name(self) -> str:
        return self._KIND.value

    @property
    def sheet_name(self) -> str:
        return self._sheet_name

    @sheet_name.setter
    def sheet_name(self, value: str):
        self._sheet_name = value

    def is_empty(self) -> bool:
        """
        Returns True if the df (dataframe)
        of this detail level is set to None
        """
        return self.df is None

    def equals(self, other: "AbstractDetailLevel") -> bool:
        """
        Compare this detail level to other.
        Returns True if they have the same kind and the same df,
        False otherwise.
        """
        if self.kind != other.kind:
            return False
        return self.df.equals(other.df)

    def load_from_path(
        self,
        path: str,
        file_name: str = cst.DL_FILE,
        missing_sheet_policy: Literal["raise", "ignore"] = "raise",
    ):
        """Load detail level data from a file path.

        Parameters:
            path (str):
                Path to the file to load
            file_name (str):
                The name of the file to read (default to cst.DL_FILE)
            missing_sheet_policy (Literal["raise", "ignore"]):
                "raise" => log error and stop execution in case of missing
                sheet
                "ignore" => do not log error and do not stop in case of
                missing sheet

        Returns:
            0 if load was successful, 1 otherwise

        Raises:
            MEMissingSheet : if the sheet does not exist in the Excel file
        """
        file_path = os.path.join(path, file_name)
        try:
            self._df = pd.read_excel(file_path, sheet_name=self._sheet_name)
        except ValueError:
            if missing_sheet_policy == "raise":
                raise MEMissingSheet(
                    file_path=file_path, sheet_name=self._sheet_name
                )
            return

        self._validate_dataframe()

    def save_to_path(
        self,
        path: str,
        file_name: str = cst.DL_FILE,
        sheet_name: str = None,
    ):
        """
        Save the detail level data to an Excel file at the specified path.

        If the file at `path/file_name` already exists, the method appends the table to it,
        replacing any existing sheet with the same name. If the file does not exist,
        a new Excel file is created.

        Parameters:
            path (str):
                Destination path for the exported detail level table, including the filename
                and .xlsx extension
            file_name (str):
                The name of the detail level file (Default to cst.DL_FILE)
            sheet_name (str):
                The sheet to write to (default set w.r.t. the detail level
                kind)

        Notes:
            - Uses the `openpyxl` engine for Excel writing.
            - The sheet name used is stored in `self._sheet_name`.
            - Overwrites any existing sheet with the same name in the target file.
        """
        if not self.is_empty():
            file_path = os.path.join(path, file_name)
            if os.path.exists(file_path):
                with pd.ExcelWriter(
                    file_path,
                    engine="openpyxl",
                    mode="a",
                    if_sheet_exists="replace",
                ) as writer:
                    self._df.to_excel(
                        writer,
                        sheet_name=(
                            sheet_name
                            if sheet_name is not None
                            else self._sheet_name
                        ),
                        index=False,
                    )

            else:
                with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                    self._df.to_excel(
                        writer,
                        sheet_name=(
                            sheet_name
                            if sheet_name is not None
                            else self._sheet_name
                        ),
                        index=False,
                    )

    def get_level_names(self) -> list[str]:
        """
        Return the names of the levels represented in this detail level.
        """
        return self.df.columns.to_list()

    def get_main_level_name(self) -> str:
        """
        Returns the "main" level name of this detail level, i.e. the first
        level name
        """
        return self.get_level_names()[0]

    def get_dl_as_df(self) -> pd.DataFrame:
        """Return the detail level data as a pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            The DataFrame representing the detail level data.
        """
        return self._df

    def get_dl_as_multi_index(self) -> pd.MultiIndex:
        """Return the detail level data as a MultiIndex.

        Returns
        -------
        pd.MultiIndex
            A MultiIndex constructed from the DataFrame.
        """
        return pd.MultiIndex.from_frame(self._df)

    def get_dl_as_dict(self) -> dict:
        """Convert detail level data to dictionary format.

        Converts the internal DataFrame to a dictionary structure based on the
        number of levels. For 2 levels, returns a flat dictionary mapping first
        level values to lists of second level values. For 3 levels, returns a
        nested dictionary structure.

        Returns:
            dict:
                Dictionary representation of the detail level:
                - 2 levels: {level1_value: [level2_values]}
                - 3 levels: {level1_value: {level2_value: [level3_values]}}

        Raises:
            NotImplementedError: If the number of level names is not 2 or 3.
        """
        if len(self._df.columns) == 2:
            return (
                self._df.groupby(self._df.columns[0], sort=False)[
                    self._df.columns[1]
                ]
                .apply(list)
                .to_dict()
            )
        if len(self._df.columns) == 3:
            result = {}
            for key1, group1 in self._df.groupby(
                self._df.columns[0], sort=False
            ):
                result[key1] = (
                    group1.groupby(self._df.columns[1], sort=False)[
                        self._df.columns[2]
                    ]
                    .apply(list)
                    .to_dict()
                )
            return result
        log.error(
            f"Method get_dl_as_dict only works for 2 or 3 columns, got {len(self._df.columns)}"
        )
        raise NotImplementedError

    def get_dl_as_list(self) -> list[str]:
        """Convert detail level data to a list.

        Extracts the values from the single column DataFrame as a list.
        Only works when there is exactly one level.

        Returns:
            list[str]: List of values from the single level column.

        Raises:
            NotImplementedError: If the number of level names is not 1.
        """
        if len(self._df.columns) == 1:
            return self._df[self._df.columns[0]].tolist()
        log.error(
            f"Method get_df_as_list only works for 1 column, got {len(self._df.columns)}"
        )
        raise NotImplementedError

    def get_dl_as_dict_or_list(self) -> dict | list[str]:
        """
        Convert detail level data to a dictionary or a list.

        Returns:
            dict | list[str]:
                Dictionary or list representing the detail level data

        Raises:
            NotImplementedError: if it is not possible to represent the detail
                                 level data as a list or as a dictionary
        """
        try:
            return self.get_dl_as_dict()
        except NotImplementedError:
            pass

        try:
            return self.get_dl_as_list()
        except NotImplementedError:
            pass

        log.error("Can't return detail levels as a dictionary nor a list")
        raise NotImplementedError

    def get_filtered_dl(
        self, *filters_: filter.AbstractFilter
    ) -> "AbstractDetailLevel":
        """
        Returns a new instance of detail level, filtered through the given
        filters
        """
        filtered_df = self.df
        for filter_ in filters_:
            filtered_df = filter_.apply_to_detail_level(df=filtered_df)
        return self.__class__(df=filtered_df)

    def get_dl_as_multi_index_propagated_on(
        self, df_on: pd.DataFrame
    ) -> pd.MultiIndex:
        """
        Returns a MultiIndex with all rows of this detail level propagated
        on each row of given dataframe

        Parameters:
            df_on (pd.DataFrame):
                The dataframe to propagate this detail levels on

        Returns:
            pd.MultiIndex

        Raises:
            MEIncorrectLevelNames: In case of identical names between
                                   this detail level and the dataframe
                                   columns. Indeed, we can't build MultiIndex
                                   with non-unique level names.
        """
        if len(set(self.get_level_names()) & set(df_on.columns.to_list())) > 0:
            raise MEIncorrectLevelNames(
                msg=f"The levels {df_on.columns.to_list()} are already present in "
                f"the {self.name} detail levels: {self.get_level_names()}. "
                "Can't build propagated multi-index. Consider changing "
                "them."
            )
        return pd.MultiIndex.from_frame(
            dl_tools.propagate_columns(
                df_from=self._df,
                df_to=df_on,
            )
        )

    def prefix_level_names_if_duplicates(
        self, prefix: str, other_dl: "AbstractDetailLevel"
    ):
        """
        Renames duplicate column level names by prefixing them with a given
        string.

        Parameters:
            prefix (str):
                The prefix string to add to duplicate level names.
            other_dl (AbstractDetailLevel):
                The object containing existing level names to check against.
        """
        for column in self._df.columns:
            if column in other_dl.get_level_names():
                self._df.rename(
                    columns={column: prefix + column}, inplace=True
                )

    @staticmethod
    def check_unicity_of_level_names(*detail_levels: "AbstractDetailLevel"):
        """
        Ensures all level names across provided detail levels are unique.

        Parameters:
            *detail_levels (AbstractDetailLevel):
                Variable number of detail levels to be validated.

        Raises:
            MEIncorrectLevelNames:
                If level names are not unique across the provided detail levels.
        """
        for i, dl1 in enumerate(detail_levels):
            for dl2 in detail_levels[i + 1 :]:
                common = set(dl1.get_level_names()) & set(
                    dl2.get_level_names()
                )
                if common:
                    log.error("Detail levels names shall be unique")
                    raise MEIncorrectLevelNames(
                        msg=f"Level names found in multiple detail levels: {common}. "
                        f"Conflicting levels: '{dl1.kind.value}' and '{dl2.kind.value}'"
                    )

    @abstractmethod
    def _validate_dataframe(self):
        """Validate the dataframe structure and content.

        Raises:
            NotImplementedError: Must be implemented by subclasses
                                 to define specific validation rules.
        """
        raise NotImplementedError


class RegionsDL(AbstractDetailLevel):
    """Detail level for regions."""

    _KIND = DetailLevelKind.REGIONS

    def get_region_levels(self) -> list[str]:
        """
        Returns the level names without the origin level
        """
        return self.get_level_names()[1:]

    def get_domestic_origin_df(self, with_origin: bool = True) -> pd.DataFrame:
        """
        Returns the detail level dataframe corresponding
        to the domestic regions
        """
        filtered_df = self._df[self._df[cst.IDX_ORIGIN] == cst.IDX_DOMESTIC]
        if with_origin:
            return filtered_df
        return filtered_df.drop(cst.IDX_ORIGIN, axis=1)

    def get_domestic_dl(self, with_origin: bool = True) -> "RegionsDL":
        """
        Returns the detail level object corresponding to the domestic regions
        """
        return RegionsDL(self.get_domestic_origin_df(with_origin))

    def get_import_origin_df(self, with_origin: bool = True) -> pd.DataFrame:
        """
        Returns the detail level dataframe corresponding
        to the import regions
        """
        filtered_df = self._df[self._df[cst.IDX_ORIGIN] == cst.IDX_IMPORT]
        if with_origin:
            return filtered_df
        return filtered_df.drop(cst.IDX_ORIGIN, axis=1)

    def get_import_dl(self, with_origin: bool = True) -> "RegionsDL":
        """
        Returns the detail level object corresponding to the import regions
        """
        return RegionsDL(self.get_import_origin_df(with_origin))

    def get_domestic_regions_list(self) -> list[str]:
        """
        Returns the list of domestic regions
        """
        return list(
            self._df[self._df[cst.IDX_ORIGIN] == cst.IDX_DOMESTIC][
                self.get_region_levels()[0]
            ],
        )

    def get_import_regions_list(self) -> list[str]:
        """
        Returns the list of import regions
        """
        return list(
            self._df[self._df[cst.IDX_ORIGIN] == cst.IDX_IMPORT][
                self.get_region_levels()[0]
            ],
        )

    def get_regions_list(self) -> list[str]:
        """
        Returns the list of regions
        """
        return list(self._df[self.get_region_levels()[0]])

    def _validate_dataframe(self):
        """
        Validate the regions dataframe structure and content:
            - The first two levels shall be "origin" and "region"
            - The regions shall be strings
        """
        level_names = self.get_level_names()
        if len(level_names) < 2 or level_names[:2] != [
            cst.IDX_ORIGIN,
            cst.IDX_REGION,
        ]:
            log.error("Incorrect levels for regions detail levels")
            log.error(
                f"Expected first two levels {[cst.IDX_ORIGIN, cst.IDX_REGION]},"
                f" found {level_names}"
            )
            raise MEIncorrectSettings(name=self.kind.value, setting=self.df)

        if not all(
            isinstance(region, str) for region in self.get_regions_list()
        ):
            log.error(f"Regions shall be a list of strings")
            raise MEIncorrectSettings(name=self.kind.value, setting=self.df)


class SectorsDL(AbstractDetailLevel):
    """Detail level for sectors."""

    _KIND = DetailLevelKind.SECTORS

    def get_as_extension_categories_dl(
        self, extension_name: str
    ) -> "ExtensionCategoriesDL":
        """
        Returns a copy of this sectors detail level set as an
        extension categories detail level
        """
        return ExtensionCategoriesDL(
            extension_name=extension_name, df=self._df.copy(deep=True)
        )

    def _validate_dataframe(self):
        """
        No validation performed for sectors detail levels.
        """
        pass


class FinalDemandCategoriesDL(AbstractDetailLevel):
    """Detail level for final demand categories."""

    _KIND = DetailLevelKind.FINAL_DEMAND_CATEGORIES

    def get_dl_wo_investment(self) -> "FinalDemandCategoriesDL":
        """
        Returns the final demand categories detail level object
        but without the investment row(s). The investment row(s) is located
        through the following criteria:
            - The value in the first column is {cst.IDX_INVESTMENT}
        If no row matches the criteria, then the final demand categories
        detail level object is returned unchanged.

        Returns:
            pd.DataFrame : the final demand categories detail level object
                           without the investment row(s)
        """

        try:
            return self.__class__(
                self._df[
                    self.df[self.get_main_level_name()] != cst.IDX_INVESTMENT
                ]
            )
        except KeyError:
            log.error(
                f"Can't locate investment category (identified by "
                f"'{cst.IDX_INVESTMENT}' in the "
                f"column '{self.get_main_level_name()}'). "
                "Return final demand categories detail levels unchanged"
            )
            return self

    def _validate_dataframe(self):
        """
        Check that there is only one investment column, or zero.
        """
        try:
            nb_of_gfcf = len(
                self._df[
                    self.df[self.get_main_level_name()] == cst.IDX_INVESTMENT
                ].index
            )
            if nb_of_gfcf > 1:
                log.error(
                    f"{self.kind.value} detail level has {nb_of_gfcf} "
                    f"investment column(s). There should only be one."
                )
                raise MEIncorrectFinalDemandCategories(categories=self._df)
        except KeyError:
            pass


class ExtensionCategoriesDL(AbstractDetailLevel):
    """Detail level for extension categories."""

    _KIND = DetailLevelKind.EXTENSION_CATEGORIES

    def __init__(
        self,
        extension_name: str,
        df: pd.DataFrame = None,
    ):
        super().__init__(df=df)
        # Override sheet name with extension name
        self._sheet_name = extension_name

    @classmethod
    def init_from_list(
        cls,
        list_: list[str],
        level_name: str,
        extension_name: str = DetailLevelKind.EXTENSION_CATEGORIES.value,
    ):
        return cls(
            df=pd.MultiIndex.from_arrays([list_], names=[level_name]).to_frame(
                index=False
            ),
            extension_name=extension_name,
        )

    def load_from_path(
        self,
        path: str,
        file_name: str = cst.DL_FILE,
        missing_sheet_policy: Literal["raise", "ignore"] = "raise",
    ):
        """
        Overriding of parent method to perform a recovery if loading
        from the <extension_name> sheet fails:
            1. Try to load from <extension_name> sheet
            2. If it fails, try to load from 'extension_categories' sheet
            3. If it fails, raise an exception
        """
        try:
            super().load_from_path(
                path=path, file_name=file_name, missing_sheet_policy="raise"
            )
        except MEMissingSheet:
            if self._sheet_name != DetailLevelKind.EXTENSION_CATEGORIES.value:
                if missing_sheet_policy == "raise":
                    log.warning(
                        f"Can't find sheet '{self._sheet_name}'. Try reading "
                        f"from sheet '{DetailLevelKind.EXTENSION_CATEGORIES.value}'"
                    )
                extension_name = self._sheet_name
                self._sheet_name = DetailLevelKind.EXTENSION_CATEGORIES.value
                try:
                    super().load_from_path(
                        path, file_name, missing_sheet_policy
                    )
                except MEMissingSheet as e:
                    if missing_sheet_policy == "raise":
                        log.error(
                            f"Can't find neither sheet '{extension_name}' "
                            f"nor '{self._sheet_name}'"
                        )
                        raise MEMissingSheet from e
                    return

    def get_filtered_dl(
        self, *filters_: filter.AbstractFilter
    ) -> "AbstractDetailLevel":
        """
        Returns a new instance of detail level, filtered through the given
        filters
        """
        filtered_df = self.df
        for filter_ in filters_:
            filtered_df = filter_.apply_to_detail_level(df=filtered_df)
        return self.__class__(df=filtered_df, extension_name=self._sheet_name)

    @property
    def extension_name(self) -> str:
        return self._sheet_name

    @extension_name.setter
    def extension_name(self, value: str):
        self._sheet_name = value

    def _validate_dataframe(self):
        """
        No validation performed for extension categories detail levels.
        """
        pass


class CombinedDetailLevel(AbstractDetailLevel):
    """
    A combined detail level, built from a set of detail levels
    """

    _KIND = DetailLevelKind.COMBINED

    @classmethod
    def init_from_dls(cls, *detail_levels: "AbstractDetailLevel"):
        """
        Instantiate a combined detail level from a list of detail levels,
        given in the order from the least granular to the most granular.

        Example: region > final demand categories > sectors
        """

        # Case when there is only 1 detail level given
        if len(detail_levels) == 1:
            return cls(df=detail_levels[0].df)

        else:
            extended_df: pd.DataFrame = None
            for dl_ in detail_levels:
                if extended_df is None:
                    extended_df = dl_.df
                else:
                    extended_df = dl_tools.propagate_columns(
                        df_from=dl_.df,
                        df_to=extended_df,
                    )
            return cls(df=extended_df)

    def _validate_dataframe(self):
        pass
