"""
Presentation
************
This module is the extension shock data factory. It provides an interface to
instantiate extension shock data.

Content
*******
- Functions:
    - :meth:`make_data`
"""

__all__ = ["make_data"]

from matmat.core.detail_level import core as dl
import matmat.core.shocks.extension.data.core as data
from matmat.utils import constants as cst, logging as log
from matmat.utils.errors import MEDataNotAllowed


def make_data(
    name: str,
    extension_name: str,
    regions: dl.RegionsDL,
    sectors: dl.SectorsDL,
    final_demand_categories: dl.FinalDemandCategoriesDL,
    extension_categories: dl.ExtensionCategoriesDL,
) -> data.AbstractExtensionShockData:
    """
    Instantiate an extension shock data w.r.t. the data name

    Parameters:
        name (str):
            The name of the data
        extension_name (str):
            The name of the extension
        regions (dl.RegionsDL):
            The regions represented in the data
        sectors (dl.SectorsDL):
            The sectors represented in the data
        final_demand_categories (pdl.FinalDemandCategoriesDL):
            The categories and subcategories of the final demand
        extension_categories (dl.ExtensionCategoriesDL):
            The categories represented in the extension
    Returns:
        AbstractExtensionData : The instantiated extension data
    Raises:
        MEDataNotAllowed:
            If the name of the data is not an extension data
    """
    # Dictionary matching names and classes
    dict_data_classes = {
        cst.D_S_X_DOM: data.SxDomShockData,
        cst.D_S_Y: data.SyShockData,
        cst.D_S_Z: data.SzShockData,
        cst.D_M_ROW: data.MRoWShockData,
    }
    log.debug(f"Instantiate shock data '{name}'")
    try:
        return dict_data_classes[name](
            extension_name=extension_name,
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            extension_categories=extension_categories,
        )
    except KeyError:
        raise MEDataNotAllowed(
            data_name=name,
            data_kind="extension shock",
            list_of_data_allowed=list(dict_data_classes.keys()),
        )
