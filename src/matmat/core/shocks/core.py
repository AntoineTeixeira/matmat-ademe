"""
Presentation
************
This module is the core module of the package `shock`.
It defines the class :class:`AccountsShock`

Content
*******
- Classes:
    - :class:`AccountsShock`
"""

__all__ = ["AccountsShock"]

import os

from matmat.core.bridge import core as bridge, pool as bridge_pool
from matmat.core.detail_level import core as dl
from matmat.core.shocks.identity import AccountsShockIdentity
from matmat.core.shocks.system.core import SystemShock
from matmat.core.shocks.extension.core import ExtensionShock
from matmat.utils.errors import (
    MEExtensionNotFound,
    MEExtensionAlreadyExisting,
)
import matmat.utils.logging as log
import matmat.utils.constants as cst
from matmat.utils.mixins import CopyMixin


# pylint: disable=C0103
class AccountsShock(CopyMixin):
    """
    This class represents a shock to be applied to an accounts

    To instantiate an `AccountsShock`, see :mod:`matmat.core.shocks.builder` module.

    It is composed with a system shock and a set of extension shocks.

    Attributes
    ----------
        _id : AccountsShockIdentity
            The identity card
        _system_shock : SystemShock
            The shock to be applied to the system of the accounts
        _extensions_shocks : dict[str, ExtensionShock]
            The map of shocks to be applied to the extensions of
            the accounts
    """

    _id: AccountsShockIdentity
    _system_shock: SystemShock
    _extensions_shocks: dict[str, ExtensionShock]

    def load_from_path(self, path: str):
        """
        Initialize the shock.

        This method initializes the shock data with the files found in path.

        The directory tree shall be as follows:
            - path/system
            - path/extensions
            - path/extensions/<extension_1>
            - path/extensions/<extension_2>
            - path/extensions/[...]

        Parameters:
            path (str):
                the path to the directory containing the files
                for initialization
        """
        log.info(f"Load AccountsShock from path {path}")
        self._system_shock.load_from_path(os.path.join(path, cst.DIR_SYSTEM))
        for name, extension_shock in self._extensions_shocks.items():
            extension_shock.load_from_path(
                os.path.join(path, cst.DIR_EXTENSIONS, name)
            )

    def save_to_path(
        self,
        path: str,
        export_format: str | list = cst.FORMAT_EXCEL,
    ):
        """
        Save the system shock and extensions shocks

        Parameters:
            path (str):
                the path to which directory the export files shall be generated
            export_format (str | list):
                the format(s) of the exported file, default is *excel*
        """
        log.info(f"Save shock with format(s) {export_format} to path {path}")
        os.makedirs(path, exist_ok=True)
        self._system_shock.save_to_path(
            os.path.join(path, cst.DIR_SYSTEM), export_format
        )
        for extension_shock in self._extensions_shocks.values():
            extension_shock.save_to_path(
                os.path.join(path, cst.DIR_EXTENSIONS), export_format
            )

    @property
    def id(self) -> AccountsShockIdentity:
        return self._id

    @property
    def system_shock(self) -> SystemShock:
        return self._system_shock

    @system_shock.setter
    def system_shock(self, value: SystemShock):
        self._system_shock = value

    @property
    def extensions_shocks(self) -> dict[str, ExtensionShock]:
        return self._extensions_shocks

    @property
    def detail_levels(self):
        """
        Returns complete accounts detail levels from the dataset
        """
        detail_levels = {
            **self._system_shock.detail_levels,
            **{
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value: {
                    k: v.extension_categories
                    for k, v in self._extensions_shocks.items()
                }
            },
        }
        return detail_levels

    def list_extensions_shocks(self) -> list[ExtensionShock]:
        return list(self._extensions_shocks.values())

    def get_extension_shock(self, name: str) -> ExtensionShock:
        """
        Retrieve the extension shock corresponding to the given name

        Returns:
            ExtensionShock : the extension shock with the matching name
        Raises:
            MEExtensionNotFound
                if there is no extension shock matching the given name
        """
        try:
            return self._extensions_shocks[name]
        except KeyError as e:
            raise MEExtensionNotFound(extension_name=name) from e

    def add_extension_shock(self, ext_shock: ExtensionShock):
        """
        Add an extension shock to the map of extension shocks

        Parameters:
            ext_shock (ExtensionShock):
                The new extension shock to add
        Raises:
            MEExtensionAlreadyExisting
                if the extension shock already exists in the extension
                shocks map
        """
        # Check that the extension shock does not already exist
        if ext_shock.name in self._extensions_shocks.keys():
            raise MEExtensionAlreadyExisting(extension_name=ext_shock.name)

        # Check if the extension shock detail levels are consistent with the system
        self._system_shock.dataset.check_detail_levels_consistency(
            other=ext_shock.dataset
        )

        self._extensions_shocks[ext_shock.name] = ext_shock
        # Add a property dynamically to ease extensions shocks reading
        # NOTE: the property shall be added to the class AccountsShock
        setattr(
            AccountsShock,
            ext_shock.name,
            property(
                fget=lambda shock: shock.get_extension_shock(ext_shock.name)
            ),
        )
        self._id.add_extension(ext_shock.name)

    def remove_extension_shock(self, extension_name: str):
        """
        Remove a shock from the map of extensions shocks

        Parameters:
            extension_name (str):
                The name of the extension shock
        """
        try:
            del self.extensions_shocks[extension_name]
            self._id.remove_extension(extension_name)
            log.info(f"Extension shock '{extension_name}' has been removed")
        except KeyError:
            log.error(f"Extension shock '{extension_name}' could not be found")

    def reset(self):
        """
        Reset the datasets of:
            - the system shock
            - all the extensions shocks
        """
        self._system_shock.dataset.reset()
        for ext_shock in self.list_extensions_shocks():
            ext_shock.dataset.reset()

    def aggregate(self, *bridges: bridge.Bridge):
        """
        Aggregate the system shock and extensions shocks w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.error(
            "The aggregation of an accounts shock is not " "yet implemented"
        )
        raise NotImplementedError

    def disaggregate(self, *bridges: bridge.Bridge):
        """
        Disaggregate the system shock and extensions shocks w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info("Disaggregate accounts shock")
        with bridge_pool.pool.context():
            self.system_shock.disaggregate(*bridges)
            for extension_shock in self._extensions_shocks.values():
                extension_shock.disaggregate(
                    *bridges, match_extension_name=True
                )

    def reformat(self, *bridges: bridge.Bridge):
        """
        Reformat the system shock and extensions shocks w.r.t. the bridges
        given as parameter.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info("Disaggregate accounts shock")
        with bridge_pool.pool.context():
            self.system_shock.reformat(*bridges)
            for extension_shock in self._extensions_shocks.values():
                extension_shock.reformat(*bridges, match_extension_name=True)

    def equals(self, other: "AccountsShock"):
        """
        Tell if this shock equals other

        Returns True if the following attributes are identical:
            - _system_shock
            - _extensions_shocks
        """
        log.info("Compare accounts")
        is_system_equal = self._system_shock.equals(other.system_shock)

        is_same_nb_of_extensions_shocks = len(self._extensions_shocks) == len(
            other.extensions_shocks
        )
        list_of_different_extensions_shocks = []
        for extension in self._extensions_shocks.values():
            try:
                if not extension.equals(
                    other.get_extension_shock(extension.name)
                ):
                    list_of_different_extensions_shocks.append(extension.name)
            except MEExtensionNotFound:
                log.info(
                    f"Extension shock {extension.name} does not exist in "
                    f"other shock"
                )
                list_of_different_extensions_shocks.append(extension.name)

        if len(list_of_different_extensions_shocks) > 0:
            log.info(
                f"Extensions shocks "
                f"{list_of_different_extensions_shocks} "
                f"differ from reference"
            )

        are_equal = is_system_equal and (
            len(list_of_different_extensions_shocks) == 0
            and is_same_nb_of_extensions_shocks
        )

        if are_equal:
            log.info("Shocks are equal")

        return are_equal

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in this accounts shock object:
            - Applies filtering to the main system shock and all extension shocks
            - Values below the threshold are set to zero
            - Operation can be applied in place or on a copy

        Parameters:
            threshold (float):
                Values with an absolute magnitude below this threshold are
                considered near zero
            inplace (bool):
                Whether to apply the filtering directly to this accounts shock
                object or return a filtered copy

        Returns:
            AccountsShock:
                A filtered accounts shock object when ``inplace`` is False
        """

        shock_ = self if inplace else self.copy()
        shock_.system_shock.filter_near_zero_values(
            threshold=threshold,
            inplace=True,
        )
        for extension_shock in shock_.list_extensions_shocks():
            extension_shock.filter_near_zero_values(
                threshold=threshold,
                inplace=True,
            )

        if not inplace:
            return shock_

    def __sub__(self, other):
        """
        Compute the difference between two accounts shock objects:
            - Only accounts shocks of the same type can be subtracted
            - Subtraction is applied to the main system shock and each extension shock
            - Missing extensions in the other object are skipped with a log

        Parameters:
            other (AccountsShock):
                The accounts shock object to subtract from this one

        Returns:
            AccountsShock:
                A new accounts shock object containing the difference between
                both accounts shock objects
        """

        log.info("Compute difference between accounts shocks")
        if isinstance(other, type(self)):
            result = self.copy()
            result.system_shock = self.system_shock - other.system_shock
            for k, v in self._extensions_shocks.items():
                try:
                    self._extensions_shocks[k] = v - other.get_extension_shock(
                        k
                    )
                except MEExtensionNotFound:
                    log.error(
                        f"Extension shock {k} not found in other "
                        "accounts shock. Passing..."
                    )
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __add__(self, other):
        """
        Compute the sum of two accounts shock objects:
            - Only accounts shocks of the same type can be added
            - Addition is applied to the main system shock and each extension shock
            - Missing extensions in the other object are skipped with a log

        Parameters:
            other (AccountsShock):
                The accounts shock object to add to this one

        Returns:
            AccountsShock:
                A new accounts shock object containing the sum of both
                accounts shock objects
        """

        log.info("Compute sum of accounts shocks")
        if isinstance(other, type(self)):
            result = self.copy()
            result.system_shock = self.system_shock + other.system_shock
            for k, v in self._extensions_shocks.items():
                try:
                    self._extensions_shocks[k] = v - other.get_extension_shock(
                        k
                    )
                except MEExtensionNotFound:
                    log.error(
                        f"Extension shock {k} not found in other accounts. Passing..."
                    )
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __abs__(self):
        """
        Compute the absolute value of this accounts shock object:
            - Absolute value is applied to the main system shock and all extension shocks
            - Operation returns a new accounts shock object

        Returns:
            AccountsShock:
                A new accounts shock object where all data contain absolute values
        """

        log.info("Compute abs of accounts shock")
        result = self.copy()
        result.system_shock = abs(self._system_shock)
        for k, v in self._extensions_shocks.items():
            self._extensions_shocks[k] = abs(v)
        return result

    def compare_with(
        self, other: "AccountsShock", threshold: float, save_to: str
    ):

        diff_system = self.system_shock.compare_with(
            other=other.system_shock, threshold=threshold
        )
        if len(diff_system) > 0:
            os.makedirs(os.path.join(save_to, cst.DIR_SYSTEM), exist_ok=True)
            for name, df in diff_system.items():
                df.to_excel(
                    os.path.join(save_to, cst.DIR_SYSTEM, f"{name}.xlsx"),
                    index=False,
                )

        diff_extensions = {}
        for extension in self.list_extensions_shocks():
            try:
                diff_extension = extension.compare_with(
                    other=other.get_extension_shock(extension.name),
                    threshold=threshold,
                )
                diff_extensions[extension.name] = diff_extension
            except MEExtensionNotFound:
                log.error(
                    f"Can't find extension shock {extension.name} in other "
                    f"accounts shock. Passing..."
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
