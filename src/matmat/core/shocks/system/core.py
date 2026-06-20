"""
Presentation
************
This module is the core module of the package `shock.system`.
It defines the class :class:`SystemShock`

Content
*******
- Classes:
    - :class:`SystemShock`
"""

__all__ = ["SystemShock"]

import os

import pandas as pd

from matmat.core.bridge import core as bridge, pool as bridge_pool
from matmat.core.shocks.system.identity import SystemShockIdentity
from matmat.core.shocks.system.dataset.core import SystemShockDataSet
from matmat.core.shocks.mixins import ManualParamMixin
from matmat.core.dataset.mixins import ToListMixin, ComparisonMixin
from matmat.utils import constants as cst, logging as log, tools
from matmat.utils.mixins import CopyMixin

# pylint: disable=C0103


class SystemShock(ToListMixin, ManualParamMixin, CopyMixin, ComparisonMixin):
    """
    This class represents a shock to be applied to a system

    To instantiate a `SystemShock`, see
    :mod:`matmat.core.shocks.builder` module.

    It is composed with a set of shock data corresponding to the shockable
    data of a system.

    Attributes
    ----------
        _id : SystemShockIdentity
            The identity card
        _dataset: SystemShockDataSet
            The dataset composing the system shock
    """

    # Identity
    _id: SystemShockIdentity
    # Dataset
    _dataset: SystemShockDataSet

    @property
    def id(self) -> SystemShockIdentity:
        return self._id

    @property
    def dataset(self) -> SystemShockDataSet:
        return self._dataset

    @dataset.setter
    def dataset(self, value: SystemShockDataSet):
        self._dataset = value
        self._dataset.update_properties(class_=self.__class__)

    @property
    def regions(self):
        """
        Returns the regions detail levels from the dataset
        """
        return self._dataset.regions

    @property
    def sectors(self):
        """
        Returns the sectors detail levels from the dataset
        """
        return self._dataset.sectors

    @property
    def final_demand_categories(self):
        """
        Returns the final demand categories detail levels from the dataset
        """
        return self._dataset.final_demand_categories

    @property
    def detail_levels(self):
        """
        Returns complete system shock detail levels from the dataset
        """
        return {dl_.kind.value: dl_ for dl_ in self._dataset.detail_levels}

    def load_from_path(self, path: str):
        """
        Initialize the shock.

        This method initializes the shock data with the files found in "path"

        Parameters:
            path (str):
                the path to the directory containing the files for
                initialization
        """
        log.info(f"Load SystemShock from path {path}")
        self.dataset.load_from_path(path=path)

    def init_from_exports_growth(
        self, x_new: pd.DataFrame, x_ref: pd.DataFrame
    ):
        """
        Initialize the shock from exports variation.

        1. Compute the exports growth rates (x_new/x_ref - 1)
        2. Initialize dY matrix to 0.0
        3. Set the domestic part of exports column(s) to the previously
           computed exports growth rates

        Parameters:
            x_new (pd.DataFrame):
                the new exports matrix
            x_ref (pd.DataFrame):
                the reference exports matrix

        """

        # Initialize dY with 0.0
        self.dataset.dY.set_values(0.0)

        # Compute exports growth rates
        dom_exports = x_new.divide(x_ref) - 1

        # Sum exports growth on all regions
        total_dom_exports = dom_exports.groupby(
            level=self.dataset.sectors.get_level_names(),
            sort=False,
        ).sum()

        # Init exports vector
        exports = pd.DataFrame(
            index=self.dataset.dY.index, columns=dom_exports.columns, data=0.0
        )

        # Feed domestic part of exports vector with total_dom_exports,
        # region by region
        for region in self.dataset.domestic_regions:
            exports.loc[cst.IDX_DOMESTIC, region] = total_dom_exports.values

        tools.clean_dataframe(exports)

        # Assign values to dY
        self.dataset.dY.set_exports(exports)

    def save_to_path(
        self,
        path: str,
        export_format: str | list = cst.FORMAT_EXCEL,
    ):
        """
        Save the shock

        Parameters:
            path (str):
                the path to which directory the export files shall be generated
            export_format (str | list):
                the format(s) of the exported file, default is *excel*
        """
        log.info(f"Save system shock with format(s) {export_format}")
        os.makedirs(path, exist_ok=True)
        self.dataset.save_to_path(path=path, export_format=export_format)
        self.id.to_json_file(
            file_name=cst.FILE_INFO,
            folder_path=path,
        )

    def aggregate(self, *bridges: bridge.Bridge):
        """
        Aggregate the data of this system shock w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.error("The aggregation of a system shock is not yet implemented")
        raise NotImplementedError

    def disaggregate(self, *bridges: bridge.Bridge):
        """
        Disaggregate the data of this system shock w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info(f"Disaggregate system shock")
        with bridge_pool.pool.context():
            self.dataset.disaggregate(*bridges)

    def reformat(self, *bridges: bridge.Bridge):
        """
        Reformat the data of this system shock w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info(f"Reformat system shock")
        with bridge_pool.pool.context():
            self.dataset.reformat(*bridges)

    def inject_shock(self, shock: "SystemShock", inject_zeros: bool = False):
        """
        This method permits to concatenate shocks by injecting the values
        of another shock into this shock.

        Parameters:
            shock (SystemShock):
                The shock to inject into this shock
            inject_zeros (bool):
                True if the zeros shall be injected, otherwise they are
                replaced by NaN. (Default to False)
        """
        # Loop on the non-null data of the shock to inject
        for data_name in shock.dataset.list_data():
            data_to_inject = getattr(shock.dataset, data_name)
            if not data_to_inject.is_df_empty():
                data_ref = getattr(self.dataset, data_name)
                # If the data is null in this shock, then replace it by the
                # data to inject
                if data_ref.is_null():
                    setattr(self.dataset, data_name, data_to_inject)
                # Otherwise update the dataframe
                else:
                    data_ref.inject_dataframe(
                        df=data_to_inject.df, inject_zeros=inject_zeros
                    )

    def equals(self, other: "SystemShock"):
        """
        Tell if this system shock equals other

        Returns True if the following attributes are identical:
            - dA, dY, dY_k, dK, dZ, imp_dom_ratio
        """
        log.info("Compare system shocks")
        is_dataset_equal = self.dataset.equals(other.dataset)

        are_equal = is_dataset_equal

        if are_equal:
            log.info("System shocks are equal")

        return are_equal

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in this system shock object:
            - Delegates filtering to the underlying dataset
            - Values below the threshold are set to zero
            - Operation can be applied in place or return a filtered copy

        Parameters:
            threshold (float):
                Values with an absolute magnitude below this threshold are
                considered near zero
            inplace (bool):
                Whether to apply the filtering directly to this system shock
                object or return a filtered copy

        Returns:
            SystemShock:
                A filtered system shock object when ``inplace`` is False
        """

        result = self if inplace else self.copy()
        result.dataset.filter_near_zero_values(
            threshold=threshold,
            inplace=True,
        )

        if not inplace:
            return result

    def __sub__(self, other):
        """
        Compute the difference between two system shock objects:
            - Only system shocks of the same type can be subtracted
            - Subtraction is delegated to the underlying datasets

        Parameters:
            other (SystemShock):
                The system shock object to subtract from this one

        Returns:
            SystemShock:
                A new system shock object containing the element-wise difference
                between both system shocks
        """

        log.info("Compute difference between system shocks")
        if isinstance(other, type(self)):
            result = self.copy()
            result.dataset = self.dataset - other.dataset
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __add__(self, other):
        """
        Compute the sum of two system shock objects:
            - Only system shocks of the same type can be added
            - Addition is delegated to the underlying datasets

        Parameters:
            other (SystemShock):
                The system shock object to add to this one

        Returns:
            SystemShock:
                A new system shock object containing the element-wise sum
                of both system shocks
        """

        log.info("Compute sum of system shocks")
        if isinstance(other, type(self)):
            result = self.copy()
            result.dataset = self.dataset + other.dataset
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __abs__(self):
        """
        Compute the absolute value of this system shock object:
            - Absolute value is applied to the underlying dataset
            - Operation returns a new system shock object

        Returns:
            SystemShock:
                A new system shock object where the underlying dataset contains
                absolute values
        """

        log.info("Compute absolute value of system shock")
        result = self.copy()
        result.dataset = abs(self.dataset)
        return result
