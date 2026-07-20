import copy
import pytest

import numpy as np
import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.core.data.strategies import structure
from matmat.utils import constants as cst, errors, config

from tests.utils import builders
from tests.utils import constants as tests_cst


class TestStructureUnitBySector:

    @pytest.fixture
    def structure_unit(
        self, dl_regions_1, dl_sectors_1, dl_final_demand_categories_1
    ):
        return structure.StructureUnitBySector(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
        )

    def test_rows_specs(self, structure_unit):
        """
        Test property `rows_specs`
        """
        assert structure_unit.rows_specs == {
            dl.DetailLevelKind.SECTORS: [],
        }

    def test_columns_specs(self, structure_unit):
        """
        Test property `columns_specs`
        """
        assert structure_unit.columns_specs is None

    def test_build_columns(self, structure_unit):
        """
        Test method `_build_columns`

        Expected results:
            As StructureUnitBySector has no columns specs, ensure that the method
            `_build_columns` is overridden properly, i.e. df_columns
            is properly built.
        """
        assert structure_unit.df_columns.equals(
            pd.MultiIndex.from_arrays([[cst.UNIT]], names=[cst.IDX_VARIABLE])
        )


class TestStructureUnitByExtensionCategory:

    @pytest.fixture
    def structure_unit(
        self,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        return structure.StructureUnitByExtensionCategory(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            extension_categories=dl_extension_categories_1,
        )

    def test_rows_specs(self, structure_unit):
        """
        Test property `rows_specs`
        """
        assert structure_unit.rows_specs == {
            dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
        }

    def test_columns_specs(self, structure_unit):
        """
        Test property `columns_specs`
        """
        assert structure_unit.columns_specs is None

    def test_build_columns(self, structure_unit):
        """
        Test method `_build_columns`

        Expected results:
            As TestStructureUnitByExtensionCategory has no columns specs,
            ensure that the method
            `_build_columns` is overridden properly, i.e. df_columns
            is properly built.
        """
        assert structure_unit.df_columns.equals(
            pd.MultiIndex.from_arrays([[cst.UNIT]], names=[cst.IDX_VARIABLE])
        )


class TestStructureUnit:
    """
    Test class for the following classes:
        - AbstractDataStructure
        - StructureUnit
    """

    sectors = builders.get_test_sectors()
    regions = tests_cst.REGIONS_W_IMPORT
    final_demand_categories = tests_cst.DEFAULT_Y_CATEGORIES

    @staticmethod
    def build_custom_bridge(
        index: pd.MultiIndex,
        columns: pd.MultiIndex,
    ) -> bridge.Bridge:
        agg_matrix = pd.DataFrame(
            index=index,
            columns=columns,
            dtype="float",
        )
        agg_matrix.loc[:, :] = 0

        for category in columns.get_level_values(0):
            if category != "Other":
                index_to_fill = agg_matrix.loc[[category]].index
                agg_matrix.loc[index_to_fill, category] = 1

        other_index = agg_matrix.loc[agg_matrix.sum(axis=1) == 0].index
        agg_matrix.loc[other_index, "Other"] = 1

        return bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=agg_matrix,
        )

    def test_aggregate_nominal(self):
        """
        Test function `apply_bridge_to_df`

        Expected results:
            - Unit system data aggregated properly
        """
        unit = builders.build_test_system_data(
            name=cst.UNIT, sectors=builders.get_test_sectors()
        )

        # Build custom aggregation matrix
        unit_category_1 = (
            unit.structure._sectors.df.iloc[:, 0].unique().tolist()[0]
        )
        unit_category_2 = (
            unit.structure._sectors.df.iloc[:, 0].unique().tolist()[1]
        )
        columns = pd.MultiIndex.from_arrays(
            [
                [
                    unit_category_1,
                    unit_category_2,
                    "Other",
                ]
            ],
            names=[unit.structure._sectors.df.columns[0]],
        )
        bridge_ = self.build_custom_bridge(
            index=unit.df.index, columns=columns
        )

        units = {
            unit_category_1: f"{unit_category_1}_unit",
            unit_category_2: f"{unit_category_2}_unit",
            "Other": "O_unit",
        }

        unit.df.loc[:, :] = units["Other"]
        for category in columns.get_level_values(0):
            if category != "Other":
                index_to_fill = unit.df.loc[[category]].index
                unit.df.loc[index_to_fill] = units[category]

        agg_unit_vector = unit.structure.apply_bridge_to_df(
            df=unit.df, bridge_=bridge_
        )

        for key, value in units.items():
            assert agg_unit_vector.loc[key, cst.UNIT].squeeze() == value

    def test_aggregate_heterogeneous(self):
        """
        Test function `apply_bridge_to_df`

        Expected results:
            An exception shall be raised as we try to aggregate heterogeneous
            units together
        """
        unit = builders.build_test_system_data(
            name=cst.UNIT, sectors=builders.get_test_sectors()
        )

        # Build custom aggregation matrix
        unit_category_1 = (
            unit.structure._sectors.df.iloc[:, 0].unique().tolist()[0]
        )
        unit_category_2 = (
            unit.structure._sectors.df.iloc[:, 0].unique().tolist()[1]
        )
        columns = pd.MultiIndex.from_arrays(
            [
                [
                    unit_category_1,
                    unit_category_2,
                    "Other",
                ]
            ],
            names=[unit.structure._sectors.df.columns[0]],
        )
        bridge_ = self.build_custom_bridge(
            index=unit.df.index, columns=columns
        )
        # Modify bridge
        df_alternate = bridge_.df
        df_alternate.iloc[0, 0] = 0.0
        df_alternate.iloc[0, 1] = 1.0
        bridge_ = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=df_alternate,
        )

        units = {
            unit_category_1: f"{unit_category_1}_unit",
            unit_category_2: f"{unit_category_2}_unit",
            "Other": "O_unit",
        }

        unit.df.loc[:, :] = units["Other"]
        for category in columns.get_level_values(0):
            if category != "Other":
                index_to_fill = unit.df.loc[[category]].index
                unit.df.loc[index_to_fill] = units[category]

        config_save = config.ALLOW_HETEROGENEOUS_AGGREGATION
        config.ALLOW_HETEROGENEOUS_AGGREGATION = False
        with pytest.raises(errors.MEAggMatrixInconsistentWithUnitVector):
            unit.structure.apply_bridge_to_df(df=unit.df, bridge_=bridge_)
        config.ALLOW_HETEROGENEOUS_AGGREGATION = config_save

    def test_disaggregate_error(self):
        """
        Test function '_perform_aggregation'

        Expected results:
            (1) Aggregation matrix has 1 column with more than one '1',
                raise MEAggMatrixInconsistentWithUnitVector
            (2) Aggregation matrix has one row with only zeros,
                raise MEAggMatrixInconsistentWithUnitVector
        """
        disagg_matrix = (
            builders.get_test_sectors_bridge()
            .get_agg_matrix()
            .to_dataframe()
            .T
        )

        unit = builders.build_test_system_data(
            name=cst.UNIT, sectors=builders.get_test_agg_sectors()
        )

        height = len(disagg_matrix.index)
        width = len(disagg_matrix.columns)

        # (1) Alter aggregation matrix: one column with several ones
        random_column = np.random.randint(0, width)
        random_row = np.random.randint(0, height - 1)
        test_agg_matrix_1 = copy.deepcopy(disagg_matrix)
        test_agg_matrix_1.iat[random_row, random_column] = 1
        test_agg_matrix_1.iat[random_row + 1, random_column] = 1

        with pytest.raises(errors.MEAggMatrixInconsistentWithUnitVector):
            unit.structure.apply_bridge_to_df(
                df=unit.df,
                bridge_=bridge.Bridge.init_from_df(
                    kind=dl.DetailLevelKind.SECTORS,
                    df=test_agg_matrix_1,
                ),
            )

        # (2) Alter aggregation matrix: one row with only zeros
        random_row = np.random.randint(0, height)
        test_agg_matrix_2 = copy.deepcopy(disagg_matrix)
        test_agg_matrix_2.iloc[random_row, :] = 0

        with pytest.raises(errors.MEAggMatrixInconsistentWithUnitVector):
            unit.structure.apply_bridge_to_df(
                df=unit.df,
                bridge_=bridge.Bridge.init_from_df(
                    kind=dl.DetailLevelKind.SECTORS,
                    df=test_agg_matrix_2,
                ),
            )
