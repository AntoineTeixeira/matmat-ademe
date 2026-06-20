import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.core.base.matrix import SparseMatrix


class TestCombinedBridge:

    def test_init_from_bridge(
        self,
        bridge_sectors_from_1_to_2,
        dl_regions_1,
        dl_final_demand_categories_1,
        dl_extension_categories_1,
    ):
        """
        Test function `CombinedBridge.init_from_bridge`

        Nominal case with both left_dls and right_dls non-empty.
        Verifies the result is a CombinedBridge with kind=DetailLevelKind.COMBINED
        and a coherent resulting DataFrame.
        """
        tested_bridge = bridge.CombinedBridge.init_from_bridge(
            bridge_=bridge_sectors_from_1_to_2,
            left_dls=[dl_regions_1, dl_extension_categories_1],
            right_dls=[dl_final_demand_categories_1],
        )

        assert isinstance(tested_bridge, bridge.CombinedBridge)
        assert tested_bridge.kind == bridge.DetailLevelKind.COMBINED
        assert isinstance(tested_bridge.df, pd.DataFrame)
        assert not tested_bridge.df.empty

    def test_init_from_bridge_no_right_dls(
        self,
        bridge_sectors_from_1_to_2,
        dl_regions_1,
        dl_extension_categories_1,
        mocker,
    ):
        """
        Test function `CombinedBridge.init_from_bridge`

        When right_dls is empty, project_agg_matrix must not be called
        and extend_agg_matrix must be called with left_dls reversed.
        """
        mock_project = mocker.patch.object(bridge.Bridge, "project_agg_matrix")
        mock_extend = mocker.patch.object(
            bridge.Bridge,
            "extend_agg_matrix",
            return_value=SparseMatrix(),
        )
        mocker.patch.object(
            bridge.Bridge,
            "init_from_df",
            return_value=mocker.MagicMock(
                df=pd.DataFrame(), kind=bridge.DetailLevelKind.COMBINED
            ),
        )
        mocker_init_from_matrix = mocker.patch.object(
            bridge.Bridge,
            "init_from_matrix",
            return_value=bridge.Bridge(kind=dl.DetailLevelKind.COMBINED),
        )

        left_dls = [dl_regions_1, dl_extension_categories_1]
        bridge.CombinedBridge.init_from_bridge(
            bridge_=bridge_sectors_from_1_to_2,
            left_dls=left_dls,
            right_dls=[],
        )

        mock_project.assert_not_called()
        mock_extend.assert_called_once_with(left_dls[::-1])

    def test_init_from_bridge_no_left_dls(
        self,
        bridge_sectors_from_1_to_2,
        dl_final_demand_categories_1,
        mocker,
    ):
        """
        Test function `CombinedBridge.init_from_bridge`

        When left_dls is empty, extend_agg_matrix must not be called
        and project_agg_matrix must be called with right_dls reversed.
        """
        mock_project = mocker.patch.object(
            bridge.Bridge,
            "project_agg_matrix",
            return_value=SparseMatrix(),
        )
        mock_extend = mocker.patch.object(bridge.Bridge, "extend_agg_matrix")
        mocker.patch.object(
            bridge.Bridge,
            "init_from_df",
            return_value=mocker.MagicMock(
                df=pd.DataFrame(), kind=bridge.DetailLevelKind.COMBINED
            ),
        )

        mocker_init_from_matrix = mocker.patch.object(
            bridge.Bridge,
            "init_from_matrix",
            return_value=bridge.Bridge(kind=dl.DetailLevelKind.COMBINED),
        )

        right_dls = [dl_final_demand_categories_1]
        bridge.CombinedBridge.init_from_bridge(
            bridge_=bridge_sectors_from_1_to_2,
            left_dls=[],
            right_dls=right_dls,
        )

        mock_extend.assert_not_called()
        mock_project.assert_called_once_with(right_dls[::-1])

    def test_init_from_bridge_chaining(
        self,
        bridge_sectors_from_1_to_2,
        dl_regions_1,
        dl_final_demand_categories_1,
        mocker,
    ):
        """
        Test function `CombinedBridge.init_from_bridge`

        Verifies that the bridge passed to extend_agg_matrix is the one
        produced by the project_agg_matrix step, not the initial bridge.
        """
        projected_df = pd.DataFrame({"projected": [1, 2]})
        projected_bridge = mocker.MagicMock(df=projected_df)
        projected_bridge.extend_agg_matrix = mocker.MagicMock(
            return_value=SparseMatrix()
        )

        initial_bridge = mocker.MagicMock(spec=bridge.Bridge)
        initial_bridge.project_agg_matrix = mocker.MagicMock(
            return_value=SparseMatrix()
        )
        initial_bridge.kind = bridge.DetailLevelKind.COMBINED

        mocker.patch.object(
            bridge.Bridge,
            "init_from_matrix",
            side_effect=[
                projected_bridge,
                mocker.MagicMock(matrix=SparseMatrix()),
                mocker.MagicMock(matrix=SparseMatrix()),
            ],
        )

        left_dls = [dl_regions_1]
        right_dls = [dl_final_demand_categories_1]

        bridge.CombinedBridge.init_from_bridge(
            bridge_=initial_bridge,
            left_dls=left_dls,
            right_dls=right_dls,
        )

        # project_agg_matrix called on initial bridge
        initial_bridge.project_agg_matrix.assert_called_once_with(
            right_dls[::-1]
        )
        # extend_agg_matrix called on the projected bridge, not the initial one
        projected_bridge.extend_agg_matrix.assert_called_once_with(
            left_dls[::-1]
        )
        initial_bridge.extend_agg_matrix.assert_not_called()
