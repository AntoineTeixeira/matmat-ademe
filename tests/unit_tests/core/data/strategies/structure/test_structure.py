import pytest

import pandas as pd
import numpy as np
from scipy.sparse import csr_array

from matmat.core.base.matrix import SparseMatrix
from matmat.core.data.strategies import structure
from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.utils import constants as cst

from tests.utils import builders


class TestStructure:
    """
    Unit tests for generic structure methods
    """

    class TestGetApplicableDls:

        @pytest.fixture
        def instance(
            self,
            dl_regions_1,
            dl_sectors_1,
            dl_final_demand_categories_1,
            dl_extension_categories_1,
        ):
            return structure.StructureZ(
                regions=dl_regions_1,
                sectors=dl_sectors_1,
                final_demand_categories=dl_final_demand_categories_1,
                extension_categories=dl_extension_categories_1,
            )

        def test_sectors_only(self, mocker, instance, dl_sectors_1):
            """
            Test function `_get_applicable_dls`

            Mock _sectors.get_filtered_dl, pass a single SECTORS spec without filters,
            verify the returned list contains the expected DL.
            """
            instance._sectors = mocker.Mock()
            instance._sectors.is_empty.return_value = False
            instance._sectors.get_filtered_dl.return_value = dl_sectors_1
            dls_specs = {dl.DetailLevelKind.SECTORS: []}

            result = instance._get_applicable_dls(dls_specs)

            instance._sectors.get_filtered_dl.assert_called_once_with()
            assert result == [dl_sectors_1]

        def test_regions_only(self, mocker, instance, dl_regions_1):
            """
            Test function `_get_applicable_dls`

            Mock _regions.get_filtered_dl, pass a single REGIONS spec without filters,
            verify the returned list contains the expected DL.
            """
            instance._regions = mocker.Mock()
            instance._regions.is_empty.return_value = False
            instance._regions.get_filtered_dl.return_value = dl_regions_1
            dls_specs = {dl.DetailLevelKind.REGIONS: []}

            result = instance._get_applicable_dls(dls_specs)

            instance._regions.get_filtered_dl.assert_called_once_with()
            assert result == [dl_regions_1]

        def test_final_demand_categories_only(
            self, mocker, instance, dl_final_demand_categories_1
        ):
            """
            Test function `_get_applicable_dls`

            Mock _final_demand_categories.get_filtered_dl, pass a single FINAL_DEMAND_CATEGORIES
            spec without filters, verify the returned list contains the expected DL.
            """
            instance._final_demand_categories = mocker.Mock()
            instance._final_demand_categories.is_empty.return_value = False
            instance._final_demand_categories.get_filtered_dl.return_value = (
                dl_final_demand_categories_1
            )
            dls_specs = {dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: []}

            result = instance._get_applicable_dls(dls_specs)

            instance._final_demand_categories.get_filtered_dl.assert_called_once_with()
            assert result == [dl_final_demand_categories_1]

        def test_extension_categories_only(
            self, mocker, instance, dl_extension_categories_1
        ):
            """
            Test function `_get_applicable_dls`

            Mock _extension_categories.get_filtered_dl, pass a single EXTENSION_CATEGORIES
            spec without filters, verify the returned list contains the expected DL.
            """
            instance._extension_categories = mocker.Mock()
            instance._extension_categories.is_empty.return_value = False
            instance._extension_categories.get_filtered_dl.return_value = (
                dl_extension_categories_1
            )
            dls_specs = {dl.DetailLevelKind.EXTENSION_CATEGORIES: []}

            result = instance._get_applicable_dls(dls_specs)

            instance._extension_categories.get_filtered_dl.assert_called_once_with()
            assert result == [dl_extension_categories_1]

        def test_with_filters(self, mocker, instance, dl_sectors_1):
            """
            Test function `_get_applicable_dls`

            Pass filters alongside a SECTORS spec, verify get_filtered_dl is called
            with the filters unpacked.
            """
            mock_filter_1, mock_filter_2 = mocker.Mock(), mocker.Mock()
            instance._sectors = mocker.Mock()
            instance._sectors.is_empty.return_value = False
            instance._sectors.get_filtered_dl.return_value = dl_sectors_1
            dls_specs = {
                dl.DetailLevelKind.SECTORS: [mock_filter_1, mock_filter_2]
            }

            instance._get_applicable_dls(dls_specs)

            instance._sectors.get_filtered_dl.assert_called_once_with(
                mock_filter_1, mock_filter_2
            )

        def test_unknown_kind_ignored(self, mocker, instance):
            """
            Test function `_get_applicable_dls`

            Pass an unknown DetailLevelKind, verify the returned list is empty
            and no attribute is accessed.
            """
            dls_specs = {mocker.Mock(): []}

            result = instance._get_applicable_dls(dls_specs)

            assert result == []

        def test_multiple_kinds_ordered(
            self,
            mocker,
            instance,
            dl_regions_1,
            dl_sectors_1,
            dl_extension_categories_1,
        ):
            """
            Test function `_get_applicable_dls`

            Pass multiple kinds, verify the returned list respects the insertion
            order of dls_specs.
            """
            instance._regions = mocker.Mock()
            instance._regions.is_empty.return_value = False
            instance._regions.get_filtered_dl.return_value = dl_regions_1
            instance._sectors = mocker.Mock()
            instance._sectors.is_empty.return_value = False
            instance._sectors.get_filtered_dl.return_value = dl_sectors_1
            instance._extension_categories = mocker.Mock()
            instance._extension_categories.is_empty.return_value = False
            instance._extension_categories.get_filtered_dl.return_value = (
                dl_extension_categories_1
            )

            dls_specs = {
                dl.DetailLevelKind.REGIONS: [],
                dl.DetailLevelKind.SECTORS: [],
                dl.DetailLevelKind.EXTENSION_CATEGORIES: [],
            }

            result = instance._get_applicable_dls(dls_specs)

            assert result == [
                dl_regions_1,
                dl_sectors_1,
                dl_extension_categories_1,
            ]

        def test_empty_specs(self, instance):
            """
            Test function `_get_applicable_dls`

            Pass an empty dls_specs, verify the returned list is empty.
            """
            result = instance._get_applicable_dls({})
            assert result == []

    class TestGetAdjacentDlLists:

        @pytest.fixture
        def instance(
            self,
            dl_regions_1,
            dl_sectors_1,
            dl_final_demand_categories_1,
            dl_extension_categories_1,
        ):
            return structure.StructureZ(
                regions=dl_regions_1,
                sectors=dl_sectors_1,
                final_demand_categories=dl_final_demand_categories_1,
                extension_categories=dl_extension_categories_1,
            )

        def test_reference_in_middle(
            self,
            mocker,
            instance,
            dl_regions_1,
            dl_sectors_1,
            dl_final_demand_categories_1,
            dl_extension_categories_1,
        ):
            """
            Test function `_get_adjacent_dl_lists`

            Test the retrieval of adjacent detail level lists when reference is in middle
            position of the list.
            """
            mocker.patch.object(
                instance,
                "_get_applicable_dls",
                return_value=[
                    dl_regions_1,
                    dl_sectors_1,
                    dl_final_demand_categories_1,
                    dl_extension_categories_1,
                ],
            )
            left, right = instance._get_adjacent_dl_lists(
                dl.DetailLevelKind.SECTORS, {}
            )
            assert left == [dl_regions_1]
            assert right == [
                dl_final_demand_categories_1,
                dl_extension_categories_1,
            ]

        def test_reference_first(
            self,
            mocker,
            instance,
            dl_sectors_1,
            dl_regions_1,
            dl_final_demand_categories_1,
            dl_extension_categories_1,
        ):
            """
            Test function `_get_adjacent_dl_lists`

            Test the retrieval of adjacent detail level lists when reference is first
            element of the list.
            """
            mocker.patch.object(
                instance,
                "_get_applicable_dls",
                return_value=[
                    dl_sectors_1,
                    dl_regions_1,
                    dl_final_demand_categories_1,
                    dl_extension_categories_1,
                ],
            )
            left, right = instance._get_adjacent_dl_lists(
                dl.DetailLevelKind.SECTORS, {}
            )
            assert left == []
            assert right == [
                dl_regions_1,
                dl_final_demand_categories_1,
                dl_extension_categories_1,
            ]

        def test_reference_last(
            self,
            mocker,
            instance,
            dl_regions_1,
            dl_final_demand_categories_1,
            dl_extension_categories_1,
            dl_sectors_1,
        ):
            """
            Test function `_get_adjacent_dl_lists`

            Test the retrieval of adjacent detail level lists when reference is last
            element of the list.
            """
            mocker.patch.object(
                instance,
                "_get_applicable_dls",
                return_value=[
                    dl_sectors_1,
                    dl_regions_1,
                    dl_final_demand_categories_1,
                    dl_extension_categories_1,
                ],
            )
            left, right = instance._get_adjacent_dl_lists(
                dl.DetailLevelKind.EXTENSION_CATEGORIES, {}
            )
            assert left == [
                dl_sectors_1,
                dl_regions_1,
                dl_final_demand_categories_1,
            ]
            assert right == []

        def test_reference_alone(
            self, mocker, instance, dl_final_demand_categories_1
        ):
            """
            Test function `_get_adjacent_dl_lists`

            Test the retrieval of adjacent detail level lists when reference is the only
            element in the list.
            """
            mocker.patch.object(
                instance,
                "_get_applicable_dls",
                return_value=[dl_final_demand_categories_1],
            )
            left, right = instance._get_adjacent_dl_lists(
                dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES, {}
            )
            assert left == []
            assert right == []

        def test_reference_absent(
            self,
            mocker,
            instance,
            dl_regions_1,
            dl_final_demand_categories_1,
            dl_extension_categories_1,
        ):
            """
            Test function `_get_adjacent_dl_lists`

            Test the retrieval of adjacent detail level lists when reference is absent
            from the list.
            """
            mocker.patch.object(
                instance,
                "_get_applicable_dls",
                return_value=[
                    dl_regions_1,
                    dl_final_demand_categories_1,
                    dl_extension_categories_1,
                ],
            )
            left, right = instance._get_adjacent_dl_lists(
                dl.DetailLevelKind.SECTORS, {}
            )
            assert left == [
                dl_regions_1,
                dl_final_demand_categories_1,
                dl_extension_categories_1,
            ]
            assert right == []

    class TestComputeCombinedBridge:

        @pytest.fixture
        def instance(
            self,
            dl_regions_1,
            dl_sectors_1,
            dl_final_demand_categories_1,
        ):
            return structure.StructureZ(
                regions=dl_regions_1,
                sectors=dl_sectors_1,
                final_demand_categories=dl_final_demand_categories_1,
            )

        def test_kind_absent_returns_none(
            self, instance, bridge_ext_cats_from_1_to_3
        ):
            result = instance._compute_combined_bridge(
                bridge_ext_cats_from_1_to_3, {}
            )
            assert result is None

        def test_no_filters(
            self,
            mocker,
            instance,
            bridge_sectors_from_1_to_3,
            dl_regions_1,
            dl_final_demand_categories_1,
        ):
            dls_specs = {
                dl.DetailLevelKind.REGIONS: [],
                dl.DetailLevelKind.SECTORS: [],
                dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [],
            }

            spy_get_filtered_bridge = mocker.spy(
                bridge.Bridge, "get_filtered_bridge"
            )
            mocker.patch.object(
                instance,
                "_get_adjacent_dl_lists",
                return_value=([dl_regions_1], [dl_final_demand_categories_1]),
            )
            mock_init = mocker.patch(
                "matmat.core.bridge.core.CombinedBridge.init_from_bridge",
                return_value=mocker.Mock(),
            )

            # Call function under test
            result = instance._compute_combined_bridge(
                bridge_sectors_from_1_to_3, dls_specs
            )

            spy_get_filtered_bridge.assert_not_called()
            mock_init.assert_called_once_with(
                bridge_=bridge_sectors_from_1_to_3,
                left_dls=[dl_regions_1],
                right_dls=[dl_final_demand_categories_1],
            )
            assert result == mock_init.return_value

        def test_with_filters(
            self,
            mocker,
            instance,
            bridge_sectors_from_1_to_3,
            dl_regions_1,
            dl_final_demand_categories_1,
        ):
            mock_filter_1 = mocker.Mock()
            mock_filter_2 = mocker.Mock()
            mock_get_filtered_bridge = mocker.patch(
                "matmat.core.bridge.core.Bridge.get_filtered_bridge",
                return_value=mocker.Mock(),
            )
            dls_specs = {
                dl.DetailLevelKind.REGIONS: [],
                dl.DetailLevelKind.SECTORS: [mock_filter_1],
                dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES: [
                    mock_filter_1,
                    mock_filter_2,
                ],
            }

            mock_get_adjacent_dl_lists = mocker.patch.object(
                instance,
                "_get_adjacent_dl_lists",
                return_value=([dl_regions_1], [dl_final_demand_categories_1]),
            )
            mock_init = mocker.patch(
                "matmat.core.bridge.core.CombinedBridge.init_from_bridge",
                return_value=mocker.Mock(),
            )

            result = instance._compute_combined_bridge(
                bridge_sectors_from_1_to_3, dls_specs
            )

            bridge_sectors_from_1_to_3.get_filtered_bridge.assert_called_once_with(
                mock_filter_1
            )
            mock_init.assert_called_once_with(
                bridge_=mock_get_filtered_bridge.return_value,
                left_dls=mock_get_adjacent_dl_lists.return_value[0],
                right_dls=mock_get_adjacent_dl_lists.return_value[1],
            )
            assert result == mock_init.return_value

    class TestComputeMatricialProduct:

        def test_left_and_right_product(self, bridge_sectors_from_1_to_3):
            """
            Test function `_compute_matricial_product`

            Test the matricial product computation with left and right matrices.
            Uses randomized factor matrix for validation.
            """

            # Define inputs
            df = pd.DataFrame(
                index=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                columns=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                dtype=cst.DTYPE_FLOAT,
            )
            builders.randomize(df=df)

            # Call function under test
            test_product = (
                structure.AbstractDataStructure._compute_matricial_product(
                    left_matrix=bridge_sectors_from_1_to_3.df.T,
                    right_matrix=bridge_sectors_from_1_to_3.df,
                    factor=df,
                )
            )

            # Check results
            assert test_product.equals(
                bridge_sectors_from_1_to_3.df.T
                @ df
                @ bridge_sectors_from_1_to_3.df
            )

        def test_left_product(self, bridge_sectors_from_1_to_3):
            """
            Test function `_compute_matricial_product`

            Test the matricial product computation with left matrix.
            Uses randomized factor matrix for validation.
            """

            # Define inputs
            df = pd.DataFrame(
                index=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                columns=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                dtype=cst.DTYPE_FLOAT,
            )
            builders.randomize(df=df)

            # Call function under test
            test_product = (
                structure.AbstractDataStructure._compute_matricial_product(
                    left_matrix=bridge_sectors_from_1_to_3.df.T,
                    right_matrix=None,
                    factor=df,
                )
            )

            # Check results
            assert test_product.equals(bridge_sectors_from_1_to_3.df.T @ df)

        def test_right_product(self, bridge_sectors_from_1_to_3):
            """
            Test function `_compute_matricial_product`

            Test the matricial product computation with right matrix.
            Uses randomized factor matrix for validation.
            """

            # Define inputs
            df = pd.DataFrame(
                index=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                columns=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                dtype=cst.DTYPE_FLOAT,
            )
            builders.randomize(df=df)

            # Call function under test
            test_product = (
                structure.AbstractDataStructure._compute_matricial_product(
                    left_matrix=None,
                    right_matrix=bridge_sectors_from_1_to_3.df,
                    factor=df,
                )
            )

            # Check results
            assert test_product.equals(df @ bridge_sectors_from_1_to_3.df)

        def test_no_product(self, bridge_sectors_from_1_to_3):
            """
            Test function `_compute_matricial_product`

            Test the matricial product computation with no matrix.
            Uses randomized factor matrix for validation.
            """

            # Define inputs
            df = pd.DataFrame(
                index=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                columns=bridge_sectors_from_1_to_3.rows_dl.get_dl_as_multi_index(),
                dtype=cst.DTYPE_FLOAT,
            )
            builders.randomize(df=df)

            # Call function under test
            test_product = (
                structure.AbstractDataStructure._compute_matricial_product(
                    left_matrix=None,
                    right_matrix=None,
                    factor=df,
                )
            )

            # Check results
            assert test_product.equals(df)

    class TestComputeNanMask:

        @pytest.fixture
        def instance(
            self,
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
        ):
            return structure.StructureZ(
                regions=dl_regions_3,
                sectors=dl_sectors_3,
                final_demand_categories=dl_final_demand_categories_3,
            )

        @pytest.fixture
        def df_raw(self):
            return pd.DataFrame(
                data=[
                    [1.0, 2.0, 3.0, 4.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                ],
                index=[0, 1, 2],
                columns=["A", "B", "C", "D"],
            )

        @pytest.fixture
        def left_matrix(self):
            return SparseMatrix.init_from_df(pd.DataFrame(
                data=[[1, 1, 0], [0, 0, 1]],
                index=["G1", "G2"],
                columns=[0, 1, 2],
            ))

        @pytest.fixture
        def right_matrix(self):
            return SparseMatrix.init_from_df(pd.DataFrame(
                data=[[1, 0], [1, 0], [0, 1], [0, 1]],
                index=["A", "B", "C", "D"],
                columns=["X", "Y"],
            ))

        def test_compute_nan_mask_no_nan(
            self, instance, df_raw, left_matrix, right_matrix
        ):
            """
            Test function `_compute_nan_mask`

            When df_raw contains no NaN, the resulting mask should be entirely False.
            """
            result = instance._compute_nan_mask(
                df_raw, left_matrix.array, right_matrix.array
            )
            assert result.shape == (2, 2)
            assert not result.any().any()

        def test_compute_nan_mask_all_nan(
            self, instance, df_raw, left_matrix, right_matrix
        ):
            """
            Test function `_compute_nan_mask`

            When df_raw is entirely NaN, the resulting mask should be entirely True.
            """
            df_all_nan = df_raw.copy()
            df_all_nan[:] = np.nan
            result = instance._compute_nan_mask(
                df_all_nan, left_matrix.array, right_matrix.array
            )
            assert result.shape == (2, 2)
            assert result.all().all()

        def test_compute_nan_mask_partial_nan_all_contributors_nan(
            self, instance, df_raw, left_matrix, right_matrix
        ):
            """
            Test function `_compute_nan_mask`

            When all contributors of an aggregated cell are NaN, that cell should be True.
            Here, (G2, X) has contributors (2,A) and (2,B), both set to NaN.
            All other aggregated cells have at least one non-NaN contributor, so they should be False.
            """
            df_partial = df_raw.copy()
            df_partial.loc[2, "A"] = np.nan
            df_partial.loc[2, "B"] = np.nan
            result = instance._compute_nan_mask(
                df_partial, left_matrix.array, right_matrix.array
            )
            expected = np.array([[False, False], [True, False]])
            np.testing.assert_array_equal(result, expected)

        def test_compute_nan_mask_partial_nan_not_all_contributors_nan(
            self, instance, df_raw, left_matrix, right_matrix
        ):
            """
            Test function `_compute_nan_mask`

            When only some contributors of an aggregated cell are NaN, that cell should be False.
            Here, (G1, X) has contributors (0,A), (0,B), (1,A), (1,B), with only (0,A) set to NaN.
            All aggregated cells should be False.
            """
            df_partial = df_raw.copy()
            df_partial.loc[0, "A"] = np.nan
            result = instance._compute_nan_mask(
                df_partial, left_matrix.array, right_matrix.array
            )
            assert not result.any().any()

    class TestApplyBridgeToDf:

        @pytest.fixture
        def instance_with_specs(
            self,
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
        ):
            return structure.StructureZ(
                regions=dl_regions_3,
                sectors=dl_sectors_3,
                final_demand_categories=dl_final_demand_categories_3,
            )

        @pytest.fixture
        def instance_no_rows_specs(
            self,
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
        ):
            instance = structure.StructureZ(
                regions=dl_regions_3,
                sectors=dl_sectors_3,
                final_demand_categories=dl_final_demand_categories_3,
            )
            instance.rows_specs = None
            return instance

        @pytest.fixture
        def instance_no_columns_specs(
            self,
            dl_regions_3,
            dl_sectors_3,
            dl_final_demand_categories_3,
        ):
            instance = structure.StructureZ(
                regions=dl_regions_3,
                sectors=dl_sectors_3,
                final_demand_categories=dl_final_demand_categories_3,
            )
            instance.columns_specs = None
            return instance

        @pytest.fixture
        def df_no_nan(self):
            return pd.DataFrame(
                [[1.0, 2.0], [3.0, 4.0]],
                index=["r1", "r2"],
                columns=["c1", "c2"],
            )

        @pytest.fixture
        def df_with_nan(self):
            return pd.DataFrame(
                [[1.0, np.nan], [3.0, 4.0]],
                index=["r1", "r2"],
                columns=["c1", "c2"],
            )

        @pytest.fixture
        def identity_matrix(self):
            df = pd.DataFrame(
                [[1.0, 0.0], [0.0, 1.0]],
                index=["r1", "r2"],
                columns=["r1", "r2"],
            )
            return SparseMatrix.init_from_df(df)

        @pytest.fixture
        def mock_bridge(self, mocker):
            return mocker.MagicMock(spec=bridge.Bridge)

        @staticmethod
        def make_identity_bridge_mock(agg_matrix, index, mocker):
            m = mocker.MagicMock()
            m.get_agg_matrix.return_value = agg_matrix
            m.rows_dl.get_dl_as_multi_index.return_value = index
            m.columns_dl.get_dl_as_multi_index.return_value = index
            return m

        def test_nominal_left_and_right_bridge(
            self,
            instance_with_specs,
            df_no_nan,
            identity_matrix,
            mock_bridge,
            mocker,
        ):
            """
            Test function `apply_bridge_to_df`

            Both left and right bridges are active (rows_specs and columns_specs defined).
            Verifies the result equals the matricial product L @ df @ R,
            and that _compute_nan_mask is not called when df has no NaN.
            """
            mock_combined_bridge_1 = self.make_identity_bridge_mock(
                identity_matrix, df_no_nan.index, mocker
            )
            mock_combined_bridge_2 = self.make_identity_bridge_mock(
                identity_matrix, df_no_nan.columns, mocker
            )

            mocker.patch.object(
                instance_with_specs,
                "_compute_combined_bridge",
                side_effect=[mock_combined_bridge_1, mock_combined_bridge_2],
            )
            mocker.patch.object(
                instance_with_specs,
                "_compute_matricial_product",
                return_value=csr_array(df_no_nan.values),
            )

            mock_nan_mask = mocker.patch.object(
                instance_with_specs, "_compute_nan_mask"
            )

            result = instance_with_specs.apply_bridge_to_df(
                df=df_no_nan, bridge_=mock_bridge
            )

            instance_with_specs._compute_matricial_product.assert_called_once()
            mock_nan_mask.assert_not_called()
            pd.testing.assert_frame_equal(result, df_no_nan)

        def test_no_left_bridge(
            self,
            instance_no_rows_specs,
            df_no_nan,
            identity_matrix,
            mock_bridge,
            mocker,
        ):
            """
            Test function `apply_bridge_to_df`

            rows_specs is None: left bridge is skipped, only right bridge is applied.
            Verifies left_matrix is None in the matricial product call.
            """
            mock_combined_bridge = self.make_identity_bridge_mock(
                identity_matrix, df_no_nan.columns, mocker
            )

            mocker.patch.object(
                instance_no_rows_specs,
                "_compute_combined_bridge",
                return_value=mock_combined_bridge,
            )
            mocker.patch.object(
                instance_no_rows_specs,
                "_compute_matricial_product",
                return_value=csr_array(df_no_nan),
            )

            # Patch _df_rows
            instance_no_rows_specs._df_rows = identity_matrix.columns

            instance_no_rows_specs.apply_bridge_to_df(
                df=df_no_nan, bridge_=mock_bridge
            )

            call_kwargs = (
                instance_no_rows_specs._compute_matricial_product.call_args.kwargs
            )
            assert call_kwargs["left_matrix"] is None

        def test_no_right_bridge(
            self,
            instance_no_columns_specs,
            df_no_nan,
            identity_matrix,
            mock_bridge,
            mocker,
        ):
            """
            Test function `apply_bridge_to_df`

            columns_specs is None: right bridge is skipped, only left bridge is applied.
            Verifies right_matrix is None in the matricial product call.
            """
            mock_combined_bridge = self.make_identity_bridge_mock(
                identity_matrix, df_no_nan.columns, mocker
            )

            mocker.patch.object(
                instance_no_columns_specs,
                "_compute_combined_bridge",
                return_value=mock_combined_bridge,
            )
            mocker.patch.object(
                instance_no_columns_specs,
                "_compute_matricial_product",
                return_value=csr_array(df_no_nan),
            )

            # Patch _df_columns
            instance_no_columns_specs._df_columns = identity_matrix.columns

            instance_no_columns_specs.apply_bridge_to_df(
                df=df_no_nan, bridge_=mock_bridge
            )

            call_kwargs = (
                instance_no_columns_specs._compute_matricial_product.call_args.kwargs
            )
            assert call_kwargs["right_matrix"] is None

        def test_nan_mask_applied_when_df_has_nan(
            self,
            instance_with_specs,
            df_with_nan,
            identity_matrix,
            mock_bridge,
            mocker,
        ):
            """
            Test function `apply_bridge_to_df`

            When df contains NaN values, verifies that _compute_nan_mask is called
            and its result is applied to the output.
            """
            mock_combined_bridge_1 = self.make_identity_bridge_mock(
                identity_matrix, df_with_nan.index, mocker
            )
            mock_combined_bridge_2 = self.make_identity_bridge_mock(
                identity_matrix, df_with_nan.columns, mocker
            )

            mocker.patch.object(
                instance_with_specs,
                "_compute_combined_bridge",
                side_effect=[mock_combined_bridge_1, mock_combined_bridge_2],
            )

            nan_mask = np.array([[False, False], [False, True]])
            mocker.patch.object(
                instance_with_specs,
                "_compute_matricial_product",
                return_value=csr_array(df_with_nan.replace(np.nan, 0.0)),
            )
            mocker.patch.object(
                instance_with_specs, "_compute_nan_mask", return_value=nan_mask
            )

            result = instance_with_specs.apply_bridge_to_df(
                df=df_with_nan, bridge_=mock_bridge
            )

            instance_with_specs._compute_nan_mask.assert_called_once()

            # nan_mask shall be applied to expected result
            expected_result = df_with_nan.copy().replace(np.nan, 0.0)
            expected_result[nan_mask] = np.nan

            # Compare results
            pd.testing.assert_frame_equal(result, expected_result)
