from matmat.core.accounts.extension.strategies import calcul
import matmat.core.accounts.extension.data.core as extension_data
from matmat.utils import constants as cst

import tests.utils.builders as builders
import tests.utils.spy as spy


class TestGrossOutputBased:
    strategy = calcul.GrossOutputBased()
    system_dataset = builders.build_test_system_dataset(
        calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
    )
    extension_dataset = builders.build_test_extension_dataset(
        extension_calcul_strategy=cst.STRATEGY_GROSS_OUTPUT_BASED,
        system_calcul_strategy=cst.STRATEGY_EXO_INVEST_MATRIX,
    )

    def test_calculate_coefficients(self, mocker):
        """
        Test function `calculate`

        If the coefficients are empty and the fluxes are not, then the coefficients shall be computed

        Expected results:
            - Check that the "calculate" methods of SxDomData is called with the correct arguments
            - Check that the "calculate" methods of Z and Y data are not called
        """
        spy_s_x_dom = mocker.spy(extension_data.SxDomData, "calculate")
        spy_s_y = mocker.spy(extension_data.SyData, "calculate")
        spy_s_z = mocker.spy(extension_data.SzData, "calculate")
        spy_f_x_dom = mocker.spy(extension_data.FxDomData, "calculate")
        spy_f_y = mocker.spy(extension_data.FyData, "calculate")
        spy_f_z = mocker.spy(extension_data.FzData, "calculate")

        # Ensure coefficients are empty and fluxes are not
        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(
            self.extension_dataset.F_x_dom.df, full_randomization=False
        )
        builders.randomize(
            self.extension_dataset.F_Y.df, full_randomization=False
        )
        builders.randomize(
            self.extension_dataset.F_Z.df, full_randomization=False
        )
        self.strategy.calculate(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        spy.check_specific_call_with_args(
            function_spy=spy_s_x_dom,
            call_number=1,
            args=[self.extension_dataset.S_x_dom],
            kwargs={
                "F_x_dom": self.extension_dataset.F_x_dom,
                "x": self.system_dataset.x,
            },
        )
        spy_f_x_dom.assert_not_called()
        spy_s_y.assert_not_called()
        spy_f_y.assert_not_called()
        spy_s_z.assert_not_called()
        spy_f_z.assert_not_called()

    def test_calculate_fluxes(self, mocker):
        """
        Test function `calculate`

        If the fluxes are empty and the coefficients are not, then the fluxes shall be computed

        Expected results:
            - Check that the "calculate" methods of FxDomData is called with the correct arguments
            - Check that the "calculate" methods of Z and Y data are not called
        """
        spy_s_x_dom = mocker.spy(extension_data.SxDomData, "calculate")
        spy_s_y = mocker.spy(extension_data.SyData, "calculate")
        spy_s_z = mocker.spy(extension_data.SzData, "calculate")
        spy_f_x_dom = mocker.spy(extension_data.FxDomData, "calculate")
        spy_f_y = mocker.spy(extension_data.FyData, "calculate")
        spy_f_z = mocker.spy(extension_data.FzData, "calculate")

        # Ensure fluxes are empty and coefficients are not
        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(
            self.extension_dataset.S_x_dom.df, full_randomization=False
        )
        builders.randomize(self.system_dataset.x.df, full_randomization=False)
        self.strategy.calculate(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        spy_s_x_dom.assert_not_called()
        spy.check_specific_call_with_args(
            function_spy=spy_f_x_dom,
            call_number=1,
            args=[self.extension_dataset.F_x_dom],
            kwargs={
                "S_x_dom": self.extension_dataset.S_x_dom,
                "x": self.system_dataset.x,
            },
        )
        spy_s_y.assert_not_called()
        spy_f_y.assert_not_called()
        spy_s_z.assert_not_called()
        spy_f_z.assert_not_called()

    def test_calculate_m(self, mocker):
        """
        Test function `calculate_m`

        Expected results:
            - Check the calcul of multiplier M:
                - Check that the method `calculate` is called with S_x_dom,
                  L_dom
        """
        spy_m = mocker.spy(extension_data.MData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.extension_dataset.S_x_dom.df)
        builders.randomize(self.system_dataset.L.df)

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
                "S_x_dom": self.extension_dataset.S_x_dom,
                "L": self.system_dataset.L,
            },
        )

    def test_calculate_mk(self, mocker):
        """
        Test function `calculate_mk`

        Expected results:
            - Check the calcul of multiplier M_k:
                - Check that the method `calculate` is called with S_x_dom,
                  L_k
        """
        spy_m = mocker.spy(extension_data.MKData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.extension_dataset.S_x_dom.df)
        builders.randomize(self.system_dataset.L_k.df)

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
                "S_x_dom": self.extension_dataset.S_x_dom,
                "L": self.system_dataset.L_k,
            },
        )

    def test_calculate_d_cba(self, mocker):
        """
        Test function `calculate_d_cba`

        Expected results:
            - Check that the method `calculate` of DCbaData is called
              with the correct arguments Y, M
        """
        spy_d_cba = mocker.spy(extension_data.DCbaData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.system_dataset.Y.df)
        builders.randomize(self.extension_dataset.M.df)

        self.strategy.calculate_d_cba(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        spy_d_cba.assert_called_once_with(
            self.extension_dataset.d_cba,
            Y=self.system_dataset.Y,
            M=self.extension_dataset.M,
        )

    def test_calculate_d_cba_k(self, mocker):
        """
        Test function `calculate_d_cba_k`

        Expected results:
            - Check that the method `calculate` of DCbaKData is called
              with the correct arguments Y, M_k
        """
        spy_d_cba_k = mocker.spy(extension_data.DCbaKData, "calculate")

        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(self.system_dataset.Y.df)
        builders.randomize(self.extension_dataset.M_k.df)

        self.strategy.calculate_d_cba_k(
            system_dataset=self.system_dataset,
            extension_dataset=self.extension_dataset,
        )

        spy_d_cba_k.assert_called_once_with(
            self.extension_dataset.d_cba_k,
            Y=self.system_dataset.Y,
            M=self.extension_dataset.M_k,
        )

    def test_reset_for_shock(self):
        """
        Test function `reset_for_shock`

        Expected results:
            - Check that F_x_dom is empty after reset
        """
        self.system_dataset.reset()
        self.extension_dataset.reset()
        builders.randomize(
            self.extension_dataset.F_x_dom.df, full_randomization=False
        )

        assert not self.extension_dataset.F_x_dom.is_df_empty()

        self.strategy.reset_for_shock(
            extension_dataset=self.extension_dataset,
        )

        assert self.extension_dataset.F_x_dom.is_df_empty()
