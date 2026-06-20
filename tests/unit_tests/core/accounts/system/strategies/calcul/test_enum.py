import pytest

from matmat.core.accounts.system.strategies import calcul


class TestEnumSystemCalcul:

    def test_build_known_strategy(self):
        """
        Check function `build_strategy`

        Expected results:
            - For each enumeration member, returns the correct calcul strategy type
        """
        dict_system_strategies = {
            calcul.EnumSystemCalcul.STANDARD: calcul.Standard,
            calcul.EnumSystemCalcul.EXO_INVEST_MATRIX: calcul.ExoInvestMatrix,
            calcul.EnumSystemCalcul.ENDO_INVEST_MATRIX: calcul.EndoInvestMatrix
        }

        for key, value in dict_system_strategies.items():
            assert isinstance(calcul.EnumSystemCalcul(key).build_strategy(), value)

    def test_build_unknown_strategy(self):
        """
        Check function `build_strategy`

        Expected results:
            - The strategy given does not exist, a ValueError shall be raised
        """
        with pytest.raises(ValueError):
            calcul.EnumSystemCalcul("unknown strategy").build_strategy()
