from abc import ABC, abstractmethod
import os
import shutil
import joblib
import types
from enum import Enum

from matmat.workflows.identity import AbstractWorkflowIdentity
from matmat.workflows.metadata import MetaData
from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.utils.formats import factory as formats_factory
from matmat.utils.formats.core import AbstractFormat
from matmat.utils import logging as log, constants as cst, tools
from matmat.utils.errors import (
    MEMissingInputData,
    MEMissingProcessedData,
    MEMissingCalculatedData,
    MEMissingPostProcessedData,
    MEUndefinedPath,
)


class WorkflowStep(Enum):
    """
    Enumeration of the possible steps of a workflow
    """

    STEP_LOAD = "load"
    STEP_PROCESS = "process"
    STEP_CALCULATE = "calculate"
    STEP_POST_PROCESS = "post_process"
    STEP_SAVE = "save"


class AbstractWorkflow(ABC):
    """
    Base class for a MatMat workflow
    """

    # Class constants
    # Keys
    # Data
    KEY_INPUT_DATA = "input_data"
    KEY_PROCESSED_DATA = "processed_data"
    KEY_CALCULATED_DATA = "calculated_data"
    KEY_POST_PROCESSED_DATA = "post_processed_data"
    # Data names
    DATA_NAMES = {
        WorkflowStep.STEP_LOAD: KEY_INPUT_DATA,
        WorkflowStep.STEP_PROCESS: KEY_PROCESSED_DATA,
        WorkflowStep.STEP_CALCULATE: KEY_CALCULATED_DATA,
        WorkflowStep.STEP_POST_PROCESS: KEY_POST_PROCESSED_DATA,
    }
    # Detail levels
    KEY_DL = "detail_levels"
    # Bridges
    KEY_BRIDGES = "bridges"

    def __init__(
        self,
        id_: AbstractWorkflowIdentity,
        perform_validation: bool = True,
        no_confirm: bool = False,
    ):

        # Identity
        self._id = id_

        # Config
        self._perform_validation = perform_validation

        # Metadata
        self._metadata: MetaData = MetaData(
            workflow_kind=self.kind(),
            workflow_name=self.name(),
            id_=id_,
        )

        # Check input directories
        if self._perform_validation:
            self._validate_path_in()
        # Manage output directory
        self._manage_path_out(no_confirm=no_confirm)

        # Export formats
        self._export_formats_names: list[str] = []
        self._export_formats: list[AbstractFormat] = []
        if self._id.export_format is not None:
            if isinstance(self._id.export_format, str):
                self._export_formats_names.append(self._id.export_format)
                self._export_formats.append(
                    formats_factory.build_format_from_name(
                        self._id.export_format
                    )
                )
            else:
                for format_ in self._id.export_format:
                    self._export_formats_names.append(format_)
                    self._export_formats.append(
                        formats_factory.build_format_from_name(format_)
                    )
        else:
            self._export_formats_names.append(cst.FORMAT_PICKLE)
            self._export_formats.append(
                formats_factory.build_format_from_name(cst.FORMAT_PICKLE)
            )

        # Data
        self.input_data: dict = {}
        self.processed_data: dict = {}
        self.calculated_data: dict = {}
        self.post_processed_data: dict = {}

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def kind(cls) -> str:
        raise NotImplementedError

    @abstractmethod
    def load(self):
        """
        Load the data from external sources and store them into
        the attribute input_data
        """

    def load_dev(self):
        """
        Development method associated to load step
        """
        pass

    @abstractmethod
    def process(self):
        """
        Process the raw data found in the attribute input_data in order to
        transform them into the format / structure expected as output of the
        adapter, and store them into the attribute processed_data
        """

    def process_dev(self):
        """
        Development method associated to process step
        """
        pass

    @abstractmethod
    def calculate(self):
        """
        Execute calculations, store results into the attribute
        calculated_data
        """

    def calculate_dev(self):
        """
        Development method associated to calculate step
        """
        pass

    @abstractmethod
    def post_process(self):
        """
        Execute post-processing, store results into the attribute
        post_processed_data
        """

    def post_process_dev(self):
        """
        Development method associated to post_process step
        """
        pass

    @abstractmethod
    def save(self):
        """
        Export the processed data into output files (.pkl, .xlsx, .csv...)
        """

    def save_dev(self):
        """
        Development method associated to save step
        """

    @property
    @abstractmethod
    def enabled_steps(self) -> set[WorkflowStep]:
        """
        Returns the set of steps enabled in this workflow
        """
        raise NotImplementedError

    @property
    def id(self):
        return self._id

    @property
    def path_in(self):
        return self._id.path_in

    @path_in.setter
    def path_in(self, value: str | dict[str, str] | dict[str, list[str]]):
        self._id.path_in = value
        if self._perform_validation:
            self._validate_path_in()

    @property
    def path_out(self):
        return self._id.path_out

    @path_out.setter
    def path_out(self, value: str | dict[str, str] | dict[str, list[str]]):
        self._id.path_out = value
        self._manage_path_out()

    def iterate_over_inputs_paths(self):
        """
        Iterate over input path(s)
        """
        yield from self.__iterate_over_paths(self.path_in)

    def iterate_over_outputs_paths(self):
        """
        Iterate over output path(s)
        """
        yield from self.__iterate_over_paths(self.path_out)

    @staticmethod
    def __iterate_over_paths(paths: str | types.SimpleNamespace):
        """
        Iterate over paths
        """
        if isinstance(paths, str):
            yield paths
        elif isinstance(paths, types.SimpleNamespace):
            for v in vars(paths).values():
                if isinstance(v, str):
                    yield v
                elif isinstance(v, list):
                    yield from v

    def first_output_path(self) -> str:
        """
        Returns the first path defined in the output paths
        """
        return next(self.iterate_over_outputs_paths())

    def __run_step(
        self,
        step: WorkflowStep,
        load_cache: bool,
        save_cache: bool,
        dev: bool,
        cache_path: str | None = None,
    ):
        """
        Execute the step given as parameter.

        Parameters:
            step (WorkflowStep):
                The step to execute
            load_cache (bool):
                Whether to load cached data if available
            save_cache (bool):
                Whether to save data to cache
            dev (bool):
                Whether to run in development mode
            cache_path (str | None):
                Path to cache file. Required if load_cache or save_cache is True

        Raises:
            FileNotFoundError: If load_cache is True and cache_path does not exist
        """
        if step in self.enabled_steps:
            # Load cached data if load_cache enabled
            if load_cache and cache_path is not None:
                if not os.path.exists(cache_path):
                    log.error(f"Could not find cache at {cache_path}")
                    log.error(f"Execute step {step.value.upper()} instead.")
                    log.log_title(title=step.value, symbol="#")
                    getattr(self, step.value)()
                else:
                    log.info(f"Dev mode: load cached {self.DATA_NAMES[step]}")
                    setattr(
                        self, self.DATA_NAMES[step], joblib.load(cache_path)
                    )
            # Otherwise execute step
            else:
                log.log_title(title=step.value, symbol="#")
                getattr(self, step.value)()

            # Optional: save data to cache
            if save_cache and cache_path is not None:
                log.info(f"Dev mode: save {self.DATA_NAMES[step]} to cache")
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                joblib.dump(getattr(self, self.DATA_NAMES[step]), cache_path)

            # Run development step if dev mode enabled
            if dev:
                log.log_title(title=f"dev mode: {step.value}", symbol="#")
                getattr(self, f"{step.value}_dev")()

    @tools.timeit
    def execute(
        self,
        load_cache: bool = False,
        save_cache: bool = False,
        clear_cache: bool = False,
        dev: bool = False,
    ):
        """
        Execute the steps defined by this workflow by calling the
        following methods in this specific order:
            - load()
            - process()
            - calculate()
            - post_process()
            - save()
        Note that only the steps defined in the property enabled_steps
        will be executed.
        These methods work as "hooks" and shall be implemented by concrete
        classes deriving from this class.

        Parameters:
            load_cache (bool):
                Enable cache loading
                    - load self.input_data from cache. In this case, the step
                      LOAD is not executed.
                    - load self.processed_data from cache if available. In this
                      case, the step PROCESS is not executed.
                Default to False
            save_cache (bool):
                Enable cache saving
                    - save self.input_data to cache
                    - save self.processed_data to cache
                Default to False
            clear_cache (bool):
                Enable cache clearing
                    - remove cache directory
                Default to False
            dev (bool):
                Enable development mode (Default to False)
        """
        log.log_title(
            title=f"{self.kind()} {self.name()}",
            symbol="-",
            is_main=True,
        )

        # Set cache directories
        cache_dir = os.path.join(self.first_output_path(), ".cache")
        input_cache = os.path.join(cache_dir, f"{self.KEY_INPUT_DATA}.joblib")
        processed_cache = os.path.join(
            cache_dir, f"{self.KEY_PROCESSED_DATA}.joblib"
        )
        calculated_cache = os.path.join(
            cache_dir, f"{self.KEY_CALCULATED_DATA}.joblib"
        )
        post_processed_cache = os.path.join(
            cache_dir, f"{self.KEY_POST_PROCESSED_DATA}.joblib"
        )

        # LOAD STEP
        self.__run_step(
            step=WorkflowStep.STEP_LOAD,
            cache_path=input_cache,
            load_cache=load_cache,
            save_cache=save_cache,
            dev=dev,
        )

        # PROCESS STEP
        self.__run_step(
            step=WorkflowStep.STEP_PROCESS,
            cache_path=processed_cache,
            load_cache=load_cache,
            save_cache=save_cache,
            dev=dev,
        )

        # CALCULATE STEP
        self.__run_step(
            step=WorkflowStep.STEP_CALCULATE,
            cache_path=calculated_cache,
            load_cache=load_cache,
            save_cache=save_cache,
            dev=dev,
        )

        # POST PROCESS STEP
        self.__run_step(
            step=WorkflowStep.STEP_POST_PROCESS,
            cache_path=post_processed_cache,
            load_cache=load_cache,
            save_cache=save_cache,
            dev=dev,
        )

        # SAVE STEP
        self.__run_step(
            step=WorkflowStep.STEP_SAVE,
            cache_path=None,
            load_cache=load_cache,
            save_cache=save_cache,
            dev=dev,
        )
        self._metadata.save_to_path(path=self.first_output_path())

        # Optional: clear cache directory
        if clear_cache:
            log.info("Dev mode: clear cache directory")
            shutil.rmtree(cache_dir, ignore_errors=True)

    @property
    def i_dl_regions(self) -> dl.RegionsDL:
        """
        Returns input data for regions detail level
        """
        return self.get_input_data(
            [self.KEY_DL, dl.DetailLevelKind.REGIONS.value]
        )

    @property
    def i_dl_sectors(self) -> dl.SectorsDL:
        """
        Returns input data for sectors detail level
        """
        return self.get_input_data(
            [self.KEY_DL, dl.DetailLevelKind.SECTORS.value]
        )

    @property
    def i_dl_final_demand_categories(self) -> dl.FinalDemandCategoriesDL:
        """
        Returns input data for final demand categories detail level
        """
        return self.get_input_data(
            [self.KEY_DL, dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value]
        )

    def get_i_dl_extension_categories(
        self, extension_name: str
    ) -> dl.ExtensionCategoriesDL:
        """
        Returns the detail level object from input data associated
        with the given extension name, if it exists.
        """
        return self.get_input_data(
            [
                self.KEY_DL,
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value,
                extension_name,
            ]
        )

    @property
    def p_dl_regions(self) -> dl.RegionsDL:
        """
        Returns processed data for regions detail level
        """
        return self.get_processed_data(
            [self.KEY_DL, dl.DetailLevelKind.REGIONS.value]
        )

    @property
    def p_dl_sectors(self) -> dl.SectorsDL:
        """
        Returns processed data for sectors detail level
        """
        return self.get_processed_data(
            [self.KEY_DL, dl.DetailLevelKind.SECTORS.value]
        )

    @property
    def p_dl_final_demand_categories(self) -> dl.FinalDemandCategoriesDL:
        """
        Returns processed data for final demand categories detail level
        """
        return self.get_processed_data(
            [self.KEY_DL, dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value]
        )

    def get_p_dl_extension_categories(
        self, extension_name: str
    ) -> dl.ExtensionCategoriesDL:
        """
        Returns the detail level object from processed data associated
        with the given extension name, if it exists.
        """
        return self.get_processed_data(
            [
                self.KEY_DL,
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value,
                extension_name,
            ]
        )

    @property
    def i_bridge_regions(self) -> bridge.Bridge | bridge.MultiBridge:
        return self.get_input_data(
            [self.KEY_BRIDGES, dl.DetailLevelKind.REGIONS.value]
        )

    @property
    def i_bridge_sectors(self) -> bridge.Bridge | bridge.MultiBridge:
        return self.get_input_data(
            [self.KEY_BRIDGES, dl.DetailLevelKind.SECTORS.value]
        )

    @property
    def i_bridge_final_demand_categories(
        self,
    ) -> bridge.Bridge | bridge.MultiBridge:
        return self.get_input_data(
            [
                self.KEY_BRIDGES,
                dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value,
            ]
        )

    def get_i_bridge_extension_categories(
        self, extension_name: str
    ) -> bridge.Bridge | bridge.MultiBridge:
        """
        Returns the bridge object from input data associated
        with the given extension name, if it exists.
        """
        return self.get_input_data(
            [
                self.KEY_BRIDGES,
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value,
                extension_name,
            ]
        )

    @property
    def p_bridge_regions(self) -> bridge.Bridge | bridge.MultiBridge:
        return self.get_processed_data(
            [self.KEY_BRIDGES, dl.DetailLevelKind.REGIONS.value]
        )

    @property
    def p_bridge_sectors(self) -> bridge.Bridge | bridge.MultiBridge:
        return self.get_processed_data(
            [self.KEY_BRIDGES, dl.DetailLevelKind.SECTORS.value]
        )

    @property
    def p_bridge_final_demand_categories(
        self,
    ) -> bridge.Bridge | bridge.MultiBridge:
        return self.get_processed_data(
            [
                self.KEY_BRIDGES,
                dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value,
            ]
        )

    def get_p_bridge_extension_categories(
        self, extension_name: str
    ) -> bridge.Bridge | bridge.MultiBridge:
        """
        Returns the bridge object from processed data associated
        with the given extension name, if it exists.
        """
        return self.get_processed_data(
            [
                self.KEY_BRIDGES,
                dl.DetailLevelKind.EXTENSION_CATEGORIES.value,
                extension_name,
            ]
        )

    @staticmethod
    def add_nested_dict_safely(dict_: dict, key: str):
        if key not in dict_.keys():
            dict_[key] = {}

    @staticmethod
    def __get_data(dict_: dict, keys: str | list, exception_type: type):
        """
        Retrieves data in dict_ based on a key or a list of keys.

        Accesses nested data if a list of keys is provided, or directly
        returns data associated with a single key.

        Raises:
            exception_type : if the key or any key in the list does not
                             exist or if the key type is incorrect.
        """
        try:
            if isinstance(keys, list):
                current = dict_
                for key in keys:
                    current = current[key]
                return current
            else:
                return dict_[keys]
        except (KeyError, TypeError):
            raise exception_type(
                data_name=keys,
                available_data=dict_,
            )

    def get_input_data(self, keys: str | list):
        """
        Retrieves input data based on a key or a list of keys.

        Accesses nested input data if a list of keys is provided, or directly
        returns data associated with a single key.

        Raises:
            MEMissingInputData : if the key or any key in the list does not
                                 exist or if the key type is incorrect.
        """
        return self.__get_data(
            dict_=self.input_data,
            keys=keys,
            exception_type=MEMissingInputData,
        )

    def get_processed_data(self, keys: str | list):
        """
        Retrieves processed data based on a key or a list of keys.

        Accesses nested processed data if a list of keys is provided, or
        directly returns data associated with a single key.

        Raises:
            MEMissingProcessedData : if the key or any key in the list does not
                                     exist or if the key type is incorrect.
        """
        return self.__get_data(
            dict_=self.processed_data,
            keys=keys,
            exception_type=MEMissingProcessedData,
        )

    def get_calculated_data(self, keys: str | list):
        """
        Retrieves calculated data based on a key or a list of keys.

        Accesses nested calculated data if a list of keys is provided, or
        directly returns data associated with a single key.

        Raises:
            MEMissingCalculatedData : if the key or any key in the list does not
                                      exist or if the key type is incorrect.
        """
        return self.__get_data(
            dict_=self.calculated_data,
            keys=keys,
            exception_type=MEMissingCalculatedData,
        )

    def get_post_processed_data(self, keys: str | list):
        """
        Retrieves post-processed data based on a key or a list of keys.

        Accesses nested post-processed data if a list of keys is provided, or
        directly returns data associated with a single key.

        Raises:
            MEMissingPostProcessedData : if the key or any key in the list does not
                                         exist or if the key type is incorrect.
        """
        return self.__get_data(
            dict_=self.post_processed_data,
            keys=keys,
            exception_type=MEMissingPostProcessedData,
        )

    def _validate_path_in(self):
        """
        Ensure that all the inputs paths exist

        Raises:
            MEUndefinedPath : if an input path does not exist
        """
        for path in self.iterate_over_inputs_paths():
            if not os.path.exists(path):
                raise MEUndefinedPath(path=path)

    def _manage_path_out(self, no_confirm: bool = False):
        """
        It the output paths do not exist, create them.
        If the output paths exist and are not empty, ask the user if they
        want to clean them.
        """
        for path in self.iterate_over_outputs_paths():
            if os.path.isdir(path) and os.listdir(path):
                log.warning(f"Output directory {path} is not empty.")
                if self.id.clean_path_out is None:
                    shall_clean = input("Do you want to clean it? (y/N) > ")
                elif self.id.clean_path_out:
                    if not no_confirm:
                        log.warning(f"Directory {path} will be cleaned.")
                        shall_clean = input("Are you sure? (y/N) > ")
                    else:
                        shall_clean = "Y"
                else:
                    shall_clean = "N"
                if str(shall_clean).upper() == "Y":
                    log.info(f"Clean directory {path}")
                    shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)
