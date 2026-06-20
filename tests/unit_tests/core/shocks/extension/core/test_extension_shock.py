import pytest
import os
import shutil

from matmat.core.shocks.extension.dataset.core import ExtensionShockDataSet
import matmat.utils.constants as cst

import tests.utils.builders as builders


class TestExtensionShock:
    """
    Test class to test the class ExtensionShock
    """

    PATH_TO_INIT_DIR = f"./{cst.DIR_SHOCKS}"
    PATH_TO_INIT_DIR_EXTENSIONS = f"{PATH_TO_INIT_DIR}/{cst.DIR_EXTENSIONS}"
    EXTENSION_NAME = "test_extension"
    extension = builders.build_use_based_extension(name=EXTENSION_NAME)

    extension_shock_dataset = builders.build_test_extension_shock_dataset(
        extension_name=EXTENSION_NAME,
    )

    @classmethod
    def setup_class(cls):

        if not os.path.isdir(cls.PATH_TO_INIT_DIR):
            os.mkdir(cls.PATH_TO_INIT_DIR)
            os.mkdir(cls.PATH_TO_INIT_DIR_EXTENSIONS)
            os.mkdir(f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}/{cls.EXTENSION_NAME}")

        builders.randomize_dataset(cls.extension_shock_dataset)
        cls.extension_shock_dataset.save_to_path(
            path=f"{cls.PATH_TO_INIT_DIR_EXTENSIONS}/{cls.EXTENSION_NAME}",
            export_format="pickle",
        )

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.PATH_TO_INIT_DIR)

    def test_load_from_path(self):
        """
        Test function `load_from_path`

        Expected results:
            - Test that the data composing the shock are the same as the data
              exported
        """

        extension_shock = builders.build_extension_shock(self.extension)
        extension_shock.load_from_path(
            path=f"{self.PATH_TO_INIT_DIR_EXTENSIONS}/{extension_shock.name}"
        )

        assert extension_shock.dataset.equals(self.extension_shock_dataset)

    def test_inject_shock(self):
        """
        Test method `inject_shock`

        Expected results:
            - Check that the shock is injected properly
        """
        ext = builders.build_use_based_extension("test_extension")
        ext_shock_1 = builders.build_extension_shock(extension=ext)
        builders.randomize(ext_shock_1.dataset.dS_x_dom.df)
        builders.randomize(ext_shock_1.dataset.dS_Y.df)

        ext_shock_2 = builders.build_extension_shock(extension=ext)
        ext_shock_2.dataset.dS_x_dom.set_values(1.0)
        ext_shock_2.dataset.dS_Y.set_values(0.0)

        assert not ext_shock_1.dataset.dS_x_dom.equals(
            ext_shock_2.dataset.dS_x_dom
        )
        assert not ext_shock_1.dataset.dS_Y.equals(ext_shock_2.dataset.dS_Y)

        ext_shock_1.inject_shock(shock=ext_shock_2, inject_zeros=False)
        assert ext_shock_1.dataset.dS_x_dom.equals(
            ext_shock_2.dataset.dS_x_dom
        )
        assert not ext_shock_1.dataset.dS_Y.equals(ext_shock_2.dataset.dS_Y)

        ext_shock_1.inject_shock(shock=ext_shock_2, inject_zeros=True)
        assert ext_shock_1.dataset.dS_x_dom.equals(
            ext_shock_2.dataset.dS_x_dom
        )
        assert ext_shock_1.dataset.dS_Y.equals(ext_shock_2.dataset.dS_Y)

    def test_disaggregate_wrt_extension_name(
        self,
        mocker,
        extension_shock_use_based_1,
        bridge_sectors_from_1_to_3,
        bridge_regions_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
    ):
        """
        Test function `disaggregate`

        Expected results:
            - If match_extension_name is True:
                - Nothing happens if the bridge extension name does not match
                - The extension is aggregated if the bridge extension name
                  match
            - Else the extension name does not matter
        """
        extension_shock = extension_shock_use_based_1.copy()

        # Prepare extension categories bridges
        bridge_ext_cats_valid = bridge_ext_cats_from_1_to_3.copy()
        bridge_ext_cats_valid.sheet_name = extension_shock.name
        bridge_ext_cats_invalid = bridge_ext_cats_from_1_to_3.copy()

        # Set up spies
        spy_dataset = mocker.spy(ExtensionShockDataSet, "disaggregate")

        # Call method under test
        extension_shock.disaggregate(
            bridge_sectors_from_1_to_3,
            bridge_regions_from_1_to_3,
            bridge_fdc_from_1_to_3,
            bridge_ext_cats_valid,
            bridge_ext_cats_invalid,
            match_extension_name=True,
        )

        # Check calls
        spy_dataset.assert_called_once_with(
            extension_shock.dataset,
            bridge_sectors_from_1_to_3,
            bridge_regions_from_1_to_3,
            bridge_fdc_from_1_to_3,
            bridge_ext_cats_valid,
        )

    def test_disaggregate(
        self,
        mocker,
        extension_shock_gross_output_based_1,
        bridge_sectors_from_1_to_3,
        bridge_regions_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
    ):
        """
        Test function `disaggregate` with various bridges

        Expected results:
            - Check that the methods `disaggregate` of dataset is called
              with the proper arguments
        """
        shock = extension_shock_gross_output_based_1.copy()

        # Set up spies
        spy_dataset = mocker.spy(ExtensionShockDataSet, "disaggregate")

        # Call method under test
        shock.disaggregate(
            bridge_sectors_from_1_to_3,
            bridge_regions_from_1_to_3,
            bridge_fdc_from_1_to_3,
            bridge_ext_cats_from_1_to_3,
            match_extension_name=False,
        )

        # Check calls
        spy_dataset.assert_called_once_with(
            shock.dataset,
            bridge_sectors_from_1_to_3,
            bridge_regions_from_1_to_3,
            bridge_fdc_from_1_to_3,
            bridge_ext_cats_from_1_to_3,
        )

    def test_aggregate(
        self,
        extension_shock_gross_output_based_1,
        bridge_sectors_from_1_to_3,
        bridge_regions_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
    ):
        """
        Test function `aggregate` with various bridges

        Expected results:
            - An exception is raised
        """
        shock = extension_shock_gross_output_based_1.copy()

        # Call method under test
        with pytest.raises(NotImplementedError):
            shock.aggregate(
                bridge_sectors_from_1_to_3,
                bridge_regions_from_1_to_3,
                bridge_fdc_from_1_to_3,
                bridge_ext_cats_from_1_to_3,
            )
