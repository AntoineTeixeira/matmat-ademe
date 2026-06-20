"""
EXIOBASE 3 EEIO adapter (MatMat).

This module defines :class:`~Exiobase3EEIO`, an adapter that loads an EXIOBASE
v3 EE-GMRIO dataset via ``pymrio``, extracts selected satellite extensions,
and exports a MatMat-compatible Accounts object.

Typical workflow
----------------
1. Instantiate the adapter with an :class:`~Exiobase3EEIOIdentity`.
2. Call ``execute()`` (or sequentially ``load()``, ``process()``, ``save()``).

Input expectations
------------------
- The adapter expects an EXIOBASE archive located at:
  ``{path_in}/{version}/IOT_{base_year}_{system}.zip``.
- If missing, the adapter attempts to download the archive using
  ``pymrio.download_exiobase3`` with the DOI associated to the selected version.

Output
------
- The MatMat Accounts object is exported to:
  ``{path_out}/{version}_{base_year}/`` in the requested formats.

Identity fields
---------------
The identity specifies the dataset location and scope:
- path_in, path_out
- export_format (e.g. ["pickle"])
- version (supported: from 3.8.2 to 3.10.2)
- system (e.g. "pxp", "ixi")
- base_year (1995–2022)
- extension_names (subset of supported extensions)

Example identity (JSON)
-----------------------
{
  "path_in": "...",
  "path_out": "...",
  "export_format": ["pickle"],
  "version": "3.8.2",
  "system": "pxp",
  "base_year": 2015,
  "extension_names": ["ghg_emissions", "energy", "..."]
}
"""

import os
import copy

import requests

from typing import Dict, Any

import pandas as pd
import pymrio
from pymrio import IOSystem

import matmat.utils.constants as cst
import matmat.utils.logging as log


from matmat.workflows.adapters.core import AbstractAdapter
from matmat.workflows.adapters.accounts.exiobase3_eeio.identity import (
    Exiobase3EEIOIdentity,
)
import matmat.workflows.adapters.accounts.exiobase3_eeio.extractor as cls_extractor

from matmat.core.detail_level import core as dl

from matmat.core.accounts.core import Accounts
from matmat.core.accounts.system.core import System
from matmat.core.accounts.system.identity import SystemIdentity
from matmat.core.accounts.system.strategies.calcul import EnumSystemCalcul
from matmat.core.accounts.extension.core import Extension
from matmat.core.accounts.extension.identity import ExtensionIdentity
from matmat.core.accounts.extension.strategies.calcul import (
    EnumExtensionCalcul,
)
import matmat.core.accounts.system.builder as sys_builders
import matmat.core.accounts.extension.builder as ext_builders
import matmat.core.accounts.builder as acc_builders


class Exiobase3EEIO(AbstractAdapter):
    EXTRACTOR_MAP = {
        cst.GHG_EMISSIONS: cls_extractor.GreenhouseGasEmissionsExtractor,
        cst.ENERGY: cls_extractor.EnergyExtractor,
        cst.RAW_MATERIALS: cls_extractor.RawMaterialsExtractor,
        cst.LABOR: cls_extractor.LabourExtractor,
        cst.VALUE_ADDED: cls_extractor.ValueAddedExtractor,
        cst.WATER: cls_extractor.WaterExtractor,
        cst.LAND_USE: cls_extractor.LandUseExtractor,
        cst.BIOGEOCHEMICAL: cls_extractor.BiogeochemicalExtractor,
    }
    SUPPORTED_VERSIONS_TO_DOI = {
        "3.8.2": "10.5281/zenodo.5589597",
        "3.8.2-restricted": None,
        "3.9.4": "10.5281/zenodo.14614930",
        "3.9.5": "10.5281/zenodo.14869924",
        "3.9.6": "10.5281/zenodo.15689391",
        "3.10.1": "10.5281/zenodo.18937492",
        "3.10.2": "10.5281/zenodo.20051562",
    }
    SUPPORTED_BASE_YEAR_RANGE = {
        elt: (
            range(1995, 2022 + 1)
            if int(elt.split(".")[1]) < 10
            # else range(1995, 2024 + 1) # 2023 and 2024 not complete yet
            else range(1995, 2022 + 1)
        )
        for elt in SUPPORTED_VERSIONS_TO_DOI.keys()
    }
    KEY_PYMRIO_ACCOUNTS = "pymrio_accounts"
    KEY_LOCAL_ACCOUNTS = "local_accounts"
    KEY_EXTENSION_CATEGORY = "indicator"

    # Identity
    _id: Exiobase3EEIOIdentity

    def __init__(
        self, id_: Exiobase3EEIOIdentity, no_confirm: bool = False
    ) -> None:
        """
        Initialize the adapter for the EXIOBASE v3 EE-GMRIO database.

        The adapter is configured from an identity object describing the target
        EXIOBASE release (version/system/base_year) and the requested satellite accounts
        (extensions). The constructor:
          - builds input/output paths from the identity,
          - checks that the requested EXIOBASE version is supported,
          - validates requested extension names,
          - initializes internal containers for raw and processed data, including
            detail-level objects.

        Parameters
        ----------
        id_ : Exiobase3EEIOIdentity
            Identity object specifying:
            - path_in : str
            - path_out : str
            - export_format : [str]
                (e.g., "pkl", "excel", "csv)
            - version : str
                EXIOBASE version identifier (must be present in
                SUPPORTED_VERSIONS_TO_DOI).
            - system : str
                System type (e.g., "ixi", "pxp").
            - base_year : int | str
                Reference year used to build input path.
            - extension_names : list[str]
                List of requested satellite accounts (must be included in
                EXTRACTOR_MAP.keys()).

        Attributes Set
        --------------
        _path_in : str
            Updated with "/{version}/IOT_{base_year}_{system}" suffix.
        _path_out : str
            Updated with "/{version}_{system}_{base_year}" suffix.
        _doi : str | None
            DOI associated with the selected EXIOBASE version.
        input_data : dict
            Contains an empty IOSystem(), initialized detail levels and bridge matrices.
        processed_data : dict
            Contains an empty IOSystem() and an empty Accounts() placeholder.

        Raises
        ------
        ValueError
            If `id_.version` is not supported or if one or more requested extensions
            are not available.
        """
        super().__init__(
            id_=id_, perform_validation=False, no_confirm=no_confirm
        )

        self._validate_version()
        self._validate_base_year()
        self._validate_extensions()

        self._build_paths()

        detail_levels = self._init_detail_levels()

        self._init_data_containers(detail_levels=detail_levels)

    @classmethod
    def name(cls) -> str:
        return "exiobase3_eeio"

    def _build_paths(self) -> None:
        """Build input/output paths from the identity card."""
        self.path_in = os.path.join(
            self.path_in,
            self._id.version,
            f"IOT_{self._id.base_year}_{self._id.system}",
        )
        self.path_out = os.path.join(
            self.path_out,
            f"{self._id.version}_{self._id.system}_{self._id.base_year}",
        )

    def _validate_version(self) -> None:
        """Validate requested EXIOBASE version and set DOI."""
        if self._id.version not in self.SUPPORTED_VERSIONS_TO_DOI:
            supported = ", ".join(self.SUPPORTED_VERSIONS_TO_DOI.keys())
            raise ValueError(
                f"Version '{self._id.version}' is not supported. Supported versions: {supported}."
            )
        self._doi = self.SUPPORTED_VERSIONS_TO_DOI[self._id.version]

    def _validate_base_year(self) -> None:
        """
        Validate that the requested reference year is supported by this adapter.
        """
        try:
            year = int(self._id.base_year)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid year {self._id.year!r}. Expected an integer year."
            ) from exc

        if year not in self.SUPPORTED_BASE_YEAR_RANGE[self._id.version]:
            min_year = self.SUPPORTED_BASE_YEAR_RANGE[self._id.version].start
            max_year = (
                self.SUPPORTED_BASE_YEAR_RANGE[self._id.version].stop - 1
            )
            raise ValueError(
                f"Unsupported year {year}. Supported years are {min_year}–{max_year} "
                f"for EXIOBASE v{self._id.version} EEIO datasets handled by this adapter."
            )

        # Normalize the identity in-place to avoid str instead of int
        self._id.base_year = year

    def _validate_extensions(self) -> None:
        """Validate requested extension names."""
        requested = set(self._id.extension_names)
        available = set(self.EXTRACTOR_MAP.keys())
        invalid = sorted(requested - available)
        if invalid:
            raise ValueError(
                f"Unavailable extensions: {invalid}. Available extensions: {sorted(available)}."
            )

    def _init_detail_levels(self) -> Dict[str, Any]:
        """
        Initialize detail-level objects.

        Returns
        -------
        dict
            Mapping {detail_level_kind: detail_level_object}, with a nested mapping
            for extension categories keyed by extension name.
        """
        detail_levels: Dict[str, Any] = {
            dl.DetailLevelKind.SECTORS.value: dl.SectorsDL(),
            dl.DetailLevelKind.REGIONS.value: dl.RegionsDL(),
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value: dl.FinalDemandCategoriesDL(),
            dl.DetailLevelKind.EXTENSION_CATEGORIES.value: {
                ext: dl.ExtensionCategoriesDL(ext)
                for ext in self._id.extension_names
            },
        }

        return detail_levels

    def _init_data_containers(self, detail_levels: Dict[str, Any]) -> None:
        """Initialize `input_data` and `processed_data` containers."""
        self.input_data = {self.KEY_PYMRIO_ACCOUNTS: IOSystem()}
        self.processed_data = {
            self.KEY_DL: detail_levels,
            self.KEY_PYMRIO_ACCOUNTS: IOSystem(),
            self.KEY_LOCAL_ACCOUNTS: Accounts(),
        }

    def load(self) -> None:
        """
        Download (if needed) and load the raw EXIOBASE3 EE-GMRIO database.

        The method ensures the EXIOBASE `.zip` archive exists in the input folder,
        downloading it via `pymrio.download_exiobase3()` when missing, then parses
        the archive into a `pymrio.IOSystem`.

        Raises
        ------
        ConnectionError
            If the DOI resolver cannot be reached when verifying the requested version.
        ValueError
            If the DOI resolver returns an HTTP error status.
        OSError
            If local file operations fail.
        """

        zip_path = f"{self.path_in}.zip"
        storage_folder = os.path.dirname(self.path_in)
        os.makedirs(storage_folder, exist_ok=True)

        # Download if missing
        if not os.path.isfile(zip_path):
            if self._doi is not None:
                url = f"https://doi.org/{self._doi}"
                try:
                    r = requests.head(url, allow_redirects=True, timeout=10)
                    if r.status_code >= 400:
                        raise ValueError(
                            f"The DOI URL '{url}' is not accessible (status {r.status_code})."
                        )
                except requests.RequestException as e:
                    raise ConnectionError(
                        f"An error occurred while verifying DOI '{self._doi}': {e}"
                    ) from e

            log.info("Download EXIOBASE 3 online started.")
            pymrio.download_exiobase3(
                storage_folder=storage_folder,
                system=self._id.system,
                years=self._id.base_year,
                doi=self._doi,
            )
            log.info("Download EXIOBASE 3 online completed.")

        # Parse locally
        log.info("Load EXIOBASE 3 locally started.")
        accounts = pymrio.parse_exiobase3(zip_path)
        self.input_data[self.KEY_PYMRIO_ACCOUNTS] = copy.deepcopy(accounts)
        self.processed_data[self.KEY_PYMRIO_ACCOUNTS] = copy.deepcopy(accounts)
        log.info("Load EXIOBASE 3 locally completed.")

    def process(self):
        """
        Extracts and computes all requested extensions listed in
        `self._extension_names`. Assumes `self._extension_names` was validated
        during initialization.
        """
        self._concat_extension_in_pymrio_format()
        self._extract_and_organize_mrio_extensions()
        self._build_detail_levels()
        self._build_accounts()
        self._fill_system()
        self._fill_extensions()

    # ToDo: to clean!
    def _concat_extension_in_pymrio_format(self):
        """Concatenate all pymrio extensions into a single extension.

        This replaces all existing extensions in the MRIO accounts object
        by one aggregated extension named 'extensions'.
        """
        accounts = self.get_processed_data(self.KEY_PYMRIO_ACCOUNTS)
        extensions = pymrio.concate_extension(
            [getattr(accounts, ext) for ext in accounts.get_extensions()],
            name=cst.KEY_EXTENSIONS,
        )

        ############## TEMP ##############
        # Harmonize stressor axis name across versions
        for attr in ("F", "F_Y", "unit"):
            df = getattr(extensions, attr)
            if not df is None:
                df.index = df.index.set_names(self.KEY_EXTENSION_CATEGORY)
            setattr(extensions, attr, df)
        ############## TEMP ##############

        accounts.remove_extension()
        accounts.extensions = extensions

    def _extract_and_organize_mrio_extensions(self):
        """
        Extract requested satellite extensions and attach them to the pymrio accounts.

        Each extension listed in ``self._id.extension_names`` is processed using the
        corresponding extractor in ``self.EXTRACTOR_MAP`` and stored as an attribute
        of the accounts. The original aggregated extension container is then removed.
        """
        accounts = self.get_processed_data(self.KEY_PYMRIO_ACCOUNTS)
        extensions = accounts.extensions

        for extension_name, extractor_cls in self.EXTRACTOR_MAP.items():
            if extension_name in self._id.extension_names:
                extractor = extractor_cls(extensions)
                setattr(accounts, extension_name, extractor.extract())
        accounts.remove_extension(extensions.name)

    def _build_detail_levels(self):
        """
        Populate detail-level objects with reference tables derived from MRIO accounts.

        This method fills ``self.processed_data[self.KEY_DL]`` by computing the
        corresponding reference DataFrames (sectors, regions, final demand categories,
        and extension categories) from the processed pymrio accounts object.

        Notes
        -----
        - The regions table is augmented with an origin column (domestic by default).
        - Extension categories are generated for each requested extension in
          ``self._id.extension_names`` using the extension ``unit`` index.
        """
        accounts = self.get_processed_data(self.KEY_PYMRIO_ACCOUNTS)
        dl_store = self.get_processed_data(self.KEY_DL)

        def _sectors_df() -> pd.DataFrame:
            return pd.DataFrame(accounts.get_sectors())

        def _regions_df() -> pd.DataFrame:
            df = pd.DataFrame(accounts.get_regions())
            df[cst.IDX_ORIGIN] = cst.IDX_DOMESTIC
            return df.iloc[:, ::-1]  # origin column first

        def _y_categories_df() -> pd.DataFrame:
            y_cat = accounts.get_Y_categories()
            y_cat.name = cst.IDX_Y_CATEGORY
            return pd.DataFrame(y_cat)

        def _extensions_category_df(ext_name: str) -> pd.DataFrame:
            idx = getattr(accounts, ext_name).unit.index
            return idx.to_frame(False)

        builders = {
            dl.DetailLevelKind.SECTORS.value: _sectors_df,
            dl.DetailLevelKind.REGIONS.value: _regions_df,
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value: _y_categories_df,
            dl.DetailLevelKind.EXTENSION_CATEGORIES.value: _extensions_category_df,
        }

        for kind, obj in dl_store.items():
            if kind != dl.DetailLevelKind.EXTENSION_CATEGORIES.value:
                obj.df = builders[kind]()
            else:
                for ext_name in self._id.extension_names:
                    obj[ext_name].df = builders[kind](ext_name)

    def _build_accounts(self) -> None:
        """
        Build the accounts object from an empty system and a set of empty extensions.

        The system and extensions are created from the configured detail levels
        (sectors, regions, final demand categories, and extension categories)
        using the default calculation strategies embedded in this builder:
        - system: ``EnumSystemCalcul.STANDARD``,
        - extensions: ``EnumExtensionCalcul.GROSS_OUTPUT``.

        The resulting accounts object is stored in
        ``self.processed_data[self.KEY_LOCAL_ACCOUNTS]``.
        """
        system = self._build_system()
        extensions = self._build_extensions()
        acc_dir = acc_builders.get_director(reset=True)
        accounts = acc_dir.make_from_system_and_extensions(
            system=system, extensions=extensions
        )
        self.processed_data[self.KEY_LOCAL_ACCOUNTS] = accounts

    def _build_system(self) -> System:
        """
        Build an empty system structure from configured detail levels.

        The system dimensions are taken from ``self.processed_data[self.KEY_DL]``:
        sectors, regions, and final demand categories. The system identity is built
        using the current base year and the default system strategy
        (``EnumSystemCalcul.STANDARD``).

        Returns
        -------
        System
            A system object initialized with the requested dimensions and identity.
        """
        sys_dir = sys_builders.get_director(reset=True)
        sys_dir.set_sectors(sectors=self.p_dl_sectors)
        sys_dir.set_regions(regions=self.p_dl_regions)
        sys_dir.set_final_demand_categories(
            final_demand_categories=self.p_dl_final_demand_categories
        )

        sys_id = SystemIdentity(
            strategy=EnumSystemCalcul.STANDARD.value,
            base_year=self._id.base_year,
        )

        # Make system
        return sys_dir.make_from_id(id_=sys_id)

    def _build_extensions(self) -> dict[str, Extension]:
        """
        Build empty extensions from configured detail levels.

        Each extension is created with the common system dimensions (sectors,
        regions, final demand categories) and its own extension categories from
        ``self.processed_data[self.KEY_DL]``. Extension identities are initialized
        with the current base year and the default extension strategy
        (``EnumExtensionCalcul.GROSS_OUTPUT``).

        Returns
        -------
        dict[str, Extension]
            Mapping from extension name to the corresponding empty `Extension` object.
        """
        ext_dir = ext_builders.get_director(reset=True)
        ext_dir.set_sectors(self.p_dl_sectors)
        ext_dir.set_regions(regions=self.p_dl_regions)
        ext_dir.set_final_demand_categories(
            final_demand_categories=self.p_dl_final_demand_categories
        )

        extensions = {}
        for extension_name in self._id.extension_names:
            ext_id = ExtensionIdentity(
                base_year=self._id.base_year,
                extension_name=extension_name,
                strategy=EnumExtensionCalcul.GROSS_OUTPUT.value,
            )
            ext_dir.set_extension_categories(
                self.get_p_dl_extension_categories(extension_name)
            )
            extensions[extension_name] = ext_dir.make_from_id(id_=ext_id)

        return extensions

    def _fill_system(self) -> None:
        """
        Fill the local (empty) system from the source (populated) pymrio IOSystem.

        The transfer is performed by copying values from the pymrio matrices into the
        corresponding local datasets (A, x, Y, Z, unit).

        Notes
        -----
        - Values are copied without reindexing (by position). This assumes that the
          local system was built with the same dimensions and ordering as the source.
        - This method mutates the local accounts system stored in
          ``self.processed_data[self.KEY_LOCAL_ACCOUNTS]``.
        """
        system_local = self.get_processed_data(self.KEY_LOCAL_ACCOUNTS).system
        accounts_pymrio = self.get_processed_data(self.KEY_PYMRIO_ACCOUNTS)

        for var in [cst.X, cst.Y, cst.Z]:
            src = getattr(accounts_pymrio, var)
            dst = getattr(system_local, var)

            if src.shape != dst.df.shape:
                raise ValueError(
                    f"Shape mismatch for {var}: "
                    f"src={src.shape}, dst={dst.df.shape}"
                )

            dst.set_values(src.values)

        src_unit = getattr(accounts_pymrio, cst.UNIT)
        dst_unit = getattr(system_local, cst.UNIT)
        dst_unit.set_values(src_unit.values[0][0])

        for data in system_local.dataset.data:
            data.clean_residual_nan()

        system_local.check_market_balance()

    def _fill_extensions(self) -> None:
        """
        Fill the local (empty) extensions from the source (populated) pymrio IOSystem.

        Notes
        -----
        - Values are copied without reindexing (by position). This assumes that each
          local extension was built with the same dimensions and ordering as its pymrio
          counterpart.
        - This method mutates the local accounts extensions stored in
          ``self.processed_data[self.KEY_LOCAL_ACCOUNTS]``.
        """
        # Map: local attribute name -> pymrio attribute name
        var_mapping = {cst.F_X_DOM: "F", cst.UNIT: "unit"}

        extensions_local = self.get_processed_data(
            self.KEY_LOCAL_ACCOUNTS
        ).extensions
        accounts_pymrio = self.get_processed_data(self.KEY_PYMRIO_ACCOUNTS)

        for extension_name, ext_local in extensions_local.items():
            ext_src = getattr(accounts_pymrio, extension_name)

            for local_attr, src_attr in var_mapping.items():
                src = getattr(ext_src, src_attr)
                dst = getattr(ext_local, local_attr)

                if src.shape != dst.df.shape:
                    raise ValueError(
                        f"Shape mismatch for extension '{extension_name}', '{local_attr}': "
                        f"src={src.shape}, dst={dst.df.shape}"
                    )
                dst.set_values(src.values)

    # ToDo : add fct to access and save detail levels at accounts level
    def save_detail_levels(self):
        for k, v in self.get_processed_data(self.KEY_DL).items():
            if k != dl.DetailLevelKind.EXTENSION_CATEGORIES.value:
                v.save_to_path(path=self.path_out)
            else:
                for ext_name in v.keys():
                    v[ext_name].save_to_path(path=self.path_out)

    def save(self):

        self.processed_data[self.KEY_LOCAL_ACCOUNTS].save_to_path(
            path=self.path_out,
            export_format=self._export_formats_names,
        )
        self.save_detail_levels()
