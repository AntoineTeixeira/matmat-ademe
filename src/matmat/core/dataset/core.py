"""
Overview
********
This module is the 'core' module of the 'core.dataset' package.
It defines the bases classes for datasets.

Contents
********
- Classes:
  - :class:`AbstractDataSet`
  - :class:`AbstractMappedDataSet`
  - :class:`AbstractListedDataSet`

"""

__all__ = [
    "AbstractMappedDataSet",
    "AbstractListedDataSet",
]

import os
from abc import ABC, abstractmethod

from matmat.core.data.core import AbstractData
from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.core.dataset.mixins import ToListMixin
from matmat.core.dataset.config import (
    DataSetConfig,
    DataSetMap,
    DataSetConversions,
)
from matmat.utils import constants as cst, logging as log
from matmat.utils.errors import (
    MEDataNotAllowed,
    MEUnknownConfigurationParameter,
    MEIncorrectArguments,
    MEInconsistentDetailLevels,
)
from matmat.utils.mixins import CopyMixin


class AbstractDataSet(ABC, ToListMixin, CopyMixin):
    """
    Abstract class representing a set of data. It implements methods which
    permit to manipulate the data contained in the set.

    Attributes
    ----------
    _regions : dl.RegionsDL
        Regions detail levels
    _sectors : dl.SectorsDL
        Sectors detail levels
    _final_demand_categories : dl.FinalDemandCategoriesDL
        Final demand categories detail levels
    """

    def __init__(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
    ):
        # Regions are required
        if regions is None:
            raise MEIncorrectArguments(
                msg="Parameter 'regions' is required to build the dataset"
            )

        # Sectors are required
        if sectors is None:
            raise MEIncorrectArguments(
                msg="Parameter 'sectors' is required to build the dataset"
            )

        # Final demand categories are required
        if final_demand_categories is None:
            raise MEIncorrectArguments(
                msg="Parameter 'final_demand_categories' is required to build the dataset"
            )

        # Persistent data
        self._regions: dl.RegionsDL = regions
        self._sectors: dl.SectorsDL = sectors
        self._final_demand_categories: dl.FinalDemandCategoriesDL = (
            final_demand_categories
        )

        # Tune dataset
        self.tune()

    @property
    def sectors(self):
        return self._sectors

    @property
    def regions(self):
        return self._regions

    @property
    def domestic_regions(self) -> list[str]:
        return self._regions.get_domestic_regions_list()

    @property
    def import_regions(self) -> list[str]:
        return self._regions.get_import_regions_list()

    @property
    def final_demand_categories(self):
        return self._final_demand_categories

    @staticmethod
    @abstractmethod
    def get_data_names():
        """
        Define the names of the data in this dataset
        """

    @abstractmethod
    def get_applicable_set(self) -> set:
        """
        Returns the current set of applicable data (represented by their
        names)
        """

    @abstractmethod
    def set_data(self, name: str):
        """
        Define the method to set a data in this dataset
        """

    @abstractmethod
    def set_null_data(self, name: str):
        """
        Define the method to set a null data in this dataset
        """

    def __iter__(self):
        """
        Iterate over all the tuples (name, data) contained in this dataset
        """
        for k, v in self.__dict__.items():
            if isinstance(v, AbstractData):
                yield k[1:] if k.startswith("_") else k, v

    @property
    def names(self):
        """
        Returns all the names of the data contained in this dataset
        """
        names = []
        for k, v in self.__dict__.items():
            if isinstance(v, AbstractData):
                names.append(k[1:] if k.startswith("_") else k)
        return names

    @property
    def data(self):
        """
        Iterate over all the data contained in this dataset
        """
        for k, v in self.__dict__.items():
            if isinstance(v, AbstractData):
                yield v

    @property
    def detail_levels(self):
        """
        Iterate over all the detail level object in this data set
        """
        for k, v in self.__dict__.items():
            if isinstance(v, dl.AbstractDetailLevel):
                yield v

    def _set_detail_level(self, detail_level: dl.AbstractDetailLevel):
        """
        Sets the detail level attribute in the dataset:
            - _sectors for SectorsDL
            - _regions for RegionsDL
            - _final_demand_categories for FinalDemandCategoriesDL

        Parameters:
            detail_level (dl.AbstractDetailLevel):
                The detail level instance used to configure the dataset
        """
        if isinstance(detail_level, dl.SectorsDL):
            self._sectors = detail_level
        elif isinstance(detail_level, dl.RegionsDL):
            self._regions = detail_level
        elif isinstance(detail_level, dl.FinalDemandCategoriesDL):
            self._final_demand_categories = detail_level

    def get_data(self, name: str):
        try:
            return getattr(self, name)
        except AttributeError:
            log.error(
                f"Data {name} does not exist in dataset {self.__class__.__name__}"
            )
            raise MEDataNotAllowed(
                data_name=name,
                data_kind=self.__class__.__name__,
                list_of_data_allowed=list(self.get_applicable_set()),
            )

    def tune(self):
        """
        Tune the data of this dataset w.r.t. current applicable data given
        through the method 'get_applicable_set'

        If a data is applicable:
            - If it was null in previous configuration, set the data using
              'set_data'
            - If it was not null, keep the previous data
        If a data is not applicable:
            - Set the data to a null data using 'set_null_data'
        """
        for data_name in self.get_data_names():
            if data_name in self.get_applicable_set():
                try:
                    prev__data = getattr(self, data_name)
                    self.set_data(name=data_name)
                    # If the data was not empty, keep the values
                    # if possible
                    if (
                        not prev__data.is_null()
                        and not prev__data.is_df_empty()
                        and type(prev__data.structure)
                        is type(getattr(self, data_name).structure)
                    ):
                        setattr(self, data_name, prev__data)
                except AttributeError:
                    self.set_data(name=data_name)
            else:
                self.set_null_data(name=data_name)

    def update_properties(self, class_: type):
        """
        Add getter and setter properties dynamically to the class class_,
        for each data in the dataset.

        Note: these properties shall be added to the class, and not the object
        """
        for data_name in self.names:
            setattr(
                class_,
                data_name,
                property(
                    fget=lambda ext, name_=data_name: getattr(
                        ext.dataset, name_
                    ),
                    fset=lambda ext, value, name_=data_name: setattr(
                        ext.dataset, name_, value
                    ),
                ),
            )

    def equals(self, other: "AbstractDataSet", excluded_data: list = None):
        """
        Compare this dataset to another one

        Parameters:
            other (AbstractDataSet):
                The dataset to compare with
            excluded_data (list):
                The names of the data to exclude from comparison
        """
        list_of_different_data = []
        for name_ in self.names:
            if excluded_data is None or name_ not in excluded_data:
                if not getattr(self, name_).equals(getattr(other, name_)):
                    list_of_different_data.append(name_)

        if len(list_of_different_data) > 0:
            log.verbose(
                f"Datasets have different data: {list_of_different_data}"
            )

        return len(list_of_different_data) == 0

    def check_detail_levels_consistency(self, other: "AbstractDataSet"):
        """
        Check the consistency of this dataset detail levels compared
        to the other dataset detail levels.

        Parameters:
            other (AbstractDataSet):
                The other dataset to compare with

        Raises:
            MEInconsistentDetailLevels : if the detail levels differ
        """
        log.verbose(f"Check consistency between datasets detail levels")
        for dl_ in self.detail_levels:
            log.verbose(f"Check consistency of '{dl_.name}' detail levels")
            dl_other = other.__getattribute__(dl_.name)
            if not dl_.equals(dl_other):
                raise MEInconsistentDetailLevels(
                    dl_kind=dl_.kind.value,
                    dl_1=dl_.df,
                    dl_2=dl_other.df,
                )

    def load_from_path(self, path: str):
        """
        Load the dataset

        Parameters:
            path (str):
                the path to the directory containing the data files
        """
        for data_ in self.data:
            data_.load_from_path(path=path)

    def save_to_path(
        self,
        path: str,
        export_format: str | list = cst.FORMAT_EXCEL,
    ):
        """
        Save the dataset

        Parameters:
            path (str):
                the path to which directory the export files shall be generated
            export_format (str | list):
                the format(s) of the exported file(s), default is *excel*
        """
        os.makedirs(path, exist_ok=True)
        for data_ in self.data:
            data_.save_to_path(path=path, export_format=export_format)
        for dl_ in self.detail_levels:
            dl_.save_to_path(path=path)

    def reset(self):
        """
        Reset all the non-null data contained in this dataset
        """
        for data_ in self.data:
            if not data_.is_null():
                data_.reset()

    def reset_coefficients(self):
        """
        Reset all the coefficients in this dataset
        """
        for data_ in self.data:
            if not data_.is_null() and data_.is_coefficient():
                data_.reset()

    def reset_fluxes(self):
        """
        Reset all the fluxes in this dataset
        """
        for data_ in self.data:
            if not data_.is_null() and data_.is_flux():
                data_.reset()

    def aggregate(self, *bridges: bridge.Bridge):
        """
        Aggregate the dataset using the provided bridges.

        Aggregates fluxes and units while resetting coefficients for each bridge.

        Parameters:
            *bridges (bridge.Bridge):
                Variable number of Bridge objects used for aggregation.
        """
        for bridge_ in bridges:
            log.verbose(
                f"Aggregate {self.__class__.__name__} over {bridge_.kind.value}"
            )
            log.verbose(f"Fluxes are aggregated, coefficients are reset")
            # Loop on data to perform aggregation
            for data_ in self.data:
                if data_.is_flux() or data_.is_unit():
                    data_.aggregate(bridge_=bridge_, reset=False)
                elif data_.is_coefficient():
                    data_.aggregate(bridge_=bridge_, reset=True)
            self._set_detail_level(detail_level=bridge_.columns_dl)

    def disaggregate(self, *bridges: bridge.Bridge):
        """
        Disaggregate the dataset using the provided bridges.

        Disaggregates coefficients and units while resetting fluxes
        for each bridge.

        Parameters:
            *bridges (bridge.Bridge):
                Variable number of Bridge objects used for disaggregation.
        """
        for bridge_ in bridges:
            log.verbose(
                f"Disaggregate {self.__class__.__name__} over {bridge_.kind.value}"
            )
            log.verbose(f"Coefficients are disaggregated, fluxes are reset")
            # Loop on data to perform disaggregation
            for data_ in self.data:
                if data_.is_coefficient() or data_.is_unit():
                    data_.disaggregate(bridge_=bridge_, reset=False)
                elif data_.is_flux():
                    data_.disaggregate(bridge_=bridge_, reset=True)
            self._set_detail_level(detail_level=bridge_.columns_dl)

    def reformat(self, *bridges: bridge.Bridge):
        """
        Reformat this dataset w.r.t. bridges given as parameters
        """
        for bridge_ in bridges:
            log.verbose(
                f"Reformat {self.__class__.__name__} over {bridge_.kind.value}"
            )
            # Loop on data to perform reformatting
            for data_ in self.data:
                if not data_.is_null():
                    data_.reformat(bridge_=bridge_)
            self._set_detail_level(detail_level=bridge_.columns_dl)

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in all applicable data objects of this dataset:
            - Null and unit data are ignored
            - Values with absolute magnitude below the threshold are removed

        Parameters:
            threshold (float):
                Values with an absolute value lower than this threshold are
                considered near zero and filtered out
            inplace (bool):
                Whether to apply the filtering directly to this dataset or
                return a filtered copy
        """

        dataset_ = self if inplace else self.copy()
        for data_ in dataset_.data:
            if not data_.is_null() and not data_.is_unit():
                data_.filter_near_zero_values(
                    threshold=threshold, inplace=True
                )

        if not inplace:
            return dataset_

    def __sub__(self, other):
        """
        Compute the difference between two datasets:
            - Only datasets of the same type can be subtracted
            - Null data are ignored
            - Each data object is subtracted by name
            - Missing or non-subtractable data are skipped

        Parameters:
            other (AbstractDataSet):
                The dataset to subtract from this one

        Returns:
            AbstractDataSet:
                A new dataset containing the element-wise difference
                between this dataset and the other
        """

        if isinstance(other, type(self)):
            result = self.copy()
            for data_ in self.data:
                if not data_.is_null():
                    try:
                        other_data = getattr(other, data_.name)
                        log.verbose(
                            f"Compute difference between both {data_.name}"
                        )
                        setattr(result, data_.name, data_ - other_data)
                    except AttributeError:
                        log.error(
                            f"Data {data_.name} not found in other dataset. Passing..."
                        )
                    except TypeError:
                        log.verbose(f"Can't subtract {data_.name}. Passing...")
            return result
        else:
            raise TypeError(
                f"Operand shall be a {type(self)}, not a {type(other)}"
            )

    def __add__(self, other):
        """
        Compute the sum between two datasets:
            - Only datasets of the same type can be summed
            - Null data are ignored
            - Each data object is summed by name
            - Missing or non-summable data are skipped

        Parameters:
            other (AbstractDataSet):
                The dataset to sum with this one

        Returns:
            AbstractDataSet:
                A new dataset containing the element-wise sum
                between this dataset and the other
        """
        if isinstance(other, type(self)):
            result = self.copy()
            for data_ in self.data:
                if not data_.is_null():
                    try:
                        other_data = getattr(other, data_.name)
                        log.verbose(f"Compute sum of both {data_.name}")
                        setattr(result, data_.name, data_ + other_data)
                    except AttributeError:
                        log.error(
                            f"Data {data_.name} not found in other dataset. Passing..."
                        )
                    except TypeError:
                        log.verbose(f"Can't sum {data_.name}. Passing...")
            return result
        else:
            raise TypeError(
                f"Operand shall be a {type(self)}, not a {type(other)}"
            )

    def __abs__(self):
        """
        Compute the absolute value of all applicable data in this dataset:
            - Null data are ignored
            - Absolute value is applied element-wise
            - Non-compatible data are skipped

        Returns:
            AbstractDataSet:
                A new dataset where each data object contains the absolute
                values of the original dataset
        """

        result = self.copy()
        for data_ in result.data:
            if not data_.is_null():
                try:
                    setattr(result, data_.name, abs(data_))
                except TypeError:
                    log.verbose(f"Can't compute abs({data_.name}). Passing...")
        return result


class AbstractMappedDataSet(AbstractDataSet, ABC):
    """
    An abstract mapped dataset is a dataset whose composition depends
    on configuration parameters.

    For each configuration parameter, a map to a set of data is defined.
    Depending on the value of the configuration parameter, the dataset
    can therefore be tuned (i.e. its composition evolves w.r.t. the
    configuration parameter).

    It is possible that there are more than one configuration parameter,
    and therefore more than one map. The applicable set of data is therefore
    the intersection between all sets.

    Note that this behaviour is managed by the 'config' object, please refer
    to :class:`DataSetConfig` for details.

    Attributes
    ----------
        conversions : DataSetConversions
            The conversions object. It defines the conversions to be executed
            when a configuration parameter changes, permitting to initialize
            the values of the new dataset from the values of the previous
            dataset. If None is given, then an object with no conversions
            is used.
        config : DataSetConfig
            The configuration object. It manages the composition of the
            dataset.
        config__<parameter_1> : str
            The configuration parameter 1
        [...]
        config__<parameter_n> : str
            The configuration parameter n
    """

    def __init__(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        conversions: DataSetConversions = None,
        **kwargs,
    ):
        # Dataset mapping
        map_kwargs = {
            k.replace(DataSetMap.PARAM_PREFIX, DataSetConfig.PARAM_PREFIX): v
            for k, v in kwargs.items()
            if k.startswith(DataSetMap.PARAM_PREFIX)
        }
        self.config: DataSetConfig = DataSetConfig(**map_kwargs)

        # Dataset configuration parameters
        for k, v in kwargs.items():
            if k.startswith(DataSetConfig.PARAM_PREFIX):
                setattr(self, k, v)

        # Dataset conversions
        self.conversions: DataSetConversions = (
            conversions if conversions is not None else DataSetConversions()
        )

        super().__init__(
            sectors=sectors,
            regions=regions,
            final_demand_categories=final_demand_categories,
        )

    @property
    def config__(self):
        return {
            k: v
            for k, v in self.__dict__.items()
            if k.startswith(DataSetConfig.PARAM_PREFIX)
        }

    def get_config(self, name: str) -> str:
        """
        Returns the value of the configuration parameter named "config__{name}"

        Raises:
            MEUnknownConfigurationParameter : if the configuration parameter
            does not exist in the dataset class
        """
        full_name = f"{DataSetConfig.PARAM_PREFIX}{name}"
        try:
            return getattr(self, full_name)
        except AttributeError as e:
            log.error(
                f"Attribute '{full_name}' does not exist in dataset "
                f"{self.__class__.__name__}"
            )
            raise MEUnknownConfigurationParameter(
                name=full_name, list_of_known_params=list(self.config__.keys())
            ) from e

    def set_config(self, name: str, value: str, tune_dataset: bool = False):
        """
        Set the value of the configuration parameter named "config__{name}"

        Parameters:
            name (str):
                The name of the configuration parameter
            value (str):
                The value of the configuration parameter
            tune_dataset (bool):
                True if the dataset shall be automatically tuned after updating
                the configuration parameter. Default to False.

        Raises:
            MEUnknownConfigurationParameter : if the configuration parameter
            does not exist in the dataset class
        """
        full_name = f"{DataSetConfig.PARAM_PREFIX}{name}"
        if not hasattr(self, full_name):
            log.error(
                f"Can't set config attribute '{full_name}' as it is not "
                f"defined in dataset {self.__class__.__name__}"
            )
            raise MEUnknownConfigurationParameter(
                name=full_name, list_of_known_params=list(self.config__.keys())
            )

        current_value = getattr(self, full_name)

        # Manage conversion and tune only if the config changes
        if current_value != value:
            setattr(self, full_name, value)

            # Activate applicable conversion
            self.conversions.activate(
                start_config=current_value,
                end_config=value,
            )

            if tune_dataset:
                self.tune()

    def tune(self):
        """
        Override tune() method in order to:
            - Save the current state of the dataset (i.e. the previous dataset)
            - Call the parent tune() method
            - Execute the conversion (if there is any pending)
              between the previous dataset to the new one
        """
        if self.conversions.is_pending():
            prev__dataset = self.copy()
            super().tune()
            self.conversions.execute(
                in_dataset=prev__dataset, out_dataset=self
            )
            del prev__dataset
        else:
            super().tune()

    def get_applicable_set(self) -> set:
        # Retrieve and returns applicable data for the current configuration
        return self.config.get_applicable_set(**self.config__)


class AbstractListedDataSet(AbstractDataSet, ABC):
    """
    An abstract listed dataset is a dataset whose composition depends on
    a list of data names.

    Attributes
    ----------
        _data_list : [str]
            The list of data composing the dataset
    """

    def __init__(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        data_list: list = None,
    ):
        # Configuration parameters
        self._data_list = (
            data_list if data_list is not None else self.get_data_names()
        )

        super().__init__(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
        )

    @property
    def data_list(self):
        return self._data_list

    @data_list.setter
    def data_list(self, value: list):
        for data_ in value:
            if data_ not in self.get_data_names():
                raise MEDataNotAllowed(
                    data_name=data_,
                    list_of_data_allowed=self.get_data_names(),
                    data_kind=self.__class__.__name__,
                )
        self._data_list = value

    def get_applicable_set(self) -> set:
        return set(self.data_list)

    def inject(
        self,
        dataset_: "AbstractListedDataSet",
        inject_zeros: bool = False,
    ):
        """
        Inject data from another dataset into this dataset.

        Parameters:
            dataset_ (AbstractListedDataSet):
                Dataset containing data to inject into this dataset
            inject_zeros (bool):
                Whether to inject zeros (default is False)
        Raises:
            MEDataNotAllowed :
                If data to inject is not defined in this dataset
        """
        for new_data in dataset_.data:
            if not new_data.is_null():
                try:
                    ref_data = getattr(self, new_data.name)
                    # If ref_data is null, then instantiate it in the dataset
                    if ref_data.is_null():
                        self.set_data(new_data.name)
                        ref_data = getattr(self, new_data.name)
                    ref_data.inject(new_data, inject_zeros=inject_zeros)

                except AttributeError:
                    log.error(
                        f"Can't process data '{new_data.name}'. "
                        f"It is not defined in {self.__class__.__name__} dataset"
                    )
                    raise MEDataNotAllowed(
                        data_name=new_data.name,
                        data_kind=self.__class__.__name__,
                        list_of_data_allowed=self.data_list,
                    )
