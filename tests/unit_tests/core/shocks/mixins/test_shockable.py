import copy

import numpy as np

from tests.utils import builders


class TestShockableMixin:
    """
    This class implements tests to test the mixin ShockableMixin
    """

    def test_shock(self):
        """
        Test function `shock`

        Expected results:
            - Check that the data after shock is equal to A0 * (1 + dA).
        """
        a = builders.build_test_a()
        da = builders.build_test_da()
        builders.randomize(a.df, with_zeros=True)
        builders.randomize(da.df, with_zeros=True)
        a0 = copy.deepcopy(a)
        a.shock(shock_data=da)

        a_ref = a0.df * (1 + da.df)

        assert np.allclose(a.df, a_ref)
