"""
Presentation
************
This module contains the definition of the system data classes

Content
*******
- Classes:
    - :class:`AbstractSystemData`
    - :class:`NullSystemData`
    - :class:`AData`
    - :class:`KData`
    - :class:`LData`
    - :class:`LKData`
    - :class:`XData`
    - :class:`YData`
    - :class:`YKData`
    - :class:`ZData`
    - :class:`UnitSystemData`
"""

__all__ = [
    "AbstractSystemData",
    "NullSystemData",
    "AData",
    "KData",
    "LData",
    "LKData",
    "XData",
    "YData",
    "YKData",
    "ZData",
    "UnitSystemData",
]

import copy
from abc import ABC

import pandas as pd
import numpy as np
import pymrio

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.core.data.core import AbstractData
from matmat.core.data.strategies import nature, structure
from matmat.core.shocks.mixins import ShockableMixin
from matmat.core.accounts.system.data.identity import SystemDataIdentity
from matmat.core.shocks.system.data.core import AbstractSystemShockData
import matmat.utils.logging as log
import matmat.utils.constants as cst
from matmat.utils.errors import MENotEnoughData


# pylint: disable=C0103


class AbstractSystemData(AbstractData, ABC):
    """
    This abstract class represents a system data class. It defines a set of
    attributes and methods common to all its subclasses. Some of these
    methods are concrete, i.e. they have an implementation. Some of these
    methods are abstract, i.e. they do not have an implementation and shall
    be overridden by subclasses.

    For the structure of the system data, refer to the concrete data classes.

    Attributes:
        _id : SystemDataIdentity
            The identity card of the system data
    """

    _id: SystemDataIdentity

    def __init__(
        self,
        *,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
    ):
        # Build identity
        self._id = SystemDataIdentity()

        # Build nature
        self._build_nature()

        # Build structure
        self._build_structure(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
        )

        # Build dataframe
        self.build_df()

    def get_origin_description(self) -> str:
        return "from system"


# pylint: disable=W0107
# (pass statements have meaning here as the methods shall do nothing)
class NullSystemData(AbstractSystemData, ShockableMixin):
    """
    Null system data.
    This class overrides all methods to do nothing.
    """

    _NAME = cst.NULL

    _nature: nature.NatureNull
    _structure: structure.StructureNull

    def __init__(self):
        super().__init__(
            regions=dl.RegionsDL(),
            sectors=dl.SectorsDL(),
            final_demand_categories=dl.FinalDemandCategoriesDL(),
        )

    def get_nature_type(self, **kwargs) -> type:
        return nature.NatureNull

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureNull

    @staticmethod
    def is_null() -> bool:
        """
        Returns True as this is a null system data
        """
        return True

    def shock(self, *args, **kwargs):
        """
        Does nothing
        """
        pass

    def load_from_path(self, path: str, format_: str = None):
        """
        Does nothing
        """
        pass

    def reset(self):
        """
        Does nothing
        """
        pass

    def calculate(self, *args, **kwargs):
        """
        Does nothing
        """
        pass

    def calculate_domestic(self, *args, **kwargs):
        """
        Does nothing
        """
        pass

    def calculate_import(self, *args, **kwargs):
        """
        Does nothing
        """
        pass

    def aggregate(self, bridge_: bridge.Bridge, reset: bool):
        """
        Does nothing
        """
        pass

    def disaggregate(self, bridge_: bridge.Bridge, reset: bool):
        """
        Does nothing
        """
        pass

    def save_to_path(
        self,
        path: str,
        export_format: str = cst.FORMAT_EXCEL,
    ):
        """
        Does nothing
        """
        pass


# pylint: enable=W0107
class XData(AbstractSystemData):
    """
    Supply vector (x)

    Refer to :class:`structure.StructureX` for the format description.
    """

    _NAME = cst.X

    _nature: nature.Flux
    _structure: structure.StructureX

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureX

    def calculate_from_interindustry_matrix(self, Z: "ZData", Y: "YData"):
        """
        Calculate the supply vector from inter-industry and final demand
        matrices (x = Z + Y)

        Parameters:
            Z (ZData):
                the inter-industry data
            Y (YData):
                the final demand data
        """
        if not (Z.is_df_empty() or Y.is_df_empty()):
            log.verbose(
                f"Calculate production ({self.name}) "
                f"from {Z.name} and {Y.name}"
            )

            x_dom = pymrio.calc_x(
                Z=Z.get_domestic_origin(), Y=Y.get_domestic_origin()
            )
            self.set_domestic_values(x_dom.values)

            if self.structure.has_import_regions():
                x_imp = pymrio.calc_x(
                    Z=Z.get_import_origin(), Y=Y.get_import_origin()
                )
                self.set_import_values(x_imp.values)
        else:
            raise MENotEnoughData(list_of_data=[cst.Y, cst.Z], all_data=True)

    def calculate_from_leontief_matrix(self, L: "LData | LKData", Y: "YData"):
        """
        Calculate the production matrix from leontief and final demand
        matrices (x = L.Y)

        Parameters:
            L (LData):
                the leontief data
            Y (YData):
                the final demand data
        """
        if not (L.is_df_empty() or Y.is_df_empty()):
            log.verbose(
                f"Calculate production ({self.name}) from "
                f"{L.name} and {Y.name}"
            )

            x_dom = pymrio.calc_x_from_L(
                L=L.get_domestic_origin(),
                y=Y.get_domestic_origin().sum(axis=1),
            )
            self.set_domestic_values(x_dom.values)

            if self.structure.has_import_regions():
                self.set_import_values(0.0)
        else:
            raise MENotEnoughData(list_of_data=[cst.Y, cst.L], all_data=True)


class YData(AbstractSystemData, ShockableMixin):
    """
    Final demand matrix (Y).
    This data can be shocked.

    Refer to :class:`structure.StructureY` for the format description.
    """

    _NAME = cst.Y

    _nature: nature.Flux
    _structure: structure.StructureY

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureY

    def set_exports_to_zero(self):
        """
        Sets all export values in the dataframe to zero.

        This method identifies the columns related to export values
        in the dataframe and sets their values to 0.0.
        """
        log.verbose(f"Set all export values in {self.name} to 0.0")
        mask = (
            self.df.columns.get_level_values(
                self.structure.final_demand_categories.get_main_level_name()
            )
            == cst.IDX_EXPORTS
        )
        self.df.loc[:, mask] = 0.0

    def set_export_values(self, values: np.ndarray):
        """
        Set the values of the exports part of Y.

        Parameters:
            values (np.ndarray):
                - A numpy array is provided, its values are assigned to the exports.
        """
        mask = (
            self.df.columns.get_level_values(
                self.structure.final_demand_categories.get_main_level_name()
            )
            == cst.IDX_EXPORTS
        )
        self.df.loc[:, mask] = values

    # ToDo: update because this is confusing due to "column".
    def get_gfcf_column(self) -> pd.DataFrame | None:
        """
        Returns the investment column(s) of the final demand matrix if
        they exist, None otherwise.
        """
        try:
            return self.df.xs(
                key=cst.IDX_INVESTMENT,
                axis=1,
                level=self.final_demand_categories.get_main_level_name(),
                drop_level=False,
            )
        except KeyError:
            log.verbose("No GFCF column(s) in Y data. Passing...")
            return None

    def get_exports(self) -> pd.DataFrame | None:
        try:
            return self.df.xs(
                key=cst.IDX_EXPORTS,
                axis=1,
                level=self.final_demand_categories.get_main_level_name(),
                drop_level=False,
            )
        except KeyError:
            log.verbose("No exports column(s) in Y data. Passing...")
            return None

    def get_domestic_exports(self) -> pd.DataFrame | None:
        try:
            return self.get_domestic_origin().xs(
                key=cst.IDX_EXPORTS,
                axis=1,
                level=self.final_demand_categories.get_main_level_name(),
                drop_level=False,
            )
        except KeyError:
            log.verbose("No exports column(s) in Y data. Passing...")
            return None

    def get_import_exports(self) -> pd.DataFrame | None:
        try:
            return self.get_import_origin().xs(
                key=cst.IDX_EXPORTS,
                axis=1,
                level=self.final_demand_categories.get_main_level_name(),
                drop_level=False,
            )
        except KeyError:
            log.verbose("No exports column(s) in Y data. Passing...")
            return None

    def has_gfcf(self) -> bool:
        """
        Returns True if this data has GFCF column(s),
        False otherwise.
        """
        return self.get_gfcf_column() is not None

    def drop_gfcf(self, inplace: bool):
        """
        If inplace is True, drop GFCF column(s) from this data, else returns
        a copy of this data without GFCF column(s)

        Notes
        -----
        The reference columns index (df_columns) is not updated which means
        calling the method reset() will retrieve the GFCF column(s)
        """
        if inplace:
            self.df.drop(
                cst.IDX_INVESTMENT,
                axis=1,
                level=self.final_demand_categories.get_level_names()[0],
                inplace=True,
            )
        else:
            y_wo_gfcf = copy.deepcopy(self)
            y_wo_gfcf.drop_gfcf(inplace=True)
            return y_wo_gfcf

    def set_gfcf(self, gfcf: pd.DataFrame):
        """
        Update the values of the investment column(s) of
        the final demand matrix

        Parameters:
            gfcf (pd.DataFrame):
                the dataframe containing the new values
        """
        self.df.update(gfcf)

    def shock(
        self,
        shock_data: AbstractSystemShockData,
        system_calcul_strategy: str = None,
    ):
        """
        Shock the final demand data, w.r.t. the system calculation strategy:
            - if standard, then dY is applied normally
            - else the investment part of Y is not modified

        Notes:
            - If system_calcul_strategy is None, then dY is applied normally
            - A warning is displayed if applying a shock with the investment
              part not null on a non-standard system, but the investment part
              of Y stays unchanged.

        Parameters:
            shock_data (AbstractSystemShockData):
                the final demand shock data (i.e. the variation to apply)
            system_calcul_strategy (str):
                the system calculation strategy, used to know how to deal
                with investment-related column(s).
                Default to None.
        """
        if not shock_data.is_null():

            if system_calcul_strategy is None:
                super().shock(shock_data=shock_data)

            elif system_calcul_strategy == cst.STRATEGY_STANDARD:
                super().shock(shock_data=shock_data)

            else:
                # Check investment part of dY
                try:
                    dy_gfcf = shock_data.df.xs(
                        key=cst.IDX_INVESTMENT,
                        axis=1,
                        level=1,
                        drop_level=False,
                    )
                    if not dy_gfcf.isna().all().all():
                        log.warning(
                            f"Investment part of {shock_data.name} should "
                            "be null when shocking a "
                            f"'{system_calcul_strategy}' "
                            f"system. It will be ignored."
                        )
                except KeyError:
                    log.verbose(
                        f"No investment part in {shock_data.name} data. "
                        "Passing..."
                    )

                # Save investment part to be re-injected
                gfcf_columns = self.get_gfcf_column()
                # Shock Y
                super().shock(shock_data=shock_data)
                # Re-inject previous investment part
                if gfcf_columns is not None:
                    self.set_gfcf(gfcf_columns)

    def update_gfcf_from_yk(self, Y_k: "YKData"):
        """
        For each region, sum the columns of Y_k and update the corresponding
        investment column in the final demand matrix

        Parameters:
            Y_k (YKData or NullSystemData):
                the investment data
        """
        if not Y_k.is_null():
            # TODO: check in case of multi-regions how to sum
            #       - sum without considering regions on rows
            #       - also consider region on rows
            gfcf_columns = (
                Y_k.df.T.groupby(
                    level=self.regions.get_region_levels(), sort=False
                )
                .sum()
                .T
            )

            gfcf_columns.columns = pd.MultiIndex.from_tuples(
                [
                    (
                        *((col,) if isinstance(col, str) else col),
                        *((extra,) if isinstance(extra, str) else extra),
                    )
                    for col in gfcf_columns.columns
                    for extra in self.get_gfcf_column()
                    .columns.droplevel(self.regions.get_region_levels())
                    .unique()
                    .to_list()
                ],
                names=self.regions.get_region_levels()
                + self.final_demand_categories.get_level_names(),
            )
            self.set_gfcf(gfcf_columns)


class ZData(AbstractSystemData, ShockableMixin):
    """
    Inter-industry matrix (Z).
    This data can be shocked.

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.Z

    _nature: nature.Flux
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, A: "AData", x: XData):
        """
        Calculate inter-industry matrix (Z = A * x_dom)

        Parameters:
            A (AData):
                the technical coefficients data
            x (XData):
                the production data
        """
        log.verbose(
            f"Calculate inter-industry matrix ({self.name}) "
            f"from {A.name} and {x.name} (dom)"
        )

        self._df = pymrio.calc_Z(A=A.df, x=x.get_domestic_origin())


class AData(AbstractSystemData, ShockableMixin):
    """
    Technical coefficients matrix (A).
    This data can be shocked.

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.A

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, Z: ZData, x: XData):
        """
        Calculate the technical coefficients matrix (A = Z / x_dom)

        Parameters:
            Z (ZData):
                the inter-industry data
            x (XData):
                the production data
        """
        log.verbose(
            f"Calculate technical coefficients ({self.name}) "
            f"from {Z.name} and {x.name} (dom)"
        )

        self._df = pymrio.calc_A(Z=Z.df, x=x.get_domestic_origin())


class KData(AbstractSystemData, ShockableMixin):
    """
    Capital coefficients matrix (K).
    This data can be shocked.

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.K

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, Y_k: "YKData", x: XData):
        """
        Calculate the capital coefficients matrix (K = Y_k / x_dom)

        Parameters:
            Y_k (YKData):
                the investment matrix
            x (XData):
                the production matrix
        """
        log.verbose(
            f"Calculate capital coefficients ({self.name}) "
            f"from {Y_k.name} and {x.name} (dom)"
        )

        self._df = pymrio.calc_A(Z=Y_k.df, x=x.get_domestic_origin())


class LData(AbstractSystemData):
    """
    Leontief matrix (L)

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.L

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, A: AData):
        """
        Calculate the leontief matrix:
            - L_dom = inv(I - A_dom)
            - L_imp = 0.0

        Parameters:
            A (AData):
                the technical coefficients data
        """
        log.verbose(
            f"Calculate domestic part of leontief matrix ({self.name})"
            f" from {A.name} (dom)"
        )

        L_dom = pymrio.calc_L(A.get_domestic_origin())
        self.set_domestic_values(L_dom.values)

        if self.structure.has_import_regions():
            log.verbose(
                f"Set import part of leontief matrix ({self.name}) to 0.0"
            )
            self.set_import_values(0.0)


class LKData(AbstractSystemData):
    """
    Augmented leontief matrix (L_k)

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.L_K

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, A: AData, K: KData):
        """
        Calculate the augmented leontief matrix:
            - L_k_dom = inv(I - (A_dom + K_dom))
            - L_k_imp = 0.0

        Parameters:
            A (AData):
                the technical coefficients data
            K (KData):
                the capital coefficients data
        """
        log.verbose(
            f"Calculate domestic part of augmented leontief matrix "
            f"({self.name}) from {A.name} (dom) and {K.name} (dom)"
        )

        L_k_dom = pymrio.calc_L(
            A.get_domestic_origin() + K.get_domestic_origin()
        )
        self.set_domestic_values(L_k_dom.values)

        if self.structure.has_import_regions():
            log.verbose(
                f"Set import part of augmented leontief matrix "
                f"({self.name}) to 0.0"
            )
            self.set_import_values(0.0)


class YKData(AbstractSystemData, ShockableMixin):
    """
    Investment matrix (Y_k).
    This data can be shocked.

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.Y_K

    _nature: nature.Flux
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, K: KData, x: XData):
        """
        Calculate the investment matrix (Y_k = K * x_dom)

        Parameters:
            K (KData):
                the capital coefficients data
            x (XData):
                the production data
        """
        log.verbose(
            f"Calculate investment matrix {self.name} "
            f"from {K.name} and {x.name} (dom)"
        )

        yk_df = K.df.mul(x.get_domestic_origin().squeeze())
        self.set_values(yk_df.values)


class UnitSystemData(AbstractSystemData):
    """
    Unit matrix for system data

    Refer to :class:`structure.StructureUnitBySector` for the format description.
    """

    _TYPE = cst.DTYPE_STRING
    _NAME = cst.UNIT

    _nature: nature.Unit
    _structure: structure.StructureUnitBySector

    def get_nature_type(self, **kwargs) -> type:
        return nature.Unit

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureUnitBySector
