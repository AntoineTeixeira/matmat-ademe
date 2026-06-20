__all__ = ["ShockableMixin", "ManualParamMixin"]

import pandas as pd

from matmat.core.shocks.system.data.core import AbstractSystemShockData
from matmat.core.shocks.extension.data.core import AbstractExtensionShockData
from matmat.utils.errors import MEIncompatibleShock
from matmat.utils import logging as log, constants as cst


class ShockableMixin:
    """
    Mixin Shockable.
    Implements a method to apply a shock to a dataframe.

    Classes using this mixin shall have:
        - a getter 'name' returning a string
        - a getter 'df' returning a dataframe
        - a setter 'df' to set said dataframe
    """

    def shock(
        self, shock_data: AbstractSystemShockData | AbstractExtensionShockData
    ):
        """
        Apply a shock to the dataframe following the equation W = W0 * (1 + dW)

        Parameters:
            shock_data (pd.DataFrame):
                The shock dataframe. It shall have the same rows and columns
                of the data to shock, otherwise an exception is raised.
        Raises:
            MEIncompatibleShock
        """
        if not shock_data.is_null():
            log.verbose(f"Apply shock {shock_data.name} to data {self.name}")

            if not self.df.index.equals(shock_data.df.index):
                log.error(
                    f"Shock data {shock_data.name} rows index is different "
                    "from the rows index of the data to shock"
                )
                raise MEIncompatibleShock()
            if not self.df.columns.equals(shock_data.df.columns):
                log.error(
                    f"Shock data {shock_data.name} columns index is different "
                    "from the columns index of the data to shock"
                )
                raise MEIncompatibleShock()

            # Raise an error if a shock data is filled only with NaN
            if shock_data.is_df_empty():
                log.error(
                    f"Shock data {shock_data.name} contains only NaN. "
                    f"Remove it or valorize it."
                )
                raise MEIncompatibleShock()

            # Clean residual NaN before applying the shock to avoid
            # propagating NaN values
            shock_data.clean_residual_nan()
            self.df = self.df.mul(1 + shock_data.df)


class ManualParamMixin:
    """
    Mixin ManualParam.
    Defines methods to inject manual parametrization into a shock object.
    This mixin can be used with SystemShock and ExtensionShock.
    """

    def set_each_manual_param(self, manual_param: pd.Series):
        """
        For each line in the table manual_param, inject parametrization
        in the corresponding shock data.

        Parameters:
            manual_param (pd.Series):
                The series containing the values to inject.
                The series index shall have the levels:
                    - "variable"
                    - "row_region"
                    - "row_name"
                    - "row_level"
                    - "col_region"
                    - "col_name"
                    - "col_level"
        """
        # Dictionary matching shock data names with data names from the
        # input file (ex: A => dA, S_x => dS_x)
        matching_dict = {
            # System shock data
            cst.A: cst.D_A,
            cst.Y: cst.D_Y,
            cst.Y_K: cst.D_Y_K,
            cst.K: cst.D_K,
            cst.Z: cst.D_Z,
            # Extension shock data
            cst.S_X_DOM: cst.D_S_X_DOM,
            cst.S_Y: cst.D_S_Y,
            cst.S_Z: cst.D_S_Z,
            cst.M_ROW: cst.D_M_ROW,
        }
        for line in manual_param.index:
            index = pd.MultiIndex.from_tuples(
                [line], names=manual_param.index.names
            )
            data_name = index.get_level_values("variable")[0]
            try:
                current_data = getattr(self, matching_dict[data_name])
            except KeyError:
                log.error(
                    f"No shock data {data_name} in {self.__class__.__name__}. "
                    f"Go to next line."
                )
                break

            value: str = manual_param.loc[[line]].values[0]
            row_regions: list = index.get_level_values("row_region")[0].split(
                ","
            )
            row_level: str = index.get_level_values("row_level")[0]
            row_name: str = index.get_level_values("row_name")[0]
            col_regions: str = index.get_level_values("col_region")[0].split(
                ","
            )
            col_level: str = index.get_level_values("col_level")[0]
            col_name: str = index.get_level_values("col_name")[0]

            # Loop on row regions split by ','
            for row_region in row_regions:
                # Loop on column regions split by ','
                for col_region in col_regions:
                    current_data.set_manual_value(
                        value=value,
                        row=(
                            row_region.strip(),
                            row_level.strip(),
                            row_name.strip(),
                        ),
                        col=(
                            col_region.strip(),
                            col_level.strip(),
                            col_name.strip(),
                        ),
                    )
