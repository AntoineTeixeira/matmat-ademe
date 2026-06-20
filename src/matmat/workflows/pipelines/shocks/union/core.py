"""
Presentation
************
This module is the core module of the package
`pipelines.shocks.union`.

It defines the "union" shocks pipeline. This pipeline permits
to concatenate a set of shocks into one unified shock.

Content
*******
- Classes:
    - :class:`PipelineUnion`
"""

import os

from matmat.workflows.pipelines.core import AbstractPipeline
from matmat.workflows.pipelines.shocks.union.identity import PipelineUnionIdentity
from matmat.core.base.identity import AbstractIdentity
from matmat.core.shocks import builder as s_builder
from matmat.core.shocks.core import AccountsShock
from matmat.core.bridge import factory as bridge_factory
from matmat.utils import logging as log, config
from matmat.utils.errors import MEExtensionNotFound


class PipelineUnion(AbstractPipeline):

    KEY_SHOCKS = "shocks"
    KEY_SECTORS = "sectors"
    KEY_OUTPUT = "output"

    # Identity
    _id: PipelineUnionIdentity

    @classmethod
    def name(cls) -> str:
        return "union"

    def load(self) -> None:
        """
        Load input data:
            - Load shocks in path_in, one by one
            - Load multibridge
        """
        log.info("### LOAD INPUT SHOCKS ###")

        list_of_ext_shocks_names = self._load_input_shocks()
        self._load_multi_bridges(list_of_ext_shocks_names)

    def _load_input_shocks(self) -> list[str]:
        """
        Load shocks from path_in, one by one
        Returns the list of extensions shocks unique names
        """
        # Prevent replacing of 0.0 by NaN when loading shocks
        # It is essential that NaN are preserved and not replaced by 0.0
        # otherwise it would be impossible to know which 0.0 is a functional
        # value to be injected and which 0.0 is actually a NaN
        prev__config = config.CLEAN_RESIDUAL_NAN_AND_INF
        config.CLEAN_RESIDUAL_NAN_AND_INF = False

        self.input_data[self.KEY_SHOCKS] = {}
        # Init a list gathering the extensions shocks names (unique)
        # It will be used to load multi-bridge matrices
        list_of_ext_shocks_names = []
        for k, v in self.path_in.shocks.items():

            # Init dictionary entry
            self.input_data[self.KEY_SHOCKS][k] = []

            # Deal with multiple inputs (can be a list[str] or a str)
            path_list = [v] if isinstance(v, str) else v

            for path_ in path_list:
                current_shock = s_builder.get_director(
                    reset=True
                ).make_from_path(path=path_, load_data=True)
                self.get_input_data([self.KEY_SHOCKS, k]).append(current_shock)
                # Fill the list with the extensions shocks names if they are not
                # already in it
                list_of_ext_shocks_names += [
                    ext_shock.name
                    for ext_shock in current_shock.list_extensions_shocks()
                    if ext_shock.name not in list_of_ext_shocks_names
                ]

        # Reset config to previous value
        config.CLEAN_RESIDUAL_NAN_AND_INF = prev__config

        return list_of_ext_shocks_names

    def _load_multi_bridges(self, list_of_ext_shocks_names: list[str]):
        """
        Load the multibridge matrices
        """
        if self.path_in.multi_bridge is not None:
            self.input_data[self.KEY_BRIDGES] = (
                bridge_factory.make_bridge_dict_from_path(
                    path=os.path.dirname(self.path_in.multi_bridge),
                    file_name=os.path.basename(self.path_in.multi_bridge),
                    sectors_is_multi=True,
                    regions_is_multi=True,
                    final_demand_categories_is_multi=True,
                    extension_categories_is_multi={
                        k: True for k in list_of_ext_shocks_names
                    },
                    multi_bridge_filter_level=self._id.multi_bridge_filter_level,
                )
            )

    def process(self) -> None:
        """
        Process input data with the following treatments:
            - Disaggregate input shocks to a common aggregation level
              using multibridge
            - Concatenate the disaggregated input shocks into one unified shock
        """

        log.info("### PROCESS INPUT SHOCKS ###")
        if self.path_in.multi_bridge is not None:
            self._disaggregate_shocks()
        else:
            self._pass_shocks_to_processed_data()

        self._build_concatenated_shock()

    def _pass_shocks_to_processed_data(self):
        """
        Transfer input shocks to processed data
        """
        # Init dictionary entry
        self.processed_data[self.KEY_SHOCKS] = {}
        for agg_level, i_shocks_list in self.get_input_data(
            self.KEY_SHOCKS
        ).items():
            # Init dictionary entry
            self.processed_data[self.KEY_SHOCKS][agg_level] = []
            for i_shock in i_shocks_list:
                p_shock = i_shock.copy()
                self.get_processed_data([self.KEY_SHOCKS, agg_level]).append(
                    p_shock
                )

    def _disaggregate_shocks(self):
        """
        Use the input multibridge to disaggregate the input shocks to the
        same aggregation level
        """

        log.info("Align shocks aggregation levels using multibridge")

        # Retrieve multi bridges
        multi_bridges = self.get_input_data(self.KEY_BRIDGES)

        # Disaggregate shocks using multibridge
        self.processed_data[self.KEY_SHOCKS] = {}
        for agg_level, i_shocks_list in self.get_input_data(
            self.KEY_SHOCKS
        ).items():
            # Init dictionary entry
            self.processed_data[self.KEY_SHOCKS][agg_level] = []
            log.info(f"Disaggregate from aggregation level '{agg_level}'")
            for i_shock in i_shocks_list:
                p_shock = i_shock.copy()

                multi_bridge = [
                    df.get_bridge(key=agg_level)
                    for df in multi_bridges.values()
                ]

                p_shock.disaggregate(*multi_bridge)
                self.get_processed_data([self.KEY_SHOCKS, agg_level]).append(
                    p_shock
                )

    def _build_concatenated_shock(self):
        """
        Initialize an empty shock from the first shock in the input list,
        then inject the remaining shocks one after another, building a
        global shock including all the input shocks.

        Notes:
            - The order in the list is relevant, as the last values injected
              override the previous ones.
        """

        log.info("Concatenate shocks into one unified shock")

        is_first_iteration = True
        concatenated_shock: AccountsShock = None

        for agg_level, shocks_list in self.get_processed_data(
            self.KEY_SHOCKS
        ).items():

            for shock in shocks_list:

                # At first iteration, initialize shock
                if is_first_iteration:
                    is_first_iteration = False
                    # Initialize shock and reset datasets
                    concatenated_shock = shock.copy()
                    concatenated_shock.reset()

                # Fill shock

                # System shock
                concatenated_shock.system_shock.dataset.inject(
                    dataset_=shock.system_shock.dataset,
                    inject_zeros=True,
                )

                # Extensions shocks
                for new_ext_shock in shock.list_extensions_shocks():
                    try:
                        ref_ext_shock = concatenated_shock.get_extension_shock(
                            new_ext_shock.name
                        )
                        ref_ext_shock.dataset.inject(
                            dataset_=new_ext_shock.dataset,
                            inject_zeros=True,
                        )
                    except MEExtensionNotFound:
                        concatenated_shock.add_extension_shock(new_ext_shock)

        def feed_id(id_: AbstractIdentity):
            id_.base_year = self._id.base_year
            id_.proj_year = self._id.proj_year
            id_.scenario_name = self._id.scenario_name

        if concatenated_shock is not None:

            feed_id(concatenated_shock.id)
            feed_id(concatenated_shock.system_shock.id)
            for ext_shock in concatenated_shock.list_extensions_shocks():
                feed_id(ext_shock.id)

            # Save to processed_data dictionary
            self.processed_data[self.KEY_OUTPUT] = concatenated_shock

    def calculate(self):
        log.info("No calculation performed")
        pass

    def save(self) -> None:
        """
        Save the unified shock to path_out
        """

        log.info("### SAVE CONCATENATED SHOCK ###")

        self.get_processed_data(self.KEY_OUTPUT).save_to_path(
            path=self.path_out,
            export_format=self._export_formats_names,
        )
