"""
Overview
********
This module provides a factory function for creating detail-level objects
from a ``DetailLevelKind``. It centralizes the mapping between detail-level
kinds and their corresponding implementations.

Contents
********
- Functions:
    - make_dl_from_kind
    - make_sectors_dl_from_path
    - make_regions_dl_from_path
    - make_final_demand_categories_dl_from_path
    - make_extension_categories_dl_from_path
    - make_dl_dict_from_path
"""

__all__ = [
    "make_dl_from_kind",
    "make_sectors_dl_from_path",
    "make_regions_dl_from_path",
    "make_final_demand_categories_dl_from_path",
    "make_extension_categories_dl_from_path",
    "make_dl_dict_from_path",
]

import os
import pandas as pd

import matmat.core.detail_level.core as dl
from matmat.utils import logging as log, constants as cst


def make_dl_from_kind(
    kind: dl.DetailLevelKind,
    df: pd.DataFrame = None,
    extension_name: str = None,
):
    """
    Create a detail-level instance based on the provided kind.

    Parameters:
        kind (DetailLevelKind):
            The detail-level kind specifying the target class to instantiate.
        df (pd.DataFrame, optional):
            Data associated with the detail level. Default is None.
        extension_name (str, optional):
            Name of the extension when ``kind`` is
            ``EXTENSION_CATEGORIES``. Default is None.

    Returns:
        AbstractDetailLevel:
            The corresponding detail-level instance.

    Raises:
        MEUnknownDetailLevelKind:
            When the kind given as input does not exist.
    """
    match kind:
        case dl.DetailLevelKind.REGIONS:
            return dl.RegionsDL(df=df)
        case dl.DetailLevelKind.SECTORS:
            return dl.SectorsDL(df=df)
        case dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES:
            return dl.FinalDemandCategoriesDL(df=df)
        case dl.DetailLevelKind.EXTENSION_CATEGORIES:
            return dl.ExtensionCategoriesDL(
                df=df,
                extension_name=extension_name,
            )
        case dl.DetailLevelKind.COMBINED:
            return dl.CombinedDetailLevel(df=df)


def make_sectors_dl_from_path(
    path: str,
    file_name: str = cst.DL_FILE,
) -> dl.SectorsDL:
    """
    Create a SectorsDL instance and load its data from a file path.

    Parameters:
        path (str):
            Path to the directory containing the detail-level file.
        file_name (str):
            Name of the detail-level file. Default is cst.DL_FILE.

    Returns:
        SectorsDL :
            A sectors detail-level instance with data loaded from the file.
    """
    log.debug(
        f"Make SectorsDL object from path {os.path.join(path, file_name)}"
    )
    dl_ = dl.SectorsDL()
    dl_.load_from_path(path=path, file_name=file_name)
    return dl_


def make_regions_dl_from_path(
    path: str, file_name: str = cst.DL_FILE
) -> dl.RegionsDL:
    """
    Create a RegionsDL instance and load its data from a file path.

    Parameters:
        path (str):
            Path to the directory containing the detail-level file.
        file_name (str):
            Name of the detail-level file. Default is cst.DL_FILE.

    Returns:
        RegionsDL :
            A regions detail-level instance with data loaded from the file.
    """
    log.debug(
        f"Make RegionsDL object from path {os.path.join(path, file_name)}"
    )
    dl_ = dl.RegionsDL()
    dl_.load_from_path(path=path, file_name=file_name)
    return dl_


def make_final_demand_categories_dl_from_path(
    path: str,
    file_name: str = cst.DL_FILE,
) -> dl.FinalDemandCategoriesDL:
    """
    Create a FinalDemandCategoriesDL instance and load its data from a file path.

    Parameters:
        path (str):
            Path to the directory containing the detail-level file.
        file_name (str):
            Name of the detail-level file. Default is cst.DL_FILE.

    Returns:
        FinalDemandCategoriesDL :
            A final-demand detail-level instance with data loaded from the file.
    """
    log.debug(
        f"Make FinalDemandCategoriesDL object from path {os.path.join(path, file_name)}"
    )
    dl_ = dl.FinalDemandCategoriesDL()
    dl_.load_from_path(path=path, file_name=file_name)
    return dl_


def make_extension_categories_dl_from_path(
    path: str,
    extension_name: str,
    file_name: str = cst.DL_FILE,
) -> dl.ExtensionCategoriesDL:
    """
    Create an ExtensionCategoriesDL instance and load its data from a file path.

    Parameters:
        path (str):
            Path to the directory containing the detail-level file.
        extension_name (str):
            Name of the extension category to instantiate.
        file_name (str):
            Name of the detail-level file. Default is cst.DL_FILE.

    Returns:
        ExtensionCategoriesDL :
            An extension-categories detail-level instance with data loaded from the file.
    """
    log.debug(
        "Make ExtensionCategoriesDL object from path "
        f"{os.path.join(path, file_name)}"
    )
    dl_ = dl.ExtensionCategoriesDL(extension_name=extension_name)
    dl_.load_from_path(path=path, file_name=file_name)
    return dl_


def make_dl_dict_from_path(
    path: str,
    file_name: str = cst.DL_FILE,
    load_regions: bool = True,
    load_sectors: bool = True,
    load_final_demand_categories: bool = True,
    load_extension_categories: bool = True,
    extension_names: list[str] = None,
) -> dict[str, dl.AbstractDetailLevel]:
    """
    Build a dictionary of detail-level instances by loading them from a file path.

    Parameters:
        path (str):
            Path to the directory containing the detail-level file.
        file_name (str):
            Name of the detail-level file to load. Default is cst.DL_FILE.
        load_regions (bool):
            True if the regions detail levels shall be loaded from the file.
        load_sectors (bool):
            True if the sectors detail levels shall be loaded from the file.
        load_final_demand_categories (bool):
            True if the final demand categories detail levels shall be loaded
            from the file.
        load_extension_categories (bool):
            True if the extension categories detail levels shall be loaded
            from the file.
            In this case, the names of the extensions to load shall be given
            in the list extension_names.
        extension_names (list[str]):
            The list of extension names. Default is None.

    Returns:
        dict[str, AbstractDetailLevel] :
            A dictionary mapping each detail-level kind to the corresponding
            loaded detail-level instance. Extension categories are stored
            in a nested dictionary.
    """

    # Initialize detail level dictionary
    dl_dict = {}

    # Build sectors detail levels
    if load_sectors:
        try:
            dl_dict[dl.DetailLevelKind.SECTORS.value] = (
                make_sectors_dl_from_path(
                    path=path,
                    file_name=file_name,
                )
            )
        except (FileNotFoundError, ValueError):
            log.error("Can't load sectors detail levels")

    # Build regions detail levels
    if load_regions:
        try:
            dl_dict[dl.DetailLevelKind.REGIONS.value] = (
                make_regions_dl_from_path(
                    path=path,
                    file_name=file_name,
                )
            )
        except (FileNotFoundError, ValueError):
            log.error("Can't load regions detail levels")

    # Build final demand categories detail levels
    if load_final_demand_categories:
        try:
            dl_dict[dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value] = (
                make_final_demand_categories_dl_from_path(
                    path=path, file_name=file_name
                )
            )
        except (FileNotFoundError, ValueError):
            log.error("Can't load final demand categories detail levels")
            del dl_dict[dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value]

    # Build extension categories detail levels
    if load_extension_categories and extension_names is not None:
        dl_dict[dl.DetailLevelKind.EXTENSION_CATEGORIES.value] = {}
        for extension_name in extension_names:
            try:
                dl_dict[dl.DetailLevelKind.EXTENSION_CATEGORIES.value][
                    extension_name
                ] = make_extension_categories_dl_from_path(
                    path=path,
                    extension_name=extension_name,
                    file_name=file_name,
                )
            except (FileNotFoundError, ValueError):
                log.error(
                    "Can't load extension categories detail levels for "
                    f"extension '{extension_name}'"
                )

        if not dl_dict[dl.DetailLevelKind.EXTENSION_CATEGORIES.value]:
            del dl_dict[dl.DetailLevelKind.EXTENSION_CATEGORIES.value]

    return dl_dict
