"""
Overview
********
This module is the 'core' module of the 'accounts.system.dataset' package.
It defines the dataset of a system.

Contents
********
- Classes:
  - :class:`SystemDataSet`

"""

__all__ = ["SystemDataSet"]

from matmat.core.detail_level import core as dl
from matmat.core.dataset.core import AbstractMappedDataSet
from matmat.core.accounts.system.dataset import config
from matmat.core.accounts.system.data import factory
from matmat.core.accounts.system.data.core import (
    AData,
    LData,
    LKData,
    KData,
    NullSystemData,
    UnitSystemData,
    XData,
    YData,
    YKData,
    ZData,
)
from matmat.utils import constants as cst


class SystemDataSet(AbstractMappedDataSet):
    """
    Class representing a system data set

    Attributes
    ----------
        _x: XData
            The supply vector x
        _Y: YData
            The final demand matrix Y
        _Z: ZData
            The inter-industry matrix Z
        _A: AData
            The technical coefficients matrix A
        _L: LData
            The Leontief matrix L
        _Y_k: YKData | NullSystemData
            The investment matrix Y_k
        _K: KData | NullSystemData
            The capital coefficients matrix K
        _L_k: LKData | NullSystemData
            The augmented Leontief matrix with capital L_k
        _unit: UnitSystemData
            The unit vector
    """

    _x: XData
    _Y: YData
    _Z: ZData
    _A: AData
    _L: LData
    _Y_k: YKData | NullSystemData
    _K: KData | NullSystemData
    _L_k: LKData | NullSystemData
    _unit: UnitSystemData

    def __init__(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        # Parameters related to the configuration of the dataset
        config__system_calcul_strategy: str,
    ):
        super().__init__(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            conversions=config.SystemDataSetConversions(),
            # Dataset mapping
            map__system_calcul_strategy=config.DATASET_MAP_WRT_SYSTEM_CALCUL_STRATEGY,
            # Dataset configuration
            config__system_calcul_strategy=config__system_calcul_strategy,
        )

    @staticmethod
    def get_data_names():
        return cst.LIST_OF_SYSTEM_DATA

    def set_data(self, name: str):
        setattr(
            self,
            name,
            factory.make_data(
                name=name,
                regions=self.regions,
                sectors=self.sectors,
                final_demand_categories=self.final_demand_categories,
            ),
        )

    def set_null_data(self, name: str):
        setattr(self, name, NullSystemData())

    @property
    def A(self):
        """Return the technical coefficients matrix `A`."""
        return self._A

    @A.setter
    def A(self, value: AData):
        """Set the technical coefficients matrix `A`."""
        self._A = value

    @property
    def Z(self):
        """Return the inter-industry matrix `Z`."""
        return self._Z

    @Z.setter
    def Z(self, value: ZData):
        """Set the inter-industry matrix `Z`."""
        self._Z = value

    @property
    def x(self):
        """Return the supply vector `x`."""
        return self._x

    @x.setter
    def x(self, value: XData):
        """Set the supply vector `x`."""
        self._x = value

    @property
    def Y(self):
        return self._Y

    @Y.setter
    def Y(self, value: YData):
        """Return the final demand matrix `Y`."""
        self._Y = value

    @property
    def L(self):
        """Return the Leontief matrix `L`."""
        return self._L

    @L.setter
    def L(self, value: LData):
        """Set the Leontief matrix `L`."""
        self._L = value

    @property
    def K(self):
        """Return the capital coefficients matrix `K`."""
        return self._K

    @K.setter
    def K(self, value: KData | NullSystemData):
        """Set the capital coefficients matrix `K`."""
        self._K = value

    @property
    def L_k(self):
        """Return the augmented Leontief matrix with capital `L_k`."""
        return self._L_k

    @L_k.setter
    def L_k(self, value: LKData | NullSystemData):
        """Set the augmented Leontief matrix with capital `L_k`."""
        self._L_k = value

    @property
    def Y_k(self):
        """Return the investment matrix `Y_k`."""
        return self._Y_k

    @Y_k.setter
    def Y_k(self, value: YKData | NullSystemData):
        """Set the investment matrix `Y_k`."""
        self._Y_k = value

    @property
    def unit(self):
        """Return the unit vector."""
        return self._unit

    @unit.setter
    def unit(self, value: UnitSystemData):
        """Set the unit vector 'unit'."""
        self._unit = value
