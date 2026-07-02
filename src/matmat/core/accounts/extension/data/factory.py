"""
Presentation
************
This module is the extension data factory. It provides an interface to
instantiate extension data.

Content
*******
- Functions:
    - :meth:`make_data`
"""

__all__ = ["make_data"]

from matmat.core.detail_level import core as dl
import matmat.core.accounts.extension.data.core as data

from matmat.utils import logging as log, constants as cst
from matmat.utils.errors import (
    MEDataNotAllowed,
)


def make_data(
    *,
    name: str,
    extension_name: str,
    regions: dl.RegionsDL,
    sectors: dl.SectorsDL,
    final_demand_categories: dl.FinalDemandCategoriesDL,
    extension_categories: dl.ExtensionCategoriesDL,
    strategy: str = None,
) -> data.AbstractExtensionData:
    """
    Instantiate an extension data w.r.t. the data name

    Parameters:
        name (str):
            The name of the data
        extension_name (str):
            The name of the extension
        regions (dl.RegionsDL):
            The regions represented in the data
        sectors (dl.SectorsDL):
            The sectors represented in the data
        final_demand_categories (dl.FinalDemandCategoriesDL):
            The categories and subcategories of the final demand
        extension_categories (dl.ExtensionCategoriesDL):
            The categories represented in the extension
        strategy (str):
            The calcul strategy (default to None)
    Returns:
        AbstractExtensionData : The instantiated extension data
    Raises:
        MEDataNotAllowed:
            If the name of the data is not an extension data
    """

    # Mapping between data name and data class
    dict_data_classes = {
        cst.S_X_DOM: data.SxDomData,
        cst.S_Y: data.SyData,
        cst.S_Z: data.SzData,
        cst.F_X_DOM: data.FxDomData,
        cst.F_Y: data.FyData,
        cst.F_Z: data.FzData,
        cst.M_ROW: data.MRoWData,
        cst.D_IMP: data.DImpData,
        cst.M: data.MData,
        cst.M_K: data.MKData,
        cst.D_CBA: data.DCbaData,
        cst.D_CBA_K: data.DCbaKData,
        cst.MAPPING: data.MappingData,
        cst.MAPPING_K: data.MappingKData,
        cst.UNIT: data.UnitExtensionData,
    }

    log.debug(f"Instantiate extension data '{name}'")
    try:
        return dict_data_classes[name](
            extension_name=extension_name,
            regions=regions,
            sectors=sectors,
            strategy=strategy,
            final_demand_categories=final_demand_categories,
            extension_categories=extension_categories,
        )
    except KeyError:
        raise MEDataNotAllowed(
            data_name=name,
            data_kind="extension",
            list_of_data_allowed=list(dict_data_classes.keys()),
        )
