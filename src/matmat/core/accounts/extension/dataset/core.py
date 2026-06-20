"""
Overview
********
This module is the 'core' module of the 'accounts.extension.dataset' package.
It defines the dataset of an extension.

Contents
********
- Classes:
  - :class:`ExtensionDataSet`

"""

__all__ = ["ExtensionDataSet"]

from matmat.core.detail_level import core as dl
from matmat.core.dataset.core import AbstractMappedDataSet
from matmat.core.accounts.extension.dataset import config
from matmat.core.accounts.extension.data import factory
from matmat.core.accounts.extension.data.core import (
    SxDomData,
    SyData,
    SzData,
    FxDomData,
    FyData,
    FzData,
    MRoWData,
    DImpData,
    MData,
    MKData,
    DCbaData,
    DCbaKData,
    UnitExtensionData,
    NullExtensionData,
    MappingData,
    MappingKData,
)
from matmat.utils import constants as cst
from matmat.utils.errors import (
    MEIncorrectArguments,
)


class ExtensionDataSet(AbstractMappedDataSet):
    """
    Class representing an extension dataset.

    Attributes
    ----------
        _S_x_dom : SxDomData
            TODO: Doc
        _S_Y : SyData or NullExtensionData
            The final demand coefficients matrix
        _S_Z : SzData or NullExtensionData
            The inter-industry coefficients matrix
        _F_x_dom : FxDomData
            The domestic production fluxes matrix
        _F_Y : FyData or NullExtensionData
            The final demand fluxes matrix
        _F_Z : FzData or NullExtensionData
            The inter-industry fluxes matrix
        _M_RoW : MRoWData
            TODO: Doc
        _d_imp : DImpData or NullExtensionData
            TODO: Doc_M : MData
            The multiplier
        _M_k : MKData or NullExtensionData
            The augmented multiplier
        _d_cba : DCbaData
            The consumption based accounts
        _d_cba_k : DCbaKData or NullExtensionData
            The consumption based accounts
        _mapping : MappingData or NullExtensionData
            The mapping
        _mapping_k : MappingKData or NullExtensionData
            The mapping
        _unit : UnitExtensionData
            The unit matrix of the extension
    """

    # Coefficients
    _S_x_dom: SxDomData | NullExtensionData
    _S_Y: SyData | NullExtensionData
    _S_Z: SzData | NullExtensionData
    _M_RoW: MRoWData | NullExtensionData

    # Fluxes
    _F_x_dom: FxDomData | NullExtensionData
    _F_Y: FyData | NullExtensionData
    _F_Z: FzData | NullExtensionData
    _d_imp: DImpData | NullExtensionData

    # Outputs
    _M: MData
    _M_k: MKData | NullExtensionData
    _d_cba: DCbaData
    _d_cba_k: DCbaKData | NullExtensionData
    _mapping: MappingData | NullExtensionData
    _mapping_k: MappingKData | NullExtensionData

    # Unit
    _unit: UnitExtensionData

    def __init__(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        extension_name: str,
        extension_categories: dl.ExtensionCategoriesDL,
        # Parameters related to the configuration of the dataset
        config__extension_calcul_strategy: str,
        config__system_calcul_strategy: str = None,
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
            conversions=config.ExtensionDataSetConversions(),
            # Dataset mapping
            map__extension_calcul_strategy=config.DATASET_MAP_WRT_EXTENSION_CALCUL_STRATEGY,
            map__system_calcul_strategy=config.DATASET_MAP_WRT_SYSTEM_CALCUL_STRATEGY,
            # Dataset configuration
            config__extension_calcul_strategy=config__extension_calcul_strategy,
            config__system_calcul_strategy=config__system_calcul_strategy,
        )

    @property
    def extension_name(self):
        return self._extension_name

    @property
    def extension_categories(self):
        return self._extension_categories

    @staticmethod
    def get_data_names():
        return cst.LIST_OF_EXTENSION_DATA

    def set_data(self, name: str):
        setattr(
            self,
            name,
            factory.make_data(
                name=name,
                regions=self.regions,
                sectors=self.sectors,
                extension_name=self.extension_name,
                final_demand_categories=self.final_demand_categories,
                extension_categories=self.extension_categories,
                strategy=self.get_config("extension_calcul_strategy"),
            ),
        )

    def set_null_data(self, name: str):
        setattr(self, name, NullExtensionData())

    def reset_outputs(self):
        for output_ in [
            self.M,
            self.M_k,
            self.d_cba,
            self.d_cba_k,
            self.mapping,
            self.mapping_k,
        ]:
            output_.reset()

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
    def F_x_dom(self):
        return self._F_x_dom

    @F_x_dom.setter
    def F_x_dom(self, value: FxDomData):
        self._F_x_dom = value

    @property
    def S_x_dom(self):
        return self._S_x_dom

    @S_x_dom.setter
    def S_x_dom(self, value: SxDomData | NullExtensionData):
        self._S_x_dom = value

    @property
    def F_Y(self):
        return self._F_Y

    @F_Y.setter
    def F_Y(self, value: FyData | NullExtensionData):
        self._F_Y = value

    @property
    def S_Y(self):
        return self._S_Y

    @S_Y.setter
    def S_Y(self, value: SyData | NullExtensionData):
        self._S_Y = value

    @property
    def F_Z(self):
        return self._F_Z

    @F_Z.setter
    def F_Z(self, value: FzData | NullExtensionData):
        self._F_Z = value

    @property
    def S_Z(self):
        return self._S_Z

    @S_Z.setter
    def S_Z(self, value: SzData | NullExtensionData):
        self._S_Z = value

    @property
    def M_RoW(self):
        return self._M_RoW

    @M_RoW.setter
    def M_RoW(self, value: MRoWData | NullExtensionData):
        self._M_RoW = value

    @property
    def d_imp(self):
        return self._d_imp

    @d_imp.setter
    def d_imp(self, value: DImpData):
        self._d_imp = value

    @property
    def M(self):
        return self._M

    @M.setter
    def M(self, value: MData):
        self._M = value

    @property
    def M_k(self):
        return self._M_k

    @M_k.setter
    def M_k(self, value: MKData):
        self._M_k = value

    @property
    def d_cba(self):
        return self._d_cba

    @d_cba.setter
    def d_cba(self, value: DCbaData):
        self._d_cba = value

    @property
    def d_cba_k(self):
        return self._d_cba_k

    @d_cba_k.setter
    def d_cba_k(self, value: DCbaKData):
        self._d_cba_k = value

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, value: MappingData):
        self._mapping = value

    @property
    def mapping_k(self):
        return self._mapping_k

    @mapping_k.setter
    def mapping_k(self, value: MappingKData):
        self._mapping_k = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value: UnitExtensionData):
        self._unit = value
