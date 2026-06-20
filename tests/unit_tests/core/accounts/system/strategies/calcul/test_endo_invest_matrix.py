import matmat.utils.constants as cst
from matmat.core.accounts.system.strategies import calcul
import matmat.core.accounts.system.data.core as system_data
import tests.utils.builders as builders
import tests.utils.spy as spy


class TestEndoInvestMatrix:

    # Dataset object defined as class variable to be reused easily
    # throughout the tests
    dataset = builders.build_test_system_dataset(
        calcul_strategy=cst.STRATEGY_ENDO_INVEST_MATRIX
    )

    def test_calculate_from_leontief(self, mocker):
        """
        Test function `calculate_from_leontief`

        Expected results:
            - Using the mocker.spy fixture, check that the calculate methods
            from XData, ZData, LKData, YKData are called with the
            correct arguments, and check that the update of GFCF is called
            for YData
        """
        self.dataset.reset()
        spy_x_1 = mocker.spy(
            system_data.XData, "calculate_from_leontief_matrix"
        )
        spy_x_2 = mocker.spy(
            system_data.XData, "calculate_from_interindustry_matrix"
        )
        spy_z = mocker.spy(system_data.ZData, "calculate")
        spy_lk = mocker.spy(system_data.LKData, "calculate")
        spy_yk = mocker.spy(system_data.YKData, "calculate")
        spy_y = mocker.spy(system_data.YData, "update_gfcf_from_yk")

        strategy = calcul.EndoInvestMatrix()

        builders.randomize_dataset(self.dataset)
        strategy.calculate_from_leontief(
            system_dataset=self.dataset,
        )

        spy_lk.assert_called_once_with(
            self.dataset.L_k, A=self.dataset.A, K=self.dataset.K
        )

        y_wo_gfcf = self.dataset.Y.drop_gfcf(inplace=False)
        # Use the custom method because it does the comparison Zof data
        # by values (if the comparison by reference fails)
        spy.check_specific_call_with_args(
            function_spy=spy_x_1,
            call_number=1,
            args=[self.dataset.x],
            kwargs={cst.L: self.dataset.L_k, cst.Y: y_wo_gfcf},
        )
        spy_z.assert_called_once_with(
            self.dataset.Z, A=self.dataset.A, x=self.dataset.x
        )
        spy_yk.assert_called_once_with(
            self.dataset.Y_k, K=self.dataset.K, x=self.dataset.x
        )
        spy_y.assert_called_once_with(self.dataset.Y, Y_k=self.dataset.Y_k)
        spy_x_2.assert_called_once_with(
            self.dataset.x, Z=self.dataset.Z, Y=self.dataset.Y
        )

    def test_calculate_from_fluxes(self, mocker):
        """
        Test function `calculate_from_fluxes`

        Expected results:
            - Using the mocker.spy fixture, check that the calculate methods
            from AData, LData, KData, LKData, YKData
            are called with the correct arguments
        """
        test_tolerance = 1e-3

        self.dataset.reset()
        spy_k = mocker.spy(system_data.KData, "calculate")
        spy_lk = mocker.spy(system_data.LKData, "calculate")
        spy_y = mocker.spy(system_data.YData, "update_gfcf_from_yk")
        spy_standard = mocker.spy(calcul.Standard, "calculate_from_fluxes")

        strategy = calcul.EndoInvestMatrix()
        builders.randomize_dataset(self.dataset)
        strategy.calculate_from_fluxes(
            system_dataset=self.dataset,
            tolerance=test_tolerance,
        )

        spy_y.assert_called_once_with(self.dataset.Y, Y_k=self.dataset.Y_k)
        spy_standard.assert_called_once_with(
            strategy,
            system_dataset=self.dataset,
            tolerance=test_tolerance,
        )
        spy_k.assert_called_once_with(
            self.dataset.K, x=self.dataset.x, Y_k=self.dataset.Y_k
        )
        spy_lk.assert_called_once_with(
            self.dataset.L_k, A=self.dataset.A, K=self.dataset.K
        )

    def test_is_shock_applicable(self):
        """
        Test function `is_shock_applicable`

        Expected results:
            - Check that the method returns True only for A, Z, Y and K
            shock data
        """
        strategy = calcul.EndoInvestMatrix()
        for shock_data in cst.LIST_OF_SYSTEM_SHOCK_DATA:
            if shock_data in [cst.D_A, cst.D_Y, cst.D_K]:
                assert strategy.is_shock_applicable(shock_data_name=shock_data)
            else:
                assert not strategy.is_shock_applicable(
                    shock_data_name=shock_data
                )
