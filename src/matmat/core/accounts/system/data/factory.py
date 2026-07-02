"""
Presentation
************
This module is the system data factory. It provides an interface to
instantiate system data.

Content
*******
- Functions:
    - :meth:`make_data`
"""

__all__ = ["make_data"]

from matmat.core.detail_level import core as dl
import matmat.core.accounts.system.data.core as data

import matmat.utils.logging as log
import matmat.utils.constants as cst
from matmat.utils.errors import MEDataNotAllowed


def make_data(
    *,
    name: str,
    regions: dl.RegionsDL,
    sectors: dl.SectorsDL,
    final_demand_categories: dl.FinalDemandCategoriesDL,
) -> data.AbstractSystemData:
    """
    Instantiate a system data w.r.t. the data name

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
        AbstractSystemData : The instantiated system data
    Raises:
        MEDataNotAllowed:
            If the name of the data is not a system data
    """

    # Mapping between data name and data class
    dict_data_classes = {
        cst.X: data.XData,
        cst.Y: data.YData,
        cst.Z: data.ZData,
        cst.A: data.AData,
        cst.L: data.LData,
        cst.L_K: data.LKData,
        cst.K: data.KData,
        cst.Y_K: data.YKData,
        cst.UNIT: data.UnitSystemData,
    }

    log.debug(f"Instantiate system data '{name}'")
    try:
        return dict_data_classes[name](
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
        )
    except KeyError:
        raise MEDataNotAllowed(
            data_name=name,
            data_kind="system",
            list_of_data_allowed=list(dict_data_classes.keys()),
        )
