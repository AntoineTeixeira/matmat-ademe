"""
Presentation
************
This module is the core module of the package `accounts`.
It defines the class :class:`Accounts`

Content
*******
- Classes:
    - :class:`Accounts`
"""

__all__ = ["Accounts"]

import os

import pandas as pd

from matmat.core.bridge import core as bridge, pool as bridge_pool
from matmat.core.accounts.identity import AccountsIdentity
from matmat.core.accounts.system.core import System
from matmat.core.accounts.extension.core import Extension
from matmat.core.shocks.core import AccountsShock
from matmat.utils.mixins import CopyMixin
from matmat.utils import logging as log, constants as cst, tools
from matmat.utils.errors import (
    MEExtensionNotFound,
    MEExtensionAlreadyExisting,
)

from matmat.core.detail_level import core as dl


# pylint: disable=R0904
class Accounts(CopyMixin):
    """
    This class manages a system and its associated extensions.

    To instantiate a `Accounts`, see
    :mod:`matmat.core.accounts.builder` module.

    Attributes
    ----------
        _id : AccountsIdentity
            the identity card of the accounts
        _system : System
            the system of the accounts
        _extensions : dict[str, Extension]
            the map of extensions associated to the system
    """

    _id: AccountsIdentity
    _system: System
    _extensions: dict[str, Extension]

    @property
    def id(self) -> AccountsIdentity:
        return self._id

    @id.setter
    def id(self, value: AccountsIdentity):
        self._id = value

    @property
    def detail_levels(self):
        """
        Returns complete accounts detail levels from the dataset
        """
        detail_levels = {
            **self.system.detail_levels,
            **{
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value: {
                    k: v.extension_categories
                    for k, v in self._extensions.items()
                }
            },
        }
        return detail_levels

    @property
    def system(self) -> System:
        return self._system

    @system.setter
    def system(self, value: System):
        self._system = value

    @property
    def extensions(self) -> dict[str, Extension]:
        return self._extensions

    def list_extensions(self) -> list[Extension]:
        return list(self._extensions.values())

    def get_extension(self, name: str) -> Extension:
        """
        Returns the extension associated to the given name, if it exists

        Parameters:
            name (str):
                the name of the extension
        Returns:
            Extension : the extension with the given name, if it exists
        Raises:
            MEExtensionNotFound
                if the name does not match any existing extension in the
                accounts
        """
        try:
            return self._extensions[name]
        except KeyError as e:
            raise MEExtensionNotFound(extension_name=name) from e

    def add_extension(self, new_extension: Extension):
        """
        Add an extension to the dict of extensions.
        Update the identity accordingly.

        Parameters:
            new_extension (Extension):
                The new extension to add
        Raises:
            MEExtensionAlreadyExisting
                if the extension already exists in the extensions map
        """
        # Check if the extension is already in the accounts
        if new_extension.name in self._extensions.keys():
            raise MEExtensionAlreadyExisting(extension_name=new_extension.name)

        # Check if the extension detail levels are consistent with the system
        self._system.dataset.check_detail_levels_consistency(
            other=new_extension.dataset
        )

        # Add the extension to the accounts
        self._extensions[new_extension.name] = new_extension
        # Add a property dynamically to ease extensions reading
        # NOTE: the property shall be added to the class Accounts
        setattr(
            Accounts,
            new_extension.name,
            property(fget=lambda acc: acc.get_extension(new_extension.name)),
        )
        self._id.add_extension(new_extension.name)

    def remove_extension(self, extension_name: str):
        """
        Remove an extension from the dict of extensions.
        Update the identity accordingly.

        Parameters:
            extension_name (str):
                The name of the extension to remove
        """
        try:
            del self.extensions[extension_name]
            self._id.remove_extension(extension_name)
            log.info(f"Extension '{extension_name}' has been removed")
        except KeyError:
            log.error(f"Extension '{extension_name}' could not be found")

    def load_from_path(self, path: str):
        """
        Load the system and its associated extensions

        Parameters:
            path (str):
                the path to the directory containing the accounts files
        """
        log.info(f"Load Accounts from path {path}")
        self._system.load_from_path(os.path.join(path, cst.DIR_SYSTEM))
        for name, extension in self._extensions.items():
            extension.load_from_path(
                os.path.join(path, cst.DIR_EXTENSIONS, name)
            )

    def save_to_path(
        self,
        path: str,
        export_format: str | list = cst.FORMAT_EXCEL,
    ):
        """
        Save the system and its associated extensions

        Parameters:
            path (str):
                the path to which directory the export files shall be generated
            export_format (str | list):
                the format(s) of the exported file, default is *excel*
        """
        log.info(
            f"Save accounts with format(s) {export_format} to path {path}"
        )
        os.makedirs(path, exist_ok=True)
        self._system.save_to_path(
            os.path.join(path, cst.DIR_SYSTEM), export_format
        )
        for extension in self._extensions.values():
            extension.save_to_path(
                os.path.join(path, cst.DIR_EXTENSIONS), export_format
            )

    def calculate(self):
        """
        Calculate the system and its associated extensions
        """
        log.info("Calculate Accounts")
        self._system.calculate()
        for extension in self._extensions.values():
            extension.calculate(system=self._system)

    def calculate_system(self):
        """
        Calculate the system
        """
        self._system.calculate()

    def calculate_extensions(self, lazy: bool = False):
        """
        Calculate the extensions

        Parameters:
            lazy (bool):
                If True, calculate only S_? and F_? data
        """
        for extension in self._extensions.values():
            extension.calculate(system=self._system, lazy=lazy)

    def shock(self, shock: AccountsShock):
        """
        Apply a shock to the system and its associated extensions

        Parameters:
            shock (:class:`AccountsShock`):
                the shock to be applied
        """
        log.info("Shock Accounts")
        self._system.shock(shock=shock.system_shock)
        for extension in self._extensions.values():
            try:
                extension_shock = shock.get_extension_shock(
                    name=extension.name
                )
                extension.shock(shock=extension_shock)
            except MEExtensionNotFound:
                log.info(f"No shock found for extension '{extension.name}'")

        # Update identity fields
        self._id.proj_year = shock.id.proj_year
        self._id.scenario_name = shock.id.scenario_name

    def reset_for_shock(self):
        """
        Reset the system and its associated extensions in preparation for a
        shock
        """
        log.info("Reset Accounts for shock")
        self._system.reset_for_shock()
        for extension in self._extensions.values():
            extension.reset_for_shock()

    def reset_for_hem(self, index_df: pd.DataFrame):
        """
        Reset the system and its associated extensions in preparation for a
        HEM analysis

        Parameters:
            index_df (pd.DataFrame):
                The dataframe representing the index of the rows to reset for
                HEM
        """
        log.info("Reset Accounts for HEM analysis")
        self._system.reset_for_hem(index_df)
        for extension in self._extensions.values():
            extension.reset_fluxes()

    def reset(self):
        """
        Reset the datasets of the system and its associated extensions
        """
        self._system.dataset.reset()
        for extension in self.list_extensions():
            extension.dataset.reset()

    def reset_coefficients(self):
        """
        Reset the coefficients of the system and its associated extensions
        """
        log.info("Reset Accounts to fluxes")
        self._system.reset_coefficients()
        for extension in self._extensions.values():
            extension.reset_coefficients()

    def reset_fluxes(self):
        """
        Reset the fluxes of the system and its associated extensions
        """
        log.info("Reset Accounts to coefficients")
        self._system.reset_fluxes()
        for extension in self._extensions.values():
            extension.reset_fluxes()

    def make_system_and_extensions_consistent(self):
        """
        If the system is a standard system, then nullify the augmented data
        of the extensions. This permits to avoid computation of non-existing
        data in extensions.
        """
        for extension in self._extensions.values():
            extension.tune_dataset(system=self.system)

    def aggregate(self, *bridges: bridge.Bridge):
        """
        Aggregate the system and extensions w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info("Aggregate accounts")
        with bridge_pool.pool.context():
            self.system.aggregate(*bridges)
            for extension in self._extensions.values():
                extension.aggregate(*bridges, match_extension_name=True)

    def disaggregate(self, *bridges: bridge.Bridge):
        """
        Disaggregate the system and extensions w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.error("The disaggregation of an accounts is not yet implemented")
        raise NotImplementedError

    def reformat(self, *bridges: bridge.Bridge):
        """
        Reformat the system and extensions w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info("Reformat accounts")
        with bridge_pool.pool.context():
            self.system.reformat(*bridges)
            for extension in self._extensions.values():
                extension.reformat(*bridges, match_extension_name=True)

    def subtract(self, accounts: "Accounts"):
        """
        Subtract an accounts to this accounts

        Parameters:
            accounts (Accounts):
                The accounts to subtract
        """
        self.system.subtract_fluxes(
            x=accounts.system.dataset.x,
            Y=accounts.system.dataset.Y,
            Z=accounts.system.dataset.Z,
        )
        for extension in self._extensions.values():
            try:
                extension.subtract(accounts.get_extension(extension.name))
            except MEExtensionNotFound:
                log.info(
                    f"Extension '{extension.name}' does not exist in HEM "
                    f"accounts. Can't compute difference."
                )

    def equals(self, other: "Accounts"):
        """
        Tell if this accounts equals other

        Returns True if the following attributes are identical:
            - _system
            - _extensions
        """
        log.info("Compare accounts")
        is_system_equal = self._system.equals(other.system)

        is_same_nb_of_extensions = len(self.extensions) == len(
            other.extensions
        )
        list_of_different_extensions = []
        for extension in self._extensions.values():
            try:
                if not extension.equals(other.get_extension(extension.name)):
                    list_of_different_extensions.append(extension.name)
            except MEExtensionNotFound:
                log.verbose(
                    f"Extension '{extension.name}' does not exist in other "
                    f"accounts"
                )
                list_of_different_extensions.append(extension.name)

        if len(list_of_different_extensions) > 0:
            log.info(
                f"Extensions {list_of_different_extensions} differ"
                f" from reference"
            )

        are_equal = is_system_equal and (
            len(list_of_different_extensions) == 0 and is_same_nb_of_extensions
        )

        if are_equal:
            log.info("Accounts are equal")

        return are_equal

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in this accounts object:
            - Applies filtering to the main system and all extensions
            - Values below the threshold are set to zero
            - Operation can be applied in place or on a copy

        Parameters:
            threshold (float):
                Values with an absolute magnitude below this threshold are
                considered near zero
            inplace (bool):
                Whether to apply the filtering directly to this accounts
                object or return a filtered copy

        Returns:
            Accounts:
                A filtered accounts object when ``inplace`` is False
        """

        accounts_ = self if inplace else self.copy()
        accounts_.system.filter_near_zero_values(
            threshold=threshold,
            inplace=True,
        )
        for extension in accounts_.list_extensions():
            extension.filter_near_zero_values(
                threshold=threshold,
                inplace=True,
            )

        if not inplace:
            return accounts_

    def __sub__(self, other):
        """
        Compute the difference between two accounts objects:
            - Only accounts of the same type can be subtracted
            - Subtraction is applied to the main system and each extension
            - Missing extensions in the other object are skipped with a log

        Parameters:
            other (Accounts):
                The accounts object to subtract from this one

        Returns:
            Accounts:
                A new accounts object containing the difference between
                both accounts objects
        """

        log.info("Compute difference between accounts")
        if isinstance(other, type(self)):
            result = self.copy()
            result.system = self.system - other.system
            for k, v in self._extensions.items():
                try:
                    self._extensions[k] = v - other.get_extension(k)
                except MEExtensionNotFound:
                    log.error(
                        f"Extension '{k}' not found in other accounts. Passing..."
                    )
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __add__(self, other):
        """
        Compute the sum of two accounts objects:
            - Only accounts of the same type can be added
            - Addition is applied to the main system and each extension
            - Missing extensions in the other object are skipped with a log

        Parameters:
            other (Accounts):
                The accounts object to add to this one

        Returns:
            Accounts:
                A new accounts object containing the sum of both accounts objects
        """

        log.info("Compute sum of accounts")
        if isinstance(other, type(self)):
            result = self.copy()
            result.system = self.system + other.system
            for k, v in self._extensions.items():
                try:
                    self._extensions[k] = v - other.get_extension(k)
                except MEExtensionNotFound:
                    log.error(
                        f"Extension '{k}' not found in other accounts. Passing..."
                    )
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __abs__(self):
        """
        Compute the absolute value of this accounts object:
            - Absolute value is applied to the main system and all extensions
            - Operation returns a new accounts object

        Returns:
            Accounts:
                A new accounts object where all data contain absolute values
        """

        log.info("Compute abs of accounts")
        result = self.copy()
        result.system = abs(self.system)
        for k, v in self._extensions.items():
            self._extensions[k] = abs(v)
        return result

    def compare_with(self, other: "Accounts", threshold: float, save_to: str):

        diff_system = self.system.compare_with(
            other=other.system, threshold=threshold
        )
        if len(diff_system) > 0:
            os.makedirs(os.path.join(save_to, cst.DIR_SYSTEM), exist_ok=True)
            for name, df in diff_system.items():
                df.to_excel(
                    os.path.join(save_to, cst.DIR_SYSTEM, f"{name}.xlsx"),
                    index=False,
                )

        diff_extensions = {}
        for extension in self.list_extensions():
            try:
                diff_extension = extension.compare_with(
                    other=other.get_extension(extension.name),
                    threshold=threshold,
                )
                diff_extensions[extension.name] = diff_extension
            except MEExtensionNotFound:
                log.error(
                    f"Can't find extension '{extension.name}' in other "
                    f"accounts. Passing..."
                )

        if len(diff_extensions) > 0:
            os.makedirs(
                os.path.join(save_to, cst.DIR_EXTENSIONS), exist_ok=True
            )
            for k, v in diff_extensions.items():
                if len(v) > 0:
                    os.makedirs(
                        os.path.join(save_to, cst.DIR_EXTENSIONS, k),
                        exist_ok=True,
                    )
                    for name, df in v.items():
                        df.to_excel(
                            os.path.join(
                                save_to,
                                cst.DIR_EXTENSIONS,
                                k,
                                f"{name}.xlsx",
                            ),
                            index=False,
                        )

    def check_zero_projections(self, projected: "Accounts", save_to: str):

        diff_system = self.system.check_zero_projections(
            projected=projected.system
        )
        if len(diff_system) > 0:
            os.makedirs(os.path.join(save_to, cst.DIR_SYSTEM), exist_ok=True)
            for name, df in diff_system.items():
                df.to_excel(
                    os.path.join(save_to, cst.DIR_SYSTEM, f"{name}.xlsx"),
                    index=False,
                )

        diff_extensions = {}
        for extension in self.list_extensions():
            try:
                diff_extension = extension.check_zero_projections(
                    projected=projected.get_extension(extension.name),
                )
                diff_extensions[extension.name] = diff_extension
            except MEExtensionNotFound:
                log.error(
                    f"Can't find extension '{extension.name}' in projected "
                    f"accounts. Passing..."
                )

        if len(diff_extensions) > 0:
            os.makedirs(
                os.path.join(save_to, cst.DIR_EXTENSIONS), exist_ok=True
            )
            for k, v in diff_extensions.items():
                if len(v) > 0:
                    os.makedirs(
                        os.path.join(save_to, cst.DIR_EXTENSIONS, k),
                        exist_ok=True,
                    )
                    for name, df in v.items():
                        df.to_excel(
                            os.path.join(
                                save_to,
                                cst.DIR_EXTENSIONS,
                                k,
                                f"{name}.xlsx",
                            ),
                            index=False,
                        )
