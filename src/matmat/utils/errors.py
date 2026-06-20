"""
Presentation
************
This module contains MatMat custom exceptions.

Content
*******
- Classes:
    - :class:`MENotEnoughData`
    - :class:`MEExtensionNotFound`
    - :class:`MEExtensionAlreadyExisting`
    - :class:`MEIncorrectArguments`
    - :class:`MEMissingKey`
    - :class:`MEDataNotAllowed`
    - :class:`MEShockExtensionInconsistency`
    - :class:`MEDataNotSuitableForWorkflow`
    - :class:`MEAggMatrixInconsistentWithUnitVector`
    - :class:`MEAggMatrixDimensionsInconsistent`
    - :class:`MEIncorrectSettings`
    - :class:`MEUnknownStrategy`
    - :class:`MEIncorrectDataFrameStructure`
    - :class:`MEUnknownDetailLevelKind`
    - :class:`MEIncompatibleDetailLevelKind`
    - :class:`MEInconsistentDetailLevels`
    - :class:`MEIncorrectLevelNames`
    - :class:`MEDetailLevelMissing`
    - :class:`MEMissingSheet`
    - :class:`MEIncorrectSectors`
    - :class:`MEIncorrectRegions`
    - :class:`MEIncorrectFinalDemandCategories`
    - :class:`MEIncorrectExtensionCategories`
    - :class:`MEIncorrectBridge`
    - :class:`MEIncompatibleShock`
    - :class:`MESystemNotBalanced`
    - :class:`MEAggregationOperationNotPossible`
    - :class:`MEUnknownConfigurationParameter`
    - :class:`MEMissingInputData`
    - :class:`MEMissingProcessedData`
    - :class:`MEMissingCalculatedData`
    - :class:`MEMissingPostProcessedData`
    - :class:`MEUndefinedAggregationLevel`
    - :class:`MEExcelFileNotReadable`
    - :class:`MEMissingInvestmentData'
"""

__all__ = [
    "file_not_found_error_handler",
    "file_not_found_error_ignore",
    "MENotEnoughData",
    "MEExtensionNotFound",
    "MEExtensionAlreadyExisting",
    "MEIncorrectArguments",
    "MEMissingKey",
    "MEUndefinedPath",
    "MEDataNotAllowed",
    "MEShockExtensionInconsistency",
    "MEDataNotSuitableForWorkflow",
    "MEAggMatrixInconsistentWithUnitVector",
    "MEAggMatrixDimensionsInconsistent",
    "MEIncorrectSettings",
    "MEUnknownStrategy",
    "MEIncorrectDataFrameStructure",
    "MEUnknownDetailLevelKind",
    "MEIncompatibleDetailLevelKind",
    "MEInconsistentDetailLevels",
    "MEIncorrectLevelNames",
    "MEDetailLevelMissing",
    "MEMissingSheet",
    "MEIncorrectSectors",
    "MEIncorrectRegions",
    "MEIncorrectFinalDemandCategories",
    "MEIncorrectExtensionCategories",
    "MEIncorrectBridge",
    "MEIncompatibleShock",
    "MESystemNotBalanced",
    "MEAggregationOperationNotPossible",
    "MEUnknownConfigurationParameter",
    "MEMissingInputData",
    "MEMissingProcessedData",
    "MEMissingCalculatedData",
    "MEMissingPostProcessedData",
    "MEUndefinedAggregationLevel",
    "MEExcelFileNotReadable",
    "MEMissingInvestmentData",
]

import sys
import os
import pandas as pd

import matmat.utils.logging as log


def file_not_found_error_handler(func):
    """
    This decorator handles a `FileNotFoundError` and asks the user
    if it is normal that the file does not exist. If yes, then the
    execution continues, otherwise it stops.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(e)
            answer = input("Do you want to proceed? (y/N)\n> ")
            if answer.lower() != "y":
                sys.exit(1)
            else:
                return pd.DataFrame()

    return wrapper


def file_not_found_error_ignore(func):
    """
    This decorator handles a `FileNotFoundError` continue the execution
    normally.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            log.debug(f"FileNotFoundError:{e.filename}")
            log.debug("Ignore error and continue.")

    return wrapper


def dict_structure(dict_: dict) -> str:
    """
    Returns a string representation of the dictionary structure (only keys)
    """
    def _recurse(d: dict, indent: int) -> str:
        lines = []
        for key in d:
            lines.append("  " * indent + str(key))
            if isinstance(d[key], dict):
                lines.append(_recurse(d[key], indent + 1))
        return "\n".join(lines)

    return _recurse(dict_, 0)


# ------------------------
# MatMat custom exceptions
# The name always starts with 'ME' which stands for MatMat Exception


class MENotEnoughData(Exception):
    """
    This exception is raised when not enough data are available to perform a
    specific operation.

    For example, you try to calculate the components of a system, but there
    are not enough initial data.
    """

    def __init__(self, list_of_data: list[str] | list[tuple], all_data: bool = False):
        self.list_of_data = list_of_data
        self.all_data = all_data

    def __str__(self):
        if self.all_data:
            return (
                f"Data {self.list_of_data} are required to perform calculation"
            )
        return (
            f"At least one data from {self.list_of_data} is required "
            f"to perform calculation"
        )


class MEExtensionNotFound(Exception):
    """
    This exception is raised when an extension could not be found.

    For example, you try to get an extension from an accounts object,
    but it has no extension.
    """

    def __init__(self, extension_name: str):
        self.extension_name = extension_name

    def __str__(self):
        return f"Extension '{self.extension_name}' could not be found"


class MEExtensionAlreadyExisting(Exception):
    """
    This exception is raised when you try to add an extension which already
    exists.

    For example, you try to add an extension with a name that is already taken.
    """

    def __init__(self, extension_name: str):
        self.extension_name = extension_name

    def __str__(self):
        return f"Extension '{self.extension_name}' already exists"


class MEIncorrectArguments(Exception):
    """
    This exception is raised when a function with args / kwargs arguments is
    called with unexpected arguments, or is missing required arguments.
    """

    def __init__(self, expected_args: list[str] | list[tuple[str, ...]] = None, msg: str = None):
        self.expected_args = expected_args
        self.msg = msg

    def __str__(self):
        if self.msg is not None:
            return self.msg
        if isinstance(self.expected_args, list):
            if len(self.expected_args) == 1:
                return f"Argument '{self.expected_args[0]}' is required"
            else:
                return f"Arguments {self.expected_args} are required"
        return "Incorrect arguments"


class MEMissingKey(Exception):
    """
    This exception is raised when a required key is missing from a JSON file.

    For example, you try to instantiate an extension from a JSON file,
    but this file is missing a required key.
    """

    def __init__(self, key: str, given_keys: list[str]):
        self.key = key
        self.given_keys = given_keys

    def __str__(self):
        return f"Missing required key '{self.key}' from {self.given_keys}"


class MEUndefinedPath(Exception):
    """
    This exception is raised if a path is given to perform operations on
    files, but the path does not exist.

    For example, you try to adapt data from a directory, but the directory
    does not exist.
    """

    def __init__(self, path: str):
        self.path = path

    def __str__(self):
        return f"The path '{self.path}' does not exist"


class MEDataNotAllowed(Exception):
    """
    This exception is raised if a data not allowed in an entity is added to
    this entity.

    For example, you try to define a data A (technical coefficients) in an
    extension.
    """

    def __init__(
        self, data_name: str, data_kind: str, list_of_data_allowed: list[str]
    ):
        self.data_name = data_name
        self.data_kind = data_kind
        self.list_of_data_allowed = list_of_data_allowed

    def __str__(self):
        return (
            f"'{self.data_name}' is not allowed for {self.data_kind}"
            f"\nThe data allowed are {self.list_of_data_allowed}"
        )


class MEShockExtensionInconsistency(Exception):
    """
    This exception is raised when you try to apply an extension shock to an
    extension but the two are not compatible.

    For example, they have different names.
    """

    def __init__(self, shock_name: str, extension_name: str):
        self._shock_name = shock_name
        self._extension_name = extension_name

    def __str__(self):
        return (
            f"Shock name '{self._shock_name}' is not equal "
            f"to extension name '{self._extension_name}'"
        )


class MEDataNotSuitableForWorkflow(Exception):
    """
    This exception is raised when a workflow manipulates a data
    which does not have the expected format.

    For example, you try to adapt a data with multiple regions while the
    workflow can only manage one single region.
    """

    def __init__(self, data_name: str, workflow_name: str):
        self._data_name = data_name
        self._workflow_name = workflow_name

    def __str__(self):
        return (
            f"The format of data {self._data_name} is not suitable "
            f"for the workflow {self._workflow_name}"
        )


class MEAggMatrixInconsistentWithUnitVector(Exception):
    """
    This exception is raised when the aggregation matrix is not consistent
    with the unit vector. Note that this behaviour can be allowed through
    config.ALLOW_HETEROGENEOUS_AGGREGATION.

    For example, you try to aggregate two fluxes but these two fluxes have
    different units.
    """

    def __str__(self):
        return "The aggregation matrix is not consistent with unit vector"


class MEAggMatrixDimensionsInconsistent(Exception):
    """
    This exception is raised when the dimensions of the aggregation matrix
    are inconsistent with the operation being performed.

    For example, you try to aggregate a dataframe, but the aggregation
    matrix has more columns than rows.
    """

    def __init__(self, agg_matrix_index: pd.Index, agg_matrix_columns: pd.Index):
        self._matrix_height = len(agg_matrix_index)
        self._matrix_width = len(agg_matrix_columns)

    def __str__(self):
        return (
            f"Dimensions of aggregation matrix not consistent. "
            f"Found {self._matrix_height} lines "
            f"and {self._matrix_width} columns"
        )


class MEIncorrectSettings(Exception):
    """
    This exception is raised when a parameter given in a settings file do
    not have the expected format.

    For example, you forgot the "domestic" key in the regions dictionary.
    """

    def __init__(self, name: str, setting):
        self._name = name
        self._setting = setting

    def __str__(self):
        return f"Settings {self._name} is incorrect: {self._setting}"


class MEUnknownStrategy(Exception):
    """
    This exception is raised when the strategy given in a settings file is
    not defined.

    For example, you define the strategy to "by_use" but the correct name is
    "by_input"
    """

    def __init__(self, strategy: str,
                 kind_of_strategy: str,
                 known_strategies: list = None):
        self._unknown_strategy = strategy
        self._kind_of_strategy = kind_of_strategy
        self._known_strategies = known_strategies

    def __str__(self):
        error_msg = (f"'{self._unknown_strategy}' is unknown "
                     f"as a {self._kind_of_strategy} strategy")
        if self._known_strategies is not None:
            error_msg += (f"\nThe list of known strategies are the following:"
                          f"{self._known_strategies}")
        return error_msg


class MEIncorrectDataFrameStructure(Exception):
    """
    This exception is raised when trying to initialize a dataframe from a
    file but the index or columns in the file are not the ones expected

    For example, you define the domestic regions to ["FR", "IT"] but in the
    file, there are three regions ["FR", "IT", "EN"]
    """

    def __init__(
        self,
        erroneous_index: pd.Index = None,
        expected_index: pd.Index = None,
        is_columns: bool = False,
        custom_msg: str = "",
    ):
        self._erroneous_index = erroneous_index
        self._expected_index = expected_index
        self._is_columns = is_columns
        self._custom_msg = custom_msg

    def __str__(self):
        if (
            self._expected_index is not None
            and self._erroneous_index is not None
        ):
            if self._expected_index.names != self._erroneous_index.names:
                return (f"Level names mismatch: "
                        f"Expected {self._expected_index.names}, "
                        f"found {self._erroneous_index.names} ")

            msg = "Columns" if self._is_columns else "Index"

            # Compute diff to help user
            diff = self._erroneous_index.difference(self._expected_index)
            if len(diff) == 0:
                diff = self._expected_index.difference(self._erroneous_index)

            return (
                f"{msg} is incorrect"
                f"\n>>>>>>>>>>>>> Expected:"
                f"\n{self._expected_index}"
                f"\n>>>>>>>>>>> but found:"
                f"\n{self._erroneous_index}"
                f"\n>>>>>>>>>>> Difference is located at:"
                f"\n{diff}"
            )
        return self._custom_msg


class MEUnknownDetailLevelKind(Exception):
    """
    This exception is raised when using an undefined detail level kind
    """

    def __init__(self, kind: str):
        self._kind = kind

    def __str__(self):
        return f"Unknown detail level kind: {self._kind}"


class MEIncompatibleDetailLevelKind(Exception):
    """
    This exception is raised when trying to build a bridge between
    two different detail level kinds
    """
    def __init__(self, rows_kind: str, columns_kind: str):
        self._rows_kind = rows_kind
        self._columns_kind = columns_kind

    def __str__(self):
        return f"Kinds '{self._rows_kind}' and '{self._columns_kind}' are incompatible"


class MEInconsistentDetailLevels(Exception):
    """
    This exception is raised when one tries to assemble two entities
    together, and they have inconsistent detail levels

    For example:
        - trying to add an extension to an accounts but the extension
          have different final demand categories than the system
        - trying to shock a system with a system shock, but they have
          different sectors detail levels
    """
    def __init__(self, dl_kind: str, dl_1: pd.DataFrame, dl_2: pd.DataFrame):
        self._dl_kind = dl_kind
        self._dl_1 = dl_1
        self._dl_2 = dl_2

    def __str__(self) -> str:
        try:
            diff = self._dl_1.compare(self._dl_2)
        except ValueError:
            # DataFrames have different lengths or indices
            idx_1 = pd.MultiIndex.from_frame(self._dl_1)
            idx_2 = pd.MultiIndex.from_frame(self._dl_2)
            only_in_1 = idx_1.difference(idx_2).to_frame(index=False)
            only_in_2 = idx_2.difference(idx_1).to_frame(index=False)

            parts = []
            if not only_in_1.empty:
                parts.append(f"Only in first:\n{only_in_1}")
            if not only_in_2.empty:
                parts.append(f"Only in second:\n{only_in_2}")

            diff_str = "\n".join(parts) if parts else ("No differences found "
                                                       "(possible column mismatch)")
            return (f"Inconsistent '{self._dl_kind}' detail levels"
                    f"\nDifference is located at:\n{diff_str}")
        except Exception as e:
            return (f"Inconsistent '{self._dl_kind}' detail levels"
                    f"\n(Could not compute diff: {e})")

        return (f"Inconsistent '{self._dl_kind}' detail levels"
                f"\nDifference is located at:\n{diff}")


class MEIncorrectLevelNames(Exception):
    """
    This exception is raised when a bridge matrix does not have
    the expected level names
    """
    def __init__(
         self,
         expected_level_names: list[str] = None,
         found_level_names: list[str] = None,
         msg: str = None
    ):
        self._expected_level_names = expected_level_names
        self._found_level_names = found_level_names
        self._msg = msg

    def __str__(self):
        if self._expected_level_names and self._found_level_names:
            return (f"Expected level names: {self._expected_level_names}, "
                    f"found level names: {self._found_level_names}")
        return self._msg


class MEDetailLevelMissing(Exception):
    """
    This exception is raised when a detail level is required but is
    missing or empty
    """
    def __init__(self, dl_kind: str):
        self._dl_kind = dl_kind

    def __str__(self):
        return f"Detail level {self._dl_kind} is missing or empty"


class MEMissingSheet(Exception):
    """
    This exception is raised when trying to read a specific sheet but
    it does not exist
    """
    def __init__(self, file_path: str, sheet_name: str, error_msg: str = None):
        self._file_path = file_path
        self._sheet_name = sheet_name
        self._error_msg = error_msg

    def __str__(self):
        msg = (f"Sheet {self._sheet_name} does not exist "
                f"in file '{os.path.basename(self._file_path)}'")
        if self._error_msg is not None:
            msg += f"\n{self._error_msg}"
        return msg


class MEIncorrectSectors(Exception):
    """
    This exception is raised when there is a problem with sectors detail
    levels
    """
    def __init__(self, sectors: pd.DataFrame, error_msg: str):
        self._sectors = sectors
        self._error_msg = error_msg

    def __str__(self):
        return (f"{self._error_msg}"
                f"\nIncorrect sectors:"
                f"\n{self._sectors}")


class MEIncorrectRegions(Exception):
    """
    This exception is raised when there is a problem with regions detail
    levels
    """
    def __init__(self, regions: pd.DataFrame, error_msg: str):
        self._regions = regions
        self._error_msg = error_msg

    def __str__(self):
        return (f"{self._error_msg}"
                f"\nIncorrect regions:"
                f"\n{self._regions}")


class MEIncorrectFinalDemandCategories(Exception):
    """
    This exception is raised when the final demand categories given do not
    have the expected format.
    """

    def __init__(self, categories: pd.DataFrame):
        self._categories = categories

    def __str__(self):
        return f"Final demand categories are incorrect: {self._categories}"


class MEIncorrectExtensionCategories(Exception):
    """
    This exception is raised when the extension categories given do not
    have the expected format.

    For example, two columns were expected and only one found
    """
    def __init__(self, expected_levels: list[str], found_levels: list[str]):
        self._expected_levels = expected_levels
        self._found_levels = found_levels

    def __str__(self):
        return (f"Extension categories don't have the expected format."
                f"Expected level names {self._expected_levels}, found {self._found_levels}")

class MEIncorrectBridge(Exception):
    """
    This exception is raised when a bridge matrix is incorrect

    For example, it contains values other than binary values
    """
    def __init__(self, bridge_kind: str, msg: str):
        self._bridge_kind = bridge_kind
        self._msg = msg

    def __str__(self):
        return f"{self._bridge_kind} bridge is incorrect: {self._msg}"


class MEIncompatibleShock(Exception):
    """
    This exception is raised when we try to apply a shock to a system or an
    extension but the shock cannot be applied.

    For example, the aggregation level is different in the shock than in the
    system.
    """


class MESystemNotBalanced(Exception):
    """
    This exception is raised when a system is not balanced and the
    configuration constant config.STOP_IF_SYSTEM_IS_NOT_BALANCED is
    set to True.
    """
    def __str__(self):
        return "The system is not balanced"


class MEAggregationOperationNotPossible(Exception):
    """
    This exception is raised when the aggregation operation
    required is not compatible with the data nature.

    For example, we try to aggregate a coefficient, or we try to
    disaggregate a flux.
    """
    def __init__(self, operation: str, nature: str):
        self._operation = operation
        self._nature = nature

    def __str__(self):
        return f"{self._operation} is not possible for a {self._nature}"


class MEUnknownConfigurationParameter(Exception):
    """
    This exception is raised when trying to set the value of a configuration
    parameter which is not defined.

    For example, we try to set the value of 'system_calcul_strategy' in a
    dataset but only the configuration parameter 'extension_calcul_strategy'
    is defined.
    """
    def __init__(self, name: str, list_of_known_params: list = None):
        self._name = name
        self._list_of_known_params = list_of_known_params if (
                list_of_known_params is not None) else []

    def __str__(self):
        return (f"Unknown configuration parameter '{self._name}'."
                f" The known parameters are: {self._list_of_known_params}")


class MEMissingData(Exception):
    """
    Base class for missing data exceptions.
    """
    def __init__(self, data_name: str, available_data: dict = None):
        self._data_name = data_name
        self._available_data = available_data if (
                available_data is not None) else {}

class MEMissingInputData(MEMissingData):
    """
    This exception is raised when trying to retrieve an input data in a
    process class, but the data has not been defined yet.
    """
    def __str__(self):
        if len(self._available_data) > 0:
            details = (f"The available input data are: "
                       f"{dict_structure(self._available_data)}")
        else:
            details = ""
        return (f"Data {self._data_name} is required but was not found in "
                f"input data. {details}")


class MEMissingProcessedData(MEMissingData):
    """
    This exception is raised when trying to retrieve a processed data in an
    process class, but the data has not been defined yet.
    """
    def __str__(self):
        if len(self._available_data) > 0:
            details = (f"The available processed data are: "
                       f"{dict_structure(self._available_data)}")
        else:
            details = ""
        return (f"Data {self._data_name} is required but was not found in "
                f"processed data. {details}")

class MEMissingCalculatedData(MEMissingData):
    """
    This exception is raised when trying to retrieve a calculated data in a
    process class, but the data has not been defined yet.
    """
    def __str__(self):
        if len(self._available_data) > 0:
            details = (f"The available calculated data are: "
                       f"{dict_structure(self._available_data)}")
        else:
            details = ""
        return (f"Data {self._data_name} is required but was not found in "
                f"calculated data. {details}")

class MEMissingPostProcessedData(MEMissingData):
    """
    This exception is raised when trying to retrieve a post-processed data in a
    process class, but the data has not been defined yet.
    """
    def __str__(self):
        if len(self._available_data) > 0:
            details = (f"The available post-processed data are: "
                       f"{dict_structure(self._available_data)}")
        else:
            details = ""
        return (f"Data {self._data_name} is required but was not found in "
                f"post-processed data. {details}")


class MEUndefinedAggregationLevel(Exception):

    def __init__(self, agg_level: str, kind: str, known_levels: list):
        self._agg_level = agg_level
        self._kind = kind
        self._known_levels = known_levels

    def __str__(self):
        return (f"Undefined {self._kind} aggregation "
                f"level '{self._agg_level}'. "
                f"The defined levels are: {self._known_levels}")


class MEExcelFileNotReadable(Exception):

    def __init__(self, file: str, msg: str):
        self._file = file
        self._msg = msg

    def __str__(self):
        return (f"The Excel file {self._file} can't be read."
                f"{self._msg}")


class MEMissingInvestmentData(Exception):

    def __init__(self, available_data: pd.Index):
        self._available_data = available_data

    def __str__(self):
        return (f"No investment data found. The available data are: "
                f"{self._available_data}")
