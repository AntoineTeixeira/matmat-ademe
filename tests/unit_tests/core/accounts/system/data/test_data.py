import numpy as np

from matmat.core.accounts.system.data.core import AData

import tests.utils.constants as tests_cst
from tests.utils import builders


class TestSystemData:

    def test_constructor(self, mocker):
        """
        Test function `__init__`

        Expected results:
            - Instantiate an object A data, and check that:
                - Check that the structure and nature are properly set
                - Check that the dataframe index and columns match the
                  attributes df_index & df_columns of the associated structure
                - Check that the reader is the one expected
                - Check that the dataframe values are all NaN
        """
        spy_nature = mocker.spy(AData, "get_nature_type")
        spy_structure = mocker.spy(AData, "get_structure_type")

        a = AData(
            sectors=builders.get_test_sectors(),
            regions=tests_cst.DEFAULT_REGIONS,
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )
        # Nature
        assert spy_nature.spy_return is a.nature.__class__
        # Structure
        assert spy_structure.spy_return is a.structure.__class__
        # Dataframe
        assert a.df.index.equals(a.df_rows)
        assert a.df.columns.equals(a.df_columns)
        assert np.isnan(a.df).all().all()

    def test_constructor_no_import_regions(self):
        """
        Test function `__init__`

        In this test case, the list of "import" regions is empty.

        Expected results:
        - Check that the regions are properly set in the data structure
          and the identity card
        """
        data_ = AData(
            regions=tests_cst.REGIONS_WO_IMPORT,
            sectors=builders.get_test_sectors(),
            final_demand_categories=tests_cst.DEFAULT_Y_CATEGORIES,
        )

        assert data_.structure.get_domestic_regions_list() == ["France"]
        assert len(data_.structure.get_import_regions_list()) == 0
        assert not data_.structure.has_import_regions()
