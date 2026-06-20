"""
Overview
********
This module serves as the core of the `system` package.
It defines the main class: :class:`System`.

The `System` class provides methods to manage and manipulate a input-output
system, including functionality to calculate flows and coefficients, apply
shocks, reset system components, and aggregate or disaggregate data.

Contents
********
- Classes:
  - :class:`System`

"""

__all__ = ["System"]

import os

import pandas as pd

from matmat.core.bridge import core as bridge, pool as bridge_pool
from matmat.core.accounts.system.identity import SystemIdentity
from matmat.core.accounts.system.dataset.core import SystemDataSet
from matmat.core.accounts.system.strategies.calcul import (
    AbstractSystemCalcul,
    EnumSystemCalcul,
    Standard,
    ExoInvestMatrix,
    EndoInvestMatrix,
)
from matmat.core.accounts.system.data.core import (
    XData,
    YData,
    ZData,
)
from matmat.core.shocks.system.core import SystemShock
from matmat.core.dataset.mixins import ToListMixin, ComparisonMixin
from matmat.utils import logging as log, constants as cst, config, tools
from matmat.utils.mixins import CopyMixin
from matmat.utils.errors import (
    MENotEnoughData,
    MESystemNotBalanced,
)


# pylint: disable=C0103, R0902, R0904
class System(ToListMixin, CopyMixin, ComparisonMixin):
    """
    This class represents a system.

    To instantiate a `System`, refer to the
    `matmat.core.accounts.system.builder` module.

    Attributes
    ----------
    _id: SystemIdentity
        The identity card of the system
    _dataset : SystemDataSet
        The dataset composing the system
    _calcul: AbstractSystemCalcul
        The calculation strategy

    See Also
    --------
    SystemShock: Class for applying shocks to the system.
    EnumSystemCalcul: Enumeration of available calculation strategies.
    """

    # Identity
    _id: SystemIdentity
    # Dataset
    _dataset: SystemDataSet
    # Strategies
    _calcul: AbstractSystemCalcul

    @property
    def id(self):
        """Return the identity card of the system."""
        return self._id

    @property
    def calcul(self):
        """Return the current calculation strategy."""
        return self._calcul

    @calcul.setter
    def calcul(self, value: str):
        """
        Set the calculation strategy and reconfigure the system dataset
        accordingly.
        """
        self._calcul = EnumSystemCalcul(value).build_strategy()
        log.verbose(f"Set system calcul strategy to '{value}'")
        self._id.strategy = value
        self.dataset.set_config(
            name="system_calcul_strategy",
            value=value,
            tune_dataset=True,
        )

    @property
    def dataset(self) -> SystemDataSet:
        return self._dataset

    @dataset.setter
    def dataset(self, value: SystemDataSet):
        self._dataset = value
        self._dataset.update_properties(class_=self.__class__)

    @property
    def regions(self):
        """
        Returns the regions detail levels from the dataset
        """
        return self._dataset.regions

    @property
    def sectors(self):
        """
        Returns the sectors detail levels from the dataset
        """
        return self._dataset.sectors

    @property
    def final_demand_categories(self):
        """
        Returns the final demand categories detail levels from the dataset
        """
        return self._dataset.final_demand_categories

    @property
    def detail_levels(self):
        """
        Returns complete system detail levels from the dataset
        """
        return {dl_.kind.value: dl_ for dl_ in self._dataset.detail_levels}

    def load_from_path(self, path: str):
        """
        Load the system w.r.t. the files found in path.

        If config.CHECK_INPUT_DATA_STRUCTURE is set to True, then the
        structure of the dataframes found in the files will be checked before
        loading them into the system.

        Parameters
        ----------
        path: str
            The path to the directory containing the system files
        """
        log.info(f"Load System from path {path}.")
        self.dataset.load_from_path(path=path)

    def save_to_path(
        self,
        path: str,
        export_format: str | list = cst.FORMAT_EXCEL,
    ):
        """
        Export the system to the specified path.

        Parameters
        ----------
        path : str
            The directory path where the export files will be generated.
        export_format : str | list, optional
            The format(s) of the exported file(s). Defaults to *excel*.
        """

        log.info(f"Save system with format(s) {export_format}.")
        os.makedirs(path, exist_ok=True)
        self.dataset.save_to_path(path=path, export_format=export_format)
        self.id.to_json_file(file_name=cst.FILE_INFO, folder_path=path)

    def reset_for_shock(self):
        """
        Reset the system in preparation for a shock.

        This method resets the system's state to ensure it is ready to
        accommodate a shock. The reset respects the calculation strategy
        and the list of shockable variables defined for the current system.

        Notes
        -----
        - This method must be called prior to applying any shock to guarantee
          accurate calculations.
        """
        log.info("Reset system for shock.")
        var_to_reset = [
            var_name
            for var_name in self.dataset.list_data()
            if var_name not in self.calcul.list_shockable_data()
        ]
        for var_name in var_to_reset:
            data_ = getattr(self.dataset, var_name)
            if not data_.is_unit():
                data_.reset()

    def reset_fluxes(self):
        """
        Reset the system fluxes and retain only coefficients.

        This method resets the flux-related variables (x, Z, Y & Y_k).
        """
        log.info("Reset system fluxes and retain only coefficients.")
        self.dataset.reset_fluxes()

    def reset_coefficients(self):
        """
        Reset the system coefficients and retain only fluxes.

        This method resets the coefficient-related variables (A, K, L, L_k).
        """
        log.info("Reset the system coefficients and retain only fluxes.")
        self.dataset.reset_coefficients()

    def calculate_from_leontief(self):
        """
        Calculate the system using the Leontief matrix and verify equilibrium.

        This method performs the calculations required to derive the system's
        state from the Leontief matrix. It ensures that the correct calculation
        strategy is applied by reconfiguring the system's data according to the
        selected strategy using the `tune_dataset` method.
        After performing the calculations, it verifies whether the system
        is equilibrated, ensuring consistency between supply and uses.

        The exact implementation of the calculations depends on the system
        calculation strategy.
        """
        log.info(
            f"Calculate system from Leontief matrix with "
            f"strategy '{self._calcul.name}'"
        )
        # self.dataset.tune()
        self._calcul.calculate_from_leontief(system_dataset=self.dataset)
        self.check_market_balance()

    def calculate_from_fluxes(self):
        """
        Calculate the system from the fluxes and verify equilibrium.

        This method derives the system's state using the provided flux data
        (x, Y, Y_k & Z). It ensures that the correct calculation strategy is
        applied by reconfiguring the system's data according to the selected
        strategy using the `tune_dataset` method. Afterward,
        it verifies whether the system is balanced, ensuring consistency
        between supply and uses.
        """
        log.info(
            f"Calculate system from fluxes x, Y and Z with "
            f"strategy '{self._calcul.name}'"
        )
        # self.dataset.tune()
        self._calcul.calculate_from_fluxes(system_dataset=self.dataset)
        self.check_market_balance()

    def calculate(self):
        """
        Calculate the missing components of the system.

        Preferred Method:
        The primary approach is to compute the system using the "Leontief
        matrix", derived from the technical coefficients and the final demand.
        Both must not be empty. All other variables will be overwritten.

        Alternative Method:
        If the primary approach is not feasible, the system is computed from
        the fluxes. In this case, both the final demand and the inter-industry
        matrix must not be empty. All other variables will be overwritten.

        Raises
        ------
        MENotEnoughData
            If there is insufficient data to execute either of the methods.

        Notes
        -----
        - This method automatically selects the appropriate approach based on
          the availability of data.
        """
        if self.calcul.is_calculable_from_leontief(
            system_dataset=self.dataset
        ):
            self.calculate_from_leontief()
        elif self.calcul.is_calculable_from_fluxes(
            system_dataset=self.dataset
        ):
            self.calculate_from_fluxes()
        else:
            raise MENotEnoughData(self.calcul.list_shockable_data())

    def is_standard(self):
        """
        Check if the current system calculation strategy is `Standard`.

        Returns:
            bool : True if the current strategy is `Standard`, False otherwise.
        """
        # pylint: disable=C0123
        # Necessary use of type() here instead of isinstance()
        return type(self._calcul) is Standard
        # pylint: enable=C0123

    def is_exo_invest_matrix(self):
        """
        Check if the current system calculation strategy is `ExoInvestMatrix`.

        Returns:
            bool : True if the current strategy is `ExoInvestMatrix`,
                   False otherwise.
        """
        # pylint: disable=C0123
        # Necessary use of type() here instead of isinstance()
        return type(self._calcul) is ExoInvestMatrix
        # pylint: enable=C0123

    def is_endo_invest_matrix(self):
        """
        Check if the current system calculation strategy is `EndoInvestMatrix`.

        Returns:
            bool : True if the current strategy is `EndoInvestMatrix`,
                   False otherwise.
        """
        # pylint: disable=C0123
        # Necessary use of type() here instead of isinstance()
        return type(self._calcul) is EndoInvestMatrix
        # pylint: enable=C0123

    # ToDo: Block to be checked. ##############################################
    def shock(self, shock: SystemShock):
        """
        Apply a system shock to the system

        Operations performed:
            - Check the consistency of detail levels between the system
              and the system shock
            - Check the compatibility of the shock and the system strategy,
              display a warning if there is an inconsistency
            - Applies the shock data to the shockable data of the system

        Parameters:
            shock (SystemShock):
                the shock to apply
        """
        log.info("Shock System")

        self._dataset.check_detail_levels_consistency(other=shock.dataset)

        for shock_data_name in shock.dataset.list_data():
            if not self.calcul.is_shock_applicable(shock_data_name):
                log.warning(
                    f"{shock_data_name} is not applicable to a "
                    f"'{self._calcul.name}' system"
                )

        self.dataset.A.shock(shock_data=shock.dataset.dA)
        self.dataset.Y.shock(
            shock_data=shock.dataset.dY,
            system_calcul_strategy=self.calcul.name,
        )
        self.dataset.Z.shock(shock_data=shock.dataset.dZ)
        self.dataset.K.shock(shock_data=shock.dataset.dK)
        self.dataset.Y_k.shock(shock_data=shock.dataset.dY_k)

        self.dataset.Y.update_gfcf_from_yk(Y_k=self.dataset.Y_k)

        # Update identity fields
        self.id.proj_year = shock.id.proj_year
        self.id.scenario_name = shock.id.scenario_name

    def reset_for_hem(self, index_df: pd.DataFrame):
        """
        Reset the system in preparation for HEM analysis

        Parameters:
            index_df (pd.DataFrame):
                The dataframe representing the index of the rows to
                reset for HEM
        """
        log.info(
            "Reset system to apply the Hypothetical Extraction Method (HEM)"
        )
        self.dataset.A.set_domestic_values(0.0)
        self.dataset.Y.set_domestic_values(0.0)
        self.dataset.Y_k.set_domestic_values(0.0)
        self.dataset.K.set_domestic_values(0.0)

        self.dataset.x.reset()
        self.dataset.Z.reset()
        self.dataset.L.reset()
        self.dataset.L_k.reset()

    def aggregate(self, *bridges: bridge.Bridge):
        """
        Aggregate the system fluxes w.r.t. the bridges given as parameters.
        The other data index are updated and the values reset.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info(f"Aggregate system")
        with bridge_pool.pool.context():
            self.dataset.aggregate(*bridges)

    def disaggregate(self, *bridges: bridge.Bridge):
        """
        Disaggregate the system w.r.t. the bridges given as parameters.
        The other data index are updated and the values reset.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.error("The disaggregation of a system is not yet implemented")
        raise NotImplementedError

    def reformat(self, *bridges: bridge.Bridge):
        """
        Reformat the system data w.r.t. the bridges given as parameters.

        Parameters:
            *bridges (bridge.Bridge):
                The bridges between the detail levels
        """
        log.info(f"Reformat system")
        with bridge_pool.pool.context():
            self.dataset.reformat(*bridges)

    # ToDo: drop as not very usefull? + need to be generalized to each stategy.
    def subtract_fluxes(self, x: XData, Y: YData, Z: ZData):
        """
        Subtract x, Y, Z to this system

        Parameters:
            x (XData):
                The system flux x to subtract
            Y (YData):
                The system flux Y to subtract
            Z (ZData):
                The system flux Z to subtract
        """
        self.dataset.x.update_values(self.dataset.x.df - x.df)
        self.dataset.Y.update_values(self.dataset.Y.df - Y.df)
        self.dataset.Z.update_values(self.dataset.Z.df - Z.df)

    def equals(self, other: "System"):
        """
        Tell if this system equals other

        Returns True if the following attributes are identical:
            - _dataset
            - _calcul
        """
        log.info("Compare systems")
        is_dataset_equal = self.dataset.equals(other.dataset)
        is_strategy_equal = type(self.calcul) is type(other.calcul)
        if not is_strategy_equal:
            log.verbose(
                f"Systems have different strategies: "
                f"{type(self.calcul)} != {type(other.calcul)}"
            )

        are_equal = is_dataset_equal and is_strategy_equal

        if are_equal:
            log.info("Systems are equal")

        return are_equal

    def get_market_imbalance(self, tolerance: float = 1e-2) -> pd.Series:
        """
        Retrieve sectors where the market imbalance exceeds the given
        tolerance.

        This method calculates the deviation from market equilibrium for each
        sector and returns only the deviations that are greater than or equal
        to the specified tolerance.

        Parameters
        ----------
        tolerance : float, optional
            The maximum acceptable absolute deviation from equilibrium.
            Deviations greater than or equal to this value are considered
            imbalances.
            Default is 1e-2.

        Returns
        -------
        pd.Series
            A series containing the absolute deviations exceeding the specified
            tolerance, indexed by sector.

        Notes
        -----
        - This method uses the `calculate_market_equilibrium_deviation` method
          of the current strategy to compute the deviations.
        """

        deviations = self._calcul.calculate_market_equilibrium_deviation(
            system_dataset=self.dataset
        )
        return deviations.loc[abs(deviations) >= tolerance]

    def check_market_balance(self, tolerance: float = 1e-2):
        """
        Check if the system is balanced within the specified tolerance.

        This method verifies whether the deviations from market equilibrium are
        within the acceptable tolerance. If any deviation exceeds the specified
        tolerance, an error message is logged, and, depending on the
        configuration, the program execution may be halted.

        Parameters
        ----------
        tolerance : float, optional
            The maximum acceptable absolute deviation from equilibrium.
            Default is 1e-2.

        Notes
        -----
        - This method relies on `is_market_equilibrium_within_tolerance` from
          the current strategy to check overall balance.
        - If the system is not balanced, it logs the sectors with deviations
          exceeding the tolerance using `get_market_imbalance`.
        - The behavior when the system is unbalanced is controlled by the
          configuration constant `STOP_IF_SYSTEM_IS_NOT_BALANCED`. If set to
          True, the program will terminate upon detecting an imbalance.
        """

        is_balanced = self._calcul.is_market_equilibrium_within_tolerance(
            system_dataset=self.dataset,
            tolerance=tolerance,
        )

        if is_balanced:
            log.info(
                f"The system is balanced. Deviation is lower than {tolerance}"
            )
        else:
            log.error(
                f"The system is not balanced. Deviation is "
                f"higher than {tolerance} for the following sectors: "
            )
            log.error(str(self.get_market_imbalance(tolerance)))
            if config.STOP_IF_SYSTEM_IS_NOT_BALANCED:
                raise MESystemNotBalanced()

    def filter_near_zero_values(
        self, threshold: float = 10e-3, inplace: bool = False
    ):
        """
        Filter out near-zero values in the underlying dataset of this system:
            - Delegates the filtering to the associated dataset
            - Values below the threshold are removed
            - Operation can be applied in place or on a copy

        Parameters:
            threshold (float):
                Values with an absolute magnitude below this threshold are
                considered near zero
            inplace (bool):
                Whether to apply the filtering directly to this system or
                return a filtered copy

        Returns:
            System:
                A filtered system when ``inplace`` is False
        """

        result = self if inplace else self.copy()
        result.dataset.filter_near_zero_values(
            threshold=threshold,
            inplace=True,
        )

        if not inplace:
            return result

    def __sub__(self, other):
        """
        Compute the difference between two systems:
            - Only systems of the same type can be subtracted
            - Subtraction is delegated to the underlying datasets

        Parameters:
            other (System):
                The system to subtract from this one

        Returns:
            System:
                A new system containing the difference between both systems
        """

        log.info("Compute difference between systems")
        if isinstance(other, type(self)):
            result = self.copy()
            result.dataset = self.dataset - other.dataset
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __add__(self, other):
        """
        Compute the sum of two systems:
            - Only systems of the same type can be added
            - Addition is delegated to the underlying datasets

        Parameters:
            other (System):
                The system to add to this one

        Returns:
            System:
                A new system containing the sum of both systems
        """

        log.info("Compute sum of systems")
        if isinstance(other, type(self)):
            result = self.copy()
            result.dataset = self.dataset + other.dataset
            return result
        else:
            raise TypeError(
                f"Operand should be a {type(self)}, not a {type(other)}"
            )

    def __abs__(self):
        """
        Compute the absolute value of this system:
            - Absolute value is applied to the underlying dataset
            - Operation returns a new system

        Returns:
            System:
                A new system where the underlying dataset contains
                absolute values
        """

        log.info("Compute absolute value of system")
        result = self.copy()
        result.dataset = abs(self.dataset)
        return result
