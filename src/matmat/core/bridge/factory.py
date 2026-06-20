"""
Overview
********
This module provides convenience factory functions to create ``Bridge``
instances for specific ``DetailLevelKind`` values. Each function returns a
bridge preconfigured for a given type of detail level.

Contents
********
- Functions:
    - make_sectors_bridge
    - make_regions_bridge
    - make_final_demand_categories_bridge
    - make_extension_categories_bridge
    - make_make_bridge_dict_from_path
"""

__all__ = [
    "make_sectors_bridge",
    "make_regions_bridge",
    "make_final_demand_categories_bridge",
    "make_extension_categories_bridge",
    "make_bridge_dict_from_path",
]

import os.path

import matmat.core.bridge.core as bridge
from matmat.core.detail_level.core import DetailLevelKind
from matmat.utils.errors import MEIncorrectArguments
from matmat.utils import logging as log, constants as cst


def _get_bridge_class(direct: bool, multi: bool) -> type:
    """
    If direct, returns DirectBridge class

    If multi, returns MultiBridge class

    Otherwise, returns Bridge class

    Raises:
        MEIncorrectArguments:
            If multi and direct are both set to True
    """

    # Multi-direct bridge are not implemented
    if multi and direct:
        raise MEIncorrectArguments(
            msg="Can't instantiate a direct multi bridge. Choose either direct or multi."
        )

    if direct:
        return bridge.DirectBridge

    if multi:
        return bridge.MultiBridge

    return bridge.Bridge


def make_sectors_bridge(
    rows_level_names: list[str] = None,
    columns_level_names: list[str] = None,
    direct: bool = False,
    multi: bool = False,
    multi_bridge_filter_level: str = None,
) -> bridge.Bridge | bridge.DirectBridge | bridge.MultiBridge:
    """
    Make a bridge between sectors detail levels

    Parameters:
        rows_level_names (list[str]):
            The names of the rows levels
        columns_level_names (list[str]):
            The names of the columns levels
        direct (bool):
            True to make a direct bridge
        multi (bool):
            True to make a multi bridge
        multi_bridge_filter_level (str):
            The name of the level on which the multi-bridge is structured (and
            which permits to retrieve specific bridges).

    Notes:
        direct and multi can't be both True
    """
    if multi:
        return _get_bridge_class(direct, multi)(
            kind=DetailLevelKind.SECTORS,
            rows_level_names=rows_level_names,
            columns_level_names=columns_level_names,
            filter_level=multi_bridge_filter_level,
        )
    return _get_bridge_class(direct, multi)(
        kind=DetailLevelKind.SECTORS,
        rows_level_names=rows_level_names,
        columns_level_names=columns_level_names,
    )


def make_regions_bridge(
    rows_level_names: list[str] = None,
    columns_level_names: list[str] = None,
    direct: bool = False,
    multi: bool = False,
    multi_bridge_filter_level: str = None,
) -> bridge.Bridge | bridge.DirectBridge | bridge.MultiBridge:
    """
    Make a bridge between regions detail levels

    Parameters:
        rows_level_names (list[str]):
            The names of the rows levels
        columns_level_names (list[str]):
            The names of the columns levels
        direct (bool):
            True to make a direct bridge
        multi (bool):
            True to make a multi bridge
        multi_bridge_filter_level (str):
            The name of the level on which the multi-bridge is structured (and
            which permits to retrieve specific bridges).

    Notes:
        direct and multi can't be both True
    """
    if multi:
        return _get_bridge_class(direct, multi)(
            kind=DetailLevelKind.REGIONS,
            rows_level_names=rows_level_names,
            columns_level_names=columns_level_names,
            filter_level=multi_bridge_filter_level,
        )
    return _get_bridge_class(direct, multi)(
        kind=DetailLevelKind.REGIONS,
        rows_level_names=rows_level_names,
        columns_level_names=columns_level_names,
    )


def make_final_demand_categories_bridge(
    rows_level_names: list[str] = None,
    columns_level_names: list[str] = None,
    direct: bool = False,
    multi: bool = False,
    multi_bridge_filter_level: str = None,
) -> bridge.Bridge | bridge.DirectBridge | bridge.MultiBridge:
    """
    Make a bridge between final demand categories detail levels

    Parameters:
        rows_level_names (list[str]):
            The names of the rows levels
        columns_level_names (list[str]):
            The names of the columns levels
        direct (bool):
            True to make a direct bridge
        multi (bool):
            True to make a multi bridge
        multi_bridge_filter_level (str):
            The name of the level on which the multi-bridge is structured (and
            which permits to retrieve specific bridges).

    Notes:
        direct and multi can't be both True
    """
    if multi:
        return _get_bridge_class(direct, multi)(
            kind=DetailLevelKind.FINAL_DEMAND_CATEGORIES,
            rows_level_names=rows_level_names,
            columns_level_names=columns_level_names,
            filter_level=multi_bridge_filter_level,
        )
    return _get_bridge_class(direct, multi)(
        kind=DetailLevelKind.FINAL_DEMAND_CATEGORIES,
        rows_level_names=rows_level_names,
        columns_level_names=columns_level_names,
    )


def make_extension_categories_bridge(
    rows_level_names: list[str] = None,
    columns_level_names: list[str] = None,
    extension_name: str | None = None,
    direct: bool = False,
    multi: bool = False,
    multi_bridge_filter_level: str = None,
) -> bridge.Bridge | bridge.DirectBridge | bridge.MultiBridge:
    """
    Make a bridge between extension categories detail levels

    Parameters:
        rows_level_names (list[str]):
            The names of the rows levels
        columns_level_names (list[str]):
            The names of the columns levels
        extension_name (str):
            The name of the extension (used for the sheet name)
        direct (bool):
            True to make a direct bridge
        multi (bool):
            True to make a multi bridge
        multi_bridge_filter_level (str):
            The name of the level on which the multi-bridge is structured (and
            which permits to retrieve specific bridges).

    Notes:
        direct and multi can't be both True
    """
    if multi:
        return _get_bridge_class(direct, multi)(
            kind=DetailLevelKind.EXTENSION_CATEGORIES,
            rows_level_names=rows_level_names,
            columns_level_names=columns_level_names,
            filter_level=multi_bridge_filter_level,
        )
    return _get_bridge_class(direct, multi)(
        kind=DetailLevelKind.EXTENSION_CATEGORIES,
        rows_level_names=rows_level_names,
        columns_level_names=columns_level_names,
        sheet_name=extension_name,
    )


def make_bridge_dict_from_path(
    path: str,
    file_name: str = cst.BRIDGES_FILE,
    load_regions: bool = True,
    load_sectors: bool = True,
    load_final_demand_categories: bool = True,
    load_extension_categories: bool = True,
    extension_names: list = None,
    sectors_is_direct: bool = False,
    sectors_is_multi: bool = False,
    regions_is_direct: bool = False,
    regions_is_multi: bool = False,
    final_demand_categories_is_direct: bool = False,
    final_demand_categories_is_multi: bool = False,
    extension_categories_is_direct: dict[str, bool] = False,
    extension_categories_is_multi: dict[str, bool] = False,
    multi_bridge_filter_level: str = None,
) -> dict[str, bridge.Bridge]:
    """
    Build a dictionary of bridges by loading them from a filesystem path.

    Parameters:
        path (str):
            Path to the bridge file or to the directory from which
            bridge data will be loaded.
        file_name (str):
            Name of the bridge file to load. Default is cst.BRIDGES_FILE.
        load_regions (bool):
            True if the regions bridge shall be loaded from the file.
        load_sectors (bool):
            True if the sectors bridge shall be loaded from the file.
        load_final_demand_categories (bool):
            True if the final demand categories bridge shall be loaded
            from the file.
        load_extension_categories (bool):
            True if the extension categories bridge shall be loaded
            from the file.
            In this case, the names of the extensions to load shall be given
            in the list extension_names.
        extension_names (list[str]):
            Names of the extensions represented in the extensions categories bridges
            (Set to None or empty list if no extensions)
        sectors_is_direct (bool):
            Whether the sectors bridge is direct (default is False).
        sectors_is_multi (bool):
            Whether the sectors bridge is multi (default is False).
        regions_is_direct (bool):
            Whether the regions bridge is direct (default is False).
        regions_is_multi (bool):
            Whether the regions bridge is multi (default is False).
        final_demand_categories_is_direct (bool):
            Whether the final-demand categories bridge is direct (default is False).
        final_demand_categories_is_multi (bool):
            Whether the final-demand categories bridge is multi (default is False).
        extension_categories_is_direct (dict[str, bool]):
            Mapping of extension names to their "direct" boolean flag (default is False).
        extension_categories_is_multi (dict[str, bool]):
            Mapping of extension names to their "multi" boolean flag (default is False).
        multi_bridge_filter_level (str):
            The name of the level on which the multi-bridge is structured (and
            which permits to retrieve specific bridges).

    Returns:
        dict[str, Bridge] :
            A dictionary mapping detail-level kinds to their corresponding bridge
            instances. Extension categories are stored in a nested dictionary.

    Raises:
        MEIncorrectArguments:
            Raised when rows, columns, and direct-flag mappings for extension categories
            do not share the same keys.
    """
    bridge_dict = {}

    # Build sectors bridge
    if load_sectors:
        try:
            sectors_bridge = make_sectors_bridge(
                direct=sectors_is_direct,
                multi=sectors_is_multi,
                multi_bridge_filter_level=multi_bridge_filter_level,
            )
            sectors_bridge.load_from_path(path=path, file_name=file_name)
            bridge_dict[DetailLevelKind.SECTORS.value] = sectors_bridge
        except (FileNotFoundError, ValueError):
            log.error("Can't load sectors bridge")

    # Build regions bridge
    if load_regions:
        try:
            regions_bridge = make_regions_bridge(
                direct=regions_is_direct,
                multi=regions_is_multi,
                multi_bridge_filter_level=multi_bridge_filter_level,
            )
            regions_bridge.load_from_path(path=path, file_name=file_name)
            bridge_dict[DetailLevelKind.REGIONS.value] = regions_bridge
        except (FileNotFoundError, ValueError):
            log.error("Can't load regions bridge")

    # Build final demand categories bridge
    if load_final_demand_categories:
        try:
            fdc_bridge = make_final_demand_categories_bridge(
                direct=final_demand_categories_is_direct,
                multi=final_demand_categories_is_multi,
                multi_bridge_filter_level=multi_bridge_filter_level,
            )
            fdc_bridge.load_from_path(path=path, file_name=file_name)
            bridge_dict[DetailLevelKind.FINAL_DEMAND_CATEGORIES.value] = (
                fdc_bridge
            )
        except (FileNotFoundError, ValueError):
            log.error("Can't load final demand categories bridge")

    # Build extension categories bridge(s)
    if (
        load_extension_categories
        and extension_names is not None
        and len(extension_names) > 0
    ):

        # Check consistency of parameters first
        try:
            if (
                extension_categories_is_direct.keys() != extension_names
                or extension_categories_is_multi.keys() != extension_names
            ):
                log.error(
                    "Parameters 'extension_categories_is_direct' and "
                    "'extension_categories_is_multi' shall be consistent with"
                    f"the extension names given: {extension_names}."
                    f" direct => {extension_categories_is_direct.keys()}"
                    f" multi => {extension_categories_is_multi.keys()}"
                    " Please check consistency."
                )
                raise MEIncorrectArguments(
                    msg="Extension categories parameters shall be consistent"
                )
        except AttributeError:
            log.debug(
                "No extension categories level names given, hence no "
                "consistency check performed."
            )

        # Add extension categories entry
        bridge_dict[DetailLevelKind.EXTENSION_CATEGORIES.value] = {}

        # Loop on extension names
        for extension_name in extension_names:

            # Get level names if given
            try:
                ec_is_direct = extension_categories_is_direct[extension_name]
                ec_is_multi = extension_categories_is_multi[extension_name]
            # Otherwise use default values
            except (TypeError, KeyError):
                ec_is_direct = False
                ec_is_multi = False

            try:
                ec_bridge = make_extension_categories_bridge(
                    extension_name=extension_name,
                    direct=ec_is_direct,
                    multi=ec_is_multi,
                    multi_bridge_filter_level=multi_bridge_filter_level,
                )
                ec_bridge.load_from_path(path=path, file_name=file_name)
                bridge_dict[DetailLevelKind.EXTENSION_CATEGORIES.value][
                    extension_name
                ] = ec_bridge
            except (FileNotFoundError, ValueError):
                log.error(
                    "Can't load extension categories bridge for extension "
                    f"'{extension_name}'"
                )

        if not bridge_dict[DetailLevelKind.EXTENSION_CATEGORIES.value]:
            del bridge_dict[DetailLevelKind.EXTENSION_CATEGORIES.value]

    return bridge_dict
