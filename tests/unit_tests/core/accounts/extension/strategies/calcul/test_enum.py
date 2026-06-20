import pytest

from matmat.core.accounts.extension.strategies import calcul
import matmat.utils.constants as cst


class TestEnumExtensionCalcul:

    def test_build_known_strategy(self):
        """
        Test function `build_strategy` with a known strategy

        Expected results:
            - Check that the instantiated strategy match the strategy
              given as parameter
        """
        list_of_known_strategies = [
            {
                "strategy_class": calcul.UseBased,
                "strategy": cst.STRATEGY_USE_BASED,
            },
            {
                "strategy_class": calcul.GrossOutputBased,
                "strategy": cst.STRATEGY_GROSS_OUTPUT_BASED,
            },
            {
                "strategy_class": calcul.EmbodiedInImport,
                "strategy": cst.STRATEGY_EMBODIED_IN_IMPORT,
            },
        ]
        for elt in list_of_known_strategies:
            strategy = calcul.EnumExtensionCalcul(
                elt["strategy"]
            ).build_strategy()
            assert type(strategy) is elt["strategy_class"]

    def test_build_unknown_strategy(self):
        """
        Test function `build_strategy` with an unknown strategy

        Expected results:
            - Check that an exception ValueError is raised
        """
        with pytest.raises(ValueError):
            calcul.EnumExtensionCalcul("unknown strategy").build_strategy()
