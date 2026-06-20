import os
import shutil

import pytest
import pandas as pd
import numpy as np

from matmat.workflows.adapters.shocks.manual.identity import AdapterManualIdentity
from matmat.workflows.adapters.shocks.manual.core import AdapterManual
from matmat.core.detail_level import core as dl
from matmat.core.shocks.system.core import SystemShock
from matmat.core.shocks.extension.core import ExtensionShock
from matmat.core.shocks import builder as as_builder
from matmat.core.dataset.core import AbstractListedDataSet
from matmat.utils import constants as cst

from tests.utils import constants as tests_cst, spy


class TestAdapterManual:

    TMP_OUTPUT_DIR = "./tmp_output"
    DATA_DIR = "data"
    MANUAL_PARAM_FILE = "TEST - manual_param.xlsx"
    MANUAL_PARAM_PATH = os.path.join(
        os.path.dirname(__file__), DATA_DIR, MANUAL_PARAM_FILE
    )

    _id: AdapterManualIdentity
    _manual_param_data: dict[str, pd.DataFrame]

    @pytest.fixture(autouse=True)
    def setup(
        self,
        dl_regions_3,
        dl_sectors_3,
        dl_final_demand_categories_3,
        dl_extension_categories_3,
    ):
        self.generate_id()
        self.generate_dl_file(
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
            dl_extension_categories_3,
        )
        self.load_manual_param_df()

    @classmethod
    def teardown_class(cls):
        os.remove(os.path.join(os.path.dirname(__file__), cst.DL_FILE))
        shutil.rmtree(cls.TMP_OUTPUT_DIR, ignore_errors=True)

    @classmethod
    def generate_id(cls):
        cls._id = AdapterManualIdentity(
            path_in={
                "manual_param_file": cls.MANUAL_PARAM_PATH,
                "detail_levels_file": os.path.join(
                    os.path.dirname(__file__), cst.DL_FILE
                ),
            },
            path_out=os.path.abspath(cls.TMP_OUTPUT_DIR),
            export_format=[cst.FORMAT_PICKLE],
            base_year=2000,
            scenario_names=["TEST_1", "TEST_2"],
            proj_years=[2030, 2040, 2050],
            extension_names=[
                tests_cst.EXT_NAME_USE_BASED,
                tests_cst.EXT_NAME_GROSS_OUTPUT_BASED,
                tests_cst.EXT_NAME_EMBODIED_IN_IMPORT,
            ],
        )

    def load_manual_param_df(self):
        self._manual_param_data = {}
        for required_sheet in [cst.KEY_SYSTEM] + self._id.extension_names:
            self._manual_param_data[required_sheet] = pd.read_excel(
                self.MANUAL_PARAM_PATH,
                sheet_name=required_sheet,
                header=[0, 1],
                index_col=[*range(0, 7)],
            )

    def generate_dl_file(
        self,
        dl_regions_3,
        dl_sectors_3,
        dl_final_demand_categories_3,
        dl_extension_categories_3,
    ):
        for dl_ in (
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
        ):
            dl_.save_to_path(path=os.path.dirname(__file__))

        for name in self._id.extension_names:
            dl_extension_categories_3.save_to_path(
                path=os.path.dirname(__file__), sheet_name=name
            )

    def set_input_data(
        self,
        adapter,
        dl_regions_3,
        dl_sectors_3,
        dl_final_demand_categories_3,
        dl_extension_categories_3,
    ):
        adapter.input_data[adapter.KEY_MANUAL_PARAM] = self._manual_param_data
        adapter.input_data[adapter.KEY_DL] = {
            dl.DetailLevelKind.REGIONS.value: dl_regions_3,
            dl.DetailLevelKind.SECTORS.value: dl_sectors_3,
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value: dl_final_demand_categories_3,
            dl.DetailLevelKind.EXTENSION_CATEGORIES.value: {
                name: dl_extension_categories_3.copy()
                for name in self._id.extension_names
            },
        }

    @staticmethod
    def _compute_masks(
        df_tested: pd.DataFrame, constraint: pd.Series
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Compute row and column masks based on constraint parameters.

        Parameters:
            df_tested (pd.DataFrame):
                DataFrame to apply masks on.
            constraint (pd.Series):
                Series containing constraint parameters for mask computation.
                Must include keys: row_level, row_name, row_region,
                col_level, col_name, col_region.
        Returns:
            tuple[np.ndarray, np.ndarray] :
                Tuple of (row_mask, col_mask) boolean arrays.
        """

        row_level = constraint["row_level"]
        row_name = constraint["row_name"]
        row_region = constraint["row_region"]
        col_level = constraint["col_level"]
        col_name = constraint["col_name"]
        col_region = constraint["col_region"]

        # Row mask
        row_mask = df_tested.index.get_level_values(row_level) == row_name
        if row_region == ":":
            pass
        elif row_region in ("domestic", "import"):
            row_mask &= (
                df_tested.index.get_level_values("origin") == row_region
            )
        else:
            regions = [r.strip() for r in row_region.split(",")]
            row_mask &= df_tested.index.get_level_values("region").isin(
                regions
            )

        # Col mask
        col_mask = df_tested.columns.get_level_values(col_level) == col_name
        if col_region != ":":
            regions = [r.strip() for r in col_region.split(",")]
            col_mask &= df_tested.columns.get_level_values("region").isin(
                regions
            )

        return row_mask, col_mask

    def assert_constraints(
        self, df_tested: pd.DataFrame, df_constraints: pd.DataFrame
    ):
        """
        Verify that DataFrame values match specified constraints.

        Parameters:
            df_tested (pd.DataFrame):
                DataFrame to validate against constraints.
            df_constraints (pd.DataFrame):
                DataFrame containing constraints to verify. Each row must
                include mask parameters and an expected 'value'.
        Raises:
            AssertionError :
                If any constraint fails or if non-NaN values exist outside
                constraint coverage.
        """

        covered = np.zeros(
            (len(df_tested), len(df_tested.columns)), dtype=bool
        )

        for _, constraint in df_constraints.iterrows():
            row_mask, col_mask = self._compute_masks(df_tested, constraint)
            expected_value = constraint["value"]

            subset = df_tested.loc[row_mask, col_mask]
            assert (
                subset.size > 0
            ), f"Empty selection for constraint: {constraint.to_dict()}"
            assert np.isclose(
                subset.values, expected_value, atol=1e-6, rtol=1e-6
            ).all(), (
                f"Constraint failed: expected {expected_value}, "
                f"got values in range [{subset.values.min()}, {subset.values.max()}] "
                f"for constraint: {constraint.to_dict()}"
            )

            covered |= (
                np.array(row_mask)[:, None] & np.array(col_mask)[None, :]
            )

        uncovered_values = df_tested.values[~covered]
        assert np.isnan(uncovered_values).all(), (
            f"Non-covered cells should be NaN, "
            f"got {(~np.isnan(uncovered_values)).sum()} non-NaN values"
        )

    def check_system_shock(self, system_shock: SystemShock):
        """
        Validate system shock data against predefined constraints.

        Parameters:
            system_shock (SystemShock):
                System shock object containing dataset to validate.
        """

        system_shock_constraints = self._manual_param_data[cst.KEY_SYSTEM][
            system_shock.id.scenario_name, system_shock.id.proj_year
        ].to_frame("value")
        self.check_dataset(
            constraints=system_shock_constraints,
            dataset=system_shock.dataset,
        )

    def check_extension_shock(self, extension_shock: ExtensionShock):
        """
        Validate extension shock data against predefined constraints.

        Parameters:
            extension_shock (ExtensionShock):
                Extension shock object containing dataset to validate.
        """

        extension_shock_constraints = self._manual_param_data[
            extension_shock.name
        ][
            extension_shock.id.scenario_name, extension_shock.id.proj_year
        ].to_frame(
            "value"
        )
        self.check_dataset(
            constraints=extension_shock_constraints,
            dataset=extension_shock.dataset,
        )

    def check_dataset(
        self, constraints: pd.DataFrame, dataset: AbstractListedDataSet
    ):
        """
        Verify dataset variables against provided constraints.

        Validates each variable in the dataset against its corresponding
        constraints using row/column masks and expected values.

        Parameters:
            constraints (pd.DataFrame):
                DataFrame containing validation constraints for dataset
                variables. Index must include 'variable' level.
            dataset (AbstractListedDataSet):
                Dataset object containing variables to validate.
        """

        for variable in constraints.index.get_level_values(
            "variable"
        ).unique():
            self.assert_constraints(
                df_tested=getattr(dataset, f"d{variable}").df,
                df_constraints=constraints.loc[variable].reset_index(),
            )

    def test_build_full_scenario_checklist(self):
        """
        Test function `_build_full_scenario_checklist`
        """
        adapter = AdapterManual(id_=self._id)

        # First case: no projected years
        adapter._id.scenario_names = ["A", "B", "C"]
        adapter._id.proj_years = []
        # Call function under test
        adapter._build_full_scenario_checklist()

        # Check that scenarios names equal id.scenario_names
        full_scenarios = adapter.get_input_data(adapter.KEY_SCENARIOS)
        assert adapter._id.scenario_names == list(full_scenarios.keys())
        assert not any(list(full_scenarios.values()))

        # Second case: projected years
        adapter._id.scenario_names = ["A", "B", "C"]
        adapter._id.proj_years = [1955, 1985, 2015]
        expected_list = [
            "A_1955",
            "A_1985",
            "A_2015",
            "B_1955",
            "B_1985",
            "B_2015",
            "C_1955",
            "C_1985",
            "C_2015",
        ]
        # Call function under test
        adapter._build_full_scenario_checklist()

        # Check that scenarios are properly built
        full_scenarios = adapter.get_input_data(adapter.KEY_SCENARIOS)
        assert list(full_scenarios.keys()) == expected_list
        assert not any(list(full_scenarios.values()))

    def test_load(self, mocker):
        """
        Test function `load`
        """

        spy_load_manual_param = mocker.spy(AdapterManual, "_load_manual_param")
        spy_load_detail_levels = mocker.spy(
            AdapterManual, "_load_detail_levels"
        )

        adapter = AdapterManual(id_=self._id)
        adapter.load()

        spy_load_manual_param.assert_called_once()
        spy_load_detail_levels.assert_called_once()

    def test_load_manual_param(self):
        """
        Test function `_load_manual_param`
        """

        adapter = AdapterManual(id_=self._id)

        # Call function under test
        adapter._load_manual_param()

        # Check that input_data is properly filled
        for k, v in self._manual_param_data.items():
            assert adapter.get_input_data(
                [adapter.KEY_MANUAL_PARAM, k]
            ).equals(v)

    def test_load_detail_levels(
        self,
        dl_regions_3,
        dl_sectors_3,
        dl_final_demand_categories_3,
        dl_extension_categories_3,
    ):
        """
        Test function `_load_detail_levels`
        """

        adapter = AdapterManual(id_=self._id)

        # Call function under test
        adapter._load_detail_levels(self._id.extension_names)

        # Check that input_data is properly filled
        assert adapter.i_dl_regions.equals(dl_regions_3)
        assert adapter.i_dl_sectors.equals(dl_sectors_3)
        assert adapter.i_dl_final_demand_categories.equals(
            dl_final_demand_categories_3
        )
        for name in self._id.extension_names:
            assert adapter.get_i_dl_extension_categories(name).equals(
                dl_extension_categories_3
            )

    def test_process(
        self,
        dl_regions_3,
        dl_sectors_3,
        dl_final_demand_categories_3,
        dl_extension_categories_3,
        mocker,
    ):
        """
        Test function `process`
        """
        adapter = AdapterManual(id_=self._id)

        # Set inputs
        self.set_input_data(
            adapter,
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
            dl_extension_categories_3,
        )

        # Update sheet_name in ext_cats bridges
        for name, dl_ in adapter.get_input_data(
            [
                adapter.KEY_DL,
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value,
            ]
        ).items():
            dl_.sheet_name = name

        # Set up spies
        spy_build_system_shocks = mocker.spy(
            AdapterManual, "_build_system_shocks"
        )
        spy_build_extension_shocks = mocker.spy(
            AdapterManual, "_build_extension_shocks"
        )

        # Call function under test
        adapter.process()

        # Check results
        spy_build_system_shocks.assert_called_once_with(
            adapter, data_=self._manual_param_data[cst.KEY_SYSTEM]
        )
        for index, name in enumerate(self._id.extension_names):
            spy.check_specific_call_with_args(
                function_spy=spy_build_extension_shocks,
                call_number=index + 1,
                args=[adapter],
                kwargs={
                    "data_": self._manual_param_data[name],
                    "extension_name": name,
                },
            )

    def test_is_scenario_applicable(self):
        """
        Test function `_is_scenario_applicable`
        """
        adapter = AdapterManual(id_=self._id)

        # Set inputs
        adapter.input_data[adapter.KEY_SCENARIOS] = {
            "A": False,
            "B": False,
            "C": False,
        }

        assert adapter._is_scenario_applicable(scenario="A")
        assert adapter._is_scenario_applicable(scenario="B")
        assert adapter._is_scenario_applicable(scenario="C")
        assert not adapter._is_scenario_applicable(scenario="D")

    def test_build_system_shock(
        self,
        dl_regions_3,
        dl_sectors_3,
        dl_final_demand_categories_3,
        dl_extension_categories_3,
    ):
        """
        Test function `_build_system_shocks`
        """
        adapter = AdapterManual(id_=self._id)

        # Set inputs
        self.set_input_data(
            adapter,
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
            dl_extension_categories_3,
        )

        # Update sheet_name in ext_cats bridges
        for name, dl_ in adapter.get_input_data(
            [
                adapter.KEY_DL,
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value,
            ]
        ).items():
            dl_.sheet_name = name

        # Call function under test
        adapter._build_system_shocks(
            data_=self._manual_param_data[cst.KEY_SYSTEM]
        )

        # Check results
        for dict_ in adapter.processed_data.values():
            self.check_system_shock(dict_[adapter.KEY_SYSTEM_SHOCK])

    def test_build_extension_shocks(
        self,
        dl_regions_3,
        dl_sectors_3,
        dl_final_demand_categories_3,
        dl_extension_categories_3,
    ):
        """
        Test function `_build_extension_shocks`
        """
        adapter = AdapterManual(id_=self._id)

        # Set inputs
        self.set_input_data(
            adapter,
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
            dl_extension_categories_3,
        )

        # Update sheet_name in ext_cats bridges
        for name, dl_ in adapter.get_input_data(
            [
                adapter.KEY_DL,
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value,
            ]
        ).items():
            dl_.sheet_name = name

        # Loop on extension names
        # -----------------------
        for name in adapter._id.extension_names:
            # Call function under test
            adapter._build_extension_shocks(
                extension_name=name, data_=self._manual_param_data[name]
            )

            # Check results
            for dict_ in adapter.processed_data.values():
                for ext_shock in dict_[adapter.KEY_EXT_SHOCKS].values():
                    self.check_extension_shock(ext_shock)

    def test_save(
        self,
        accounts_shock_1,
        accounts_shock_2,
    ):
        """
        Test function `save`
        """

        adapter = AdapterManual(id_=self._id)

        # Set outputs
        adapter.processed_data = {
            "TEST_1": {
                adapter.KEY_SYSTEM_SHOCK: accounts_shock_1.system_shock,
                adapter.KEY_EXT_SHOCKS: {
                    name: accounts_shock_1.get_extension_shock(name)
                    for name in accounts_shock_1._id.extension_names
                },
            },
            "TEST_2": {
                adapter.KEY_SYSTEM_SHOCK: accounts_shock_2.system_shock,
                adapter.KEY_EXT_SHOCKS: {
                    name: accounts_shock_2.get_extension_shock(name)
                    for name in accounts_shock_2._id.extension_names
                },
            },
        }

        # Call function under test
        adapter.save()

        # Read exported shocks
        map_scenario_shock = {
            "TEST_1": accounts_shock_1,
            "TEST_2": accounts_shock_2,
        }
        as_director = as_builder.get_director(reset=True)
        for scenario in adapter.processed_data.keys():
            shock = as_director.make_from_path(
                path=os.path.join(self.TMP_OUTPUT_DIR, scenario),
                load_data=True,
            )
            assert shock.equals(map_scenario_shock[scenario])
