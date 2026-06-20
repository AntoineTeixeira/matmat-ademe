from matmat.core.accounts.extension.strategies import calcul
import matmat.core.accounts.extension.data.core as extension_data
from matmat.utils import constants as cst

import tests.utils.builders as builders
import tests.utils.spy as spy


class TestEmbodiedInImport:
    strategy = calcul.EmbodiedInImport()
    system_dataset = builders.build_test_system_dataset(
        calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
    )
    extension_dataset = builders.build_test_extension_dataset(
        extension_calcul_strategy=cst.STRATEGY_EMBODIED_IN_IMPORT,
        system_calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
    )

    def test_calculate_m(self, mocker):
        """
        Test function `calculate_m`

        Expected results:
            - Check the calcul of multiplier M:
                - Check that the method `calculate` is called with
                  M_RoW, L, A
        """
        spy_m = mocker.spy(extension_data.MData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.extension_dataset.M_RoW.df)
        builders.randomize(self.system_dataset.L.df)
        builders.randomize(self.system_dataset.A.df)

        self.strategy.calculate_m(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        # Check call to MData.calculate
        assert spy_m.call_count == 1
        spy.check_specific_call_with_args(
            function_spy=spy_m,
            call_number=1,
            args=[self.extension_dataset.M],
            kwargs={
                "M_RoW": self.extension_dataset.M_RoW,
                "L": self.system_dataset.L,
                "A": self.system_dataset.A,
            },
        )

    def test_calculate_mk(self, mocker):
        """
        Test function `calculate_mk`

        Expected results:
            - Check the calcul of multiplier M_k:
                - Check that the method `calculate` is called with
                  M_RoW, L_k, A, K
        """
        spy_m = mocker.spy(extension_data.MKData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.extension_dataset.M_RoW.df)
        builders.randomize(self.system_dataset.L_k.df)
        builders.randomize(self.system_dataset.A.df)
        builders.randomize(self.system_dataset.K.df)

        self.strategy.calculate_mk(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        # Check call to MKData.calculate
        assert spy_m.call_count == 1
        spy.check_specific_call_with_args(
            function_spy=spy_m,
            call_number=1,
            args=[self.extension_dataset.M_k],
            kwargs={
                "M_RoW": self.extension_dataset.M_RoW,
                "L": self.system_dataset.L_k,
                "A": self.system_dataset.A,
                "K": self.system_dataset.K,
            },
        )

    def test_calculate_d_cba(self, mocker):
        """
        Test function `calculate_d_cba`

        Expected results:
            - Check that the method `calculate` of DCbaData is called
              with the correct arguments M, Y, M_RoW
        """
        spy_d_cba = mocker.spy(extension_data.DCbaData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.system_dataset.Y.df)
        builders.randomize(self.extension_dataset.M.df)
        builders.randomize(self.extension_dataset.M_RoW.df)

        self.strategy.calculate_d_cba(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        spy_d_cba.assert_called_once_with(
            self.extension_dataset.d_cba,
            Y=self.system_dataset.Y,
            M=self.extension_dataset.M,
            M_RoW=self.extension_dataset.M_RoW,
        )

    def test_calculate_d_cba_k(self, mocker):
        """
        Test function `calculate_d_cba_k`

        Expected results:
            - Check that the method `calculate` of DCbaKData is called
              with the correct arguments M_k, M_RoW, Y
        """
        spy_d_cba_k = mocker.spy(extension_data.DCbaKData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.system_dataset.Y.df)
        builders.randomize(self.extension_dataset.M_k.df)
        builders.randomize(self.extension_dataset.M_RoW.df)

        self.strategy.calculate_d_cba_k(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        spy_d_cba_k.assert_called_once_with(
            self.extension_dataset.d_cba_k,
            Y=self.system_dataset.Y,
            M=self.extension_dataset.M_k,
            M_RoW=self.extension_dataset.M_RoW,
        )
