"""
Presentation
************
This module is the core module of the package
`adapters.shocks.manual`.

It defines the "manual" adapter. This adapter permits
to generate system and extensions shocks from a manual parametrization file.

This adapter takes as input:
    - a file describing the manual parametrization
    - a detail_levels file
and performs the following treatments:
    - depending on the manual parametrization file content:
        - build system shocks and valorize them
        - build extensions shocks and valorize them
    - Save the generated shocks

Content
*******
- Classes:
    - :class:`AdapterManual`
"""

import os

import pandas as pd

from matmat.core.detail_level import factory as dl_factory
from matmat.workflows.adapters.core import AbstractAdapter
from matmat.workflows.adapters.shocks.manual.identity import (
    AdapterManualIdentity,
)
import matmat.core.shocks.system.builder as ss_builder
import matmat.core.shocks.extension.builder as se_builder
from matmat.core.shocks.system.identity import SystemShockIdentity
from matmat.core.shocks.extension.identity import ExtensionShockIdentity
from matmat.utils import logging as log, constants as cst
from matmat.utils.errors import (
    MEDataNotSuitableForWorkflow,
    MEMissingProcessedData,
    MEMissingInputData,
)


class AdapterManual(AbstractAdapter):
    """
    Adapter to create shocks by manually setting values.
    This adapter permits to create system and/or extensions shocks.
    """

    # Constants
    SHEET_SYSTEM = "system"
    KEY_MANUAL_PARAM = "manual_param"
    KEY_SCENARIOS = "scenarios"
    KEY_DL = "detail_levels"
    KEY_SYSTEM_SHOCK = "system_shock"
    KEY_EXT_SHOCKS = "extensions_shocks"

    # Identity
    _id: AdapterManualIdentity

    @classmethod
    def name(cls) -> str:
        return "manual"

    def __init__(self, id_: AdapterManualIdentity, no_confirm: bool = False):

        super().__init__(id_=id_, no_confirm=no_confirm)
        self._build_full_scenario_checklist()

        # This adapter only deals with Excel files for manual param input
        if not self.path_in.manual_param_file.endswith(".xlsx"):
            raise MEDataNotSuitableForWorkflow(
                data_name=os.path.basename(self.path_in.manual_param_file),
                workflow_name=self.__class__.__name__,
            )

    def _build_full_scenario_checklist(self):
        """
        Builds the full checklist of scenarios, appending project years to each
        scenario name if project years are specified.

        This method initializes the scenario checklist within the input_data
        attribute using the predefined key `KEY_SCENARIOS`.
        """
        if self._id.proj_years:
            full_scenario_names = [
                f"{scenario}_{year}"
                for scenario in self._id.scenario_names
                for year in self._id.proj_years
            ]
        else:
            full_scenario_names = self._id.scenario_names
        # Initialize scenarios checklist
        self.input_data[self.KEY_SCENARIOS] = {
            scenario: False for scenario in full_scenario_names
        }

    def load(self):
        """
        Load input data
        """
        self._load_manual_param()
        self._load_detail_levels(
            [
                name
                for name in self.get_input_data(self.KEY_MANUAL_PARAM).keys()
                if name != self.SHEET_SYSTEM
            ]
        )

    def _load_manual_param(self):
        """
        Load data from manual param input file

        Load all the sheets of the Excel input file, and store them one
        by one in the input_data dictionary at KEY_MANUAL_PARAM entry

        Fill self.input_data[self.KEY_MANUAL_PARAM]
        """
        excel_data = {}
        for required_sheet in [self.SHEET_SYSTEM] + self._id.extension_names:
            try:
                log.debug(f"Load sheet '{required_sheet}'")
                excel_data[required_sheet] = pd.read_excel(
                    self.path_in.manual_param_file,
                    sheet_name=required_sheet,
                    header=[0, 1],
                    index_col=[*range(0, 7)],
                )
            except ValueError as e:
                log.error(f"Can't find sheet '{required_sheet}' in input file")
                raise ValueError from e

        # Store each sheet in the input data dictionary, at
        # KEY_MANUAL_PARAM entry
        self.add_nested_dict_safely(self.input_data, self.KEY_MANUAL_PARAM)
        for k, v in excel_data.items():
            self.get_input_data(self.KEY_MANUAL_PARAM)[k] = v

    def _load_detail_levels(self, extension_names: list[str]):
        """
        Loads detail levels based on the provided extension names.

        This method generates a dictionary of detail levels and assigns it to
        the input data attribute using the specified extension names.

        Parameters:
            extension_names (list[str]):
                A list of extension names used to create the detail level
                dictionary.
        """

        if os.path.isfile(self.path_in.detail_levels_file):
            self.input_data[self.KEY_DL] = dl_factory.make_dl_dict_from_path(
                path=os.path.dirname(self.path_in.detail_levels_file),
                file_name=os.path.basename(self.path_in.detail_levels_file),
                extension_names=extension_names,
            )
        else:
            self.input_data[self.KEY_DL] = dl_factory.make_dl_dict_from_path(
                path=self.path_in.detail_levels_file,
                extension_names=extension_names,
            )

    def process(self):
        """
        Processes input data and builds shocks based on the provided sheet
        names.

        Iterates over input data to handle specific types of sheets, such as
        system shocks and extension shocks.

        Logs warnings for scenarios that are not found
        in the input file.
        """
        for sheet_name, manual_param in self.get_input_data(
            self.KEY_MANUAL_PARAM
        ).items():

            match sheet_name:
                # Detail levels entry => pass
                case self.KEY_DL:
                    continue
                # System shock sheet
                case self.SHEET_SYSTEM:
                    self._build_system_shocks(data_=manual_param)
                # Other sheets => extensions shocks
                case _:
                    self._build_extension_shocks(
                        extension_name=sheet_name, data_=manual_param
                    )

        # Inform user about the scenarios that were not processed
        for scenario, scenario_status in self.input_data[
            self.KEY_SCENARIOS
        ].items():
            if not scenario_status:
                log.warning(
                    f"Scenario '{scenario}' was not found in input file"
                )

    @staticmethod
    def _compute_scenario_name(column: str | tuple[str, ...]) -> str:
        """
        Computes a scenario name based on the input column.

        The column can either be a string or a tuple of strings. If a tuple
        is provided, the elements are concatenated with underscores.

        Parameters:
            column (str | tuple[str, ...]):
                A string or a tuple of strings used to define the scenario
                name.

        Returns:
            str: The computed scenario name.
        """
        if isinstance(column, str):
            column_name = column
        else:
            column_name = column[0]
            if len(column) > 1:
                for elt in column[1:]:
                    column_name += f"_{elt}"
        return column_name

    def _is_scenario_applicable(self, scenario: str):
        """
        Checks if the given scenario exists in the predefined scenarios
        within the input data.

        Parameters:
            scenario (str):
                The scenario to be checked for applicability.

        Returns:
            bool: True if the scenario exists, False otherwise.
        """
        return scenario in self.input_data[self.KEY_SCENARIOS].keys()

    def _build_system_shocks(self, data_: pd.DataFrame):
        """
        Builds and processes system shocks for scenarios present in the provided
        data. This method iterates over each column in the input data and
        generates the system shock if required, skipping scenarios not applicable
        as per the settings.

        Parameters:
            data_ (pd.DataFrame):
                DataFrame containing scenario data to be processed.
        """
        for column in list(data_.columns):

            scenario_name = self._compute_scenario_name(column)

            # Skip scenarios not in the list of scenarios from settings file
            if not self._is_scenario_applicable(scenario_name):
                log.warning(
                    f"Skip scenario '{scenario_name}' as it is "
                    "not in settings file."
                )
                continue

            try:
                sys_shock = self.get_processed_data(
                    [self.KEY_SYSTEM_SHOCK, scenario_name]
                )
            except MEMissingProcessedData:
                log.verbose(
                    f"Generating system shock for scenario '{scenario_name}'"
                )

                # Generate system shock
                ss_dir = ss_builder.get_director(reset=True)

                # Set detail levels
                ss_dir.set_regions(self.i_dl_regions)
                ss_dir.set_sectors(self.i_dl_sectors)
                ss_dir.set_final_demand_categories(
                    self.i_dl_final_demand_categories
                )

                # Set identity card
                ss_dir.set_id(
                    id_=SystemShockIdentity(
                        base_year=self._id.base_year,
                        scenario_name=(
                            column if isinstance(column, str) else column[0]
                        ),
                        proj_year=(
                            column[1] if isinstance(column, tuple) else None
                        ),
                    )
                )

                sys_shock = ss_dir.make_shock_complete()

                # Add processed data entry for this scenario
                self.add_nested_dict_safely(self.processed_data, scenario_name)
                self.get_processed_data(scenario_name)[
                    self.KEY_SYSTEM_SHOCK
                ] = sys_shock

            sys_shock.set_each_manual_param(
                manual_param=data_.loc[:, column],
            )

            # Update scenarios checklist
            self.get_input_data(self.KEY_SCENARIOS)[scenario_name] = True

    def _build_extension_shocks(
        self, extension_name: str, data_: pd.DataFrame
    ):
        """
        Builds and processes extension shocks for given scenarios and data.

        This method processes extension shocks for specific scenarios by
        validating applicable scenarios, generating shocks if not already
        present, and setting required manual parameters.

        Parameters:
            extension_name (str):
                The name of the extension for which the shocks are processed.
            data_ (pd.DataFrame):
                Data containing manual parameters for shocks.

        Raises:
            MEMissingInputData:
                Raised if extension categories are missing in the detail levels file.

        """
        for column in list(data_.columns):

            scenario_name = self._compute_scenario_name(column)

            # Skip scenarios not in the list of scenarios from settings file
            if not self._is_scenario_applicable(scenario_name):
                log.warning(
                    f"Skip scenario '{scenario_name}' as it is "
                    "not in settings file."
                )
                continue

            try:
                ext_shock = self.get_processed_data(
                    [scenario_name, self.KEY_EXT_SHOCKS, extension_name]
                )
            except MEMissingProcessedData:
                log.verbose(
                    f"Generating extension shock '{extension_name}' "
                    f"for '{scenario_name}'"
                )

                # Generate system shock
                se_dir = se_builder.get_director(reset=True)

                # Set detail levels
                se_dir.set_regions(self.i_dl_regions)
                se_dir.set_sectors(self.i_dl_sectors)
                se_dir.set_final_demand_categories(
                    self.i_dl_final_demand_categories
                )
                try:
                    se_dir.set_extension_categories(
                        self.get_i_dl_extension_categories(extension_name)
                    )
                except MEMissingInputData as e:
                    log.error(
                        "Can't find extension categories for "
                        f"extension '{extension_name}'. Add them to "
                        f"detail levels file and re-run the adapter."
                    )
                    raise e

                # Set identity card
                se_dir.set_id(
                    id_=ExtensionShockIdentity(
                        extension_name=extension_name,
                        base_year=self._id.base_year,
                        scenario_name=(
                            column if isinstance(column, str) else column[0]
                        ),
                        proj_year=(
                            column[1] if isinstance(column, tuple) else None
                        ),
                    )
                )

                ext_shock = se_dir.make_shock_complete(extension_name)

                # Add processed data entry for this scenario
                self.add_nested_dict_safely(
                    dict_=self.processed_data, key=scenario_name
                )
                self.add_nested_dict_safely(
                    dict_=self.get_processed_data(scenario_name),
                    key=self.KEY_EXT_SHOCKS,
                )
                self.get_processed_data([scenario_name, self.KEY_EXT_SHOCKS])[
                    extension_name
                ] = ext_shock

            ext_shock.set_each_manual_param(
                manual_param=data_.loc[:, column],
            )

    def save(self):
        """
        Export generated shocks to specified output directory.

        Exports system and extension shocks stored in `processed_data`
        using configured export formats. Skips scenarios without system
        or extension shocks.
        """

        for k, v in self.processed_data.items():
            try:
                v[self.KEY_SYSTEM_SHOCK].save_to_path(
                    path=os.path.join(self.path_out, k, cst.DIR_SYSTEM),
                    export_format=self._export_formats_names,
                )
            except KeyError:
                # No system shock generated for this scenario
                pass

            try:
                for ext_name, ext in v[self.KEY_EXT_SHOCKS].items():
                    ext.save_to_path(
                        path=os.path.join(
                            self.path_out, k, cst.DIR_EXTENSIONS
                        ),
                        export_format=self._export_formats_names,
                    )
            except KeyError:
                # No extension shock generated for this scenario
                pass
