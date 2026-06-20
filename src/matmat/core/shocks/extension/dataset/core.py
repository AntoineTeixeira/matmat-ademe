"""
Overview
********
This module is the 'core' module of the 'shocks.extension.dataset' package.
It defines the dataset of an extension shock.

Contents
********
- Classes:
  - :class:`ExtensionShockDataSet`

"""

__all__ = ["ExtensionShockDataSet"]

from matmat.core.detail_level import core as dl
from matmat.core.dataset.core import AbstractListedDataSet
from matmat.core.shocks.extension.data import factory
from matmat.core.shocks.extension.data.core import (
    SxDomShockData,
    SyShockData,
    SzShockData,
    MRoWShockData,
    NullExtensionShockData,
)
from matmat.utils import constants as cst
from matmat.utils.errors import MEIncorrectArguments


class ExtensionShockDataSet(AbstractListedDataSet):
    """
    Class representing an extension shock data set

    Attributes
    ----------
        _dS_x_dom : SxDomShockData or NullExtensionShockData
            The production coefficients shock matrix
        _dS_Y : SyShockData or NullExtensionShockData
            The final demand coefficients shock matrix
        _dS_Z : SzShockData or NullExtensionShockData
            The inter-industry coefficients shock matrix
        _dM_RoW : MRoWShockData or NullExtensionShockData
            The multiplier of the Rest Of the World shock matrix
    """

    _dS_x_dom: SxDomShockData | NullExtensionShockData
    _dS_Y: SyShockData | NullExtensionShockData
    _dS_Z: SzShockData | NullExtensionShockData
    _dM_RoW: MRoWShockData | NullExtensionShockData

    def __init__(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        extension_name: str,
        extension_categories: dl.ExtensionCategoriesDL,
        data_list: list = None,
    ):
        # Extension categories are required
        if extension_categories is None:
            raise MEIncorrectArguments(
                msg="Parameter 'extension_categories' "
                "is required to build the dataset"
            )

        # Persistent data
        self._extension_name: str = extension_name
        self._extension_categories: dl.ExtensionCategoriesDL = (
            extension_categories
        )

        super().__init__(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            data_list=data_list,
        )

    @property
    def extension_name(self):
        return self._extension_name

    @property
    def extension_categories(self):
        return self._extension_categories

    @staticmethod
    def get_data_names():
        return cst.LIST_OF_EXTENSION_SHOCK_DATA

    def set_data(self, name: str):
        setattr(
            self,
            name,
            factory.make_data(
                name=name,
                regions=self.regions,
                sectors=self.sectors,
                extension_name=self.extension_name,
                extension_categories=self.extension_categories,
                final_demand_categories=self.final_demand_categories,
            ),
        )

    def set_null_data(self, name: str):
        setattr(self, name, NullExtensionShockData())

    def _set_detail_level(self, detail_level: dl.AbstractDetailLevel):
        """
        Sets the detail level attribute in the dataset:
            - _extension_categories for ExtensionCategoriesDL
            - otherwise call the parent method

        Parameters:
            detail_level (dl.AbstractDetailLevel):
                The detail level instance used to configure the dataset
        """
        if isinstance(detail_level, dl.ExtensionCategoriesDL):
            self._extension_categories = detail_level
        else:
            super()._set_detail_level(detail_level=detail_level)

    @property
    def dS_x_dom(self) -> SxDomShockData | NullExtensionShockData:
        return self._dS_x_dom

    @dS_x_dom.setter
    def dS_x_dom(self, value: SxDomShockData | NullExtensionShockData):
        self._dS_x_dom = value

    @property
    def dS_Y(self) -> SyShockData | NullExtensionShockData:
        return self._dS_Y

    @dS_Y.setter
    def dS_Y(self, value: SyShockData | NullExtensionShockData):
        self._dS_Y = value

    @property
    def dS_Z(self) -> SzShockData | NullExtensionShockData:
        return self._dS_Z

    @dS_Z.setter
    def dS_Z(self, value: SzShockData | NullExtensionShockData):
        self._dS_Z = value

    @property
    def dM_RoW(self) -> MRoWShockData | NullExtensionShockData:
        return self._dM_RoW

    @dM_RoW.setter
    def dM_RoW(self, value: MRoWShockData | NullExtensionShockData):
        self._dM_RoW = value
