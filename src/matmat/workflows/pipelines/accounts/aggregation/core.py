"""
Presentation
************
This module is the 'aggregation' module of the
package `pipelines`.
It defines the aggregation pipeline.

This engine takes as input:
    - an accounts
    - a set of bridges
and performs the following treatments:
    - Check that the bridges contain only 0 and 1
    - Check that the sum on columns of the bridges matrices is 1
    - Check that the regions bridge do not mismatch domestic/import regions
    - Ensure that the bridges match the accounts detail levels
    - Aggregate the accounts (with the bridges)
    - Save the accounts

Content
*******
- Classes:
    - :class:`PipelineAggregation`
"""

import os

import pandas as pd
import numpy as np

from matmat.workflows.pipelines.core import AbstractPipeline
from matmat.workflows.pipelines.accounts.aggregation.identity import (
    PipelineAggregationIdentity,
)
from matmat.core.accounts import builder as a_builder
from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge, factory as bridge_factory
from matmat.utils import logging as log, constants as cst
from matmat.utils.errors import (
    MEInconsistentDetailLevels,
    MEIncorrectBridge,
    MEMissingInputData,
)


class PipelineAggregation(AbstractPipeline):

    KEY_ACCOUNTS = "accounts"

    _id: PipelineAggregationIdentity

    @classmethod
    def name(cls) -> str:
        return "aggregation"

    def load(self) -> None:
        self._load_accounts()
        self._load_bridges()

    def _load_accounts(self):
        """
        Load accounts

        Fill self.input_data[self.KEY_ACCOUNTS]
        """
        log.info("### LOAD ACCOUNTS ###")
        self.input_data[self.KEY_ACCOUNTS] = a_builder.get_director(
            reset=True
        ).make_from_path(
            path=self.path_in.accounts,
            extensions_names=self._id.extension_names,
            load_data=True,
        )

    def _load_bridges(self):
        """
        Load bridges

        Fill self.input_data[self.KEY_BRIDGES]
        """
        log.info("### LOAD BRIDGE ###")
        self.input_data[self.KEY_BRIDGES] = (
            bridge_factory.make_bridge_dict_from_path(
                path=os.path.dirname(self.path_in.bridges),
                file_name=os.path.basename(self.path_in.bridges),
                extension_names=self.id.extension_names,
            )
        )

    def process(self) -> None:
        self._check_bridge_is_binary()
        self._check_columns_sum()
        self._check_bridge_regions()
        self._check_accounts_vs_bridges_consistency()
        self._ensure_accounts_fluxes_for_aggregation()
        self._aggregate_accounts()

    def _check_bridge_is_binary(self):
        """
        Check that all bridges contain only binary values (0 or 1).

        Raises:
            MEIncorrectBridge: If any bridge contains values other than 0 or 1.
        """
        log.info("### CHECK BRIDGES BINARY COMPLIANCE ###")

        def is_binary_dataframe(df: pd.DataFrame) -> bool:
            values = df.to_numpy()
            unique = np.unique(values)
            return np.all(np.isin(unique, [0, 1]))

        def raise_error(current_bridge: bridge.Bridge):
            raise MEIncorrectBridge(
                bridge_kind=current_bridge.kind,
                msg=(
                    f"Bridge {current_bridge.sheet_name} "
                    f"contains values which are not 0 or 1"
                ),
            )

        for bridge_ in self.get_input_data(self.KEY_BRIDGES).values():
            if isinstance(bridge_, dict):
                for bridge_ext_cats in bridge_.values():
                    if not is_binary_dataframe(bridge_ext_cats.df):
                        raise_error(bridge_ext_cats)
            else:
                if not is_binary_dataframe(bridge_.df):
                    raise_error(bridge_)

    def _check_columns_sum(self):
        """
        Check that the sum of each column in all bridges equals 1.

        Raises:
            MEIncorrectBridge: If any column sum in a bridge is not equal to 1.
        """

        def get_invalid_column_sums(df: pd.DataFrame) -> list:
            col_sums = df.to_numpy().sum(axis=1)
            mask = ~np.isclose(col_sums, 1)
            return df.index[mask].tolist()

        def raise_error(current_bridge: bridge.Bridge, rows: list):
            raise MEIncorrectBridge(
                bridge_kind=current_bridge.kind,
                msg=(
                    f"Bridge {current_bridge.sheet_name} "
                    f"sum on columns shall be 1. "
                    f"Invalid rows: {rows}"
                ),
            )

        log.info("### CHECK BRIDGES COLUMNS SUM")

        for bridge_ in self.get_input_data(self.KEY_BRIDGES).values():
            if isinstance(bridge_, dict):
                for bridge_ext_cats in bridge_.values():
                    invalid_rows = get_invalid_column_sums(bridge_ext_cats.df)
                    if len(invalid_rows) > 0:
                        raise_error(bridge_ext_cats, invalid_rows)
            else:
                invalid_rows = get_invalid_column_sums(bridge_.df)
                if len(invalid_rows) > 0:
                    raise_error(bridge_, invalid_rows)

    def _check_bridge_regions(self):
        """
        Check that domestic regions remain domestic and import regions
        remain import in the regions bridge.

        Raises:
            MEIncorrectBridge: If any region origin mismatch is found.
        """

        def check_origin_consistency(df: pd.DataFrame) -> list[tuple]:
            arr = df.to_numpy() != 0
            row_origins = df.index.get_level_values(cst.IDX_ORIGIN).to_numpy()
            col_origins = df.columns.get_level_values(
                cst.IDX_ORIGIN
            ).to_numpy()

            mismatch = row_origins[:, None] != col_origins[None, :]
            bad = arr & mismatch
            rows, cols = np.where(bad)
            return [(df.index[i], df.columns[j]) for i, j in zip(rows, cols)]

        try:
            regions_bridge = self.i_bridge_regions
            log.info("### CHECK REGIONS BRIDGE ###")
            invalid_cells = check_origin_consistency(regions_bridge.df)
            if len(invalid_cells) > 0:
                raise MEIncorrectBridge(
                    bridge_kind=self.i_bridge_regions.kind,
                    msg=(
                        "Mismatch between domestic / "
                        "import regions in regions bridge:\n"
                        + "\n".join(str(cell) for cell in invalid_cells)
                    ),
                )
        except MEMissingInputData:
            pass

    def _check_accounts_vs_bridges_consistency(self):
        """
        Check that the accounts and the bridges detail levels are consistent
        to avoid errors when aggregating.

        This operation is done prior to aggregation as the aggregation
        may take a long time, and an error could occur at the end if the
        check has not been performed first.

        Raises:
            MEInconsistentDetailLevels: If detail levels do not match between
            accounts and bridges.
        """

        def check_bridge(current_bridge: bridge.Bridge):

            def compare_dls(entity_compared: str, dl_1, dl_2):
                if not dl_1.equals(dl_2):
                    log.error(
                        f"{dl_1.kind} detail level does not match "
                        f"between {entity_compared} and input bridge"
                    )
                    raise MEInconsistentDetailLevels(
                        dl_kind=dl_1.kind,
                        dl_1=dl_1.df,
                        dl_2=dl_2.df,
                    )

            match current_bridge.kind:
                case dl.DetailLevelKind.REGIONS:
                    compare_dls(
                        entity_compared="system",
                        dl_1=accounts.system.dataset.regions,
                        dl_2=current_bridge.rows_dl,
                    )
                    for ext_ in accounts.list_extensions():
                        compare_dls(
                            entity_compared=f"extension '{ext_.name}'",
                            dl_1=ext_.dataset.regions,
                            dl_2=current_bridge.rows_dl,
                        )
                case dl.DetailLevelKind.SECTORS:
                    compare_dls(
                        entity_compared="system",
                        dl_1=accounts.system.dataset.sectors,
                        dl_2=current_bridge.rows_dl,
                    )
                    for ext_ in accounts.list_extensions():
                        compare_dls(
                            entity_compared=f"extension '{ext_.name}'",
                            dl_1=ext_.dataset.sectors,
                            dl_2=current_bridge.rows_dl,
                        )
                case dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES:
                    compare_dls(
                        entity_compared="system",
                        dl_1=accounts.system.dataset.final_demand_categories,
                        dl_2=current_bridge.rows_dl,
                    )
                    for ext_ in accounts.list_extensions():
                        compare_dls(
                            entity_compared=f"extension '{ext_.name}'",
                            dl_1=ext_.dataset.final_demand_categories,
                            dl_2=current_bridge.rows_dl,
                        )
                case dl.DetailLevelKind.EXTENSION_CATEGORIES:
                    compare_dls(
                        entity_compared=f"extension '{current_bridge.extension_name}'",
                        dl_1=accounts.get_extension(
                            current_bridge.extension_name
                        ).dataset.extension_categories,
                        dl_2=current_bridge.rows_dl,
                    )

        log.info("### CHECK ACCOUNTS & BRIDGES CONSISTENCY ###")
        accounts = self.input_data[self.KEY_ACCOUNTS]
        for bridge_ in self.get_input_data(self.KEY_BRIDGES).values():
            if isinstance(bridge_, dict):
                for bridge_ext_cats in bridge_.values():
                    check_bridge(bridge_ext_cats)
            else:
                check_bridge(bridge_)

    def _ensure_accounts_fluxes_for_aggregation(self):
        """
        Ensure that the necessary fluxes are not empty before aggregating,
        in order to not lose information.

        Fill self.processed_data[self.KEY_ACCOUNTS]
        """
        log.info("### CALCULATE ACCOUNTS BEFORE AGGREGATION ###")
        accounts = self.input_data[self.KEY_ACCOUNTS].copy()
        accounts.system.calculate()
        accounts.calculate_extensions(lazy=True)
        self.processed_data[self.KEY_ACCOUNTS] = accounts

    def _aggregate_accounts(self):
        """
        Aggregate accounts with bridge

        Update self.processed_data[self.KEY_ACCOUNTS]
        """
        log.info("### AGGREGATE ACCOUNTS ###")
        accounts = self.get_processed_data(self.KEY_ACCOUNTS)
        # Apply bridges one by one to make debugging easier if necessary
        for bridge_ in self.get_input_data(self.KEY_BRIDGES).values():
            if isinstance(bridge_, dict):
                for bridge_ext_cats in bridge_.values():
                    accounts.aggregate(bridge_ext_cats)
            else:
                accounts.aggregate(bridge_)
        self.processed_data[self.KEY_ACCOUNTS] = accounts

    def calculate(self):
        self._calculate_accounts()

    def _calculate_accounts(self):
        """
        Calculate accounts if parameter calculate_accounts is True
        """
        accounts = self.get_processed_data(self.KEY_ACCOUNTS).copy()
        if self._id.calculate_accounts:
            log.info("### CALCULATE ACCOUNTS ###")
            accounts.calculate()
            self.calculated_data[self.KEY_ACCOUNTS] = accounts
        else:
            log.info(
                "Do not calculate accounts as parameter "
                f"'calculate_accounts' is {self._id.calculate_accounts}"
            )
        self.calculated_data[self.KEY_ACCOUNTS] = accounts

    def save(self) -> None:
        """
        Save aggregated accounts to output directory
        """
        log.info("### SAVE ACCOUNTS ###")
        self.calculated_data[self.KEY_ACCOUNTS].save_to_path(
            path=self.path_out,
            export_format=self._export_formats_names,
        )
