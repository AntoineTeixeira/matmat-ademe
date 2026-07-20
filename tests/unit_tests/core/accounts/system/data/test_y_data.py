import pandas as pd
import numpy as np
import copy

import matmat.utils.constants as cst
from matmat.core.shocks.mixins import ShockableMixin
from matmat.core.data.strategies import structure, nature

from tests.utils import builders, constants as tests_cst


class TestYData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert builders.build_test_y().get_nature_type() is nature.Flux

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_y().get_structure_type()
            is structure.StructureY
        )

    def test_gfcf_column_set_and_get(self):
        """
        Test functions `set_gfcf` and `get_gfcf_column`
        Expected results:
            - The column retrieved has the expected values after being set
        """
        y = builders.build_test_y()
        gfcf = pd.DataFrame(
            index=y.df.index,
            columns=[
                (
                    y.get_domestic_regions_list()[0],
                    cst.IDX_INVESTMENT,
                    cst.IDX_INVESTMENT_I,
                )
            ],
            dtype=cst.DTYPE_FLOAT,
        )
        builders.randomize(gfcf, full_randomization=True)
        y.set_gfcf(gfcf)
        assert np.allclose(y.get_gfcf_column(), gfcf)

    def test_update_gfcf_from_yk(self):
        """
        Test functions `update_gfcf_from_yk`
        Expected results:
            - The GFCF column is the sum of the columns of Y_k
        """
        y = builders.build_test_system_data(
            name=cst.Y,
            regions=tests_cst.REGIONS_W_IMPORT,
        )
        yk = builders.build_test_system_data(
            name=cst.Y_K,
            regions=tests_cst.REGIONS_W_IMPORT,
        )

        y.final_demand_categories._validate_dataframe()

        builders.randomize(yk.df, full_randomization=True)
        y.update_gfcf_from_yk(Y_k=yk)

        gfcf_ref_df = pd.DataFrame(yk.df.sum(axis=1))
        assert np.allclose(y.get_gfcf_column(), gfcf_ref_df)

    def test_shock(self, mocker):
        """
        Test function `shock`

        Expected results:
            - Check that the method 'shock' from ShockableMixin is called
              once with the correct arguments
        """
        y = builders.build_test_y()
        dy = builders.build_test_dy()
        builders.randomize(y.df, with_zeros=True)
        builders.randomize(dy.df, with_zeros=True)

        spy_shock = mocker.spy(ShockableMixin, "shock")

        y.shock(shock_data=dy)

        spy_shock.assert_called_once_with(self=y, shock_data=dy)

    def test_shock_standard(self, mocker):
        """
        Test function `shock` for a standard system

        Expected results:
            - Check that the method 'shock' from ShockableMixin is called
              once with the correct arguments
        """
        y = builders.build_test_y()
        dy = builders.build_test_dy()
        builders.randomize(y.df, with_zeros=True)
        builders.randomize(dy.df, with_zeros=True)

        spy_shock = mocker.spy(ShockableMixin, "shock")

        y.shock(shock_data=dy, system_calcul_strategy=cst.STRATEGY_STANDARD)

        spy_shock.assert_called_once_with(self=y, shock_data=dy)

    def test_shock_exo_invest_matrix(self, mocker):
        """
        Test function `shock` for a non-standard system

        Expected results:
            - Check that the method 'shock' from ShockableMixin is called
              once with the correct arguments
            - Ensure that the investment column(s) has not been modified
        """
        y = builders.build_test_y()
        dy = builders.build_test_dy()
        builders.randomize(y.df, with_zeros=True)
        builders.randomize(dy.df, with_zeros=True)
        y0 = copy.deepcopy(y)

        spy_shock = mocker.spy(ShockableMixin, "shock")

        y.shock(
            shock_data=dy,
            system_calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
        )

        spy_shock.assert_called_once_with(self=y, shock_data=dy)
        assert np.allclose(y.get_gfcf_column(), y0.get_gfcf_column())
