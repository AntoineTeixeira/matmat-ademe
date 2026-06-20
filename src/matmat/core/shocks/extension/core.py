"""
Presentation
************
This module is the core module of the package `shock.extension`.
It defines the class :class:`ExtensionShock`

Content
*******
- Classes:
    - :class:`ExtensionShock`
"""

__all__ = ["ExtensionShock"]

import os

from matmat.core.bridge import (
    core as bridge,
    tools as bridge_tools,
    pool as bridge_pool,
)
from matmat.core.shocks.extension.identity import ExtensionShockIdentity
from matmat.core.shocks.extension.dataset.core import ExtensionShockDataSet
from matmat.core.shocks.mixins import ManualParamMixin
from matmat.core.dataset.mixins import ToListMixin, ComparisonMixin
from matmat.utils import logging as log, constants as cst
from matmat.utils.mixins import CopyMixin


# pylint: disable=C0103
class ExtensionShock(
    ToListMixin, ManualParamMixin, CopyMixin, ComparisonMixin
):
    """
    This class represents a shock to be applied to an extension

    To instantiate a `ExtensionShock`, see
    :mod:`matmat.core.shocks.builder` module.

    It is composed with a set of shock data corresponding to the shockable
    data of an extension.

    Attributes
    ----------
        _id : ExtensionShockIdentity
            The identity card
        _dataset : ExtensionShockDataSet
            The dataset composing the extension shock
    """

    # Identity
    _id: ExtensionShockIdentity
    # Dataset
    _dataset: ExtensionShockDataSet

    @property
    def id(self) -> ExtensionShockIdentity:
        return self._id

    @property
    def name(self) -> str:
        return self._id.name

    @property
    def dataset(self) -> ExtensionShockDataSet:
        return self._dataset

    @dataset.setter
    def dataset(self, value: ExtensionShockDataSet):
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
    def extension_categories(self):
        """
        Returns the extension categories detail levels from the dataset
        """
        return self._dataset.extension_categories

    @property
    def detail_levels(self):
        """
        Returns complete extension shock detail levels from the dataset
        """
        return {dl_.kind.value: dl_ for dl_ in self._dataset.detail_levels}

    def load_from_path(self, path: str):
        """
        Initialize the shock.

        This method initializes the shock data with the files found in
        "path"

        Parameters:
            path (str):
                the path to the directory containing the extension shock data
                files for initialization (it is usually named after the
                extension name)
        """
        log.info(f"Load ExtensionShock '{self._id.name}' from path {path}")
        self.dataset.load_from_path(path=path)

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
        log.info(
            f"Save shock for extension '{self._id.name}' with "
            f"format(s) {export_format}"
        )
        ext_path = os.path.join(path, self.name)
        os.makedirs(ext_path, exist_ok=True)
        self.dataset.save_to_path(path=ext_path, export_format=export_format)
        self.id.to_json_file(
            file_name=cst.FILE_INFO,
            folder_path=ext_path,
        )

    def aggregate(
        self,
        *bridges: bridge.Bridge,
        match_extension_name: bool = True,
    ):
        """
        Aggregate the data of this extension shock w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
            match_extension_name (bool):
                If True, the extension name of any extension categories
                bridge must match this extension name in order to be applied.
                The others will be filtered.
                Otherwise, any extension categories bridge will be applied
                without filtering.
                Default to True.
        """
        log.error(
            "The aggregation of an extension shock is not yet implemented"
        )
        raise NotImplementedError

    def disaggregate(
        self,
        *bridges: bridge.Bridge,
        match_extension_name: bool = True,
    ):
        """
        Disaggregate the data of this extension shock w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
            match_extension_name (bool):
                If True, the extension name of any extension categories
                bridge must match this extension name in order to be applied.
                The others will be filtered.
                Otherwise, any extension categories bridge will be applied
                without filtering.
                Default to True.
        """
        log.info(f"Disaggregate extension shock '{self.name}'")
        with bridge_pool.pool.context():
            self.dataset.disaggregate(
                *(
                    bridges
                    if not match_extension_name
                    else bridge_tools.filter_ec_bridges(
                        bridges=bridges, extension_name=self.name
                    )
                )
            )

    def reformat(
        self,
        *bridges: bridge.Bridge,
        match_extension_name: bool = True,
    ):
        """
        Reformat the data of this extension shock w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
            match_extension_name (bool):
                If True, the extension name of any extension categories
                bridge must match this extension name in order to be applied.
                The others will be filtered.
                Otherwise, any extension categories bridge will be applied
                without filtering.
                Default to True.
        """
        log.info(f"Reformat extension shock '{self.name}'")
        with bridge_pool.pool.context():
            self.dataset.reformat(
                *(
                    bridges
                    if not match_extension_name
                    else bridge_tools.filter_ec_bridges(
                        bridges=bridges, extension_name=self.name
                    )
                )
            )

    def inject_shock(
        self, shock: "ExtensionShock", inject_zeros: bool = False
    ):
        """
        This method permits to concatenate shocks by injecting the values
        of another shock into this shock.

        Parameters:
            shock (ExtensionShock):
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

    def equals(self, other: "ExtensionShock"):
        """
        Tell if this extension shock equals other

        Returns True if the following attributes are identical:
            - _name
            - dS_x_dom, dS_Y, dS_Z, dM_RoW
        """
        log.info(f"Compare extension shocks '{self.name}'")

        is_dataset_equal = self.dataset.equals(other.dataset)

        is_name_equal = self._id.name == other.id.name
        if not is_name_equal:
            log.info(
                f"Extension shocks have different names: "
                f"{self._id.name} != {other.id.name}"
            )

        are_equal = is_dataset_equal and is_name_equal

        if are_equal:
            log.info(f"Extensions shocks '{self.name}' are equal")

        return are_equal

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in this extension shock object:
            - Delegates filtering to the underlying dataset
            - Values below the threshold are set to zero
            - Operation can be applied in place or return a filtered copy

        Parameters:
            threshold (float):
                Values with an absolute magnitude below this threshold are
                considered near zero
            inplace (bool):
                Whether to apply the filtering directly to this extension shock
                object or return a filtered copy

        Returns:
            ExtensionShock:
                A filtered extension shock object when ``inplace`` is False
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
        Compute the difference between two extension shock objects:
            - Only extension shocks of the same type can be subtracted
            - Subtraction is delegated to the underlying datasets

        Parameters:
            other (ExtensionShock):
                The extension shock object to subtract from this one

        Returns:
            ExtensionShock:
                A new extension shock object containing the element-wise difference
                between both extension shocks
        """

        log.info("Compute difference between extension shocks")
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
        Compute the sum of two extension shock objects:
            - Only extension shocks of the same type can be added
            - Addition is delegated to the underlying datasets

        Parameters:
            other (ExtensionShock):
                The extension shock object to add to this one

        Returns:
            ExtensionShock:
                A new extension shock object containing the element-wise sum
                of both extension shocks
        """

        log.info("Compute sum of extension shocks")
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
        Compute the absolute value of this extension shock object:
            - Absolute value is applied to the underlying dataset
            - Operation returns a new extension shock object

        Returns:
            ExtensionShock:
                A new extension shock object where the underlying dataset contains
                absolute values
        """

        log.info("Compute absolute value of extension shock")
        result = self.copy()
        result.dataset = abs(self.dataset)
        return result
