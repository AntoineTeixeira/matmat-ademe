"""
Presentation
************
This module contains functions to instantiate and use formats objects

Content
*******
- Functions:
    - :meth:`build_build_name_from_extension`
    - :meth:`build_build_format_from_name`
"""

__all__ = ["build_name_from_extension", "build_format_from_name"]

import os

from matmat.utils.formats.core import (
    AbstractFormat,
    PickleFormat,
    CsvFormat,
    ExcelFormat,
    NullFormat,
)

import matmat.utils.logging as log
import matmat.utils.constants as cst

LIST_FORMATS_NOT_NULL = [
    PickleFormat(),
    CsvFormat(),
    ExcelFormat(),
]
LIST_FORMATS = LIST_FORMATS_NOT_NULL + [NullFormat()]


def build_name_from_extension(extension: str) -> str:
    """
    Returns the name of the format from the extension

    Example: from ".pkl", returns "pickle"

    Parameters:
        extension (str):
            The extension of the file
    Returns:
        str
    """
    for format_ in LIST_FORMATS:
        if format_.EXTENSION == extension:
            return format_.name
    log.error(f"Can't process extension '{extension}'")
    log.error(
        f"List of known extensions: {[format_.extension for format_ in LIST_FORMATS_NOT_NULL]}"
    )
    raise NotImplementedError


def build_format_from_name(name: str) -> AbstractFormat:
    """
    Returns the correct format object w.r.t. the name given:
        - pickle => PickleFormat()
        - excel => ExcelFormat()
        - csv => CsvFormat()

    Parameters:
        name (str):
            The name of the format
    Returns:
        AbstractFormat
    """
    for format_ in LIST_FORMATS:
        if format_.name == name:
            return format_
    log.error(f"Can't process format '{name}'")
    log.error(
        f"List of known formats: {[format_.name for format_ in LIST_FORMATS_NOT_NULL]}"
    )
    raise NotImplementedError


def build_format_from_path(path: str, data_name: str) -> AbstractFormat:
    """
    Returns the format w.r.t. the files matching data_name found in path,
    following this policy:
        - If a pickle file is found, returns PickleFormat()
        - Elif an Excel file is found, returns ExcelFormat()
        - Elif a CSV file is found, returns CsvFormat()
        - Else returns a NullFormat()

    Parameters:
        path (str):
            The path to the directory containing the data files
        data_name (str):
            The name of the data (used to identify the files)
    Returns:
        AbstractFormat
    """
    list_formats = []
    for elt in os.listdir(path):
        elt_path = os.path.join(path, elt)
        if not os.path.isdir(elt_path):
            elt_name = elt.split(".")[0]
            if elt_name == data_name:
                elt_extension = elt.split(".")[1]
                list_formats.append(build_name_from_extension(elt_extension))
    if list_formats:
        format_ = build_format_from_name(pick_favorite_format(list_formats))
        if len(list_formats) > 1:
            log.debug(
                f"Found {len(list_formats)} files for data {data_name}. "
                f"Pick the {format_.name} one."
            )
    else:
        format_ = NullFormat()

    return format_


def pick_favorite_format(list_formats: list) -> str:
    """
    Pick the preferred format out of a list of formats. The order of
    preference is the following:
        - pickle
        - excel
        - csv

    Parameters:
        list_formats (list):
            The list of formats to choose from
    Returns:
        str : the preferred format
    """
    # If the list contains only one format, returns this format
    if len(list_formats) == 1:
        return list_formats[0]
    # If the list has more than one format, return pickle if in the list
    if cst.FORMAT_PICKLE in list_formats:
        return cst.FORMAT_PICKLE
    # If the list has more than one format and no pickle, return excel
    if cst.FORMAT_EXCEL in list_formats:
        return cst.FORMAT_EXCEL
    # Else return csv
    return cst.FORMAT_CSV
