import pytest

from matmat.core.dataset.core import (
    AbstractMappedDataSet,
    AbstractListedDataSet,
)
from matmat.core.dataset.config import (
    DataSetMap,
    DataSetConfig,
    DataSetConversions,
)
from matmat.core.accounts.system.dataset.core import SystemDataSet
from matmat.core.data.core import AbstractData
from matmat.utils.errors import MEUnknownConfigurationParameter
from matmat.utils import constants as cst

from tests.utils import builders, constants as tests_cst, spy


class MockedData:
    """
    Represents mocked data with basic utility methods.

    The class contains essential static methods to determine
    properties or states of data.
    """

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def is_null():
        return True

    @staticmethod
    def is_df_empty():
        return True


class TestDataSetAggregation:

    def test_aggregate(
        self,
        mocker,
        dl_regions_2,
        dl_sectors_2,
        dl_final_demand_categories_2,
        bridge_sectors_from_2_to_1,
    ):
        dataset = SystemDataSet(
            regions=dl_regions_2,
            sectors=dl_sectors_2,
            final_demand_categories=dl_final_demand_categories_2,
            config__system_calcul_strategy=cst.STRATEGY_STANDARD,
        )

        # Set up spies
        spy_aggregate = mocker.spy(AbstractData, "aggregate")


        # Call function under test
        dataset.aggregate(bridge_sectors_from_2_to_1)

        # Check calls
        call_number = 0
        for data_ in dataset.data:
            if not data_.is_null():
                call_number += 1
                if data_.is_unit():
                    spy.check_specific_call_with_args(
                        function_spy=spy_aggregate,
                        call_number=call_number,
                        args=[data_],
                        kwargs={
                            "bridge_": bridge_sectors_from_2_to_1,
                            "reset": False,
                        },
                    )
                if data_.is_flux():
                    spy.check_specific_call_with_args(
                        function_spy=spy_aggregate,
                        call_number=call_number,
                        args=[data_],
                        kwargs={
                            "bridge_": bridge_sectors_from_2_to_1,
                            "reset": False,
                        },
                    )
                if data_.is_coefficient():
                    spy.check_specific_call_with_args(
                        function_spy=spy_aggregate,
                        call_number=call_number,
                        args=[data_],
                        kwargs={
                            "bridge_": bridge_sectors_from_2_to_1,
                            "reset": True,
                        },
                    )

    def test_disaggregate(
        self,
        mocker,
        dl_regions_1,
        dl_sectors_1,
        dl_final_demand_categories_1,
        bridge_sectors_from_1_to_2,
    ):
        dataset = SystemDataSet(
            regions=dl_regions_1,
            sectors=dl_sectors_1,
            final_demand_categories=dl_final_demand_categories_1,
            config__system_calcul_strategy=cst.STRATEGY_STANDARD,
        )

        # Set up spies
        spy_disaggregate = mocker.spy(AbstractData, "disaggregate")

        # Call function under test
        dataset.disaggregate(bridge_sectors_from_1_to_2)

        # Check calls
        call_number = 0
        for data_ in dataset.data:
            if not data_.is_null():
                call_number += 1
                if data_.is_unit():
                    spy.check_specific_call_with_args(
                        function_spy=spy_disaggregate,
                        call_number=call_number,
                        args=[data_],
                        kwargs={
                            "bridge_": bridge_sectors_from_1_to_2,
                            "reset": False,
                        },
                    )
                if data_.is_flux():
                    spy.check_specific_call_with_args(
                        function_spy=spy_disaggregate,
                        call_number=call_number,
                        args=[data_],
                        kwargs={
                            "bridge_": bridge_sectors_from_1_to_2,
                            "reset": True,
                        },
                    )
                if data_.is_coefficient():
                    spy.check_specific_call_with_args(
                        function_spy=spy_disaggregate,
                        call_number=call_number,
                        args=[data_],
                        kwargs={
                            "bridge_": bridge_sectors_from_1_to_2,
                            "reset": False,
                        },
                    )

    def test_reformat(
        self,
        mocker,
        dl_regions_2,
        dl_sectors_2,
        dl_final_demand_categories_2,
        bridge_sectors_from_2_to_1,
    ):
        dataset = SystemDataSet(
            regions=dl_regions_2,
            sectors=dl_sectors_2,
            final_demand_categories=dl_final_demand_categories_2,
            config__system_calcul_strategy=cst.STRATEGY_STANDARD,
        )

        # Set up spies
        spy_reformat = mocker.spy(AbstractData, "reformat")

        # Call function under test
        dataset.reformat(bridge_sectors_from_2_to_1)

        # Check calls
        call_number = 0
        for data_ in dataset.data:
            if not data_.is_null():
                call_number += 1
                spy.check_specific_call_with_args(
                    function_spy=spy_reformat,
                    call_number=call_number,
                    args=[data_],
                    kwargs={"bridge_": bridge_sectors_from_2_to_1},
                )


class TestMappedDataSet:

    test_map_1 = DataSetMap(
        {
            "config_11": {"A", "B", "C"},
            "config_12": {"B", "C"},
            "config_13": {"A", "C"},
            "config_14": {"B"},
            "config_15": {"A", "B", "C", "D"},
        }
    )

    class Conversions(DataSetConversions):

        @staticmethod
        def conversion__config_11_to_config_12(in_dataset, out_dataset):
            pass

        @staticmethod
        def conversion__config_15_to_config_11(in_dataset, out_dataset):
            pass

    # Define a concrete class to test AbstractMappedDataSet mechanisms
    class MappedDataSet(AbstractMappedDataSet):

        def __init__(self):
            super().__init__(
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                regions=tests_cst.DEFAULT_REGIONS,
                # Dataset conversions
                conversions=TestMappedDataSet.Conversions(),
                # Dateset mapping
                map__1=TestMappedDataSet.test_map_1,
                # Dataset configuration
                config__1=list(TestMappedDataSet.test_map_1.map_.keys())[0],
            )
            self.tune()

        @staticmethod
        def get_data_names():
            return ["A", "B", "C", "D"]

        def set_data(self, name: str):
            setattr(self, name, MockedData(name))

        def set_null_data(self, name: str):
            setattr(self, name, MockedData("null"))

    # Dataset to be reused throughout the tests
    dataset: MappedDataSet = None

    def set_up_dataset(self):
        self.dataset = self.MappedDataSet()

    def test_set_config(self):
        """
        Test function 'set_config'

        Expected results:
            The configuration parameter is properly set
        """
        self.set_up_dataset()

        for k in self.test_map_1.map_.keys():
            self.dataset.set_config(
                name="1",
                value=k,
                tune_dataset=False,
            )
            assert (
                self.dataset.__getattribute__(f"{DataSetConfig.PARAM_PREFIX}1")
                == k
            )

    def test_set_config_error(self):
        """
        Test function 'set_config'

        Expected results:
            In this test, the configuration parameter does not exist (wrong
            name) and an MEUnknownConfigurationParameter shall be raised
        """
        self.set_up_dataset()

        with pytest.raises(MEUnknownConfigurationParameter):
            self.dataset.set_config(
                name="wrong_name",
                value="config_11",
                tune_dataset=False,
            )

    def test_get_config(self):
        """
        Test function 'get_config'

        Expected results:
            Check that the config parameter is properly returned
        """
        self.set_up_dataset()

        for k in self.test_map_1.map_.keys():
            self.dataset.set_config(
                name="1",
                value=k,
                tune_dataset=False,
            )
            assert self.dataset.get_config(name="1") == k

    def test_properties(self):
        """
        Test the properties:
            - regions
            - sectors
            - final_demand_categories
            - domestic_regions
            - import_regions
        """
        self.set_up_dataset()
        assert self.dataset.regions.equals(tests_cst.DEFAULT_REGIONS)
        assert self.dataset.sectors.equals(builders.get_test_sectors())
        assert self.dataset.final_demand_categories.equals(
            tests_cst.DEFAULT_Y_CATEGORIES
        )
        assert (
            self.dataset.domestic_regions
            == tests_cst.DEFAULT_REGIONS.get_domestic_regions_list()
        )
        assert (
            self.dataset.import_regions
            == tests_cst.DEFAULT_REGIONS.get_import_regions_list()
        )

    def test_get_applicable_set(self):
        """
        Test function `get_applicable_set`

        Expected results:
            The applicable data match map value w.r.t. current configuration
            parameter value
        """
        self.set_up_dataset()

        for k, v in self.test_map_1.map_.items():

            self.dataset.set_config(
                name="1",
                value=k,
                tune_dataset=False,
            )
            assert self.dataset.get_applicable_set() == v

    def test_tune(self, mocker):
        """
        Test function 'tune'

        Expected results:
            - The 'set_data' method shall be called as many times as there are
              not null data in the applicable set
            - The 'set_null_data' shall be called as many times as there are
              null data in the applicable set
            - Also checks that the attributes are set properly w.r.t.
              implementation of 'set_data' and 'set_null_data' in
              MappedDataSet
        """
        self.set_up_dataset()

        # Set up spies
        spy_set_data = mocker.spy(self.MappedDataSet, "set_data")
        spy_set_null_data = mocker.spy(self.MappedDataSet, "set_null_data")
        spy_tune = mocker.spy(self.MappedDataSet, "tune")

        for k, v in self.test_map_1.map_.items():

            # Reset all spies
            mocker.resetall()

            prev_config = self.dataset.get_config(name="1")

            self.dataset.set_config(
                name="1",
                value=k,
                tune_dataset=True,  # Force the tuning of dataset after config
            )

            # Check only applies if config has changed
            if k != prev_config:

                # Check on null data
                nb_of_null_data = 0
                for data_name in self.dataset.get_data_names():
                    if data_name not in v:
                        nb_of_null_data += 1
                        # Check w.r.t. set_null_data implementation in
                        # MappedDataSet
                        assert (
                            self.dataset.__getattribute__(data_name).name == "null"
                        )
                assert spy_set_null_data.call_count == nb_of_null_data

                # Check on not null data
                nb_of_not_null_data = len(v)

                # Compute the list of data names which have been passed to set_data
                list_of_set_data = []
                for call_args in spy_set_data.call_args_list:
                    list_of_set_data.append(call_args.kwargs["name"])

                # Check the set_data call count
                assert spy_set_data.call_count == nb_of_not_null_data
                # Check that the list of data names which have been passed to
                # set_data match the applicable set of data
                assert list_of_set_data.sort() == list(v).sort()

                for data_name in v:
                    # Check w.r.t. set_data implementation in MappedDataSet
                    assert (
                        self.dataset.__getattribute__(data_name).name == data_name
                    )

            # Otherwise check that tune() is not called
            else:
                spy_tune.assert_not_called()

    def test_conversions(self, mocker):
        """
        Test the proper execution of the applicable conversions

        Expected results:
            - When a conversion is applicable, check that it is added to the
              queue, and the executed
            - When no conversion are applicable, check that the queue stays
              empty
        """
        self.set_up_dataset()
        spy_conversion_11_to_12 = mocker.spy(
            self.Conversions, "conversion__config_11_to_config_12"
        )
        spy_conversion_15_to_11 = mocker.spy(
            self.Conversions, "conversion__config_15_to_config_11"
        )

        self.dataset.set_config(
            name="1",
            value="config_15",
            tune_dataset=False,
        )
        assert not self.dataset.conversions.is_pending()

        self.dataset.set_config(
            name="1",
            value="config_11",
            tune_dataset=False,
        )
        assert (
            self.Conversions.conversion__config_15_to_config_11
            is self.dataset.conversions._pending_conversion
        )
        self.dataset.tune()
        spy_conversion_15_to_11.assert_called_once()

        self.dataset.set_config(
            name="1",
            value="config_12",
            tune_dataset=False,
        )
        assert (
            self.Conversions.conversion__config_11_to_config_12
            is self.dataset.conversions._pending_conversion
        )
        self.dataset.tune()
        spy_conversion_11_to_12.assert_called_once()


class TestListedDataSet:

    # Define a concrete class to test AbstractListedDataSet mechanisms
    class ListedDataSet(AbstractListedDataSet):

        def __init__(self):
            super().__init__(
                sectors=builders.get_test_sectors(),
                final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
                regions=tests_cst.DEFAULT_REGIONS,
            )
            self.tune()

        @staticmethod
        def get_data_names():
            return ["A", "B", "C", "D"]

        def set_data(self, name: str):
            setattr(self, name, name)

        def set_null_data(self, name: str):
            setattr(self, name, "null")

    # Dataset to be reused throughout the tests
    dataset: ListedDataSet = None

    def set_up_dataset(self):
        self.dataset = self.ListedDataSet()

    def test_get_applicable_set(self):
        """
        Test function `get_applicable_set`

        Expected results:
            The applicable data match the attribute data_list
        """
        self.set_up_dataset()
        for list_ in [
            ["A", "B", "C"],
            ["A", "C"],
            ["B"],
            [],
        ]:
            self.dataset.data_list = list_
            assert (
                list(self.dataset.get_applicable_set()).sort() == list_.sort()
            )
