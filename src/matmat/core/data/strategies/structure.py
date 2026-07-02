"""
Overview
********
This module defines the different possible structure strategies for a data.
It defines an abstract class :class:`AbstractDataStructure`, which is the
contract to be implemented, and then a set of subclasses to define the
concrete implementations of structures.

To simplify integration and maintenance, each structure is
encapsulated within a dedicated strategy class. A data object contains
a structure object responsible for the definition of the matrice structure.
The specific implementation of the structure depends on the structure
strategy class chosen.

Contents
********
- Classes:
  - :class:`AbstractDataStructure`
  - :class:`StructureNull`
  - :class:`StructureX`
  - :class:`StructureSx`
  - :class:`StructureMRoW`
  - :class:`StructureZ`
  - :class:`StructureY`
  - :class:`StructureUnitBySector`
  - :class:`StructureUnitByExtensionCategory`
  - :class:`AbstractStructureCba`
  - :class:`StructureDCbaBySector`
  - :class:`StructureDCbaByExtensionCategory`
  - :class:`StructureDCbaKBySector`
  - :class:`StructureDCbaKByExtensionCategory`
  - :class:`StructureMappingDirect`
  - :class:`StructureMappingIndirect`
  - :class:`StructureMappingKDirect`
  - :class:`StructureMappingKIndirect`
"""

__all__ = [
    "AbstractDataStructure",
    "StructureNull",
    "StructureX",
    "StructureSx",
    "StructureMRoW",
    "StructureZ",
    "StructureY",
    "StructureUnitBySector",
    "StructureUnitByExtensionCategory",
    "StructureDCbaBySector",
    "StructureDCbaByExtensionCategory",
    "StructureDCbaKBySector",
    "StructureDCbaKByExtensionCategory",
    "StructureMappingDirect",
    "StructureMappingIndirect",
    "StructureMappingKDirect",
    "StructureMappingKIndirect",
]


from abc import ABC, abstractmethod
from functools import cached_property

import numpy as np
import pandas as pd
from scipy import sparse as sp
import pymrio

from matmat.core.detail_level import core as dl, tools as dl_tools
from matmat.core.bridge import core as bridge, pool as bridge_pool
from matmat.core.base import filter
from matmat.utils import constants as cst, logging as log, config, tools
from matmat.utils.errors import (
    MEAggMatrixInconsistentWithUnitVector,
    MEIncorrectDataFrameStructure,
    MEDetailLevelMissing,
)


class AbstractDataStructure(ABC):
    """
    Abstract class for data structure strategy. It defines the contract
    to be implemented by subclasses.

    This class defines the way of using detail levels and filters to build the
    rows and columns index of the structure.

    To specify a rows index (resp. a columns index), the subclass must EITHER:
        - implement the method :meth:`rows_specs()` (resp. :meth:`columns_specs()`)
          by returning a dictionary, with the keys defining, in order,
          the detail levels used in the rows index (resp.
          columns index), from the least granular to the most granular.
          The keys shall be enumerated from the enum class
          :class:`dl.DetailLevelKind`. For each key, the value
          associated is the list of filters to be applied to the detail level.
          It can be empty (which means the detail level is used as such). The
          list shall be composed by instances of :class:`filter.AbstractFilter`.

          Example::

              {
                  DetailLevelKind.REGIONS: [],
                  DetailLevelKind.SECTORS: [],
              }
              OR
              {
                  DetailLevelKind.REGIONS: [
                      filter.get_filter_keep_domestic_regions(),
                      filter.get_filter_remove_origin_level(),
                  ],
                  DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                      filter.get_filter_remove_investment(),
                  ],
              }
        - OR implement the property :meth:`rows_specs()`
          (resp. :meth:`columns_specs()`) with the instruction
          'return None' and override the method _build_rows()
          (resp. _build_columns())
          /!\  the prefix '_' is important. The method build_rows()
          (resp. build_columns) shall not be overridden.

    Attributes:
        _sectors : dl.SectorsDL
            This represents the sectors manipulated
            by the building methods of the structure class
        _regions : dl.RegionsDL
            This represents the regions manipulated
            by the building methods of the structure class
        _final_demand_categories : dl.FinalDemandCategoriesDL
            This represents the final demand categories manipulated
            by the building methods of the structure class
        _extension_categories : dl.ExtensionCategoriesDL
            This represents the customization of extension categories
            manipulated by the building methods of the structure class
            (Set to None in case there are no extension categories, for
            example with a system data structure)
        _df_rows : pd.Index
            The rows index of the dataframe structure
        _df_columns : pd.Index
            The columns index of the dataframe structure
    """

    # Attributes
    # Granular detail levels
    _sectors: dl.SectorsDL
    _regions: dl.RegionsDL
    _final_demand_categories: dl.FinalDemandCategoriesDL
    _extension_categories: dl.ExtensionCategoriesDL
    # Index & Columns structure
    _df_rows: pd.Index
    _df_columns: pd.Index

    def __init__(
        self,
        *,
        sectors: dl.SectorsDL,
        regions: dl.RegionsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        extension_categories: dl.ExtensionCategoriesDL = None,
        **kwargs,
    ):
        # Set detail levels attributes
        self._sectors: dl.SectorsDL = sectors
        self._regions: dl.RegionsDL = regions
        self._final_demand_categories: dl.FinalDemandCategoriesDL = (
            final_demand_categories
        )
        self._extension_categories: dl.ExtensionCategoriesDL = (
            extension_categories
        )

        # Initialize index attributes
        # They are initialized to None for performance reasons
        # They will be built on request
        self._df_rows = None
        self._df_columns = None

    @property
    @abstractmethod
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        pass

    @property
    @abstractmethod
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        pass

    @property
    def regions(self):
        return self._regions

    @regions.setter
    def regions(self, value: dl.RegionsDL):
        self._regions = value

    @property
    def sectors(self):
        return self._sectors

    @sectors.setter
    def sectors(self, value: dl.SectorsDL):
        self._sectors = value

    @property
    def final_demand_categories(self):
        return self._final_demand_categories

    @final_demand_categories.setter
    def final_demand_categories(self, value: dl.FinalDemandCategoriesDL):
        self._final_demand_categories = value

    @property
    def extension_categories(self):
        return self._extension_categories

    @extension_categories.setter
    def extension_categories(self, value: dl.ExtensionCategoriesDL):
        self._extension_categories = value

    @property
    def df_rows(self):
        if not self.is_df_rows_initialized():
            self.build_rows()
        return self._df_rows

    @df_rows.setter
    def df_rows(self, value: pd.Index):
        self._df_rows = value

    @property
    def df_columns(self):
        if not self.is_df_columns_initialized():
            self.build_columns()
        return self._df_columns

    @df_columns.setter
    def df_columns(self, value: pd.Index):
        self._df_columns = value

    def is_df_rows_initialized(self) -> bool:
        """
        True if the attribute _df_rows is initialized, False otherwise
        """
        return self._df_rows is not None

    def is_df_columns_initialized(self) -> bool:
        """
        True if the attribute _df_columns is initialized, False otherwise
        """
        return self._df_columns is not None

    def build_rows(self, *args, **kwargs):
        """
        Update detail levels then build rows index
        """
        self._update_detail_levels(*args)
        self._build_rows(*args, **kwargs)

    def _build_rows(self, *args, **kwargs):
        """
        Build the rows index of the structure into the attribute _df_rows
        """
        self._df_rows = dl.CombinedDetailLevel.init_from_dls(
            *self._get_applicable_dls(self.rows_specs)
        ).get_dl_as_multi_index()

    def build_columns(self, *args, **kwargs):
        """
        Update detail levels then build columns index
        """
        self._update_detail_levels(*args)
        self._build_columns(*args, **kwargs)

    def _build_columns(self, *args, **kwargs):
        """
        Build the columns index of the structure into the attribute _df_columns
        """
        self._df_columns = dl.CombinedDetailLevel.init_from_dls(
            *self._get_applicable_dls(self.columns_specs)
        ).get_dl_as_multi_index()

    def check_df_index(self, df_index: pd.Index):
        """
        Check the rows of the dataframe w.r.t. the expected rows
        of the data

        Parameters:
            df_index (pd.Index):
                The rows index to check
        Raises:
            MEIncorrectDataFrameStructure
        """
        if df_index.names != self._df_rows.names or not df_index.equals(
            self._df_rows
        ):
            raise MEIncorrectDataFrameStructure(
                erroneous_index=df_index,
                expected_index=self._df_rows,
                is_columns=False,
            )

    def check_df_columns(self, df_columns: pd.Index):
        """
        Check the columns of the dataframe w.r.t. the expected columns
        of the data

        Parameters:
            df_columns (pd.Index):
                The columns index to check
        Raises:
            MEIncorrectDataFrameStructure
        """
        if (
            df_columns.names != self._df_columns.names
            or not df_columns.equals(self._df_columns)
        ):
            raise MEIncorrectDataFrameStructure(
                erroneous_index=df_columns,
                expected_index=self._df_columns,
                is_columns=True,
            )

    def set_detail_level(self, detail_level: dl.AbstractDetailLevel):
        """
        Sets the detail level attribute in the structure:
            - _sectors for SectorsDL
            - _regions for RegionsDL
            - _final_demand_categories for FinalDemandCategoriesDL
            - _extension_categories for ExtensionCategoriesDL

        Parameters:
            detail_level (dl.AbstractDetailLevel):
                The detail level instance used to configure the structure

        Raises:
            ValueError: If the provided detail level type is not recognized
        """
        match detail_level:
            case dl.SectorsDL():
                self._sectors = detail_level
            case dl.RegionsDL():
                self._regions = detail_level
            case dl.FinalDemandCategoriesDL():
                self._final_demand_categories = detail_level
            case dl.ExtensionCategoriesDL():
                self._extension_categories = detail_level
            case _:
                raise ValueError(
                    f"Unknown detail level type: {detail_level.__class__.__name__}"
                )

    def apply_bridge_to_df(
        self, df: pd.DataFrame, bridge_: bridge.Bridge
    ) -> pd.DataFrame:
        """
        Apply a bridge to a dataframe

        Compute the combined bridge matrices, i.e. project/extend it to match
        this structure

        Then perform the matricial products left_matrix @ df @ right_matrix,
        after replacing all NaN by 0.0 in df to avoid NaN propagation.

        Identify cells in the result where all original contributors are NaN,
        and set these cells to NaN.

        Parameters:
            df (pd.DataFrame):
                The dataframe to apply the bridge to
            bridge_ (bridge.Bridge):
                The bridge to apply to the dataframe

        Returns:
            pd.DataFrame: the dataframe after applying the bridge
        """
        # Build left and right matrices
        left_bridge = (
            self._compute_combined_bridge(
                bridge_=bridge_, dls_specs=self.rows_specs
            )
            if self.rows_specs
            else None
        )
        left_matrix = (
            left_bridge.get_agg_matrix().array.T if left_bridge else None
        )

        right_bridge = (
            self._compute_combined_bridge(
                bridge_=bridge_, dls_specs=self.columns_specs
            )
            if self.columns_specs
            else None
        )
        right_matrix = (
            right_bridge.get_agg_matrix().array if right_bridge else None
        )

        # Apply bridges
        agg_csr_matrix = self._compute_matricial_product(
            left_matrix=left_matrix,
            factor=sp.csr_array(df.replace(np.nan, 0.0, inplace=False)),
            right_matrix=right_matrix,
        )

        # Deal with NaN
        if df.isna().any().any():
            nan_mask = self._compute_nan_mask(
                df_raw=df,
                left_matrix=left_matrix,
                right_matrix=right_matrix,
            )
            agg_csr_matrix[nan_mask] = np.nan

        return pd.DataFrame(
            agg_csr_matrix.toarray(),
            index=(
                left_bridge.columns_dl.get_dl_as_multi_index()
                if left_bridge is not None
                else self.df_rows
            ),
            columns=(
                right_bridge.columns_dl.get_dl_as_multi_index()
                if right_bridge is not None
                else self.df_columns
            ),
        )

    @staticmethod
    def _compute_matricial_product(
        left_matrix: sp.csr_array | None,
        factor: sp.csr_array,
        right_matrix: sp.csr_array | None,
    ) -> sp.csr_array:
        """
        Compute the matricial product, depending on the data available:
            - if left_matrix and right_matrix are given,
              compute left_matrix @ df @ right_matrix
            - if only left_matrix is given,
              compute left_matrix @ df
            - if only right_matrix is given,
              compute df @ right_matrix

        Parameters:
            left_matrix (sp.csr_array | None):
                The left factor of the matricial product
            factor (sp.csr_array):
                The data to apply the product to
            right_matrix (sp.csr_array | None):
                The right factor of the matricial product

        Returns:
            sp.csr_array: The result of the matricial product
        """
        result = factor
        if left_matrix is not None:
            result = left_matrix @ result
        if right_matrix is not None:
            result = result @ right_matrix
        return result

    def _compute_nan_mask(
        self,
        df_raw: pd.DataFrame,
        left_matrix: sp.csr_array,
        right_matrix: sp.csr_array,
    ) -> np.ndarray:
        """
        Compute a boolean mask indicating aggregated cells where all
        original contributors were NaN.

        Since the aggregation step replaces NaN with 0 before applying
        bridge matrices, meaningful NaN information is lost. This method
        recovers it by propagating a binary NaN mask through the same
        matricial product used for aggregation, and comparing it to the
        total number of contributors per aggregated cell. Where both are
        equal (up to floating-point tolerance), every original
        contributor was NaN.

        Parameters:
            df_raw (pd.DataFrame):
                The original (non-aggregated) DataFrame, possibly containing
                NaN values.
            left_matrix (sp.csr_array):
                Matrix applied on the left (row aggregation).
            right_matrix (sp.csr_array):
                Matrix applied on the right (column aggregation).

        Returns:
            np.ndarray:
                Boolean mask with the shape of the aggregated DataFrame.
                True where all contributors were NaN.
        """
        nan_mask = sp.csr_array(df_raw.isna().astype(cst.DTYPE_FLOAT).values)

        nan_mask_propagated = self._compute_matricial_product(
            left_matrix=left_matrix,
            factor=nan_mask,
            right_matrix=right_matrix,
        )
        total_contributors = self._compute_matricial_product(
            left_matrix=left_matrix,
            factor=sp.csr_array(np.ones_like(df_raw)),
            right_matrix=right_matrix,
        )
        nan_mask_to_apply = np.isclose(
            nan_mask_propagated.toarray(),
            total_contributors.toarray(),
        )

        return nan_mask_to_apply

    def _update_detail_levels(self, *detail_levels: dl.AbstractDetailLevel):
        """
        Update detail levels attributes if given
        """
        for dl_ in detail_levels:
            match dl_:
                case dl.SectorsDL():
                    self._sectors = dl_
                case dl.RegionsDL():
                    self._regions = dl_
                case dl.FinalDemandCategoriesDL():
                    self._final_demand_categories = dl_
                case dl.ExtensionCategoriesDL():
                    self._extension_categories = dl_
                case _:
                    log.error(f"Detail level {type(dl_)} is not supported")
                    raise NotImplementedError

    def _get_applicable_dls(
        self, dls_specs: dict[dl.DetailLevelKind, list[filter.AbstractFilter]]
    ) -> list[dl.AbstractDetailLevel]:
        """
        Returns the ordered list of detail levels used to build an index:
            - Get the applicable detail level from the specification dict
            - Apply the associated filters if defined
            - Append to the list
        """

        def _ensure_dl_is_not_empty(dl_: dl.AbstractDetailLevel):
            if dl_.is_empty():
                log.error(
                    f"Missing/Empty detail level {dl_.kind.value} when building "
                    f"structure {self.__class__.__name__}"
                )
                raise MEDetailLevelMissing(dl_kind=dl_.kind.value)

        applicable_dls = []
        for dl_kind, filters_ in dls_specs.items():
            match dl_kind:
                case dl.DetailLevelKind.SECTORS:
                    _ensure_dl_is_not_empty(self._sectors)
                    applicable_dls.append(
                        self._sectors.get_filtered_dl(*filters_)
                    )
                case dl.DetailLevelKind.REGIONS:
                    _ensure_dl_is_not_empty(self._regions)
                    applicable_dls.append(
                        self._regions.get_filtered_dl(*filters_)
                    )
                case dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES:
                    _ensure_dl_is_not_empty(self._final_demand_categories)
                    applicable_dls.append(
                        self._final_demand_categories.get_filtered_dl(
                            *filters_
                        )
                    )
                case dl.DetailLevelKind.EXTENSION_CATEGORIES:
                    _ensure_dl_is_not_empty(self._extension_categories)
                    applicable_dls.append(
                        self._extension_categories.get_filtered_dl(*filters_)
                    )
                case _:
                    pass

        if applicable_dls:
            # Ensure that the level names are unique
            dl.AbstractDetailLevel.check_unicity_of_level_names(
                *applicable_dls
            )

        return applicable_dls

    def _get_adjacent_dl_lists(
        self,
        dl_kind: dl.DetailLevelKind,
        dls_specs: dict[dl.DetailLevelKind, list[filter.AbstractFilter]],
    ) -> tuple[list[dl.AbstractDetailLevel], list[dl.AbstractDetailLevel]]:
        """
        Sort detail levels according to the position in the specs (i.e.
        granularity)
        If a DL is defined left to the one of kind dl_kind, add to left_dls
        If a DL is defined right to the one of kind dl_kind, add to right_dls

        Parameters:
            dl_kind (dl.DetailLevelKind):
                The kind of the detail level to use as reference
            dls_specs (dict[dl.DetailLevelKind, list[filter.AbstractFilter]]):
                The rows or columns specs of the detail levels

        Returns:
             tuple[list[dl.AbstractDetailLevel], list[dl.AbstractDetailLevel]]:
             left_dls, right_dls
        """
        left_dls = []
        right_dls = []
        is_left = True
        for dl_ in self._get_applicable_dls(dls_specs):
            if dl_.kind == dl_kind:
                is_left = False
                continue
            if is_left:
                left_dls.append(dl_)
            else:
                right_dls.append(dl_)

        return left_dls, right_dls

    @staticmethod
    def _get_bridge_pool_key(bridge_, left_dls, right_dls) -> str:

        key = (
            f"{[f'<dl_{dl_.kind.value}-{tools.hash_df(dl_.df)}>' for dl_ in left_dls]}-"
            f"<bridge_{bridge_.kind.value}-{tools.hash_csr_array(bridge_.matrix.array)}>-"
            f"{[f'<dl_{dl_.kind.value}-{tools.hash_df(dl_.df)}>' for dl_ in right_dls]}-"
        )
        return str(key)

    def _compute_combined_bridge(
        self,
        bridge_: bridge.Bridge,
        dls_specs: dict[dl.DetailLevelKind, list[filter.AbstractFilter]],
    ) -> bridge.CombinedBridge | None:
        """
        Compute a combined bridge from a bridge and detail levels (DL)
        specifications, following this logic:
            - If the bridge kind is not represented in the DL specs, then
              return None
            - If the bridge kind is represented in the DL specs, then apply
              the filters which may be associated to this kind
            - Then, two cases:
                - Either the combined bridge has already been built and
                  is available in the bridge pool => return it
                - Or it has not been built yet:
                    - Identify the detail levels other than the bridge kind,
                      splitting in two lists, more and less granular than the bridge
                      kind
                    - Instantiate a combined bridge from the filtered bridge and
                      the lists of detail levels
                    - Store it in the bridge pool for further re-use
                    - Returns this combined bridge

        Parameters:
            bridge_ (bridge.Bridge):
                The bridge to combine
            dls_specs: dict[dl.DetailLevelKind, list[filter.AbstractFilter]]:
                The rows or columns specs

        Returns:
            CombinedBridge | None
        """
        if bridge_.kind not in dls_specs.keys():
            return None

        # Retrieve adjacent detail levels
        left_dls, right_dls = self._get_adjacent_dl_lists(
            dl_kind=bridge_.kind,
            dls_specs=dls_specs,
        )

        pool_key = None
        full_bridge = None

        # Filter bridge if necessary
        filtered_bridge = bridge_
        try:
            bridge_filters = dls_specs[bridge_.kind]
            if len(bridge_filters) > 0:
                filtered_bridge = bridge_.get_filtered_bridge(*bridge_filters)
        except KeyError:
            pass

        # Try to retrieve from pool if active
        if bridge_pool.pool.is_active():
            pool_key = self._get_bridge_pool_key(
                bridge_=filtered_bridge,
                left_dls=left_dls,
                right_dls=right_dls,
            )
            full_bridge = bridge_pool.pool.get(key=pool_key)
            if full_bridge is not None:
                log.debug("Re-use available bridge from bridge pool")
                log.debug(f"Key is {pool_key}")

        # If not already available, build the combined bridge
        if full_bridge is None:

            full_bridge = bridge.CombinedBridge.init_from_bridge(
                bridge_=filtered_bridge,
                left_dls=left_dls,
                right_dls=right_dls,
            )
            # Add it to the pool if active
            if bridge_pool.pool.is_active():
                bridge_pool.pool.store(key=pool_key, value=full_bridge)

        return full_bridge

    def get_domestic_regions_list(self) -> list[str]:
        """
        Returns the list of domestic regions represented in this structure
        """
        return self._regions.get_domestic_regions_list()

    def has_domestic_regions(self) -> bool:
        """
        Returns True if the list of domestic regions represented in this
        structure is not empty
        """
        return len(self.get_domestic_regions_list()) > 0

    def get_import_regions_list(self) -> list[str]:
        """
        Returns the list of import regions represented in this structure
        """
        return self._regions.get_import_regions_list()

    def has_import_regions(self) -> bool:
        """
        Returns True if the list of import regions represented in this
        structure is not empty
        """
        return len(self.get_import_regions_list()) > 0


class StructureNull(AbstractDataStructure):
    """
    A null structure, with rows and columns set to cst.NULL_INDEX
    """

    def __init__(self, **kwargs):
        super().__init__(
            sectors=dl.SectorsDL(),
            regions=dl.RegionsDL(),
            final_demand_categories=dl.FinalDemandCategoriesDL(),
        )

    @property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return None

    @property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return None

    def build_rows(self, *args, **kwargs):
        self.df_rows = cst.NULL_INDEX

    def build_columns(self, *args, **kwargs):
        self.df_columns = cst.NULL_INDEX

    def apply_bridge_to_df(
        self, df: pd.DataFrame, bridge_: bridge.Bridge
    ) -> pd.DataFrame:
        return df


class StructureX(AbstractDataStructure):
    """
    - The structure is as follows (circles represent data):

        - By default, it is only one column 'x':

        +----------+----------+----------------+---+
        | *origin* | *region* |                | x |
        +----------+----------+----------------+---+
        | domestic | R1       |                | - |
        +----------+----------+----------------+---+
        | domestic | R2       |                | - |
        +----------+----------+----------------+---+
        | domestic | [...]    |                | - |
        +----------+----------+----------------+---+
        | import   | RA       |                | - |
        +----------+----------+----------------+---+
        | import   | RB       |                | - |
        +----------+----------+----------------+---+
        | import   | [...]    |                | - |
        +----------+----------+----------------+---+
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return None

    def _build_columns(self, *args, **kwargs):
        self._df_columns = pd.MultiIndex.from_arrays(
            [[cst.X]], names=[cst.IDX_VARIABLE]
        )


class StructureSx(AbstractDataStructure):
    """
    - The structure is as follows (circles represent data):

    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    |                       |                           |                     |    *region*    | R1 | R2 | [...] |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    |                       |                           |                     |   *category*   |    |    |       |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    |                       |                           |                     | *sub_category* |    |    |       |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    |                       |                           |                     |    *sector*    |    |    |       |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    | *category* (optional) | *sub_category* (optional) | *sector* (optional) |                |    |    |       |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    |                       |                           |                     |                | -  | -  | -     |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    |                       |                           |                     |                | -  | -  | -     |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    |                       |                           |                     |                | -  | -  | -     |
    +-----------------------+---------------------------+---------------------+----------------+----+----+-------+
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureMRoW(AbstractDataStructure):
    """
    This structure is similar to StructureSx except it deals with import
    regions instead of domestic regions.
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_import_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureZ(AbstractDataStructure):
    """
    - The structure is as follows (circles represent data):

        +----------+----------+----------------+----+----+-------+
        |          |          |    *region*    | R1 | R2 | [...] |
        +----------+----------+----------------+----+----+-------+
        |          |          |   *category*   |    |    |       |
        +----------+----------+----------------+----+----+-------+
        |          |          | *sub_category* |    |    |       |
        +----------+----------+----------------+----+----+-------+
        |          |          |    *sector*    |    |    |       |
        +----------+----------+----------------+----+----+-------+
        | *origin* | *region* |                |    |    |       |
        +----------+----------+----------------+----+----+-------+
        | domestic | R1       |                | -  | -  | -     |
        +----------+----------+----------------+----+----+-------+
        | domestic | R2       |                | -  | -  | -     |
        +----------+----------+----------------+----+----+-------+
        | domestic | [...]    |                | -  | -  | -     |
        +----------+----------+----------------+----+----+-------+
        | import   | RA       |                | -  | -  | -     |
        +----------+----------+----------------+----+----+-------+
        | import   | RB       |                | -  | -  | -     |
        +----------+----------+----------------+----+----+-------+
        | import   | [...]    |                | -  | -  | -     |
        +----------+----------+----------------+----+----+-------+
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureY(AbstractDataStructure):
    """
    - The structure is as follows (circles represent data):

        +----------+----------+------------------+----+----+-------+
        |          |          |    *region*      | R1 | R2 | [...] |
        +----------+----------+------------------+----+----+-------+
        |          |          |   *Y_category*   |    |    |       |
        +----------+----------+------------------+----+----+-------+
        |          |          | *Y_sub_category* |    |    |       |
        +----------+----------+------------------+----+----+-------+
        | *origin* | *region* |                  |    |    |       |
        +----------+----------+------------------+----+----+-------+
        | domestic | R1       |                  | -  | -  | -     |
        +----------+----------+------------------+----+----+-------+
        | domestic | R2       |                  | -  | -  | -     |
        +----------+----------+------------------+----+----+-------+
        | domestic | [...]    |                  | -  | -  | -     |
        +----------+----------+------------------+----+----+-------+
        | import   | RA       |                  | -  | -  | -     |
        +----------+----------+------------------+----+----+-------+
        | import   | RB       |                  | -  | -  | -     |
        +----------+----------+------------------+----+----+-------+
        | import   | [...]    |                  | -  | -  | -     |
        +----------+----------+------------------+----+----+-------+
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
        }

    def diagonalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Diagonalize final-demand-shaped dataframe

        This function performs a diagonalization of the dataframe per region
        and per column. Each region block is individually diagonalized. Each
        column is individually diagonalized.

        Parameters:
            df (pd.DataFrame):
                The dataframe to diagonalize
        Returns:
            pd.DataFrame : the diagonalized dataframe
        """
        # Define block size and columns index
        block_size = len(self.sectors.get_dl_as_multi_index())
        df_columns_per_region = (
            self._sectors.get_dl_as_multi_index_propagated_on(
                df_on=self._final_demand_categories.df
            ).to_frame(index=False)
        )
        columns = pd.MultiIndex.from_frame(
            dl_tools.propagate_columns(
                df_from=df_columns_per_region,
                df_to=self._regions.get_domestic_origin_df(with_origin=False),
            )
        )

        output = pd.DataFrame(
            pymrio.tools.ioutil.diagonalize_blocks(
                df.values, blocksize=block_size
            ),
            index=df.index,
            columns=columns,
        )

        return output


class StructureDCbaBySector(AbstractDataStructure):
    """
    - The structure is as follows (circles represent data):

        - It can be disaggregated by regions:
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        |          |          |            |                |          |    *region*      | R1 | R2 | [...] |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        |          |          |            |                |          |   *Y_category*   |    |    |       |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        |          |          |            |                |          | *Y_sub_category* |    |    |       |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        |          |          |            |                |          |    *category*    |    |    |       |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        |          |          |            |                |          |  *sub_category*  |    |    |       |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        |          |          |            |                |          |     *sector*     |    |    |       |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        | *origin* | *region* | *category* | *sub_category* | *sector* |                  |    |    |       |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        | domestic | R1       |            |                |          |                  | -  | -  | -     |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        | domestic | R2       |            |                |          |                  | -  | -  | -     |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        | domestic | [...]    |            |                |          |                  | -  | -  | -     |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        | import   | R3       |            |                |          |                  | -  | -  | -     |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        | import   | R4       |            |                |          |                  | -  | -  | -     |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+
        | import   | [...]    |            |                |          |                  | -  | -  | -     |
        +----------+----------+------------+----------------+----------+------------------+----+----+-------+

    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureDCbaByExtensionCategory(AbstractDataStructure):
    """
    - The structure is as follows (circles represent data):

        - It can be aggregated on all regions:
        +-------------+------------------+----+----+-------+
        |             |    *region*      | R1 | R2 | [...] |
        +-------------+------------------+----+----+-------+
        |             |   *Y_category*   |    |    |       |
        +-------------+------------------+----+----+-------+
        |             | *Y_sub_category* |    |    |       |
        +-------------+------------------+----+----+-------+
        |             |    *category*    |    |    |       |
        +-------------+------------------+----+----+-------+
        |             |  *sub_category*  |    |    |       |
        +-------------+------------------+----+----+-------+
        |             |     *sector*     |    |    |       |
        +-------------+------------------+----+----+-------+
        | *perimeter* |                  |    |    |       |
        | (or other)  |                  |    |    |       |
        +-------------+------------------+----+----+-------+
        |             |                  | -  | -  | -     |
        +-------------+------------------+----+----+-------+
        |             |                  | -  | -  | -     |
        +-------------+------------------+----+----+-------+
        |             |                  | -  | -  | -     |
        +-------------+------------------+----+----+-------+
        |             |                  | -  | -  | -     |
        +-------------+------------------+----+----+-------+
        |             |                  | -  | -  | -     |
        +-------------+------------------+----+----+-------+
        |             |                  | -  | -  | -     |
        +-------------+------------------+----+----+-------+
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureDCbaKBySector(AbstractDataStructure):
    """
    The structure is the same as a d_cba structure by sector, but without
    the GFCF column(s).
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureDCbaKByExtensionCategory(AbstractDataStructure):
    """
    The structure is the same as a d_cba structure by extension category,
    but without the GFCF column(s).
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureMappingDirect(AbstractDataStructure):

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureMappingIndirect(AbstractDataStructure):

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_import_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureMappingKDirect(AbstractDataStructure):

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class StructureMappingKIndirect(AbstractDataStructure):

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_import_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            dl.DetailLevelKind.SECTORS: [],
        }

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_domestic_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                filter.get_filter_remove_investment(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }


class AbstractStructureUnit(AbstractDataStructure, ABC):

    @cached_property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return None

    def _build_columns(self, *args, **kwargs):
        self._df_columns = pd.MultiIndex.from_arrays(
            [[cst.UNIT]], names=[cst.IDX_VARIABLE]
        )

    @staticmethod
    def _perform_aggregation(
        df: pd.DataFrame, agg_matrix: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate the unit vector while checking that the aggregation matrix
        is consistent with it

        Parameters:
            df (pd.DataFrame):
                The unit vector matrix to aggregate
            agg_matrix (pd.DataFrame):
                The aggregation matrix to apply
        Raises:
            MEAggMatrixInconsistentWithUnitVector
                if ALLOW_HETEROGENEOUS_AGGREGATION is False
                and the aggregation matrix defines aggregation between values
                with different units
        """
        if len(df.index) > 1:
            log.verbose("Check aggregation matrix with unit vector")
            agg_unit_vector = pd.DataFrame(
                index=df.columns,
                columns=agg_matrix.columns,
                dtype=cst.DTYPE_STRING,
            )
            for column in agg_matrix.columns:
                matching_indices = (
                    agg_matrix[column].loc[agg_matrix[column] == 1].index
                )
                matching_df = df.loc[matching_indices]
                if matching_df.size > 1:
                    values = df.loc[matching_indices].squeeze().unique()
                    if len(values) > 1:
                        list_sectors = list(
                            matching_df.index.get_level_values(-1)
                        )
                        if not config.ALLOW_HETEROGENEOUS_AGGREGATION:
                            log.error(
                                "Aggregation matrix not consistent with unit "
                                "vector"
                            )
                            log.error(
                                f"Indexes {list_sectors} have inconsistent units: "
                                f"{values}"
                            )
                            raise MEAggMatrixInconsistentWithUnitVector

                        log.warning(
                            "Aggregation matrix not consistent with unit vector"
                        )
                        log.warning(
                            f"Indexes {list_sectors} have inconsistent units: "
                            f"{values}"
                        )
                        log.warning(f"Keep only unit '{values[0]}'")
                        values = values[0]
                elif matching_df.size == 0:
                    values = pd.NA
                else:
                    values = df.loc[matching_indices].squeeze()
                agg_unit_vector[column] = values

            return agg_unit_vector.T
        else:
            return df

    @staticmethod
    def _perform_disaggregation(
        df: pd.DataFrame, agg_matrix: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Disaggregate the unit vector while checking that the aggregation
        matrix is consistent

        Parameters:
            df (pd.DataFrame):
                The unit vector matrix to disaggregate
            agg_matrix (pd.DataFrame):
                The aggregation matrix to apply
        Raises:
            MEAggMatrixInconsistentWithUnitVector
                if the aggregation matrix is badly built
                (several ones per column, rows with only zeros)
        """
        if len(df.index) > 1:
            log.verbose("Check disaggregation matrix with unit vector")
            agg_unit_vector = pd.DataFrame(
                index=df.columns,
                columns=agg_matrix.columns,
                dtype=cst.DTYPE_STRING,
            )

            for row in agg_matrix.index:
                matching_indices = agg_matrix.loc[row][
                    agg_matrix.loc[row] == 1
                ].index
                if len(matching_indices) < 1:
                    log.error(
                        "Disaggregation matrix shall have at least one '1' "
                        "per row"
                    )
                    log.error(f"None was found at row {row}")
                    raise MEAggMatrixInconsistentWithUnitVector
            for column in agg_matrix.columns:
                matching_indices = (
                    agg_matrix[column].loc[agg_matrix[column] == 1].index
                )
                if len(matching_indices) != 1:
                    log.error(
                        "Disaggregation matrix shall have one and only one "
                        "'1' per column"
                    )
                    log.error(
                        f"{len(matching_indices)} found at column {column}"
                    )
                    raise MEAggMatrixInconsistentWithUnitVector

                agg_unit_vector[column] = df.loc[matching_indices[0]]

            return agg_unit_vector.T
        else:
            return df


class StructureUnitBySector(AbstractStructureUnit):
    """
    - The structure is as follows (circles represent data):

        +------------+----------------+------------+------+
        | *category* | *sub_category* | *sector*   | unit |
        | (optional) | (optional)     | (optional) |      |
        +------------+----------------+------------+------+
        |            |                |            | -    |
        +------------+----------------+------------+------+
        |            |                |            | -    |
        +------------+----------------+------------+------+
        |            |                |            | -    |
        +------------+----------------+------------+------+
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.SECTORS: [],
        }

    def apply_bridge_to_df(
        self, df: pd.DataFrame, bridge_: bridge.Bridge
    ) -> pd.DataFrame:
        if bridge_.kind is dl.DetailLevelKind.SECTORS:
            agg_matrix = bridge_.get_agg_matrix()
            if len(agg_matrix.rows) >= len(agg_matrix.columns):
                return self._perform_aggregation(df, agg_matrix.to_dataframe())
            else:
                return self._perform_disaggregation(
                    df, agg_matrix.to_dataframe()
                )
        return df


class StructureUnitByExtensionCategory(AbstractStructureUnit):
    """
    - The structure is as follows (circles represent data):

        +------------+----------------+------------+------+
        | *category* | *sub_category* | *sector*   | unit |
        | (optional) | (optional)     | (optional) |      |
        +------------+----------------+------------+------+
        |            |                |            | -    |
        +------------+----------------+------------+------+
        |            |                |            | -    |
        +------------+----------------+------------+------+
        |            |                |            | -    |
        +------------+----------------+------------+------+
    """

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    def apply_bridge_to_df(
        self, df: pd.DataFrame, bridge_: bridge.Bridge
    ) -> pd.DataFrame:
        if bridge_.kind is dl.DetailLevelKind.EXTENSION_CATEGORIES:
            agg_matrix = bridge_.get_agg_matrix()
            if len(agg_matrix.index) >= len(agg_matrix.columns):
                return self._perform_aggregation(df, agg_matrix)
            else:
                return self._perform_disaggregation(df, agg_matrix)
        return df


class StructureImpDomRatio(AbstractDataStructure):

    @cached_property
    def rows_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return {
            dl.DetailLevelKind.REGIONS: [
                filter.get_filter_keep_import_regions(),
                filter.get_filter_remove_origin_level(),
            ],
            dl.DetailLevelKind.SECTORS: [],
        }

    @property
    def columns_specs(
        self,
    ) -> dict[dl.DetailLevelKind, list[filter.AbstractFilter]] | None:
        return None

    def _build_columns(self, *args, **kwargs):
        self._df_columns = pd.MultiIndex.from_arrays(
            [[cst.IMP_DOM_RATIO]], names=[cst.IDX_VARIABLE]
        )
