from matmat.core.bridge import core as bridge


def filter_ec_bridges(
    bridges: tuple[bridge.Bridge, ...], extension_name: str
) -> list[bridge.Bridge]:
    """
    Filters a list of bridges based on their extension categories and the matching
    extension name.

    Iterates through the provided tuple of bridges and evaluates whether each
    bridge is either not categorized under extension categories or belongs to
    the specified extension. The resulting subset of filtered bridges is returned
    as a list.

    Arguments:
        bridges (tuple[bridge.Bridge, ...]):
            A tuple containing Bridge objects to be filtered.
        extension_name (str):
            The specific extension name to filter bridges by.

    Returns:
        list[bridge.Bridge]: A list of Bridge objects satisfying the filter
        conditions.
    """
    return [
        bridge_
        for bridge_ in bridges
        if (
            not bridge_.is_extension_categories_bridge()
            or (bridge_.extension_name == extension_name)
        )
    ]
