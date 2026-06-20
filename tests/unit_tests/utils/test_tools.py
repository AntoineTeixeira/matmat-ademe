import pandas as pd
import numpy as np

import matmat.utils.tools as tools
import matmat.utils.constants as cst
from tests.utils import builders, constants as tests_cst


class TestTools:
    def test_clean_dataframe(self):
        """
        Test function `clean_dataframe`

        Expected results:
            - Check that the dataframe is cleaned from NaN, INF and -INF,
              and that they are replaced by 0.0
        """
        df_test = pd.DataFrame(
            index=pd.Index(["a", "b", "c"]),
            columns=pd.Index(["1", "2", "3"]),
            dtype="float",
        )
        builders.randomize(df_test)
        df_test.iloc[0, 2] = np.nan
        df_test.iloc[1, 0] = np.inf
        df_test.iloc[2, 2] = -np.inf

        tools.clean_dataframe(df_test)

        assert not df_test.isin([np.nan, np.inf, -np.inf]).any().any()
        assert df_test.iloc[0, 2] == 0.0
        assert df_test.iloc[1, 0] == 0.0
        assert df_test.iloc[2, 2] == 0.0

    def test_sum_on_sectors(self):
        """
        Test function `sum_on_sectors`

        Expected results:
            - Check that the computed dataframe values correspond to the sum relatively
            to the levels ["category", "sub_category", "sector"] on the row axis
        """
        test_sectors = builders.get_test_sectors()
        a = builders.build_test_system_data(
            name=cst.A,
            regions=tests_cst.DEFAULT_MULTI_REGIONS,
            sectors=test_sectors,
        )
        builders.randomize(a.df)

        # (1)
        df_test = tools.sum_on_sectors(
            a.df, axis=0, sectors_levels=test_sectors.get_level_names()
        )
        assert df_test.equals(
            a.df.groupby(
                level=test_sectors.get_level_names(),
                sort=False,
            ).sum()
        )
