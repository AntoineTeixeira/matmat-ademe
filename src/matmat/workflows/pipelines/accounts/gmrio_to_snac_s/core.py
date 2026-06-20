"""
Pipeline for extracting SNAC-S accounts from a global MRIO database.

This module implements the core transformation workflow used to derive
SNAC-S accounts from a global multi-regional input-output database already
formatted as MatMat accounts.

The input accounts are expected to describe a global MRIO system with several
regions and no import-origin regions. The output accounts follow the SNAC-S
accounting convention, where regions are split into domestic and import origins.

The pipeline is database-agnostic. Database-specific loading, naming
conventions, and raw data formatting must be handled upstream by dedicated
adapters, such as an EXIOBASE adapter. This module assumes that the input data
have already been converted to the MatMat data model.

The current workflow performs the following operations:

1. Load input GMRIO accounts, regional detail level, and bridge matrices.
2. Check that the input accounts, regional detail level, and bridge matrices
   are compatible with the GMRIO-to-SNAC-S transformation.
3. Harmonise final demand categories using a user-defined bridge matrix.
4. Build regional bridge matrices distinguishing domestic and import origins.
5. Convert the production system to a SNAC-S system by:
   - aggregating regions according to the regional bridge;
   - deriving import and exports vectors from GMRIO system;
   - assigning import and exports vectors to x and Y system data.
6. Build domestic extensions by aggregating GMRIO extensions over the SNAC-S
   regional structure.
7. Build import extensions using rest-of-world multipliers under one of the
   available assumptions for foreign production feedbacks.
8. Optionally calculate the resulting SNAC-S accounts if requested by the
   pipeline identity.
9. Save the resulting SNAC-S accounts.

Notes
-----
The transformation relies on the following assumptions:

- Input accounts must use the standard system strategy.
- Input extensions must be gross-output-based.
- Required system variables are `x`, `Y`, and `Z`.
- Required extension variables include `F_x_dom`.
- The final demand bridge must contain an export category.
- The regional detail level must allow domestic/import origins to be derived.

The import-extension multipliers can be computed using three modes:

`foreign_isolated`
    Use the isolated rest-of-world production system. Domestic-foreign feedback
    loops are excluded, and only impacts occurring outside the domestic block
    are accounted for.

`foreign_global_feedback`
    Use the full global production system while setting domestic direct
    extensions to zero. Domestic-foreign feedback loops are included, but only
    impacts occurring outside the domestic block are accounted for.

`world_global_feedback`
    Use the full global production system and the full set of direct
    extensions. Domestic-foreign feedback loops are included, and impacts
    occurring both inside and outside the domestic block are accounted for.
"""

import os

from typing import Dict
from numpy.typing import NDArray

import pandas as pd
import numpy as np

import matmat.utils.logging as log

from matmat.workflows.pipelines.core import AbstractPipeline
from matmat.workflows.pipelines.accounts.gmrio_to_snac_s.identity import (
    GmrioToSnacSIdentity,
)

from matmat.core.accounts.core import Accounts
from matmat.core.accounts.system.core import System

from matmat.core.detail_level import core as dl
from matmat.core.bridge.core import Bridge

from matmat.core.accounts import builder as a_builder
from matmat.core.detail_level import factory as dl_factory
from matmat.core.bridge import factory as bridge_factory

import matmat.utils.constants as cst

from matmat.core.accounts.system.data.factory import make_data

from matmat.core.accounts.system.data.core import (
    LData,
    AData,
    XData,
    ZData,
    YData,
)
from matmat.core.accounts.extension.data.core import SxDomData, MRoWData

import matmat.core.accounts.extension.builder as ext_builders
from matmat.core.accounts.extension.core import Extension
from matmat.core.accounts.extension.identity import ExtensionIdentity
from matmat.utils.errors import MEDataNotSuitableForWorkflow


class GmrioToSnacS(AbstractPipeline):
    """
    Pipeline converting global MRIO accounts into SNAC-S accounts.

    The pipeline takes MatMat-compatible GMRIO accounts as input and produces
    SNAC-S accounts in which domestic and import-origin regions are explicitly
    represented.

    Parameters
    ----------
    id_ : GmrioToSnacSIdentity
        Pipeline identity containing input/output paths, selected extensions,
        export format, and options such as the rest-of-world multiplier mode.
    no_confirm : bool, default=False
        If True, disables interactive confirmation steps inherited from
        `AbstractPipeline`.

    Attributes
    ----------
    input_data : dict
        Raw inputs loaded by the pipeline, including GMRIO accounts, detail
        levels, and bridge matrices.
    processed_data : dict
        Intermediate and output data produced by the pipeline, including
        final-demand-reformatted accounts, regional bridges, and SNAC-S
        accounts.
    """

    KEY_ACCOUNTS = "gmrio_accounts"
    KEY_ACCOUNTS_FD_AGG = "gmrio_accounts_fd_agg"
    KEY_ACCOUNTS_SNAC_S = "snac_s_accounts"

    KEY_M_ROW_MODE_1 = "foreign_isolated"
    KEY_M_ROW_MODE_2 = "foreign_global_feedback"
    KEY_M_ROW_MODE_3 = "world_global_feedback"

    M_ROW_MODES = {
        KEY_M_ROW_MODE_1: (
            "Use the isolated rest-of-world production system."
            "Domestic-foreign feedback loops are excluded, and only impacts "
            "occurring outside the domestic block are accounted for."
        ),
        KEY_M_ROW_MODE_2: (
            "Use the full global production system while setting domestic "
            "direct environmental extensions to zero."
            "Domestic-foreign feedback loops are included, but only impacts "
            "occurring outside the domestic block are accounted for."
        ),
        KEY_M_ROW_MODE_3: (
            "Use the full global production system and the full set of direct "
            "environmental extensions."
            "Domestic-foreign feedback loops are included, and impacts occurring "
            "both inside and outside the domestic block are accounted for."
        ),
    }

    _id: GmrioToSnacSIdentity

    @classmethod
    def name(cls) -> str:
        return "gmrio_to_snac_s"

    def __init__(self, id_: GmrioToSnacSIdentity, no_confirm: bool = False):
        super().__init__(id_=id_, no_confirm=no_confirm)

        # Initialize input_data and processed_data containers
        self.input_data = {
            self.KEY_ACCOUNTS: Accounts(),
            self.KEY_DL: {
                dl.DetailLevelKind.REGIONS.value: dl.DetailLevelKind.REGIONS
            },
            self.KEY_BRIDGES: {
                dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value: Bridge(
                    dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES
                )
            },
        }
        self.processed_data = {
            self.KEY_BRIDGES: {
                dl.DetailLevelKind.REGIONS.value: Bridge(
                    dl.DetailLevelKind.REGIONS
                ),
                cst.IDX_DOMESTIC: Bridge(dl.DetailLevelKind.REGIONS),
                cst.IDX_IMPORT: Bridge(dl.DetailLevelKind.REGIONS),
            },
            self.KEY_ACCOUNTS_FD_AGG: Accounts(),
            self.KEY_ACCOUNTS_SNAC_S: Accounts(),
        }

    def load(self) -> None:
        self._load_dl()
        self._load_bridges()
        self._load_accounts()

    def _load_dl(self) -> None:
        log.info("### LOAD REGION DETAIL LEVEL ###")
        self.input_data[self.KEY_DL][dl.DetailLevelKind.REGIONS.value] = (
            dl_factory.make_regions_dl_from_path(
                path=self.id.path_in.detail_levels.split(cst.DL_FILE)[0],
                file_name=cst.DL_FILE,
            )
        )  # ToDo: update with make_dl_dict_from_path()

    def _load_bridges(self) -> None:
        log.info("### LOAD FINAL DEMAND BRIDGE ###")
        self.input_data[self.KEY_BRIDGES] = (
            bridge_factory.make_bridge_dict_from_path(
                path=os.path.dirname(self.path_in.bridges),
                file_name=os.path.basename(self.path_in.bridges),
                extension_names=self.id.extension_names,
                load_regions=False,
                load_sectors=False,
                load_final_demand_categories=True,
                load_extension_categories=False,
            )
        )

    def _load_accounts(self) -> None:
        """
        Load existing gmrio accounts from path_in

        Fill self.input_data[self.KEY_ACCOUNTS]
        """
        log.info("### LOAD GMRIO ACCOUNTS ###")
        self.input_data[self.KEY_ACCOUNTS] = a_builder.get_director(
            reset=True
        ).make_from_path(
            path=self.path_in.accounts,
            extensions_names=self._id.extension_names,
            load_data=True,
        )

    def process(self) -> None:

        self._check_loads()

        self.processed_data[self.KEY_ACCOUNTS_FD_AGG] = (
            self._reformat_accounts_final_demand_categories(
                input_accounts=self.input_data[self.KEY_ACCOUNTS],
                final_demand_bridge=self.i_bridge_final_demand_categories,
            )
        )

        self._build_region_bridges()
        self._convert_accounts_to_snac_s()

    def _check_loads(self) -> None:
        """
        Validate that loaded inputs are compatible with the transformation.

        The method checks that:

        - input accounts do not already contain import-origin regions;
        - the system uses the standard strategy;
        - all input extensions are gross-output-based;
        - required system variables are available and non-empty;
        - required extension variables are available and non-empty;
        - regional detail levels are consistent between input accounts and the
          user-provided detail level;
        - the final demand bridge contains an export category.

        Raises
        ------
        ValueError
            If one of the compatibility checks fails.
        """
        accounts = self.get_input_data(self.KEY_ACCOUNTS)

        # check origin only with domestic in accounts
        accounts_dl_region = accounts.detail_levels[
            dl.DetailLevelKind.REGIONS.value
        ]
        if cst.IDX_IMPORT in accounts_dl_region.df[cst.IDX_ORIGIN].tolist():
            raise ValueError(
                "The input accounts are not GMRIO-compatible. Its detail levels"
                " contain import regions."
            )

        # check system strategy is standard
        system_strategy = accounts.system.id.strategy
        if not system_strategy == cst.STRATEGY_STANDARD:
            raise ValueError(
                "The input accounts system is not standard. The GMRIO to "
                "SNAC-S pipeline only works on standard system yet."
            )

        # check extensions strategy only gross_output_based
        for k, v in accounts.extensions.items():
            extension_strategy = v.id.strategy
            if not extension_strategy == cst.STRATEGY_GROSS_OUTPUT_BASED:
                raise ValueError(
                    f"The input accounts extension {k} is not gross "
                    f"output based."
                )

        # check system fluxes not empty
        variables = [cst.X, cst.Y, cst.Z]
        for var in variables:
            check_var = getattr(accounts.system.dataset, var)
            if check_var.is_df_empty():
                raise ValueError(
                    f"The variable {var} in input accounts system is empty."
                )

        # check F_x_dom extensions fluxes not empty
        var = cst.F_X_DOM
        for k, v in accounts.extensions.items():
            check_var = getattr(v.dataset, var)
            if check_var.is_df_empty():
                raise ValueError(
                    f"The variable {var} in input accounts extensions {k} "
                    f"is empty."
                )

        # check region are the same in accounts than in input detail levels
        def reorder_dl(df: pd.DataFrame) -> pd.DataFrame:
            output = df.sort_values(by=df.columns.tolist())
            output.reset_index(drop=True, inplace=True)
            return output

        regions_accounts = accounts_dl_region.df.drop(cst.IDX_ORIGIN, axis=1)
        regions_accounts = reorder_dl(regions_accounts)
        regions_dl = self.i_dl_regions.df.drop(cst.IDX_ORIGIN, axis=1)
        regions_dl = reorder_dl(regions_dl)

        if not regions_accounts.equals(regions_dl):
            raise ValueError(
                "Detail levels of input accounts and input detail "
                "levels do not contain the same regions."
            )

        if len(self.i_dl_regions.get_import_regions_list()) == 0:
            log.error("Regions detail level shall define at least one "
                      "import region")
            raise MEDataNotSuitableForWorkflow(
                data_name="regions detail level",
                workflow_name=f"{self.kind()} {self.name()}",
            )

        # check input bridge contain cst.IDX_Y_CATEGORY in columns names
        bridges = self.i_bridge_final_demand_categories
        columns_dl = bridges.columns_dl.df
        columns_level_names = columns_dl.columns.tolist()

        if not cst.IDX_Y_CATEGORY in columns_level_names:
            raise ValueError(f"{cst.IDX_Y_CATEGORY} not in bridge columns.")
        if not cst.IDX_EXPORTS in columns_dl[cst.IDX_Y_CATEGORY].tolist():
            raise ValueError(f"{cst.IDX_EXPORTS} not in bridge columns.")

    @staticmethod
    def _reformat_accounts_final_demand_categories(
        input_accounts: Accounts,
        final_demand_bridge: Bridge,
    ) -> Accounts:
        """
        Reformat final demand categories using a bridge matrix.

        The method copies the input accounts, calculates required coefficients,
        resets shock-sensitive variables, applies the final demand bridge, and
        recalculates the resulting accounts lazily.

        Parameters
        ----------
        input_accounts : Accounts
            Input GMRIO accounts.
        final_demand_bridge : Bridge
            Bridge mapping input final demand categories to the target categories.

        Returns
        -------
        Accounts
            A copy of the input accounts with reformatted final demand categories.
        """

        accounts = input_accounts.copy()
        extension_names = [*accounts.extensions.keys()]

        # lazy calculate
        accounts.system.calculate()
        for extension_name in extension_names:
            extension = accounts.get_extension(extension_name)
            extension.calculate(system=accounts.system, lazy=True)

        # adapted reset
        accounts.system.reset_for_shock()
        for extension_name in extension_names:
            extension = accounts.get_extension(extension_name)
            ext_calc_mode = extension.calcul.name
            if ext_calc_mode == cst.STRATEGY_USE_BASED:
                extension.dataset.F_Z.reset()
                extension.dataset.S_Y.reset()
            else:
                extension.reset_for_shock()

        # reformat
        accounts.reformat(final_demand_bridge)

        # lazy calculate
        accounts.system.calculate()
        for extension_name in [*accounts.extensions.keys()]:
            accounts.get_extension(extension_name).calculate(
                system=accounts.system, lazy=True
            )
        accounts.reset_coefficients()

        return accounts

    def _build_region_bridges(self) -> None:

        # build associate region bridge
        input_dl = (
            self.get_input_data(self.KEY_ACCOUNTS)
            .detail_levels[dl.DetailLevelKind.REGIONS.value]
            .df
        )
        output_dl = self.i_dl_regions.df
        df = pd.DataFrame(
            index=pd.MultiIndex.from_frame(input_dl),
            columns=pd.MultiIndex.from_frame(output_dl),
        )

        regions = df.index.droplevel(cst.IDX_ORIGIN).to_frame(False)
        for nb, region in regions.iterrows():
            row_mask = pd.Series(True, index=df.index)
            col_mask = pd.Series(True, index=df.columns)

            for level_name, level_value in region.items():
                if level_name in df.index.names:
                    row_mask &= (
                        df.index.get_level_values(level_name) == level_value
                    )

                if level_name in df.columns.names:
                    col_mask &= (
                        df.columns.get_level_values(level_name) == level_value
                    )

            df.loc[row_mask, col_mask] = 1.0

        bridge = Bridge.init_from_df(
            kind=dl.DetailLevelKind.REGIONS,
            df=df.apply(pd.to_numeric, errors="coerce").fillna(0.0),
        )  # ToDo JG: to add in factory similarly to make_dl_from_kind?
        self.processed_data[self.KEY_BRIDGES][
            dl.DetailLevelKind.REGIONS.value
        ] = bridge

        decomp_bridges = GmrioToSnacS._extract_region_bridge_by_columns_origin(
            bridge
        )
        for k, v in decomp_bridges.items():
            self.processed_data[self.KEY_BRIDGES][k] = v

    @staticmethod
    def _extract_region_bridge_by_columns_origin(
        bridge: Bridge,
    ) -> Dict[str, Bridge]:
        """Extract regions associated with a given origin from the region bridge."""
        bridge_df_dict = {
            origin: bridge.df[[origin]]
            for origin in bridge._columns_dl.df[cst.IDX_ORIGIN].unique()
        }
        bridge_df_dict = {
            k: v.loc[v.sum(axis=1) != 0] for k, v in bridge_df_dict.items()
        }
        output_bridges = {
            k: Bridge.init_from_df(kind=dl.DetailLevelKind.REGIONS, df=v)
            for k, v in bridge_df_dict.items()
        }

        return output_bridges

    def _convert_accounts_to_snac_s(self) -> None:

        system = self.processed_data[self.KEY_ACCOUNTS_FD_AGG].system
        extensions = self.processed_data[self.KEY_ACCOUNTS_FD_AGG].extensions

        snac_s_system = self._convert_system_to_snac_s(
            input_system=system,
            reg_bridges=self.processed_data[self.KEY_BRIDGES],
        )

        snac_s_dom_extensions = self._build_domestic_extensions(
            input_extensions=extensions,
            reg_bridges=self.processed_data[self.KEY_BRIDGES],
        )

        snac_s_imp_extensions = self._build_extensions_embodied_in_imports(
            input_system=system,
            input_extensions=extensions,
            reg_bridges=self.processed_data[self.KEY_BRIDGES],
            m_row_mode=self._id.m_row_mode,
        )

        a_director = a_builder.get_director()
        snac_s_accounts = a_director.make_from_system_and_extensions(
            system=snac_s_system,
            extensions={**snac_s_dom_extensions, **snac_s_imp_extensions},
        )
        self.processed_data[self.KEY_ACCOUNTS_SNAC_S] = snac_s_accounts

    @staticmethod
    def _convert_system_to_snac_s(
        input_system: System,
        reg_bridges: Dict[str, Bridge],
    ) -> System:
        """
        Convert a GMRIO system into a SNAC-S system.

        The method aggregates the input system over the SNAC-S regional bridge,
        resets import and export placeholders, computes imports and exports from
        interregional flows, and updates the output and final demand accounts so
        that the resulting system remains market-balanced.

        Parameters
        ----------
        input_system : System
            Input GMRIO system.
        reg_bridges : dict[str, Bridge]
            Regional bridges, including the full regional bridge, the domestic
            regional bridge, and the import regional bridge.

        Returns
        -------
        System
            SNAC-S-compatible production system.

        Raises
        ------
        ValueError
            If the resulting system does not satisfy market balance checks.
        """

        system = input_system.copy()
        system.aggregate(reg_bridges[dl.DetailLevelKind.REGIONS.value])

        # reset to nan irrelevant parts on trades
        system.dataset.x.set_import_values(np.nan)
        y_categories = system.detail_levels[
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value
        ].df
        if cst.IDX_Y_CATEGORY in y_categories.columns:
            if cst.IDX_EXPORTS in y_categories[cst.IDX_Y_CATEGORY].tolist():
                system.dataset.Y.set_export_values(np.nan)
            else:
                log.warning(
                    f"{cst.IDX_EXPORTS} not in bridges for fd categories"
                )
        else:
            log.warning(
                f"{cst.IDX_Y_CATEGORY} not in bridges for fd categories"
            )

        imports = GmrioToSnacS._build_imports_for_snac_s_system(
            input_system=input_system, reg_bridges=reg_bridges
        )
        system.dataset.x.set_import_values(imports.get_import_origin().values)

        exports = GmrioToSnacS._build_exports_for_snac_s_system(
            input_system=input_system, reg_bridges=reg_bridges
        )
        update_y = system.dataset.Y.df.copy()
        update_y = update_y.apply(pd.to_numeric, errors="coerce").fillna(0.0)
        update_y += exports.df.apply(pd.to_numeric, errors="coerce").fillna(
            0.0
        )
        system.dataset.Y.set_values(update_y.values)

        system.check_market_balance()

        return system

    @staticmethod
    def _build_imports_for_snac_s_system(
        input_system: System, reg_bridges: Dict[str, Bridge]
    ) -> XData:

        import_df = GmrioToSnacS._extract_trade_vector(
            index_regions=reg_bridges[cst.IDX_IMPORT].df.index,
            col_regions=reg_bridges[cst.IDX_DOMESTIC].df.index,
            Z=input_system.dataset.Z,
            Y=input_system.dataset.Y,
        )
        import_data = make_data(
            name=cst.X,
            regions=input_system.regions,
            sectors=input_system.sectors,
            final_demand_categories=input_system.final_demand_categories,
        )
        import_data.df.loc[import_df.index, :] = import_df.values
        import_data.aggregate(
            reg_bridges[dl.DetailLevelKind.REGIONS.value], reset=False
        )

        return import_data

    @staticmethod
    def _build_exports_for_snac_s_system(
        input_system: System, reg_bridges: Dict[str, Bridge]
    ) -> YData:

        export_df = GmrioToSnacS._extract_trade_vector(
            index_regions=reg_bridges[cst.IDX_DOMESTIC].df.index,
            col_regions=reg_bridges[cst.IDX_IMPORT].df.index,
            Z=input_system.dataset.Z,
            Y=input_system.dataset.Y,
        )

        export_data = make_data(
            name=cst.Y,
            regions=input_system.regions,
            sectors=input_system.sectors,
            final_demand_categories=input_system.final_demand_categories,
        )

        dom_regions = (
            reg_bridges[cst.IDX_DOMESTIC]
            .df.index.droplevel(cst.IDX_ORIGIN)
            .to_frame(False)
        )

        for nb, region in dom_regions.iterrows():
            row_mask = pd.Series(True, index=export_data.df.index)
            col_mask = pd.Series(True, index=export_data.df.columns)

            for level_name, level_value in region.items():
                if level_name in export_data.df.index.names:
                    row_mask &= (
                        export_data.df.index.get_level_values(level_name)
                        == level_value
                    )

                if level_name in export_data.df.columns.names:
                    col_mask &= (
                        export_data.df.columns.get_level_values(level_name)
                        == level_value
                    )
            col_mask &= (
                export_data.df.columns.get_level_values(cst.IDX_Y_CATEGORY)
                == cst.IDX_EXPORTS
            )
            values = export_df.reindex(export_data.df.index[row_mask])
            export_data.df.loc[row_mask, col_mask] = values.to_numpy()[:, None]

        export_data.aggregate(
            reg_bridges[dl.DetailLevelKind.REGIONS.value], reset=False
        )

        return export_data

    @staticmethod
    def _extract_trade_vector(
        index_regions: pd.Index, col_regions: pd.Index, Z: ZData, Y: YData
    ) -> pd.DataFrame:
        """Build a trade vector from index regions to columns regions."""
        variables = [Z, Y]

        trade_matrix = sum(
            [
                var.df.loc[
                    var.index.isin(index_regions),
                    col_regions.get_level_values(cst.IDX_REGION),
                ]
                .T.groupby(level=cst.IDX_REGION, sort=False)
                .sum()
                .T
                for var in variables
            ]
        )

        return trade_matrix.sum(axis=1)

    @staticmethod
    def _build_domestic_extensions(
        input_extensions: Dict[str, Extension], reg_bridges: Dict[str, Bridge]
    ) -> Dict[str, Extension]:

        extensions = {k: v.copy() for k, v in input_extensions.items()}
        for k, v in extensions.items():
            v.aggregate(reg_bridges[dl.DetailLevelKind.REGIONS.value])

        extension_names = {
            ext_name: cst.IDX_DOMESTIC[0:3] + "_" + ext_name
            for ext_name in [*extensions.keys()]
        }

        for k, v in extension_names.items():
            extensions[v] = extensions.pop(k)
            extensions[v].id.extension_name = v
            extensions[v].detail_levels[
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value
            ].sheet_name = v

        return extensions

    @staticmethod
    def _build_extensions_embodied_in_imports(
        input_system: System,
        input_extensions: Dict[str, Extension],
        reg_bridges: Dict[str, Bridge],
        m_row_mode: str,
    ) -> Dict[str, Extension]:
        """
        Build import extensions using rest-of-world multipliers.

        For each input extension, this method creates an embodied-in-import
        extension and fills its `M_RoW` matrix according to the selected
        multiplier mode.

        Parameters
        ----------
        input_system : System
            Input GMRIO system used to compute technical coefficients and
            Leontief matrix.
        input_extensions : dict[str, Extension]
            Input environmental or satellite extensions.
        reg_bridges : dict[str, Bridge]
            Regional bridges distinguishing domestic and import regions.
        m_row_mode : str
            Rest-of-world multiplier mode. Must be one of:
            `foreign_isolated`, `foreign_global_feedback`, or
            `world_global_feedback`.

        Returns
        -------
        dict[str, Extension]
            Import extensions indexed by their generated extension names.

        Raises
        ------
        ValueError
            If `m_row_mode` is not a supported mode.
        """

        extensions = GmrioToSnacS._build_empty_extensions_embodied_in_imports(
            input_extensions=input_extensions,
            reg_bridges=reg_bridges,
        )

        system = input_system.copy()
        system.calculate()
        A = system.dataset.A
        L = system.dataset.L

        imp_bridge = reg_bridges[cst.IDX_IMPORT].df
        row_mask = A.index.droplevel(cst.IDX_SECTOR).isin(imp_bridge.index)
        col_mask = A.columns.droplevel(cst.IDX_SECTOR).isin(
            imp_bridge.index.droplevel(cst.IDX_ORIGIN)
        )

        for k, v in input_extensions.items():

            v.calcul.calculate(
                extension_dataset=v.dataset,
                system_dataset=input_system.dataset,
            )
            S_x_dom = v.dataset.S_x_dom

            # foreign_isolated
            if m_row_mode == GmrioToSnacS.KEY_M_ROW_MODE_1:
                extensions[cst.IDX_IMPORT[0:3] + f"_{k}"].M_RoW.df = (
                    GmrioToSnacS._calc_m_row_foreign_isolated(
                        A, L, S_x_dom, row_mask, col_mask
                    )
                )

            # foreign_global_feedback
            if m_row_mode == GmrioToSnacS.KEY_M_ROW_MODE_2:
                extensions[cst.IDX_IMPORT[0:3] + f"_{k}"].M_RoW.df = (
                    GmrioToSnacS._calc_m_row_foreign_global_feedback(
                        A, L, S_x_dom, row_mask, col_mask
                    )
                )

            # world_global_feedback
            if m_row_mode == GmrioToSnacS.KEY_M_ROW_MODE_3:
                extensions[cst.IDX_IMPORT[0:3] + f"_{k}"].M_RoW.df = (
                    GmrioToSnacS._calc_m_row_world_global_feedback(
                        A, L, S_x_dom, row_mask, col_mask
                    )
                )

            if m_row_mode not in GmrioToSnacS.M_ROW_MODES:
                raise ValueError(
                    f"Unsupported M_RoW mode: {m_row_mode}. "
                    f"Expected one of {list(GmrioToSnacS.M_ROW_MODES)}."
                )

        return extensions

    @staticmethod
    def _build_empty_extensions_embodied_in_imports(
        input_extensions: Dict[str, Extension], reg_bridges: Dict[str, Bridge]
    ) -> Dict[str, Extension]:

        output = dict()

        dom_bridge = reg_bridges[cst.IDX_DOMESTIC].df
        dom_region = dom_bridge.index.droplevel(cst.IDX_ORIGIN).to_frame(True)
        imp_bridge = reg_bridges[cst.IDX_IMPORT].df
        imp_region = imp_bridge.index.droplevel(cst.IDX_ORIGIN).to_frame(True)

        dl_regions_df = pd.concat(
            {cst.IDX_DOMESTIC: dom_region, cst.IDX_IMPORT: imp_region},
            names=[cst.IDX_ORIGIN],
        ).index.to_frame(False)

        ext_dir = ext_builders.get_director(reset=True)

        for k, v in input_extensions.items():

            extension_name = cst.IDX_IMPORT[0:3] + f"_{k}"

            ext_dir.set_sectors(v.sectors)
            ext_dir.set_regions(dl.RegionsDL(dl_regions_df))
            ext_dir.set_final_demand_categories(v.final_demand_categories)
            ext_dir.set_extension_categories(v.extension_categories)
            ext_id = ExtensionIdentity(
                base_year=v.id.base_year,
                extension_name=extension_name,
                strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
            )
            imp_extension = ext_dir.make_from_id(id_=ext_id)
            imp_extension.detail_levels[
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value
            ].sheet_name = extension_name

            output[extension_name] = imp_extension

        return output

    @staticmethod
    def _calc_m_row_foreign_isolated(
        A: AData,
        L: LData,
        S_x: SxDomData,
        row_mask: NDArray[np.bool_],
        col_mask: NDArray[np.bool_],
    ) -> pd.DataFrame:

        S_RoW = S_x.df.loc[:, col_mask]
        A_RoW = A.df.loc[row_mask, col_mask]

        I = pd.DataFrame(
            np.eye(len(A_RoW)),
            index=A_RoW.index,
            columns=A_RoW.columns,
        )

        L_RoW = pd.DataFrame(
            np.linalg.inv(I - A_RoW),
            index=A_RoW.index,
            columns=A_RoW.columns,
        )

        M_RoW = S_RoW @ L_RoW.droplevel(cst.IDX_ORIGIN)

        return M_RoW

    @staticmethod
    def _calc_m_row_foreign_global_feedback(
        A: AData,
        L: LData,
        S_x: SxDomData,
        row_mask: NDArray[np.bool_],
        col_mask: NDArray[np.bool_],
    ) -> pd.DataFrame:

        S_w_dom_region_zero = S_x.df.copy()
        S_w_dom_region_zero.loc[:, ~col_mask] = 0.0

        M = S_w_dom_region_zero @ L.df.droplevel(cst.IDX_ORIGIN)

        M_RoW = M.loc[:, col_mask]

        return M_RoW

    @staticmethod
    def _calc_m_row_world_global_feedback(
        A: AData,
        L: LData,
        S_x: SxDomData,
        row_mask: NDArray[np.bool_],
        col_mask: NDArray[np.bool_],
    ) -> pd.DataFrame:

        M = S_x.df @ L.df.droplevel(cst.IDX_ORIGIN)
        M_RoW = M.loc[:, col_mask]
        return M_RoW

    def calculate(self) -> None:
        """Optionally recalculate the resulting SNAC-S accounts."""
        if self.id.calculate_accounts:
            self.processed_data[self.KEY_ACCOUNTS_SNAC_S].calculate()

    def save(self) -> None:

        self.processed_data[self.KEY_ACCOUNTS_SNAC_S].save_to_path(
            path=self._id.path_out, export_format=self._id.export_format
        )
