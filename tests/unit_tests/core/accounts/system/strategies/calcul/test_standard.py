import matmat.utils.constants as cst
from matmat.core.accounts.system.strategies import calcul
import matmat.core.accounts.system.data.core as system_data
from tests.utils import builders


class TestStandard:

    # Dataset object defined as class variable to be reused easily
    # throughout the tests
    dataset = builders.build_test_system_dataset(
        calcul_strategy=cst.STRATEGY_STANDARD
    )

    def test_calculate_from_leontief(self, mocker):
        """
        Test function `calculate_from_leontief`

        Expected results:
            - Using the mocker.spy fixture, check that the calculate methods
            from LData, XData and ZData
            are called with the correct arguments
        """
        self.dataset.reset()
        spy_l = mocker.spy(system_data.LData, "calculate")
        spy_x_1 = mocker.spy(
            system_data.XData, "calculate_from_leontief_matrix"
        )
        spy_x_2 = mocker.spy(
            system_data.XData, "calculate_from_interindustry_matrix"
        )
        spy_z = mocker.spy(system_data.ZData, "calculate")

        strategy = calcul.Standard()
        builders.randomize_dataset(self.dataset)
        strategy.calculate_from_leontief(
            system_dataset=self.dataset,
        )

        spy_l.assert_called_once_with(self.dataset.L, A=self.dataset.A)
        spy_x_1.assert_any_call(
            self.dataset.x, L=self.dataset.L, Y=self.dataset.Y
        )
        spy_z.assert_called_once_with(
            self.dataset.Z, A=self.dataset.A, x=self.dataset.x
        )
        spy_x_2.assert_any_call(
            self.dataset.x, Z=self.dataset.Z, Y=self.dataset.Y
        )

    def test_calculate_from_fluxes_x_empty(self, mocker):
        """
        Test function `calculate_from_fluxes`

        Expected results:
            - Using the mocker.spy fixture, check that the calculate methods
            from XData, AData and LData
            are called with the correct arguments
        """
        test_tolerance = 1e-3

        self.dataset.reset()
        spy_l = mocker.spy(system_data.LData, "calculate")
        spy_a = mocker.spy(system_data.AData, "calculate")
        spy_x = mocker.spy(
            system_data.XData, "calculate_from_interindustry_matrix"
        )

        strategy = calcul.Standard()
        builders.randomize_dataset(self.dataset)
        # Ensure x is empty
        self.dataset.x.reset()

        strategy.calculate_from_fluxes(
            system_dataset=self.dataset,
            tolerance=test_tolerance,
        )

        spy_x.assert_called_once_with(
            self.dataset.x, Y=self.dataset.Y, Z=self.dataset.Z
        )
        spy_a.assert_called_once_with(
            self.dataset.A, Z=self.dataset.Z, x=self.dataset.x
        )
        spy_l.assert_called_once_with(self.dataset.L, A=self.dataset.A)

    def test_calculate_from_fluxes_market_equilibrium_not_verified(
        self, mocker
    ):
        """
        Test function `calculate_from_fluxes`

        Expected results:
            - Using the mocker.spy fixture, check that the calculate methods
            from XData, AData and LData
            are called with the correct arguments
        """
        test_tolerance = 1e-3

        self.dataset.reset()

        # Ensure x is not empty
        builders.randomize(df=self.dataset.x.df)
        # Ensure market is not balanced
        builders.randomize(df=self.dataset.Y.df)
        builders.randomize(df=self.dataset.Z.df)

        spy_l = mocker.spy(system_data.LData, "calculate")
        spy_a = mocker.spy(system_data.AData, "calculate")
        spy_x = mocker.spy(
            system_data.XData, "calculate_from_interindustry_matrix"
        )

        strategy = calcul.Standard()

        strategy.calculate_from_fluxes(
            system_dataset=self.dataset,
            tolerance=test_tolerance,
        )

        spy_x.assert_called_once_with(
            self.dataset.x, Y=self.dataset.Y, Z=self.dataset.Z
        )
        spy_a.assert_called_once_with(
            self.dataset.A, Z=self.dataset.Z, x=self.dataset.x
        )
        spy_l.assert_called_once_with(self.dataset.L, A=self.dataset.A)

    def test_calculate_from_fluxes_market_equilibrium_verified(self, mocker):
        """
        Test function `calculate_from_fluxes`

        Expected results:
            - Using the mocker.spy fixture, check that the calculate methods
            from AData and LData
            are called with the correct arguments
            - Check that x is not re-calculated
        """
        test_tolerance = 1e-3

        self.dataset.reset()

        # Ensure market is balanced
        builders.randomize(df=self.dataset.Y.df)
        builders.randomize(df=self.dataset.Z.df)
        self.dataset.x.calculate_from_interindustry_matrix(
            Z=self.dataset.Z, Y=self.dataset.Y
        )

        spy_l = mocker.spy(system_data.LData, "calculate")
        spy_a = mocker.spy(system_data.AData, "calculate")
        spy_x = mocker.spy(
            system_data.XData, "calculate_from_interindustry_matrix"
        )

        strategy = calcul.Standard()
        strategy.calculate_from_fluxes(
            system_dataset=self.dataset,
            tolerance=test_tolerance,
        )

        spy_x.assert_not_called()
        spy_a.assert_called_once_with(
            self.dataset.A, Z=self.dataset.Z, x=self.dataset.x
        )
        spy_l.assert_called_once_with(self.dataset.L, A=self.dataset.A)

    def test_is_shock_applicable(self):
        """
        Test function `is_shock_applicable`

        Expected results:
            - Check that the method returns True only for A and Y shock data
        """
        strategy = calcul.Standard()
        for shock_data in cst.LIST_OF_SYSTEM_SHOCK_DATA:
            if shock_data in [cst.D_A, cst.D_Y]:
                assert strategy.is_shock_applicable(shock_data_name=shock_data)
            else:
                assert not strategy.is_shock_applicable(
                    shock_data_name=shock_data
                )
