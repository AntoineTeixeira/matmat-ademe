"""
Presentation
************
This module is the system shock data factory. It provides an interface to
instantiate system shock data.

Content
*******
- Functions:
    - :meth:`make_data`
"""

__all__ = ["make_data"]

from matmat.core.detail_level import core as dl
import matmat.core.shocks.system.data.core as data
from matmat.utils.errors import MEDataNotAllowed
from matmat.utils import constants as cst, logging as log


def make_data(
    *,
    name: str,
    regions: dl.RegionsDL,
    sectors: dl.SectorsDL,
    final_demand_categories: dl.FinalDemandCategoriesDL,
) -> data.AbstractSystemShockData:
    """
    Instantiate a system shock data w.r.t. the data name

    Parameters:
        name (str):
            The name of the data
        regions (dl.RegionsDL):
            The regions represented in the data
        sectors (dl.SectorsDL):
            The sectors represented in the data
        final_demand_categories (dl.FinalDemandCategoriesDL):
            The categories and subcategories of the final demand
    Returns:
        AbstractSystemShockData : The instantiated system data
    Raises:
        MEDataNotAllowed:
            If the name of the data is not a system shock data
    """
    # Dictionary matching names and classes
    dict_data_classes = {
        cst.D_A: data.AShockData,
        cst.D_K: data.KShockData,
        cst.D_Y: data.YShockData,
        cst.D_Y_K: data.YkShockData,
        cst.D_Z: data.ZShockData,
    }
    log.debug(f"Instantiate shock data '{name}'")
    try:
        return dict_data_classes[name](
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
        )
    except KeyError:
        raise MEDataNotAllowed(
            data_name=name,
            data_kind="system shock",
            list_of_data_allowed=list(dict_data_classes.keys()),
        )
