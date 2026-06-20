"""
Presentation
************
This module is the builder module of the package `accounts`.

This module implements a design pattern **builder** to manage instantiation of
accounts objects.

The Builder design pattern is used to construct complex objects step by step,
allowing greater flexibility in the creation process.

The director class (here :class:`AccountsDirector`) is simplified here compared
to system and extensions builders, and directly use system and extensions
directors. It serves the roles of builder and director.

To instantiate an accounts object, one shall retrieve the director
singleton (though :meth:`get_director`) and use the appropriate methods.

Content
*******
- Classes:
    - :class:`AccountsDirector`
- Functions:
    - :meth:`get_director`
"""

__all__ = ["AccountsDirector", "get_director"]

import os

from matmat.core.detail_level import core as dl
from matmat.core.accounts.core import Accounts
from matmat.core.accounts.system.core import System
from matmat.core.accounts.extension.core import Extension
from matmat.core.accounts.identity import AccountsIdentity
from matmat.core.accounts.system.builder import SystemDirector
from matmat.core.accounts.extension.builder import ExtensionDirector
import matmat.utils.constants as cst
import matmat.utils.logging as log
from matmat.utils.errors import MEExtensionNotFound

# Director singleton
# pylint: disable=C0103
accounts_director = None
# pylint: enable=C0103


class AccountsDirector:
    """
    This class manages the building steps of a `Accounts` object. It
    provides a set of methods used to build various kind of accounts.
    """

    ATTR_ID = "_id"
    ATTR_SYSTEM = "_system"
    ATTR_EXTENSIONS = "_extensions"

    def __init__(self):
        """
        Constructor of class `AccountsDirector`
        """
        self.system_director: SystemDirector = SystemDirector()
        self.extension_director: ExtensionDirector = ExtensionDirector()

    def reset(self):
        self.system_director.reset()
        self.extension_director.reset()

    def set_regions(self, regions: dl.RegionsDL):
        """
        Setter for regions
        """
        self.system_director.set_regions(regions)
        self.extension_director.set_regions(regions)

    def set_final_demand_categories(
        self, final_demand_categories: dl.FinalDemandCategoriesDL
    ):
        """
        Setter for final demand categories
        """
        self.system_director.set_final_demand_categories(
            final_demand_categories
        )
        self.extension_director.set_final_demand_categories(
            final_demand_categories
        )

    def set_sectors(self, sectors: dl.SectorsDL):
        """
        Setter for sectors
        """
        self.system_director.set_sectors(sectors)
        self.extension_director.set_sectors(sectors)

    def make_from_path(
        self,
        path: str,
        extensions_names: list[str] = None,
        raise_error_if_extension_not_found: bool = True,
        load_data: bool = True,
    ) -> Accounts:
        """
        Make an 'Accounts' object from the files found in path.

        The path shall contain two directories:
            - *system*

              Refer to :meth:`SystemDirector.make_from_path` for the content of
              this directory.

            - *extensions* with for each extension, a subdirectory
              <extension_name>.

              Refer to :meth:`ExtensionDirector.make_from_path` for the content
              of these subdirectories.

        Parameters:
            path (str):
                The path to the directory containing *system*
                and *extensions* directories.
            extensions_names (list[str]):
                The names of the extensions which shall be loaded.
                If there are others in the directory, they will be ignored.
            raise_error_if_extension_not_found (bool):
                True if an exception shall be raised when an extension required
                in extensions_names is not found, False otherwise (default to
                True)
            load_data (bool):
                True if the dataframes shall be initialized with the values
                read in the files (default to True)

        Returns:
            Accounts

        Raises:
            MEExtensionNotFound : if a name in extensions_names has no matching
                                  directory
        """
        log.debug(f"Make Accounts object from path {path}")

        # Initialize accounts object
        accounts = Accounts()

        # Set system
        setattr(
            accounts,
            self.ATTR_SYSTEM,
            self.system_director.make_from_path(
                path=os.path.join(path, cst.DIR_SYSTEM), load_data=load_data
            ),
        )

        # Set identity
        setattr(
            accounts,
            self.ATTR_ID,
            AccountsIdentity(
                base_year=accounts.system.id.base_year,
                extension_names=[],
            ),
        )

        # Set extensions
        # Initialize empty map
        setattr(accounts, self.ATTR_EXTENSIONS, {})
        # Add extensions
        if os.path.isdir(os.path.join(path, cst.DIR_EXTENSIONS)):
            ext_directories = os.listdir(
                os.path.join(path, cst.DIR_EXTENSIONS)
            )

            # Ensure that all required extensions have a corresponding
            # directory
            if extensions_names is not None:
                for name in extensions_names:
                    if name not in ext_directories:
                        if raise_error_if_extension_not_found:
                            log.error(
                                f"Can't load extension '{name}'. Directory "
                                "does not exist."
                            )
                            raise MEExtensionNotFound(name)
                        else:
                            log.warning(
                                f"No directory found for extension '{name}'"
                            )

            for element in ext_directories:
                # Skip this directory if not in the extension names if given
                if (
                    extensions_names is not None
                    and element not in extensions_names
                ):
                    log.debug(f"Ignore directory {element}")
                    continue

                # Make extension
                full_path = os.path.join(path, cst.DIR_EXTENSIONS, element)
                if os.path.isdir(full_path):
                    file_path = os.path.join(full_path, cst.FILE_INFO)
                    try:
                        accounts.add_extension(
                            self.extension_director.make_from_path(
                                path=full_path, load_data=load_data
                            )
                        )
                    except FileNotFoundError:
                        log.warning(f"File {file_path} not found. Passing...")
        else:
            log.warning(f"No 'extensions' directory. Passing...")

        # Ensure system and extensions consistency
        accounts.make_system_and_extensions_consistent()

        return accounts

    def make_from_system_and_extensions(
        self, system: System, extensions: dict[str, Extension]
    ) -> Accounts:
        """
        Make an accounts directly from a system and a map of extensions

        Parameters:
            system (System)
                The system of the accounts
            extensions (dict[str, Extension])
                The map of extensions of the accounts
        Returns:
            Accounts
        """
        log.debug("Make Accounts object from a system and extensions")

        # Initialize accounts object
        accounts = Accounts()

        # Set id
        setattr(
            accounts,
            self.ATTR_ID,
            AccountsIdentity(
                base_year=system.id.base_year,
                extension_names=[],
            ),
        )

        # Set system
        setattr(accounts, self.ATTR_SYSTEM, system)

        # Set extensions
        # Initialize empty map
        setattr(accounts, self.ATTR_EXTENSIONS, {})
        # Add extensions
        for extension in extensions.values():
            accounts.add_extension(extension)

        # Ensure system and extensions consistency
        accounts.make_system_and_extensions_consistent()

        return accounts


# pylint: disable=W0603
def get_director(reset: bool = False) -> AccountsDirector:
    """
    Returns the `Accounts` director singleton. If reset is True, call the
    director method reset() before returning it.
    """
    global accounts_director

    if accounts_director is None:
        accounts_director = AccountsDirector()
    if reset:
        accounts_director.reset()
    return accounts_director


# pylint: enable=W0603
