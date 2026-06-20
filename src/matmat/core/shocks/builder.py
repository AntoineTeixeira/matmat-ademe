"""
Presentation
************
This module is the builder module of the package `shock`.

This module implements a design pattern **builder** to manage instantiation of
accounts objects.

The Builder design pattern is used to construct complex objects step by step,
allowing greater flexibility in the creation process.

The director class (here :class:`AccountsShockDirector`) is simplified here compared
to system and extensions shock builders, and directly use system and extensions
shock directors. It serves the roles of builder and director.

To instantiate an accounts object, one shall retrieve the director
singleton (though :meth:`get_director`) and use the appropriate methods.

Content
*******
- Classes:
    - :class:`AccountsShockDirector`
- Functions:
    - :meth:`get_director`
"""

__all__ = [
    "AccountsShockDirector",
    "get_director",
]

import os

from matmat.core.detail_level import core as dl
from matmat.core.accounts.core import Accounts
from matmat.core.shocks.core import AccountsShock
from matmat.core.shocks.identity import AccountsShockIdentity
from matmat.core.shocks.system.core import SystemShock
from matmat.core.shocks.extension.core import ExtensionShock
from matmat.core.shocks.system.builder import SystemShockDirector
from matmat.core.shocks.extension.builder import ExtensionShockDirector
import matmat.utils.constants as cst
import matmat.utils.logging as log
from matmat.utils.errors import MEExtensionNotFound

# Directors singletons
# pylint: disable=C0103
accounts_shock_director = None
# pylint: enable=C0103


class AccountsShockDirector:
    """
    This class is a builder class which permits to build the components of a
    `AccountsShock`
    """

    ATTR_ID = "_id"
    ATTR_SYSTEM_SHOCK = "_system_shock"
    ATTR_EXTENSIONS_SHOCKS = "_extensions_shocks"

    def __init__(self):
        """
        Constructor of class `AccountsShockDirector`
        """
        self.system_shock_director: SystemShockDirector = SystemShockDirector()
        self.extension_shock_director: ExtensionShockDirector = (
            ExtensionShockDirector()
        )

    def reset(self):
        self.system_shock_director.reset()
        self.extension_shock_director.reset()

    def set_regions(self, regions: dl.RegionsDL):
        """
        Setter for regions
        """
        self.system_shock_director.set_regions(regions)
        self.extension_shock_director.set_regions(regions)

    def set_final_demand_categories(
        self, final_demand_categories: dl.FinalDemandCategoriesDL
    ):
        """
        Setter for final demand categories
        """
        self.system_shock_director.set_final_demand_categories(
            final_demand_categories
        )
        self.extension_shock_director.set_final_demand_categories(
            final_demand_categories
        )

    def set_sectors(self, sectors: dl.SectorsDL):
        """
        Setter for sectors
        """
        self.system_shock_director.set_sectors(sectors)
        self.extension_shock_director.set_sectors(sectors)

    def make_from_system_and_extensions_shocks(
        self,
        system_shock: SystemShock,
        extensions_shocks: dict[str, ExtensionShock],
    ) -> AccountsShock:
        """
        Make a shock directly from a system shock and a map of
        extensions shocks

        Parameters:
            system_shock (SystemShock)
                The system shock
            extensions_shocks (dict[str, ExtensionShock])
                The map of extensions shocks
        Returns:
            AccountsShock
        """
        log.debug(
            "Make AccountsShock object from a system shock and "
            "extensions shocks"
        )

        # Initialize shock object
        shock = AccountsShock()

        # Set id
        setattr(
            shock,
            self.ATTR_ID,
            AccountsShockIdentity(
                base_year=system_shock.id.base_year,
                proj_year=system_shock.id.proj_year,
                scenario_name=system_shock.id.scenario_name,
                extension_names=[],
            ),
        )

        # Set system shock
        setattr(shock, self.ATTR_SYSTEM_SHOCK, system_shock)

        # Set extensions shocks
        # Initialize empty map
        setattr(shock, self.ATTR_EXTENSIONS_SHOCKS, {})
        # Add extensions shocks
        for extension_shock in extensions_shocks.values():
            shock.add_extension_shock(extension_shock)

        log.warning(
            "Need to check consistency between system and extension "
            "shocks in function make_from_system_and_extensions_shocks."
        )

        return shock

    def make_from_path(
        self,
        path: str,
        extensions_names: list[str] = None,
        raise_error_if_extension_not_found: bool = True,
        load_data: bool = True,
    ) -> AccountsShock:
        """
        Make a 'Shock' object from the files found in path.

        The path shall contain two directories:
            - *system*

              Refer to :meth:`SystemShockDirector.make_from_path` for the
              content of this directory.

            - *extensions* with for each extension, a subdirectory
              <extension_name>.

              Refer to :meth:`ExtensionShockDirector.make_from_path` for the
              content of these subdirectories.

        Parameters:
            path (dict):
                The path to the directory containing the files.
            extensions_names (list[str]):
                The names of the extensions shocks which shall be loaded.
                If there are others in the directory, they will be ignored.
            raise_error_if_extension_not_found (bool):
                True if an exception shall be raised when an extension shock
                required in extensions_names is not found, False otherwise
                (default to True)
            load_data (bool):
                True if the dataframes shall be initialized with the values
                read in the files (default to True)
        Returns
            Shock
        """
        log.debug(f"Make AccountsShock object from path {path}")

        # Initialize shock object
        shock = AccountsShock()

        # Set system shock
        setattr(
            shock,
            self.ATTR_SYSTEM_SHOCK,
            self.system_shock_director.make_from_path(
                path=os.path.join(path, cst.DIR_SYSTEM), load_data=load_data
            ),
        )

        # Set identity
        setattr(
            shock,
            self.ATTR_ID,
            AccountsShockIdentity(
                base_year=shock.system_shock.id.base_year,
                extension_names=[],
            ),
        )

        # Set extensions shocks
        # Initialize empty map
        setattr(shock, self.ATTR_EXTENSIONS_SHOCKS, {})
        # Add extensions shocks
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
                                f"Can't load extension shock '{name}'. Directory "
                                "does not exist."
                            )
                            raise MEExtensionNotFound(name)
                        else:
                            log.warning(
                                f"No shock found for extension '{name}'"
                            )

            for element in ext_directories:
                # Skip this directory if not in the extension names if given
                if (
                    extensions_names is not None
                    and element not in extensions_names
                ):
                    log.debug(f"Ignore directory {element}")
                    continue

                full_path = os.path.join(path, cst.DIR_EXTENSIONS, element)
                if os.path.isdir(full_path):
                    file_path = os.path.join(full_path, cst.FILE_INFO)
                    try:
                        shock.add_extension_shock(
                            self.extension_shock_director.make_from_path(
                                path=full_path, load_data=load_data
                            )
                        )
                    except FileNotFoundError:
                        log.warning(f"File {file_path} not found. Passing...")
        else:
            log.warning(f"No 'extensions' directory. Passing...")

        return shock

    def make_from_accounts(
        self, accounts_from: Accounts, accounts_to: Accounts
    ) -> AccountsShock:
        """
        Make an accounts shock from the difference between two accounts

        Parameters:
            accounts_from (Accounts):
                The reference accounts
            accounts_to (Accounts):
                The projected accounts

        Returns:
            AccountsShock
        """
        log.debug("Make AccountsShock object from the difference of accounts")

        # Initialize shock object
        shock = AccountsShock()

        # Set system shock
        setattr(
            shock,
            self.ATTR_SYSTEM_SHOCK,
            self.system_shock_director.make_from_systems(
                system_from=accounts_from.system,
                system_to=accounts_to.system,
            ),
        )

        # Set id
        setattr(
            shock,
            self.ATTR_ID,
            AccountsShockIdentity(
                base_year=shock.system_shock.id.base_year,
                proj_year=shock.system_shock.id.proj_year,
                scenario_name=shock.system_shock.id.scenario_name,
                extension_names=[],
            ),
        )

        # Set extensions shocks
        # Initialize empty map
        setattr(shock, self.ATTR_EXTENSIONS_SHOCKS, {})
        # Add extensions shocks
        for extension_from in accounts_from.list_extensions():
            try:
                extension_to = accounts_to.get_extension(
                    name=extension_from.name
                )
                shock.add_extension_shock(
                    self.extension_shock_director.make_from_extensions(
                        extension_from=extension_from,
                        extension_to=extension_to,
                    )
                )
            except MEExtensionNotFound:
                log.debug(
                    f"No extension '{extension_from.name}' in projected "
                    f"accounts. Passing..."
                )
            except NotImplementedError:
                log.error(
                    f"Can't process extension '{extension_from.name}'. "
                    f"Passing..."
                )

        return shock


# pylint: disable=W0603
def get_director(reset: bool = False) -> AccountsShockDirector:
    """
    Returns the `AccountsShock` director singleton. If reset is True, call the
    director method reset() before returning it.
    """
    global accounts_shock_director

    if accounts_shock_director is None:
        accounts_shock_director = AccountsShockDirector()
    if reset:
        accounts_shock_director.reset()
    return accounts_shock_director


# pylint: enable=W0603
