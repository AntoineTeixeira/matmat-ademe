"""
Overview
********
This module defines the system calcul strategy classes, which provide different
approaches for calculating and manipulating a system depending on the
available data and the objectives of the analysis.

To simplify integration and maintenance, each calculation approach is
encapsulated within a dedicated strategy class. A system object contains
a strategy object responsible for performing the necessary calculations.
The specific implementation of these calculations depends on the selected
strategy class.

Parameters
**********
system_dataset: SystemDataSet
    The dataset containing the system data. Its composition depends on
    the calcul strategy.
tolerance : float, optional
    The maximum allowed absolute deviation for considering the
    system balanced, by default 1e-2.

Notes
*****
- **Input data**: Most methods in this module require the parameters listed
  above as input (excluding tolerance). All input data must be structured and
  pre-validated before being passed to the calculation methods. Invalid or
  empty data will result in errors during computation.

- **Consistency checks**: Each strategy ensures consistency between the
  system's variables by:

  1. Verifying that the supply vector (`x`) aligns with the inter-industry
     matrix (`Z`) and the final demand (`Y`), i.e. market equilibrium.
  2. Ensuring that the Gross Fixed Capital Formation (GFCF) vectors in the
     final demand (`Y`) are correctly aligned with the investment matrix
     (`Y_k`), when applicable.
  3. Ensuring the consistency of the system's variables (flows and
     coefficients) in accordance with the Leontief framework.

- **Extensibility**: New strategies can be added by following these steps:

  1. **Define a new strategy class**: Create a class inheriting from
     :class:`AbstractSystemCalcul`.
  2. **Implement the required abstract methods**: Ensure all abstract methods
     defined in the base class are implemented.
  3. **Register the new strategy**: Update the enumeration class
     :class:`EnumSystemCalcul` to include the new strategy and link it to the
     corresponding class.
  4. **Write unit tests**: Add comprehensive unit tests for the new strategy
     in **`tests/unit_tests/core/system/strategies/calcul`**.
     These tests should cover:
        - Correct handling of inputs.
        - Proper calculation of outputs.
        - Compatibility with shocks and other operations.

Contents
********
- Classes:
    - :class:`EnumSystemCalcul`
    - :class:`AbstractSystemCalcul`
    - :class:`Standard`
    - :class:`InvestMatrix`
    - :class:`ExoInvestMatrix`
    - :class:`EndoInvestMatrix`
"""

__all__ = [
    "EnumSystemCalcul",
    "AbstractSystemCalcul",
    "Standard",
    "ExoInvestMatrix",
    "EndoInvestMatrix",
]

from enum import Enum, verify, UNIQUE
from abc import ABC, abstractmethod
import pandas as pd

from matmat.core.accounts.system.dataset.core import SystemDataSet
import matmat.utils.constants as cst
from matmat.utils.errors import MEUnknownStrategy

# noinspection PyPep8Naming
# pylint: disable=C0103, R0913
# C0103: some variables / parameters names are not lowercase because they match
#        MatMat literature case
# R0913: it is necessary to pass many arguments to have one single
#        interface for the calcul strategy


class AbstractSystemCalcul(ABC):
    """
    Abstract class representing a system calculation strategy.

    This class defines the abstract methods that must be implemented by any
    concrete system calcul class. It serves as a blueprint for creating
    specific strategies to perform calculations on a system object.

    Notes
    -----
    - Concrete implementations must inherit from this class.
    - All abstract methods defined here must be implemented in derived classes.

    See Also
    --------
    Standard : A strategy with exogenous investment demand vector.
    ExoInvestMatrix : A strategy with exogenous investment demand matrix.
    EndoInvestMatrix : A strategy with endogenous investment demand matrix.
    EnumSystemCalcul : Enumeration of available strategy classes.
    """

    NAME: str

    @property
    def name(self):
        return self.NAME

    @staticmethod
    @abstractmethod
    def list_shockable_data() -> list:
        """
        List the names of data that can be shocked in this strategy.

        Returns
        -------
        list
            A list of strings representing the names of data that can be
            shocked within this strategy.
        """

    @abstractmethod
    def calculate_market_equilibrium_deviation(
        self, system_dataset: SystemDataSet
    ):
        """
        Compute the deviation from market equilibrium.

        This method calculates the absolute deviation between supply and
        total use (inter-industry flows and final demand) of goods
        and services.

        Returns
        -------
        pd.Series
            A series representing the absolute deviation for each good and
            service between supply and total uses.

        Notes
        -----
        - A zero deviation indicates that supply equals total use for all goods
          and services, ensuring market equilibrium.
        - This method can be used to verify the consistency of the system
          after calculation.
        """

    @abstractmethod
    def is_market_equilibrium_within_tolerance(
        self,
        system_dataset: SystemDataSet,
        tolerance: float = 1e-2,
    ) -> bool:
        """
        Verify if the system fluxes are balanced within a specified tolerance.
        This method checks whether the absolute deviation from market
        equilibrium is less than the specified tolerance.

        Returns
        -------
        bool
            `True` if the absolute deviation is within the specified
            tolerance, `False` otherwise.
        """

    @abstractmethod
    def is_calculable_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ) -> bool:
        """
        Determine if the system can be calculated using the Leontief matrix.

        Returns
        -------
        bool
            True if the required variables for calculation from the Leontief
            matrix are not empty, False otherwise.
        """

    @abstractmethod
    def calculate_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ):
        """Perform system calculations using the Leontief matrix."""

    @abstractmethod
    def is_calculable_from_fluxes(
        self,
        system_dataset: SystemDataSet,
    ) -> bool:
        """
        Determine if the system can be calculated using flux data.

        Returns
        -------
        bool
            True if the required variables for calculation from fluxes
            are not empty, False otherwise.
        """

    @abstractmethod
    def calculate_from_fluxes(
        self,
        system_dataset: SystemDataSet,
        tolerance: float = 1e-2,
    ):
        """Perform system calculations using flux data."""

    def is_shock_applicable(self, shock_data_name: str) -> bool:
        """
        Check if a shock data is applicable to the system.

        Parameters
        ----------
        shock_data_name : str
            The name of the shock data to verify against the system strategy.

        Returns
        -------
        bool
            True if the shock data is compatible with the strategy,
            False otherwise.
        """
        # [:1] to slice the leading "d" from the data name
        # Example: "dA" becomes "A"
        return shock_data_name[1:] in self.list_shockable_data()


# noinspection PyPep8Naming
class Standard(AbstractSystemCalcul):
    """
    Standard strategy for system calculations.

    In this strategy, the capital coefficients matrix (K), the augmented
    Leontief matrix with capital (L_k), and the investment matrix (Y_k)
    are null.

    This is the default strategy for systems where investment matrix-related
    variables are not considered.
    """

    NAME: str = cst.STRATEGY_STANDARD

    @staticmethod
    def list_shockable_data() -> list:
        return [cst.A, cst.Y]

    def calculate_market_equilibrium_deviation(
        self, system_dataset: SystemDataSet
    ):
        deviation = abs(
            system_dataset.x.df.sum(axis=1)
            - system_dataset.Y.df.sum(axis=1)
            - system_dataset.Z.df.sum(axis=1)
        )
        return deviation

    def is_market_equilibrium_within_tolerance(
        self,
        system_dataset: SystemDataSet,
        tolerance: float = 1e-2,
    ) -> bool:
        deviation = self.calculate_market_equilibrium_deviation(
            system_dataset=system_dataset
        ).sum()
        return deviation < tolerance

    def is_calculable_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ) -> bool:
        return (
            not system_dataset.A.is_df_empty()
            and not system_dataset.Y.is_df_empty()
        )

    def calculate_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the system data using the Leontief matrix.

        This method performs the following calculations:

        1. Calculate the Leontief matrix (L) from the technical coefficients
           matrix (A).
        2. Calculate the domestic production vector (x_dom) from L and the
           final demand matrix (Y).
        3. Calculate the inter-industry matrix (Z) from A and x.
        4. Recalculate the entire supply vector x from Z and Y to ensure
           consistency.
        """
        system_dataset.L.calculate(A=system_dataset.A)
        system_dataset.x.calculate_from_leontief_matrix(
            L=system_dataset.L, Y=system_dataset.Y
        )
        system_dataset.Z.calculate(A=system_dataset.A, x=system_dataset.x)
        system_dataset.x.calculate_from_interindustry_matrix(
            Z=system_dataset.Z, Y=system_dataset.Y
        )

    def is_calculable_from_fluxes(
        self,
        system_dataset: SystemDataSet,
    ) -> bool:
        return (
            not system_dataset.Z.is_df_empty()
            and not system_dataset.Y.is_df_empty()
        )

    def calculate_from_fluxes(
        self,
        system_dataset: SystemDataSet,
        tolerance: float = 1e-2,
    ):
        """
        Calculate the system data using system fluxes.

        This method performs the following calculations:

        1. If supply vector (x) is empty or if market equilibrium is not
           verified, derive the supply vector (x) from the demand matrices
           (Y and Z).
        2. Derive the technical coefficients matrix (A) from the inter-industry
           matrix (Z) and the production vector (x_dom).
        3. Derive the Leontief matrix (L) from the technical coefficients
           matrix (A).
        """
        recalc_x_cond_1 = system_dataset.x.is_df_empty()
        recalc_x_cond_2 = not self.is_market_equilibrium_within_tolerance(
            system_dataset=system_dataset, tolerance=tolerance
        )
        if recalc_x_cond_1 | recalc_x_cond_2:
            system_dataset.x.calculate_from_interindustry_matrix(
                Y=system_dataset.Y, Z=system_dataset.Z
            )
        system_dataset.A.calculate(Z=system_dataset.Z, x=system_dataset.x)
        system_dataset.L.calculate(A=system_dataset.A)


# noinspection PyPep8Naming
class InvestMatrix(Standard):
    """
    Class defining common methods for system strategies involving
    an investment matrix.

    This class serves as a base for strategies where the capital coefficients
    matrix (K), the augmented Leontief matrix with capital (L_k), and the
    investment matrix (Y_k) are not null. It encapsulates shared logic and
    behaviors for derived classes that manage systems with investment dynamics.

    Inherited by
    ------------
    - :class:`ExoInvestMatrix`: Strategy with exogenous investment matrix.
    - :class:`EndoInvestMatrix`: Strategy with endogenous investment matrix.
    """

    NAME: str = "invest_matrix"

    def is_calculable_from_fluxes(
        self,
        system_dataset: SystemDataSet,
    ) -> bool:
        return (
            super().is_calculable_from_fluxes(system_dataset=system_dataset)
            and not system_dataset.Y_k.is_df_empty()
        )

    def calculate_from_fluxes(
        self,
        system_dataset: SystemDataSet,
        tolerance: float = 1e-2,
    ):
        """
        Calculate the system data using system fluxes.

        This method performs the following calculations:

        1. Update the Gross Fixed Capital Formation (GFCF) vectors in the final
           demand matrix (Y) based on the investment matrix (Y_k).
        2. Perform the same set of calculations of the standard system.
        3. Derive the capital coefficients matrix (K) from Y_k and x, and the
           augmented Leontief matrix (L_k) from A and K.
        """
        system_dataset.Y.update_gfcf_from_yk(system_dataset.Y_k)
        super().calculate_from_fluxes(
            system_dataset=system_dataset, tolerance=tolerance
        )
        system_dataset.K.calculate(Y_k=system_dataset.Y_k, x=system_dataset.x)
        system_dataset.L_k.calculate(A=system_dataset.A, K=system_dataset.K)


# noinspection PyPep8Naming
class ExoInvestMatrix(InvestMatrix):
    """
    Exogenous investment matrix strategy for system calculations.

    In this strategy, the capital coefficients matrix (K), the augmented
    Leontief matrix with capital (L_k), and the investment matrix (Y_k)
    are not null. Y_k is exogenous and K is endogenous.

    Shockable variables in this strategy are limited to:
        - Technical coefficients matrix (A)
        - Final demand matrix (Y)
        - Investment matrix (Y_k)
    """

    NAME: str = cst.STRATEGY_EXO_INVEST_MATRIX

    @staticmethod
    def list_shockable_data():
        return [cst.A, cst.Y, cst.Y_K]

    def is_calculable_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ) -> bool:
        return (
            super().is_calculable_from_leontief(system_dataset=system_dataset)
            and not system_dataset.Y_k.is_df_empty()
        )

    def calculate_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the system data using the Leontief matrix.

        This method performs the following calculations:

        1. Update the Gross Fixed Capital Formation (GFCF) vectors in the final
           demand matrix (Y) based on the investment matrix (Y_k).
        2. Perform the same set of calculations of the standard system.
        3. Derive the capital coefficients matrix (K) from Y_k and x, and the
           augmented Leontief matrix (L_k) from A and K.
        """

        system_dataset.Y.update_gfcf_from_yk(system_dataset.Y_k)
        super().calculate_from_leontief(system_dataset=system_dataset)
        system_dataset.K.calculate(Y_k=system_dataset.Y_k, x=system_dataset.x)
        system_dataset.L_k.calculate(A=system_dataset.A, K=system_dataset.K)


# noinspection PyPep8Naming
class EndoInvestMatrix(InvestMatrix):
    """
    Endogenous investment matrix strategy for system calculations.

    In this strategy, the capital coefficients matrix (K), the augmented
    Leontief matrix with capital (L_k), and the investment matrix (Y_k)
    are not null. K is exogenous and Y_k is endogenous.

    Shockable variables in this strategy are:
        - Technical coefficients matrix (A)
        - Final demand matrix (Y)
        - Capital coefficients matrix (K)
    """

    NAME: str = cst.STRATEGY_ENDO_INVEST_MATRIX

    @staticmethod
    def list_shockable_data():
        return [cst.A, cst.Y, cst.K]

    def is_calculable_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ) -> bool:
        return (
            super().is_calculable_from_leontief(system_dataset=system_dataset)
            and not system_dataset.K.is_df_empty()
        )

    def calculate_from_leontief(
        self,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the system data using the Leontief matrix.

        This method performs the following calculations:

        1. Calculate the Leontief matrix (L_k) from the technical and capital
           coefficients matrices (A and K).
        2. Calculate the domestic production vector (x_dom) from L_k
            and the final demand matrix (Y), excluding GFCF vector.
        3. Calculate the inter-industry and investment matrices (Z and Y_k)
           from A, K and x.
        4. Update the Gross Fixed Capital Formation (GFCF) vectors in the final
           demand matrix (Y) based on the investment matrix (Y_k).
        4. Recalculate the entire supply vector x from Z and Y to ensure
           consistency.
        """
        system_dataset.L_k.calculate(A=system_dataset.A, K=system_dataset.K)
        system_dataset.L.calculate(A=system_dataset.A)
        Y_wo_gfcf = system_dataset.Y.drop_gfcf(inplace=False)
        system_dataset.x.calculate_from_leontief_matrix(
            L=system_dataset.L_k, Y=Y_wo_gfcf
        )
        system_dataset.Z.calculate(A=system_dataset.A, x=system_dataset.x)
        system_dataset.Y_k.calculate(K=system_dataset.K, x=system_dataset.x)
        system_dataset.Y.update_gfcf_from_yk(Y_k=system_dataset.Y_k)
        system_dataset.x.calculate_from_interindustry_matrix(
            Z=system_dataset.Z, Y=system_dataset.Y
        )


@verify(UNIQUE)
class EnumSystemCalcul(Enum):
    """
    Enumeration of available system calculation strategies.

    This enumeration defines the existing strategies for system calculations.
    Each strategy corresponds to a specific implementation of the abstract
    system calculation strategy.

    Available strategies
    --------------------
    - **`standard`**: Default strategy with null `K`, `L_k`, and `Y_k`.
    - **`exo_invest_matrix`**: Strategy with non-null `K`, `L_k`, and `Y_k`,
      where only `A`, `Y`, and `Y_k` are shockable.
    - **`endo_invest_matrix`**: Strategy with non-null `K`, `L_k`, and `Y_k`,
      where `A`, `Y`, and `K` are shockable.
    """

    STANDARD = Standard.NAME
    EXO_INVEST_MATRIX = ExoInvestMatrix.NAME
    ENDO_INVEST_MATRIX = EndoInvestMatrix.NAME

    @classmethod
    def map_enum_to_classes(cls) -> dict:
        return {
            cls.STANDARD: Standard,
            cls.EXO_INVEST_MATRIX: ExoInvestMatrix,
            cls.ENDO_INVEST_MATRIX: EndoInvestMatrix,
        }

    def build_strategy(self) -> AbstractSystemCalcul:
        """
        Instantiate the corresponding system calculation strategy.

        Returns
        -------
        AbstractSystemCalcul
            An instance of the appropriate system calculation strategy.

        Raises
        ------
        KeyError
            If the strategy is not recognized.
        """
        map_strategies = self.map_enum_to_classes()
        try:
            return map_strategies[self]()
        except KeyError:
            raise MEUnknownStrategy(
                strategy=self.value,
                kind_of_strategy="calcul",
                known_strategies=[key.value for key in map_strategies.keys()],
            )
