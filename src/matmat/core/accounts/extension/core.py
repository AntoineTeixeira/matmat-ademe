"""
Presentation
************
This module is the core module of the package `extension`.
It defines the class :class:`Extension`

Content
*******
- Classes:
    - :class:`Extension`
"""

__all__ = ["Extension"]

import os

from matmat.core.bridge import (
    core as bridge,
    tools as bridge_tools,
    pool as bridge_pool,
)
from matmat.core.accounts.extension.identity import ExtensionIdentity
from matmat.core.accounts.system.core import System
from matmat.core.shocks.extension.core import ExtensionShock
from matmat.core.accounts.extension.strategies.calcul import (
    AbstractExtensionCalcul,
    EnumExtensionCalcul,
    UseBased,
    GrossOutputBased,
    EmbodiedInImport,
)
from matmat.core.accounts.extension.dataset.core import ExtensionDataSet
from matmat.core.dataset.mixins import ToListMixin, ComparisonMixin
from matmat.utils import constants as cst, logging as log, tools
from matmat.utils.errors import (
    MEShockExtensionInconsistency,
)
from matmat.utils.mixins import CopyMixin


# pylint: disable=C0103, R0902, R0904
class Extension(ToListMixin, CopyMixin, ComparisonMixin):
    """
    This class represents an extension

    To instantiate an `Extension`, see
    :mod:`matmat.core.accounts.extension.builder` module.

    Attributes
    ----------
        _id : ExtensionIdentity
            The identity card
        _dataset : ExtensionDataSet
            The dataset composing the extension
        _calcul : AbstractExtensionCalcul
            The strategy of calcul

    """

    # Identity
    _id: ExtensionIdentity
    # Dataset
    _dataset: ExtensionDataSet
    # Strategies
    _calcul: AbstractExtensionCalcul

    @property
    def id(self):
        return self._id

    @property
    def calcul(self):
        return self._calcul

    @calcul.setter
    def calcul(self, value: str):
        """
        Set the calculation strategy and reconfigure the extension dataset
        accordingly.
        """
        self._calcul = EnumExtensionCalcul(value).build_strategy()
        log.verbose(f"Set extension '{self.name}' calcul strategy to '{value}'")
        self._id.strategy = value
        self.dataset.set_config(
            name="extension_calcul_strategy",
            value=value,
            tune_dataset=True,
        )

    @property
    def name(self) -> str:
        return self._id.name

    @property
    def dataset(self) -> ExtensionDataSet:
        return self._dataset

    @dataset.setter
    def dataset(self, value: ExtensionDataSet):
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
        Returns complete extension detail levels from the dataset
        """
        return {dl_.kind.value: dl_ for dl_ in self._dataset.detail_levels}

    def load_from_path(self, path: str):
        """
        Load the extension

        Parameters:
            path (str):
                the path to the directory containing the extension data
                files (it is usually named after the extension name)
        """
        log.info(f"Load Extension '{self._id.name}' from path {path}")
        self.dataset.load_from_path(path=path)

    def save_to_path(
        self,
        path: str,
        export_format: str | list = cst.FORMAT_EXCEL,
    ):
        """
        Save the extension

        Parameters:
            path (str):
                the path to which directory the export files shall be generated
            export_format (str | list):
                the format(s) of the exported file, default is *excel*
        """
        log.info(
            f"Save extension '{self.name}' with " f"format(s) {export_format}"
        )
        ext_path = os.path.join(path, self.name)
        os.makedirs(ext_path, exist_ok=True)
        self.dataset.save_to_path(path=ext_path, export_format=export_format)
        self.id.to_json_file(
            file_name=cst.FILE_INFO,
            folder_path=ext_path,
        )

    def reset_for_shock(self):
        """
        Reset the extension in preparation for a shock.
        The multipliers and consumption based accounts are reset.
        The rest depends on the extension strategy.
        """
        log.info(f"Reset extension '{self._id.name}' for shock")
        self._calcul.reset_for_shock(extension_dataset=self.dataset)
        self.dataset.reset_outputs()

    def reset_coefficients(self):
        """
        Reset the extension coefficients, i.e. reset S_x_dom,
        S_Y, S_Z, M_RoW
        as well as the multipliers and the consumption based accounts.
        """
        log.info(
            f"Reset extension '{self._id.name}' coefficients "
            f"(i.e. keep only fluxes)"
        )
        self.dataset.reset_coefficients()
        self.dataset.reset_outputs()

    def reset_fluxes(self):
        """
        Reset the extension fluxes, i.e. reset F_x_dom,
        F_Y, F_Z, as well
        as the multipliers and the consumption based accounts.
        """
        log.info(
            f"Reset extension '{self._id.name}' fluxes "
            f"(i.e. keep only coefficients)"
        )
        self.dataset.reset_fluxes()
        self.dataset.reset_outputs()

    def calculate(self, system: System, lazy: bool = False):
        """
        Calculate the extension components

        The different calculations are performed by the strategy object and
        decomposed in 3 steps:
            1. Calculate the extension coefficients or fluxes (depending on
               what is available as input)
            2. Calculate the multipliers
            3. Calculate the consumption based accounts

        Parameters:
            system (System):
                The system to which the extension is associated
            lazy (bool):
                If True, calculate only S_? and F_? data
        """
        log.info(
            f"Calculate extension '{self._id.name}' with "
            f"strategy '{self._calcul.name}'"
        )

        self.tune_dataset(system=system)
        system.dataset.check_detail_levels_consistency(other=self._dataset)

        self._calcul.calculate(
            extension_dataset=self.dataset,
            system_dataset=system.dataset,
        )

        if not lazy:
            self._calcul.calculate_m(
                extension_dataset=self.dataset,
                system_dataset=system.dataset,
            )
            self._calcul.calculate_d_cba(
                extension_dataset=self.dataset,
                system_dataset=system.dataset,
            )

            if not self.dataset.M_k.is_null():
                self._calcul.calculate_mk(
                    extension_dataset=self.dataset,
                    system_dataset=system.dataset,
                )
            if not self.dataset.d_cba_k.is_null():
                self._calcul.calculate_d_cba_k(
                    extension_dataset=self.dataset,
                    system_dataset=system.dataset,
                )

    def calculate_mapping(self, system: System):
        """
        Calculates the mapping

        Parameters:
            system (System):
                The system to which the extension is associated
        """
        log.info(f"Calculate mapping for extension '{self._id.name}'")
        self._calcul.calculate_mapping(
            extension_dataset=self.dataset,
            system_dataset=system.dataset,
        )
        if not self._dataset.mapping_k.is_null():
            log.info(f"Calculate mapping_k for extension '{self._id.name}'")
            self._calcul.calculate_mapping_k(
                extension_dataset=self.dataset,
                system_dataset=system.dataset,
            )

    def is_use_based(self):
        """
        Check if the current extension calculation strategy is `UseBased`.

        Returns:
            bool : True if the current strategy is `UseBased`, False otherwise.
        """
        # pylint: disable=C0123
        # Necessary use of type() here instead of isinstance()
        return type(self._calcul) is UseBased
        # pylint: enable=C0123

    def is_gross_output_based(self):
        """
        Check if the current extension calculation strategy is
        `GrossOutputBased`.

        Returns:
            bool : True if the current strategy is `GrossOutputBased`,
                   False otherwise.
        """
        # pylint: disable=C0123
        # Necessary use of type() here instead of isinstance()
        return type(self._calcul) is GrossOutputBased
        # pylint: enable=C0123

    def is_embodied_in_import(self):
        """
        Check if the current extension calculation strategy is
        `EmbodiedInImport`.

        Returns:
            bool : True if the current strategy is `EmbodiedInImport`,
                   False otherwise.
        """
        # pylint: disable=C0123
        # Necessary use of type() here instead of isinstance()
        return type(self._calcul) is EmbodiedInImport
        # pylint: enable=C0123

    def shock(self, shock: ExtensionShock):
        """
        Apply an extension shock to the extension

        Operations performed:
            - Check the consistency of detail levels between the extension
              and the extension shock
            - Check that the shock is intended for this extension (by comparing
              their name)
            - Check the compatibility of the shock and the extension strategy,
              display a warning if there is an inconsistency
            - Applies the shock data to the shockable data of the extension

        Parameters:
            shock (ExtensionShock):
                the shock to apply
        Raises:
            MEShockExtensionInconsistency
                if the name of the shock and the name of the extension
                are different
        """
        log.info(f"Shock Extension '{self.name}'")

        self._dataset.check_detail_levels_consistency(other=shock.dataset)

        # Check that the names match
        if self.name != shock.name:
            raise MEShockExtensionInconsistency(
                shock_name=shock.name, extension_name=self.name
            )

        for shock_data_name in shock.dataset.list_data():
            if not self.calcul.is_shock_applicable(shock_data_name):
                log.warning(
                    f"{shock_data_name} should not be shocked in an "
                    f"extension '{self._calcul.name}'"
                )

        self.dataset.S_x_dom.shock(shock_data=shock.dataset.dS_x_dom)
        self.dataset.S_Y.shock(shock_data=shock.dataset.dS_Y)
        self.dataset.S_Z.shock(shock_data=shock.dataset.dS_Z)
        self.dataset.M_RoW.shock(shock_data=shock.dataset.dM_RoW)

        # Update identity fields
        self.id.proj_year = shock.id.proj_year
        self.id.scenario_name = shock.id.scenario_name

    def aggregate(
        self,
        *bridges: bridge.Bridge,
        match_extension_name: bool = True,
    ):
        """
        Aggregate the extension fluxes w.r.t. the bridges given as parameters.
        The other data index are updated and the values reset.

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
        log.info(f"Aggregate extension '{self.name}'")
        with bridge_pool.pool.context():
            self.dataset.aggregate(
                *(
                    bridges
                    if not match_extension_name
                    else bridge_tools.filter_ec_bridges(
                        bridges=bridges, extension_name=self.name
                    )
                )
            )

    def disaggregate(
        self,
        *bridges: bridge.Bridge,
        match_extension_name: bool = True,
    ):
        """
        Disaggregate the extension fluxes w.r.t. the bridges given as parameters.
        The other data index are updated and the values reset.

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
        log.error("The disaggregation of an extension is not yet implemented")
        raise NotImplementedError

    def reformat(
        self,
        *bridges: bridge.Bridge,
        match_extension_name: bool = True,
    ):
        """
        Reformat the extension data w.r.t. the bridges given as parameters.

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
        log.info(f"Reformat extension '{self.name}'")
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

    def subtract(self, extension: "Extension"):
        """
        Subtract an extension to this extension:
            - Subtract fluxes F_x_dom, F_Y, F_Z
            - Subtract d_cba, d_cba_k

        Parameters:
            extension (Extension):
                The extension containing the data to subtract
        """
        if self.name != extension.name:
            log.warning(
                f"Trying to sum two extensions with different "
                f"names: '{self.name}' and '{extension.name}'"
            )

        self.dataset.F_x_dom.update_values(
            self.dataset.F_x_dom.df - extension.dataset.F_x_dom.df
        )
        if not self.dataset.F_Y.is_null():
            self.dataset.F_Y.update_values(
                self.dataset.F_Y.df - extension.dataset.F_Y.df
            )
        if not self.dataset.F_Z.is_null():
            self.dataset.F_Z.update_values(
                self.dataset.F_Z.df - extension.dataset.F_Z.df
            )

        self.dataset.d_cba.update_values(
            self.dataset.d_cba.df - extension.dataset.d_cba.df
        )
        if not self.dataset.d_cba_k.is_null():
            self.dataset.d_cba_k.update_values(
                self.dataset.d_cba_k.df - extension.dataset.d_cba_k.df
            )

    def equals(self, other: "Extension"):
        """
        Tell if this extension equals other

        Returns True if the following attributes are identical:
            - _name
            - _dataset
            - _calcul
        """
        log.info(f"Compare extensions '{self.name}'")
        is_dataset_equal = self.dataset.equals(
            other.dataset, excluded_data=[cst.M, cst.M_K]
        )
        is_name_equal = self._id.name == other.id.name
        if not is_name_equal:
            log.info(
                f"Extensions have different names: "
                f"{self._id.name} != {other.id.name}"
            )
        is_strategy_equal = type(self._calcul) is type(other.calcul)
        if not is_strategy_equal:
            log.info(
                f"Extensions have different strategies: "
                f"{type(self._calcul)} != {type(other.calcul)}"
            )

        are_equal = is_dataset_equal and is_name_equal and is_strategy_equal

        if are_equal:
            log.info(f"Extensions '{self.name}' are equal")

        return are_equal

    def tune_dataset(
        self,
        system: System = None,
    ):
        """
        Update the dataset w.r.t. configuration parameters including:
            - calcul strategy
        """
        self.dataset.set_config(
            name="system_calcul_strategy",
            value=system.calcul.name,
            tune_dataset=True,
        )

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in the underlying dataset of this extension:
            - Delegates the filtering to the associated dataset
            - Values below the threshold are removed
            - Operation can be applied in place or on a copy

        Parameters:
            threshold (float):
                Values with an absolute magnitude below this threshold are
                considered near zero
            inplace (bool):
                Whether to apply the filtering directly to this extension or
                return a filtered copy

        Returns:
            Extension:
                A filtered extension when ``inplace`` is False
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
        Compute the difference between two extensions:
            - Only extensions of the same type can be subtracted
            - Subtraction is delegated to the underlying datasets

        Parameters:
            other (Extension):
                The extension to subtract from this one

        Returns:
            Extension:
                A new extension containing the difference between both extensions
        """

        log.info(f"Compute difference between extensions {self.name}")
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
        Compute the sum of two extensions:
            - Only extensions of the same type can be added
            - Addition is delegated to the underlying datasets

        Parameters:
            other (Extension):
                The extension to add to this one

        Returns:
            Extension:
                A new extension containing the sum of both extensions
        """

        log.info(f"Compute sum of extensions {self.name}")
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
        Compute the absolute value of this extension:
            - Absolute value is applied to the underlying dataset
            - Operation returns a new extension

        Returns:
            Extension:
                A new extension where the underlying dataset contains
                absolute values
        """

        log.info(f"Compute absolute value of extension '{self.name}'")
        result = self.copy()
        result.dataset = abs(self.dataset)
        return result
