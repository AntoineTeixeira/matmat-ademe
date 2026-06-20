import os
import shutil

import pandas as pd

from matmat.core.shocks.extension.core import ExtensionShock
from matmat.workflows.pipelines.shocks.union import core as union, identity as union_id
from matmat.core.shocks import builder as s_builder
from matmat.core.shocks.core import AccountsShock
from matmat.core.shocks.system.core import SystemShock
from matmat.core.shocks.system import builder as ss_builder
from matmat.core.shocks.extension import builder as se_builder
from matmat.core.shocks.system.dataset.core import SystemShockDataSet
from matmat.core.shocks.extension.dataset.core import ExtensionShockDataSet
from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.utils import constants as cst, config

from tests.utils import constants as tests_cst, builders, spy


class TestPipelineUnion:

    TMP_INPUT_DIR = "./tmp_input"
    TMP_OUTPUT_DIR = "./tmp_output"
    MULTI_BRIDGE_FILE = "multibridge.xlsx"
    KEY_SECTORS = "sectors"
    KEY_FD = "final_demand_categories"

    FILTER_LEVEL = "type"

    SECTORS_1 = ["A", "B", "C", "D", "E"]
    SECTORS_2 = ["F", "G"]
    SECTORS_3 = ["C", "D", "E"]
    SECTORS_4 = ["B"]
    SECTORS_FULL = ["A", "B", "C", "D", "E", "F", "G"]

    FD_1 = ["fd_cat_1", "fd_cat_2", "fd_cat_3", "fd_cat_4"]
    FD_2 = ["fd_cat_2", "fd_cat_4"]
    FD_3 = ["fd_cat_3"]
    FD_4 = ["fd_cat_1", "fd_cat_4"]
    FD_FULL = ["fd_cat_1", "fd_cat_2", "fd_cat_3", "fd_cat_4"]

    MAP_AGG_LEVELS = {
        "agg_level_1": {
            "0": {KEY_SECTORS: SECTORS_1, KEY_FD: FD_1},
            "1": {KEY_SECTORS: SECTORS_1, KEY_FD: FD_1},
        },
        "agg_level_2": {
            "0": {
                KEY_SECTORS: SECTORS_2,
                KEY_FD: FD_2,
            }
        },
        "agg_level_3": {
            "0": {
                KEY_SECTORS: SECTORS_3,
                KEY_FD: FD_3,
            }
        },
        "agg_level_4": {
            "0": {
                KEY_SECTORS: SECTORS_4,
                KEY_FD: FD_4,
            }
        },
    }

    # Reference data
    input_shocks: dict[str, list[AccountsShock]] = {}
    multi_bridge_sectors: bridge.MultiBridge
    multi_bridge_fd: bridge.MultiBridge
    id_: union_id.PipelineUnionIdentity

    @classmethod
    def setup_class(cls):
        cls.generate_input_shocks()
        cls.generate_multi_bridges()
        cls.generate_id()

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.TMP_INPUT_DIR, ignore_errors=True)
        shutil.rmtree(cls.TMP_OUTPUT_DIR, ignore_errors=True)

    @staticmethod
    def build_concordance_matrix(
        sectors_reduced: list,
        sectors_full: list,
        row_level_name: str,
        col_level_name: str,
    ) -> pd.DataFrame:
        index = pd.Index(sectors_reduced, name=row_level_name)
        columns = pd.Index(sectors_full, name=col_level_name)

        data = [
            [1 if s == f else 0 for f in sectors_full] for s in sectors_reduced
        ]

        return pd.DataFrame(data, index=index, columns=columns)

    @classmethod
    def build_full_concordance_matrix(
        cls,
        dl_dict: dict,
        dl_values: list,
        row_level_name: str,
        col_level_name: str,
    ) -> pd.DataFrame:
        frames = []

        for level, sectors in dl_dict.items():
            df = cls.build_concordance_matrix(
                sectors,
                dl_values,
                row_level_name=row_level_name,
                col_level_name=col_level_name,
            )
            df.index = pd.MultiIndex.from_arrays(
                [[level] * len(sectors), df.index],
                names=[cls.FILTER_LEVEL, row_level_name],
            )
            frames.append(df)

        result = pd.concat(frames)

        result.columns = pd.MultiIndex.from_arrays(
            [dl_values],
            names=[col_level_name],
        )

        return result

    @classmethod
    def generate_input_shocks(cls):

        def generate_shock(
            regions: dl.RegionsDL,
            sectors: dl.SectorsDL,
            final_demand_categories: dl.FinalDemandCategoriesDL,
            extension_categories: dl.ExtensionCategoriesDL,
            path_out: str,
        ) -> AccountsShock:
            s_dir = s_builder.get_director(reset=True)
            ss_dir = ss_builder.get_director(reset=True)
            se_dir = se_builder.get_director(reset=True)

            for director in ss_dir, se_dir:
                director.set_regions(regions)
                director.set_sectors(sectors)
                director.set_final_demand_categories(final_demand_categories)

            system_shock = ss_dir.make_shock_exo()

            se_dir.set_extension_categories(extension_categories)
            ext_shock_1 = se_dir.make_shock_s_x(name="ext_1")
            ext_shock_2 = se_dir.make_shock_m_row(name="ext_2")
            ext_shock_3 = se_dir.make_shock_s_y(name="ext_3")

            for entity in system_shock, ext_shock_1, ext_shock_2, ext_shock_3:
                builders.randomize_dataset(
                    entity.dataset,
                    with_zeros=True,
                    proportion_to_randomize=0.3,
                )

            shock = s_dir.make_from_system_and_extensions_shocks(
                system_shock=system_shock,
                extensions_shocks={
                    "ext_1": ext_shock_1,
                    "ext_2": ext_shock_2,
                    "ext_3": ext_shock_3,
                },
            )
            shock.save_to_path(path=path_out, export_format=[cst.FORMAT_EXCEL])
            return shock

        for agg_level, agg_level_element in cls.MAP_AGG_LEVELS.items():

            cls.input_shocks[agg_level] = []

            # Iterate twice
            for number, current_dls in agg_level_element.items():

                current_shock = generate_shock(
                    regions=tests_cst.DEFAULT_MULTI_REGIONS,
                    sectors=dl.SectorsDL(
                        builders.generate_sectors(
                            categories=[],
                            sub_categories=[],
                            sectors=current_dls[cls.KEY_SECTORS],
                        )
                    ),
                    final_demand_categories=dl.FinalDemandCategoriesDL(
                        builders.generate_final_demand_categories(
                            categories=current_dls[cls.KEY_FD],
                            sub_categories=[],
                        )
                    ),
                    extension_categories=tests_cst.DEFAULT_EXTENSION_CATEGORIES_WITH_1_LEVEL,
                    path_out=os.path.join(
                        cls.TMP_INPUT_DIR, f"{agg_level}_{number}"
                    ),
                )
                # Save accounts shock
                cls.input_shocks[agg_level].append(current_shock)

    @classmethod
    def generate_multi_bridges(cls):

        # SECTORS
        multi_bridge_sectors = bridge.MultiBridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=cls.build_full_concordance_matrix(
                dl_dict={
                    k: v["0"][cls.KEY_SECTORS]
                    for k, v in cls.MAP_AGG_LEVELS.items()
                },
                dl_values=cls.SECTORS_FULL,
                row_level_name=cst.IDX_SECTOR,
                col_level_name=cst.IDX_SECTOR,
            ),
        )
        multi_bridge_sectors.save_to_path(
            path=cls.TMP_INPUT_DIR,
            file_name=cls.MULTI_BRIDGE_FILE,
        )
        cls.multi_bridge_sectors = multi_bridge_sectors

        # FINAL DEMAND
        multi_bridge_fd = bridge.MultiBridge.init_from_df(
            kind=dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES,
            df=cls.build_full_concordance_matrix(
                dl_dict={
                    k: v["0"][cls.KEY_FD]
                    for k, v in cls.MAP_AGG_LEVELS.items()
                },
                dl_values=cls.FD_FULL,
                row_level_name=cst.IDX_Y_CATEGORY,
                col_level_name=cst.IDX_Y_CATEGORY,
            ),
        )
        multi_bridge_fd.save_to_path(
            path=cls.TMP_INPUT_DIR,
            file_name=cls.MULTI_BRIDGE_FILE,
        )

        cls.multi_bridge_fd = multi_bridge_fd

    @classmethod
    def generate_id(cls):
        cls._id = union_id.PipelineUnionIdentity(
            path_in={
                "shocks": {
                    k: [
                        os.path.abspath(
                            os.path.join(cls.TMP_INPUT_DIR, f"{k}_{number}")
                        )
                        for number in v.keys()
                    ]
                    for k, v in cls.MAP_AGG_LEVELS.items()
                },
                "multi_bridge": os.path.join(
                    os.path.abspath(
                        os.path.join(cls.TMP_INPUT_DIR, cls.MULTI_BRIDGE_FILE)
                    )
                ),
            },
            path_out=os.path.abspath(cls.TMP_OUTPUT_DIR),
            export_format=cst.FORMAT_EXCEL,
            base_year=2000,
            multi_bridge_filter_level=cls.FILTER_LEVEL,
        )

    def test_load(self):
        """
        Test function `load`

        Expected results:
            - The input data are properly loaded
        """

        # Instantiate pipeline and call function under test
        pipeline = union.PipelineUnion(self._id)
        pipeline.load()

        # Check that the loading works
        for agg_level, shocks_list in self.input_shocks.items():
            assert len(shocks_list) == len(
                pipeline.get_input_data([pipeline.KEY_SHOCKS, agg_level])
            )
            for index, shock in enumerate(shocks_list):
                assert shock.equals(
                    pipeline.get_input_data([pipeline.KEY_SHOCKS, agg_level])[
                        index
                    ]
                )

        assert self.multi_bridge_sectors.equals(
            pipeline.get_input_data(
                [pipeline.KEY_BRIDGES, dl.DetailLevelKind.SECTORS.value]
            )
        )

    def test_process(self, mocker):
        """
        Test function `process`

        Expected results:
            - The sub-functions are called once
        """

        spy_ds = mocker.spy(union.PipelineUnion, "_disaggregate_shocks")
        spy_bcs = mocker.spy(union.PipelineUnion, "_build_concatenated_shock")

        # Instantiate pipeline and call function under test
        pipeline = union.PipelineUnion(self._id)
        pipeline.load()
        pipeline.process()

        spy_ds.assert_called_once()
        spy_bcs.assert_called_once()

    def test_disaggregate_shocks(self, mocker):
        """
        Test function `disaggregate_shocks`

        Expected results:
            - Check that the method 'disaggregate' of each shock is called
              with the proper arguments
        """
        # Instantiate pipeline
        pipeline = union.PipelineUnion(self._id)
        pipeline.load()

        # Setup spies
        spy_system_shock = mocker.spy(SystemShock, "disaggregate")
        spy_extension_shock = mocker.spy(ExtensionShock, "disaggregate")

        # Call function under test
        pipeline._disaggregate_shocks()

        # Init base index for checks on spies
        base_system_index = 0
        base_extension_index = 0
        for agg_level in self.MAP_AGG_LEVELS.keys():

            # Build list of bridges which are applicable to the current
            # agg_level
            applicable_bridges = [
                mb.get_bridge(agg_level)
                for mb in pipeline.get_input_data(
                    [pipeline.KEY_BRIDGES]
                ).values()
            ]

            for disagg_shock in pipeline.get_processed_data(
                [pipeline.KEY_SHOCKS, agg_level]
            ):

                # Check system shock
                spy.check_specific_call_with_args(
                    function_spy=spy_system_shock,
                    call_number=base_system_index + 1,
                    args=[
                        disagg_shock.system_shock,
                        *applicable_bridges,
                    ],
                    kwargs={},
                )
                base_system_index += 1

                # Check extensions shocks
                nb_of_extensions = 0
                for ext_number, ext_shock in enumerate(
                    disagg_shock.list_extensions_shocks()
                ):

                    # Check extension shock
                    spy.check_specific_call_with_args(
                        function_spy=spy_extension_shock,
                        call_number=base_extension_index + 1 + ext_number,
                        args=[
                            ext_shock,
                            *applicable_bridges,
                        ],
                        kwargs={"match_extension_name": True},
                    )

                    nb_of_extensions += 1

                base_extension_index += nb_of_extensions

    def test_build_concatenated_shock(self, mocker):
        """
        Test function `_build_concatenated_shock`

        Expected results:
            - The shocks are injected in the proper order to build the
              unified shock
        """
        # Instantiate pipeline
        pipeline = union.PipelineUnion(self._id)
        pipeline.load()
        pipeline._disaggregate_shocks()

        # Setup spies
        spy_system_shock_dataset = mocker.spy(SystemShockDataSet, "inject")
        spy_extension_shock_dataset = mocker.spy(
            ExtensionShockDataSet, "inject"
        )

        # Call function under test
        pipeline._build_concatenated_shock()
        concatenated_shock = pipeline.get_processed_data(pipeline.KEY_OUTPUT)

        # Init base index for checks on spies
        base_system_index = 0
        base_extension_index = 0
        for agg_level in self.MAP_AGG_LEVELS.keys():

            shocks_list = pipeline.get_processed_data(
                [pipeline.KEY_SHOCKS, agg_level]
            )

            for shock_to_inject in shocks_list:

                # Check system shock
                spy.check_specific_call_with_args(
                    function_spy=spy_system_shock_dataset,
                    call_number=base_system_index + 1,
                    args=[concatenated_shock.system_shock.dataset],
                    kwargs={
                        "dataset_": shock_to_inject.system_shock.dataset,
                        "inject_zeros": True,
                    },
                )
                base_system_index += 1

                # Check extensions shocks
                nb_of_extensions = 0
                for ext_number, ext_shock in enumerate(
                    shock_to_inject.list_extensions_shocks()
                ):

                    # Check extension shock
                    spy.check_specific_call_with_args(
                        function_spy=spy_extension_shock_dataset,
                        call_number=base_extension_index + 1 + ext_number,
                        args=[
                            concatenated_shock.get_extension_shock(
                                ext_shock.name
                            ).dataset,
                        ],
                        kwargs={
                            "dataset_": ext_shock.dataset,
                            "inject_zeros": True,
                        },
                    )

                    nb_of_extensions += 1

                base_extension_index += nb_of_extensions

    def test_save(self):
        """
        Check function `save`

        Expected results:
            The unified shock is properly saved
        """
        pipeline = union.PipelineUnion(self._id)
        pipeline.load()
        pipeline.process()

        ref_shock = pipeline.get_processed_data(pipeline.KEY_OUTPUT)

        # Call function under test
        pipeline.save()

        # Update config to load shock without replacing NaN by 0.0
        config.CLEAN_RESIDUAL_NAN_AND_INF = False

        s_director = s_builder.get_director(reset=True)
        test_shock = s_director.make_from_path(
            path=pipeline.path_out,
            load_data=True,
        )

        # Reset config
        config.CLEAN_RESIDUAL_NAN_AND_INF = True

        assert test_shock.system_shock.equals(ref_shock.system_shock)
