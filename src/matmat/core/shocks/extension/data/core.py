"""
Presentation
************
This module contains the definition of the extension shock data classes

Content
*******
- Classes:
    - :class:`AbstractExtensionShockData`
    - :class:`NullExtensionShockData`
    - :class:`SxDomShockData`
    - :class:`SyShockData`
    - :class:`SzShockData`
    - :class:`MRoWShockData`
"""

__all__ = [
    "AbstractExtensionShockData",
    "NullExtensionShockData",
    "SxDomShockData",
    "SyShockData",
    "SzShockData",
    "MRoWShockData",
]

from abc import ABC

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.core.data.core import AbstractData
from matmat.core.data.strategies import nature, structure
from matmat.core.shocks.extension.data.identity import (
    ExtensionShockDataIdentity,
)
from matmat.utils import constants as cst


class AbstractExtensionShockData(AbstractData, ABC):
    """
    This abstract class represents an extension shock data class.
    It defines a set of attributes and methods common to all its subclasses.
    Some of these methods are concrete, i.e. they have an implementation.
    Some of these methods are abstract, i.e. they do not have an implementation
     and shall be overridden by subclasses.

    Refer to subclasses for dataframes formats.

    Attributes
    ----------
    _id : ExtensionShockDataIdentity
        the identity card of the extension shock data
    """

    _id: ExtensionShockDataIdentity

    def __init__(
        self,
        *,
        extension_name: str,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        extension_categories: dl.ExtensionCategoriesDL,
    ):
        # Build identity
        self._id = ExtensionShockDataIdentity(extension_name=extension_name)

        # Build nature
        self._build_nature()

        # Build structure
        self._build_structure(
            sectors=sectors,
            regions=regions,
            final_demand_categories=final_demand_categories,
            extension_categories=extension_categories,
        )

        # Build dataframe
        self.build_df()

    def get_origin_description(self) -> str:
        return f"from extension shock '{self._id.extension_name}'"


# pylint: disable=W0107
# (pass statements have meaning here as the methods shall do nothing)
class NullExtensionShockData(AbstractExtensionShockData):
    """
    Null extension shock data.
    This class overrides all methods to do nothing.
    """

    _NAME = "null"

    _nature: nature.NatureNull
    _structure: structure.StructureNull

    def get_nature_type(self, **kwargs):
        return nature.NatureNull

    def get_structure_type(self, **kwargs):
        return structure.StructureNull

    def __init__(self):
        super().__init__(
            regions=dl.RegionsDL(),
            sectors=dl.SectorsDL(),
            final_demand_categories=dl.FinalDemandCategoriesDL(),
            extension_name=cst.NULL,
            extension_categories=dl.ExtensionCategoriesDL(
                extension_name=cst.NULL
            ),
        )

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


class SxDomShockData(AbstractExtensionShockData):
    """
    Domestic production coefficients shock matrix

    Refer to :class:`structure.StructureSx` for the format description.
    """

    _NAME = cst.D_S_X_DOM

    _nature: nature.Coefficient
    _structure: structure.StructureSx

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureSx


class SyShockData(AbstractExtensionShockData):
    """
    Final demand coefficients shock matrix

    Refer to :class:`structure.StructureY` for the format description.
    """

    _NAME = cst.D_S_Y

    _nature: nature.Coefficient
    _structure: structure.StructureY

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureY


class SzShockData(AbstractExtensionShockData):
    """
    Inter-industry coefficients shock matrix

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.D_S_Z

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ


class MRoWShockData(AbstractExtensionShockData):
    """
    Multiplier for the Rest Of The World shock matrix

    Refer to :class:`structure.StructureMRoW` for the format description.
    """

    _NAME = cst.D_M_ROW

    _nature: nature.Coefficient
    _structure: structure.StructureMRoW

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureMRoW
