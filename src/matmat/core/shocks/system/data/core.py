"""
Presentation
************
This module contains the definition of the shock data classes

Content
*******
- Classes:
    - :class:`AbstractSystemShockData`
    - :class:`NullSystemShockData`
    - :class:`AShockData`
    - :class:`KShockData`
    - :class:`YShockData`
    - :class:`YkShockData`
    - :class:`ZShockData`
"""

__all__ = [
    "AbstractSystemShockData",
    "NullSystemShockData",
    "AShockData",
    "KShockData",
    "YShockData",
    "YkShockData",
    "ZShockData",
]

from abc import ABC

import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.core.data.core import AbstractData
from matmat.core.data.strategies import nature, structure
from matmat.core.shocks.system.data.identity import SystemShockDataIdentity
from matmat.utils import constants as cst


class AbstractSystemShockData(AbstractData, ABC):
    """
    This abstract class represents a system shock data class.
    It defines a set of attributes and methods common to all its subclasses.
    Some of these methods are concrete, i.e. they have an implementation.
    Some of these methods are abstract, i.e. they do not have an implementation
     and shall be overridden by subclasses.

    Refer to subclasses for dataframes formats.

    Attributes
    ----------
    _id : SystemShockDataIdentity
        the identity card of the system shock data
    """

    _id: SystemShockDataIdentity

    def __init__(
        self,
        *,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
    ):
        # Build identity
        self._id = SystemShockDataIdentity()

        # Build nature
        self._build_nature()

        # Build structure
        self._build_structure(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
        )

        # Build dataframe
        self.build_df()

    def get_origin_description(self) -> str:
        return "from system shock"


# pylint: disable=W0107
# (pass statements have meaning here as the methods shall do nothing)
class NullSystemShockData(AbstractSystemShockData):
    """
    Null system shock data.
    This class overrides all methods to do nothing.
    """

    _NAME = "null"

    _nature: nature.NatureNull
    _structure: structure.StructureNull

    def __init__(self):
        super().__init__(
            regions=dl.RegionsDL(),
            sectors=dl.SectorsDL(),
            final_demand_categories=dl.FinalDemandCategoriesDL(),
        )

    def get_nature_type(self, **kwargs):
        return nature.NatureNull

    def get_structure_type(self, **kwargs):
        return structure.StructureNull

    @staticmethod
    def is_null() -> bool:
        """
        Returns True as this is a null shock data
        """
        return True

    def save_to_path(
        self,
        path: str,
        export_format: str = cst.FORMAT_EXCEL,
    ):
        """
        Does nothing
        """
        pass

    def aggregate(self, bridge_: bridge.Bridge, reset: bool):
        """
        Does nothing
        """
        pass

    def disaggregate(self, bridge_: bridge.Bridge, reset: bool):
        """
        Does nothing
        """
        pass


# pylint: enable=W0107


class AShockData(AbstractSystemShockData):
    """
    Technical coefficients shock matrix (dA)

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.D_A

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs):
        return nature.Coefficient

    def get_structure_type(self, **kwargs):
        return structure.StructureZ


class KShockData(AbstractSystemShockData):
    """
    Capital coefficients shock matrix (dK)

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.D_K

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs):
        return nature.Coefficient

    def get_structure_type(self, **kwargs):
        return structure.StructureZ


class YShockData(AbstractSystemShockData):
    """
    Final demand shock matrix (dY)

    Refer to :class:`structure.StructureY` for the format description.
    """

    _NAME = cst.D_Y

    _nature: nature.Coefficient
    _structure: structure.StructureY

    def get_nature_type(self, **kwargs):
        return nature.Coefficient

    def get_structure_type(self, **kwargs):
        return structure.StructureY

    def set_exports(self, exports: pd.DataFrame):
        """
        Set the exports column(s)

        Parameters:
            exports (pd.DataFrame):
                The new exports column(s)
        """
        mask = (
            self.df.columns.get_level_values(
                self.final_demand_categories.get_main_level_name()
            )
            == cst.IDX_EXPORTS
        )
        self.df.loc[:, mask] = exports.values

    def set_gfcf_to_zero(self):
        """
        Set the GFCF column(s) to 0.0
        """
        for region in self.regions[cst.IDX_DOMESTIC]:
            self.df[(region, cst.IDX_INVESTMENT, cst.IDX_INVESTMENT_I)] = 0.0


class YkShockData(AbstractSystemShockData):
    """
    Investment shock matrix (dY_k)

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.D_Y_K

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ


class ZShockData(AbstractSystemShockData):
    """
    Inter-industry shock matrix

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.D_Z

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ
