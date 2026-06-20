"""
Overview
********
This module is the 'core' module of the 'shocks.system.dataset' package.
It defines the dataset of a system shock.

Contents
********
- Classes:
  - :class:`SystemShockDataSet`

"""

__all__ = ["SystemShockDataSet"]

from matmat.core.dataset.core import AbstractListedDataSet
from matmat.core.shocks.system.data import factory
from matmat.core.shocks.system.data.core import (
    AShockData,
    KShockData,
    NullSystemShockData,
    YShockData,
    YkShockData,
    ZShockData,
)
from matmat.utils import constants as cst


class SystemShockDataSet(AbstractListedDataSet):
    """
    Class representing a system shock data set

    Attributes
    ----------
        _dA : AShockData or NullSystemShockData
            The technical coefficients shock matrix
        _dK : YShockData or NullSystemShockData
            The capital coefficients shock matrix
        _dY : YShockData or NullSystemShockData
            The final demand shock matrix
        _dY_k : YkShockData or NullSystemShockData
            The investment shock matrix
        _dZ : ZShockData or NullSystemShockData
            The inter-industry shock matrix
    """

    _dA: AShockData | NullSystemShockData
    _dK: KShockData | NullSystemShockData
    _dY: YShockData | NullSystemShockData
    _dY_k: YkShockData | NullSystemShockData
    _dZ: ZShockData | NullSystemShockData

    @staticmethod
    def get_data_names():
        return cst.LIST_OF_SYSTEM_SHOCK_DATA

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
        setattr(self, name, NullSystemShockData())

    @property
    def dA(self) -> AShockData | NullSystemShockData:
        return self._dA

    @dA.setter
    def dA(self, value: AShockData | NullSystemShockData):
        self._dA = value

    @property
    def dY(self) -> YShockData | NullSystemShockData:
        return self._dY

    @dY.setter
    def dY(self, value: YShockData | NullSystemShockData):
        self._dY = value

    @property
    def dY_k(self) -> YkShockData | NullSystemShockData:
        return self._dY_k

    @dY_k.setter
    def dY_k(self, value: YkShockData | NullSystemShockData):
        self._dY_k = value

    @property
    def dK(self) -> KShockData | NullSystemShockData:
        return self._dK

    @dK.setter
    def dK(self, value: KShockData | NullSystemShockData):
        self._dK = value

    @property
    def dZ(self) -> ZShockData | NullSystemShockData:
        return self._dZ

    @dZ.setter
    def dZ(self, value: ZShockData | NullSystemShockData):
        self._dZ = value
