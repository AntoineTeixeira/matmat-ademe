"""
Overview
********
This module is the 'config' module of the 'core.dataset' package.
It defines a set of classes used to manage the configuration of datasets.

Contents
********
- Classes:
  - :class:`DataSetMap`
  - :class:`DataSetConfig`
  - :class:`DataSetConversions`

"""

__all__ = [
    "DataSetMap",
    "DataSetConfig",
    "DataSetConversions",
]

from matmat.utils import logging as log
from matmat.utils.errors import (
    MEIncorrectArguments,
    MEUnknownConfigurationParameter,
)


class DataSetMap:
    """
    A dataset map

    A DataSetMap object contains a map which defines a set of data (the value
    of the dictionary)  w.r.t. a configuration parameter
    (the key of the dictionary).
    """

    PARAM_PREFIX = "map__"

    def __init__(self, map_: dict):
        self._validate_map(map_=map_)
        self.map_ = map_

    def get_data_map(self, key: str):
        try:
            return self.map_[key]
        except KeyError as e:
            log.error(f"Unknown key '{key}' in dataset map")
            log.error(f"List of known keys: {list(self.map_.keys())}")
            raise KeyError from e

    @staticmethod
    def _validate_map(map_: dict):
        if not isinstance(map_, dict):
            raise MEIncorrectArguments(
                msg="The map given shall be a dictionary. "
                f"Found {str(type(map_))}"
            )
        for k, v in map_.items():
            if not isinstance(v, set):
                raise MEIncorrectArguments(
                    msg="The values of the map shall be of type 'set'. "
                    f"Found {str(type(v))} for the key '{k}'"
                )
            if not all(isinstance(item, str) for item in v):
                raise MEIncorrectArguments(
                    msg="Each value shall be a set of strings. "
                    f"It is not the case for '{k}': {v}"
                )


class DataSetConfig:
    """
    A dataset configuration

    A DataSetConfig object contains a set of DataSetMap objects, and is
    able to tell the set of data which is currently applicable to a dataset
    w.r.t. the given configuration parameters.

    Each parameter given in the constructor shall be a DataSetMap, and the
    name of the parameter shall be the name of the associated configuration
    parameter.

    Example:
        config_ = DataSetConfig(config__system_strategy=map_system_strategy,
                                config__extension_strategy=map_extension_strategy)
    """

    PARAM_PREFIX = "config__"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, DataSetMap):
                setattr(self, k, v)
            else:
                log.error("Can't instantiate DataSetConfig")
                raise MEIncorrectArguments(
                    msg=f"{k} shall be an instance of DataSetMap, "
                    f"found {str(type(v))}"
                )

    def get_applicable_set(self, **kwargs) -> set:
        """
        Returns the set of applicable data w.r.t. the configuration parameters
        given:
            - If only one parameter is given, then returns the set of data
              defined by the map related to this parameter, at this value.
            - If more than one parameter is given, then for each parameter,
              get set of data defined by the map related to this parameter,
              at this value, and returns the intersection of all these sets.

        Parameters:
            **kwargs:
                The configuration parameters names and values
        Raises:
            MEUnknownConfigurationParameter : if there is no map related to the
                                              given configuration parameter
        """
        applicable_set = None
        for k, v in kwargs.items():
            if v is not None and isinstance(v, str):
                try:
                    state_: DataSetMap = getattr(self, k)
                    if applicable_set is None:
                        applicable_set = state_.get_data_map(key=v)
                    else:
                        applicable_set = applicable_set & state_.get_data_map(
                            key=v
                        )
                except AttributeError as e:
                    raise MEUnknownConfigurationParameter(name=k) from e
        return applicable_set


class DataSetConversions:
    """
    This class is a template class to be used to define a set of conversions
    to be executed when a dataset changes its configuration.

    Subclasses of this class shall define methods with a signature following
    this structure:
        conversion__<start_config>_to_<end_config>(in_dataset, out_dataset)

    Example:
        def conversion__standard_to_exo_invest_matrix(in_dataset, out_dataset):
            ...
    """

    FUNC_PREFIX = "conversion__"
    CONF_LINK = "_to_"

    def __init__(self):
        self._pending_conversion = None

    def activate(
        self,
        start_config: str,
        end_config: str,
    ):
        """
        Set the applicable conversion (if it exists) as the pending
        conversion

        Parameters:
            start_config (str):
                The value of the configuration parameter before the change
            end_config (str):
                The value of the configuration parameter after the change
        """
        try:
            conversion = getattr(
                self,
                f"{self.FUNC_PREFIX}{start_config}{self.CONF_LINK}{end_config}",
            )
            self._pending_conversion = conversion
            log.verbose(
                f"Found conversion '{conversion.__name__}' between '{start_config}'"
                f" and '{end_config}'"
            )
        except AttributeError:
            log.debug(
                f"No conversion defined between config '{start_config}'"
                f" and '{end_config}'. Passing..."
            )

    def execute(self, in_dataset, out_dataset):
        """
        Execute the pending conversion

        Parameters:
            in_dataset:
                The dataset before the conversion
            out_dataset:
                The dataset after the conversion
        """
        if self._pending_conversion is not None:
            log.verbose(f"Execute conversion '{self._pending_conversion.__name__}'")
            self._pending_conversion(in_dataset, out_dataset)
        self.reset()

    def reset(self):
        """
        Clear the pending conversion
        """
        self._pending_conversion = None

    def is_pending(self):
        """
        Returns True if a conversion is pending, False otherwise
        """
        return self._pending_conversion is not None
