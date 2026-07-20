import pytest

import pandas as pd

from matmat.core.bridge import core as bridge
from matmat.core.detail_level import core as dl
from matmat.core.data.strategies import nature, structure
from matmat.utils import errors

from tests.utils import constants as tests_cst, builders


class TestNatureFlux:
    """
    Test class for the following classes:
        - AbstractDataNature
        - Flux

    Notes
    -----

    About the tests on aggregation / disaggregation methods:

    The idea of these tests is to check that the method 'aggregate' of the
    nature class under test calls the method 'aggregate' of the structure
    class given as parameter, and returns the df returned by the structure
    class 'aggregate' method.

    To avoid problems of dimensions and consistent matrices (which is not
    the point in this test as we do not test the aggregation method itself)
    we mock the 'aggregate' method of the structure class. This also
    makes this test independent of the implementation in the structure
    class, which eases the maintenance.

    Same applies for the method 'disaggregate'
    """

    def test_aggregate_sectors(self, mocker):
        """
        Test function 'aggregate' with sectors bridge
        """
        df_mocked = pd.DataFrame()
        df_input = pd.DataFrame()
        bridge_ = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=pd.DataFrame(),
        )

        # Patch "apply_bridge_to_df" function of structure class
        mock_function = mocker.patch.object(
            structure.StructureZ, "apply_bridge_to_df", return_value=df_mocked
        )

        nature_ = nature.Flux()
        structure_ = structure.StructureZ(
            sectors=builders.get_test_sectors(),
            regions=tests_cst.DEFAULT_REGIONS,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

        df_output = nature_.aggregate(
            df=df_input,
            structure=structure_,
            bridge_=bridge_,
        )

        assert mock_function.call_count == 1
        assert mock_function.call_args.kwargs["df"] is df_input
        assert mock_function.call_args.kwargs["bridge_"] is bridge_
        assert df_output is df_mocked

    def test_disaggregate_sectors(self, mocker):
        """
        Test function 'disaggregate' with sectors bridge

        Expected results:
            Disaggregation operation is not allowed for a flux.
            An exception MEAggregationOperationNotPossible shall be raised
        """
        df_mocked = pd.DataFrame()
        df_input = pd.DataFrame()
        bridge_ = bridge.Bridge.init_from_df(
            kind=dl.DetailLevelKind.SECTORS,
            df=pd.DataFrame(),
        )

        # Patch "apply_bridge_to_df" function of StructureUnit class
        mock_function = mocker.patch.object(
            structure.StructureX,
            "apply_bridge_to_df",
            return_value=df_mocked,
        )

        nature_ = nature.Flux()
        structure_ = structure.StructureX(
            sectors=builders.get_test_sectors(),
            regions=tests_cst.DEFAULT_REGIONS,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

        with pytest.raises(errors.MEAggregationOperationNotPossible):
            nature_.disaggregate(
                df=df_input, structure=structure_, bridge_=bridge_
            )
