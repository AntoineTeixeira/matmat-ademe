"""
Presentation
************
This module is the tools module of the package `shocks`.
It defines useful methods to work with accounts shocks.

This module implements a design pattern **builder** to manage instantiation
of system shock objects.

Content
*******
- Functions:
    - :meth:`compute_shock_data`
"""

__all__ = ["compute_shock_data"]

from matmat.core.accounts.system.data.core import AbstractSystemData
from matmat.core.accounts.extension.data.core import AbstractExtensionData
from matmat.core.shocks.system.data.core import AbstractSystemShockData
from matmat.core.shocks.extension.data.core import AbstractExtensionShockData
from matmat.utils import logging as log


def compute_shock_data(
    shock_data: AbstractSystemShockData | AbstractExtensionShockData,
    accounts_data_from: AbstractSystemData | AbstractExtensionData,
    accounts_data_to: AbstractSystemData | AbstractExtensionData,
):
    """
    Compute relative shocks between two accounts data.
    Results are written in place to ``shock_data.df``.

    The shock is computed element-wise as::

        shock = (to / from) - 1

    If the source value is zero, the shock is set to 0.0 to avoid division
    by zero.

    Parameters:
        shock_data (AbstractSystemShockData | AbstractExtensionShockData):
            Target object storing the computed shock values.
        accounts_data_from (AbstractSystemData | AbstractExtensionData):
            Source (baseline) accounting data.
        accounts_data_to (AbstractSystemData | AbstractExtensionData):
            Target accounting data.
    """
    log.verbose(
        f"Compute shock data '{shock_data.name}' from accounts "
        f"reference and projected data '{accounts_data_from.name}'"
    )
    for row in accounts_data_from.df.index:
        for column in accounts_data_from.df.columns:
            cell_from = accounts_data_from.df.loc[row, column]
            cell_to = accounts_data_to.df.loc[row, column]
            if cell_from == 0.0:
                cell_shock = 0.0
            else:
                cell_shock = cell_to / cell_from - 1.0
            shock_data.df.loc[row, column] = cell_shock
