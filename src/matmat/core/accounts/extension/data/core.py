"""
Presentation
************
This module contains the definition of the extensions data classes

Content
*******
- Classes:
    - :class:`AbstractExtensionData`
    - :class:`NullExtensionData`
    - :class:`SxDomData`
    - :class:`SyData`
    - :class:`SzData`
    - :class:`FxDomData`
    - :class:`FyData`
    - :class:`FzData`
    - :class:`MRoWData`
    - :class:`DImpData`
    - :class:`MData`
    - :class:`MKData`
    - :class:`DCbaData`
    - :class:`DCbaKData`
    - :class:`MappingData`
    - :class:`MappingKData`
    - :class:`UnitExtensionData`
"""

__all__ = [
    "AbstractExtensionData",
    "NullExtensionData",
    "SxDomData",
    "SyData",
    "SzData",
    "FxDomData",
    "FyData",
    "FzData",
    "MRoWData",
    "DImpData",
    "MData",
    "MKData",
    "DCbaData",
    "DCbaKData",
    "MappingData",
    "MappingKData",
    "UnitExtensionData",
]

import gc
from abc import ABC

import pandas as pd
import numpy as np

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
import matmat.core.accounts.system.data.core as system_data
from matmat.core.shocks.extension.data.core import AbstractExtensionShockData
from matmat.utils.errors import (
    MEIncorrectArguments,
    MEMissingInvestmentData,
)
from matmat.core.shocks.mixins import ShockableMixin
from matmat.core.accounts.extension.data.identity import ExtensionDataIdentity
from matmat.core.data.core import AbstractData
from matmat.core.data.strategies import nature, structure
from matmat.utils import logging as log, constants as cst, tools

# pylint: disable=C0103, R0902


class AbstractExtensionData(AbstractData, ABC):
    """
    This abstract class represents an extension data class. It defines a set
    of attributes and methods common to all its subclasses. Some of these
    methods are concrete, i.e. they have an implementation. Some of these
    methods are abstract, i.e. they do not have an implementation and shall
    be overridden by subclasses.

    For the structure of the system data, refer to the concrete data classes.

    Attributes:
        _id : ExtensionDataIdentity
            The identity card of the extension data
    """

    _id: ExtensionDataIdentity

    def __init__(
        self,
        *,
        extension_name: str,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        extension_categories: dl.ExtensionCategoriesDL,
        strategy: str = None,
    ):
        # Build identity
        self._id = ExtensionDataIdentity(extension_name=extension_name)

        # Build nature
        self._build_nature()

        # Build structure
        self._build_structure(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            extension_categories=extension_categories,
            strategy=strategy,
        )

        # Build dataframe
        self.build_df()

    def get_origin_description(self) -> str:
        return f"from extension '{self._id.extension_name}'"


# pylint: disable=W0107
# (pass statements have meaning here as the methods shall do nothing)
class NullExtensionData(AbstractExtensionData, ShockableMixin):
    """
    Null extension data.
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
            extension_name=cst.NULL,
            extension_categories=dl.ExtensionCategoriesDL(
                extension_name=cst.NULL
            ),
        )

    @staticmethod
    def is_null() -> bool:
        """
        Returns True as this is a null extension data
        """
        return True

    def get_nature_type(self, **kwargs) -> type:
        return nature.NatureNull

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureNull

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


class SxDomData(AbstractExtensionData, ShockableMixin):
    """
    Domestic production coefficients matrix (S_x).

    This data is shockable.

    Refer to :class:`structure.StructureSx` for the format description.
    """

    _NAME = cst.S_X_DOM

    _nature: nature.Coefficient
    _structure: structure.StructureSx

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureSx

    def shock(self, shock_data: AbstractExtensionShockData):
        """
        Shock the production coefficients data with a specificity:
            - If shock_data has one row and S_x has more than one
              rows, then multiply each row by (1 + shock_data)
            - Otherwise call the parent method

        Parameters:
            shock_data (AbstractExtensionShockData):
                the production coefficients shock data (i.e. the
                variation to apply)
        """
        if not shock_data.is_null():
            if len(self.df.index) > 1 and len(shock_data.df.index) == 1:
                log.verbose(f"Apply shock to data {self.name}")
                self.df = self.df.mul(1 + shock_data.df.squeeze(), axis=1)
            else:
                super().shock(shock_data=shock_data)

    def calculate(self, F_x_dom: "FxDomData", x: system_data.XData):
        """
        Calculate the production coefficients (S_x_dom = F_x_dom / x_dom)

        Parameters:
            F_x_dom (FxDomData):
                The domestic production fluxes of the extension
            x (XData):
                The production data of the associated system
        """
        log.verbose(f"Calculate {self.name} from {F_x_dom.name} and {x.name}")
        self.update_values(
            F_x_dom.df.div(x.get_domestic_origin().squeeze(), axis=1)
        )
        tools.clean_dataframe(self.df)


class SyData(AbstractExtensionData, ShockableMixin):
    """
    Final demand coefficients matrix (S_Y).
    This data is shockable.

    Refer to :class:`structure.StructureY` for the format description.
    """

    _NAME = cst.S_Y

    _nature: nature.Coefficient
    _structure: structure.StructureY

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureY

    def get_gfcf_column(self) -> pd.DataFrame | pd.Series:
        """
        Returns the dataframe corresponding to the investment column(s) if
        it exists, otherwise returns a null Series.
        """
        try:
            return self.df.xs(
                key=cst.IDX_INVESTMENT, axis=1, level=1, drop_level=False
            )
        except KeyError:
            log.error(f"No column '{cst.IDX_INVESTMENT}' found in {self.name}")
            return pd.Series(
                index=self.df.index,
                data=0.0,
                dtype=cst.DTYPE_FLOAT,
            )

    def calculate(self, F_Y: "FyData", Y: system_data.YData):
        """
        Calculate the final demand coefficients (S_Y = F_Y / Y)

        Parameters:
            F_Y (FyData):
                The final demand fluxes of the extension
            Y (YData):
                The final demand data of the associated system
        """
        log.verbose(f"Calculate {self.name}")
        self._df = F_Y.df.div(Y.df)
        tools.clean_dataframe(self.df)


class SzData(AbstractExtensionData, ShockableMixin):
    """
    Inter-industry coefficients matrix (S_Z).
    This data is shockable.

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.S_Z

    _nature: nature.Coefficient
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, F_Z: "FzData", Z: system_data.ZData):
        """
        Calculate the inter-industry coefficients (S_Z = F_Z / Z)

        Parameters:
            F_Z (FzData):
                The inter-industry fluxes of the extension
            Z (ZData):
                The inter-industry data of the associated system
        """
        log.verbose(f"Calculate {self.name}")
        self._df = F_Z.df.div(Z.df)
        tools.clean_dataframe(self.df)


class FxDomData(AbstractExtensionData):
    """
    Domestic production fluxes matrix (F_x).

    Refer to :class:`structure.StructureSx` for the format description.
    """

    _NAME = cst.F_X_DOM

    _nature: nature.Flux
    _structure: structure.StructureSx

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureSx

    def calculate(self, S_x_dom: "SxDomData", x: system_data.XData):
        log.verbose(f"Calculate {self.name} from {S_x_dom.name} and {x.name}")
        self.update_values(
            S_x_dom.df.mul(x.get_domestic_origin().squeeze(), axis=1)
        )


class FyData(AbstractExtensionData):
    """
    Final demand fluxes matrix (F_Y)

    Refer to :class:`structure.StructureY` for the format description.
    """

    _NAME = cst.F_Y

    _nature: nature.Flux
    _structure: structure.StructureY

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureY

    def calculate(self, S_Y: SyData, Y: system_data.YData):
        """
        Calculate the final demand fluxes from coefficients (F_Y = S_Y * Y)

        Parameters:
            S_Y (SyData):
                The final demand coefficients
            Y (YData):
                The final demand data of the associated system
        """
        log.verbose(f"Calculate {self.name}")
        if not S_Y.df.columns.equals(Y.df.columns):
            log.warning(
                "S_Y and Y have different columns index. "
                "Computation of F_Y might be incorrect"
            )
        self._df = S_Y.df.mul(Y.df)


class FzData(AbstractExtensionData):
    """
    Inter-industry fluxes matrix (F_Z)

    Refer to :class:`structure.StructureZ` for the format description.
    """

    _NAME = cst.F_Z

    _nature: nature.Flux
    _structure: structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureZ

    def calculate(self, S_Z: SzData, Z: system_data.ZData):
        """
        Calculate inter-industry fluxes from coefficients (F_Z = S_Z * Z)

        Parameters:
            S_Z (SzData):
                The inter-industry coefficients
            Z (ZData):
                The inter-industry data of the associated system
        """
        log.verbose(f"Calculate {self.name}")
        self._df = S_Z.df.mul(Z.df)


class MRoWData(AbstractExtensionData, ShockableMixin):
    """
    Multiplier for the Rest Of The World.

    This data is shockable.

    Refer to :class:`structure.StructureSx` for the format description.
    """

    _NAME = cst.M_ROW

    _nature: nature.Coefficient
    _structure: structure.StructureMRoW

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureMRoW

    def calculate(self, d_imp: "DImpData", x: system_data.XData):
        """
        Calculate M_RoW from d_imp and x (M_RoW = d_imp / x_imp)

        Parameters:
            d_imp (DImpData):
                TODO: complete doc
            x (XData):
                The production vector of the associated system
        """
        log.verbose(f"Calculate {self.name}")
        self._df = d_imp.df.div(x.get_import_origin().squeeze())
        tools.clean_dataframe(self.df)

    def update_imports_from_world(
        self, d_cba_world: "DCbaData", x_domestic: system_data.XData
    ):
        """
        Update the import part of the production coefficients from
        world accounts

        Parameters:
            d_cba_world (DCbaData):
                The consumption based accounts from which to calibrate S_x from
            x_domestic (XData):
                The production data from the associated domestic system
        """
        log.warning(
            f"TODO: Implement update of {self.name} through a "
            f"shock d{self.name}"
        )

        d_imp = d_cba_world.get_domestic_exports().droplevel(
            level=self.final_demand_categories.get_level_names(), axis=1
        )

        # If import part of d_cba from the world extension is aggregated
        # (i.e. has only one row, no sectors) whereas M_RoW is
        # disaggregated, then we need to diagonalize the d_cba_imp
        if len(d_imp.index) == 1 and len(d_imp.index) != len(self.df.index):
            log.verbose(
                f"d_cba from world extension '{self.id.extension_name}'"
                f" needs to be diagonalized"
            )
            if (
                len(self.regions.get_domestic_regions_list()) > 1
                or len(self.regions.get_import_regions_list()) > 1
            ):
                log.error(
                    "Diagonalization of d_cba not implemented "
                    "for multi-regions"
                )
                raise NotImplementedError
            d_imp_diag = pd.DataFrame(np.diag(d_imp.iloc[0]))
            d_imp_diag.index = self.df.index
            d_imp_diag.columns = d_imp.columns
            d_imp = d_imp_diag

        imports = x_domestic.get_import_origin().squeeze()
        m_row = d_imp.divide(imports, axis=1)
        tools.clean_dataframe(m_row)
        self.set_values(m_row.values)


class DImpData(AbstractExtensionData):
    """
    TODO: to be completed
    """

    _TYPE = cst.DTYPE_FLOAT
    _NAME = cst.D_IMP

    _nature = nature.Flux
    _structure = structure.StructureMRoW

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        return structure.StructureMRoW

    def calculate(self, M_RoW: "MRoWData", x: system_data.XData):
        """
        Calculate d_imp from M_RoW and x (d_imp = M_RoW * x_imp)

        Parameters:
            M_RoW (MRoWData):
                The multiplier of the rest of the world
            x (XData):
                The production vector of the associated system
        """
        log.verbose(f"Calculate {self.name}")
        self._df = M_RoW.df.mul(x.get_import_origin().squeeze())


class MData(AbstractExtensionData):
    """
    Multiplier matrix (M)

    The structure of this data is variable. Depending on the extension
    calcul strategy, it may be
    :class:`structure.StructureSx` or :class:`structure.StructureZ`. Refer
    to these classes for the format description.
    """

    _NAME = cst.M

    _nature: nature.Coefficient
    _structure: structure.StructureSx | structure.StructureZ

    def get_nature_type(self, **kwargs) -> type:
        return nature.Coefficient

    def get_structure_type(self, **kwargs) -> type:
        """
        Determine the structure based on 'strategy' in kwargs

        Returns:
            StructureSx if 'strategy' is cst.STRATEGY_GROSS_OUTPUT_BASED
            or cst.STRATEGY_EMBODIED_IN_IMPORT

            StructureZ if 'strategy' is cst.STRATEGY_USE_BASED

            StructureZ otherwise
        """
        strategy = kwargs.get("strategy")

        match strategy:
            case (
                cst.STRATEGY_GROSS_OUTPUT_BASED
                | cst.STRATEGY_EMBODIED_IN_IMPORT
            ):
                return structure.StructureSx
            case cst.STRATEGY_USE_BASED:
                return structure.StructureZ
            case _:
                return structure.StructureZ

    def calculate(self, **kwargs):
        """
        Calculate multiplier matrix.

        Case 1 - from F_Z, x, and L:
            M = (F_Z / x_dom).L_dom

        Case 2 - from S_x_dom and L:
            M = S_x_dom.L_dom

        Case 3 - from M_RoW, A and L:
            M = M_RoW.A_imp.L_dom

        Parameters:
            F_Z (FzData):
                The inter-industry flux matrix
            x (XData):
                The production vector of the associated system
            L (LData):
                The leontief matrix of the associated system
            S_x_dom (SxDomData):
                The domestic production coefficients matrix
            A (AData):
                The technical coefficients matrix of the associated system
            M_RoW (MRoWData):
                The multiplier of the rest of the world

        Raises:
            MEIncorrectArguments
                if the parameters given are incorrect
        """
        log.verbose(f"Calculate {self.name}")

        is_calcul_completed = False

        L = kwargs.get("L")

        if L is not None:
            if "F_Z" in kwargs.keys() and "x" in kwargs.keys():
                self._calculate_from_f_z_and_x(
                    L=L, F_Z=kwargs.get("F_Z"), x=kwargs.get("x")
                )
                is_calcul_completed = True

            elif "S_x_dom" in kwargs.keys():
                self._calculate_from_s_x_dom(
                    L=L, S_x_dom=kwargs.get("S_x_dom")
                )
                is_calcul_completed = True

            elif "M_RoW" in kwargs.keys() and "A" in kwargs.keys():
                self._calculate_from_m_row_and_a(
                    L=L, M_RoW=kwargs.get("M_RoW"), A=kwargs.get("A")
                )
                is_calcul_completed = True

        if not is_calcul_completed:
            raise MEIncorrectArguments(
                expected_args=[
                    ("L", "F_Z", "x"),
                    ("L", "S_x_dom"),
                    ("L", "M_RoW", "A"),
                ]
            )

    def _calculate_from_f_z_and_x(
        self, L: system_data.LData, F_Z: "FzData", x: system_data.XData
    ):
        log.verbose(
            f"Calculate {self.name} from {L.name}, {F_Z.name} and {x.name}"
        )

        s_z_x = F_Z.df.divide(x.get_domestic_origin().squeeze(), axis=1)
        tools.clean_dataframe(df=s_z_x)
        self._df = s_z_x.dot(L.get_domestic_origin())

    def _calculate_from_s_x_dom(
        self, L: system_data.LData, S_x_dom: SxDomData
    ):
        log.verbose(f"Calculate {self.name} from {L.name} and {S_x_dom.name}")
        self._df = S_x_dom.df.dot(L.get_domestic_origin())

    def _calculate_from_m_row_and_a(
        self,
        L: system_data.LData,
        M_RoW: MRoWData,
        A: system_data.AData,
    ):
        log.verbose(
            f"Calculate {self.name} from {L.name}, {M_RoW.name} and {A.name}"
        )

        self._df = M_RoW.df.dot(A.get_import_origin()).dot(
            L.get_domestic_origin()
        )


class MKData(MData):
    """
    Augmented multiplier matrix (M_k)

    For the format of the dataframe, refer to :class:`MData`
    """

    _NAME = cst.M_K

    def calculate(self, **kwargs):
        """
        Calculate augmented multiplier matrix.

        Case 1 - from F_Z, S_Y, Y_k, x, and L:
            M_k = ((F_Z + Y_k * S_Y_GFCF) / x_dom).L_dom

        Case 2 - from M_RoW, A, K, and L:
            M_k = M_RoW.(A_imp + K_imp).L_dom

        For other cases, refer to method 'calculate' of :class:`MData`

        Parameters:
            F_Z (FzData):
                The inter-industry flux matrix
            Y_k (YKData):
                The investment data of the associated system
            S_Y (SyData):
                The final demand coefficients matrix
            x (XData):
                The production vector of the associated system
            L (LData):
                The leontief matrix of the associated system
            S_x_dom (SxDomData):
                The domestic production coefficients matrix
            A (AData):
                The technical coefficients matrix of the associated system
            K (KData):
                The capital coefficients matrix of the associated system
            M_RoW (MRoWData):
                The multiplier of the rest of the world

        Raises:
            MEIncorrectArguments
                if the parameters given are incorrect
        """
        log.verbose(f"Calculate {self.name}")

        is_calcul_completed = False

        L = kwargs.get("L")

        if L is not None:

            if (
                "F_Z" in kwargs.keys()
                and "Y_k" in kwargs.keys()
                and "S_Y" in kwargs.keys()
                and "x" in kwargs.keys()
            ):
                self._calculate_from_f_z_and_s_y_and_y_k_and_x(
                    L_k=L,
                    F_Z=kwargs.get("F_Z"),
                    Y_k=kwargs.get("Y_k"),
                    S_Y=kwargs.get("S_Y"),
                    x=kwargs.get("x"),
                )
                is_calcul_completed = True

            elif (
                "M_RoW" in kwargs.keys()
                and "A" in kwargs.keys()
                and "K" in kwargs.keys()
            ):
                self._calculate_from_m_row_and_a_and_k(
                    L_k=L,
                    M_RoW=kwargs.get("M_RoW"),
                    A=kwargs.get("A"),
                    K=kwargs.get("K"),
                )
                is_calcul_completed = True

        if not is_calcul_completed:
            super().calculate(**kwargs)

    def _calculate_from_f_z_and_s_y_and_y_k_and_x(
        self,
        L_k: system_data.LKData,
        F_Z: FzData,
        Y_k: system_data.YKData,
        S_Y: SyData,
        x: system_data.XData,
    ):
        log.verbose(
            f"Calculate {self.name} from {L_k.name}, {F_Z.name}, {x.name}, "
            f"{Y_k.name} and {S_Y.name}"
        )

        investment_contrib = Y_k.df.mul(
            S_Y.get_gfcf_column().squeeze(), axis=0
        )
        s_z_x_k = (F_Z.df + investment_contrib).divide(
            x.get_domestic_origin().squeeze(), axis=1
        )
        tools.clean_dataframe(df=s_z_x_k)
        self._df = s_z_x_k.dot(L_k.get_domestic_origin())

    def _calculate_from_m_row_and_a_and_k(
        self,
        L_k: system_data.LKData,
        M_RoW: MRoWData,
        A: system_data.AData,
        K: system_data.KData,
    ):
        a_augmented: pd.DataFrame = (
            A.get_import_origin() + K.get_import_origin()
        )
        self._df = M_RoW.df.dot(a_augmented).dot(L_k.get_domestic_origin())


class DCbaData(AbstractExtensionData):
    """
    Consumption based accounts matrix (d_cba)

    The structure of this data is variable. Depending on the extension
    calcul strategy, it may be
    :class:`structure.StructureDCbaBySector`
    or :class:`structure.StructureDCbaByExtensionCategory`. Refer
    to these classes for the format description.
    """

    _NAME = cst.D_CBA
    _IS_LAZY = True

    _nature: nature.Flux
    _structure: (
        structure.StructureDCbaBySector
        | structure.StructureDCbaByExtensionCategory
    )

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        """
        Determines and returns the type of structure for the d_cba matrix
        based on the given strategy.

        Strategy-based logic:
            - If the strategy is `cst.STRATEGY_USE_BASED`,
              the structure is of type `StructureDCbaBySector`.
            - If the strategy is `cst.STRATEGY_GROSS_OUTPUT_BASED`,
              the structure is of type `StructureDCbaByExtensionCategory`.`.
            - If the strategy is `cst.STRATEGY_EMBODIED_IN_IMPORT`,
              the structure is of type `StructureDCbaByExtensionCategory`.`.
            - For any other value of "strategy," defaults to `StructureDCbaBySector`.

        Parameters:
            **kwargs:
                Keyword arguments. It must include:
                - "strategy" (str): A string representing the calculation strategy.

        Returns:
            type: The structure type corresponding to the provided strategy.
        """
        strategy = kwargs.get("strategy")

        match strategy:
            case cst.STRATEGY_USE_BASED:
                return structure.StructureDCbaBySector
            case cst.STRATEGY_GROSS_OUTPUT_BASED:
                return structure.StructureDCbaByExtensionCategory
            case cst.STRATEGY_EMBODIED_IN_IMPORT:
                return structure.StructureDCbaByExtensionCategory
            case _:
                return structure.StructureDCbaBySector

    def get_domestic_exports(self) -> pd.DataFrame:
        """
        If there is an "origin" level, returns the exports column(s) of
        the domestic origin.

        Otherwise returns the exports column(s)
        """
        if cst.IDX_ORIGIN in self.df.index.names:
            return self.get_domestic_origin(keep_origin=True).xs(
                key=cst.IDX_EXPORTS, level=1, axis=1, drop_level=False
            )
        else:
            return self.df.xs(
                key=cst.IDX_EXPORTS, level=1, axis=1, drop_level=False
            )

    def calculate(self, **kwargs):
        """
        Calculate consumption based accounts matrix.

        Case 1 - from M, Y:
            d_cba = M.Y_diag_dom

        Case 2 - from M, Y and F_Y:
            d_cba = M.Y_diag_dom + F_Y_diag

        Case 3 - from M, Y and M_RoW:
            d_cba = M.Y_diag_dom + M_RoW.Y_diag_imp

        Parameters:
            M (MData):
                The multiplier
            Y (YData):
                The final demand data of the associated system
            F_Y (FyData):
                **OPTIONAL** The final demand fluxes
            M_RoW (MRoWData):
                **OPTIONAL** The multiplier of the rest of the world

        Raises:
            MEIncorrectArguments
                if the parameters given are incorrect
        """
        log.verbose(f"Calculate {self.name}")

        M = kwargs.get("M")
        Y = kwargs.get("Y")

        if M is not None and Y is not None:

            # Compute Y diag here to avoid doing it several times
            y_diag = self._diagonalize_y(y_data=Y)

            self._calculate_from_y(M=M, y_diag=y_diag)

            if "F_Y" in kwargs.keys():
                self._add_final_demand_contribution(F_Y=kwargs.get("F_Y"))

            elif "M_RoW" in kwargs.keys():
                self._add_row_contribution(
                    M_RoW=kwargs.get("M_RoW"), y_diag=y_diag
                )

        else:
            raise MEIncorrectArguments(
                expected_args=[
                    ("M", "Y"),
                    ("M", "Y", "F_Y"),
                    ("M", "Y", "M_RoW"),
                ]
            )

    def _calculate_from_y(self, M: MData, y_diag: pd.DataFrame):
        log.verbose(f"Calculate {self.name} from M and Y_diag")

        y_diag_dom = y_diag.loc[cst.IDX_DOMESTIC]
        self._df = M.df.dot(y_diag_dom)

    def _add_final_demand_contribution(self, F_Y: "FyData"):
        log.verbose(f"Add F_Y contribution to {self.name}")

        f_y_diag = self._diagonalize_y(y_data=F_Y)
        self.update_values(self.df + f_y_diag)

    def _add_row_contribution(self, M_RoW: "MRoWData", y_diag: pd.DataFrame):
        log.verbose(f"Add RoW contribution to {self.name}")

        y_diag_imp = y_diag.loc[cst.IDX_IMPORT]
        row_contrib = M_RoW.df.dot(y_diag_imp)
        self.update_values(self.df + row_contrib)

    def _diagonalize_y(
        self,
        y_data: system_data.YData | SyData | FyData,
    ) -> pd.DataFrame:
        return y_data.structure.diagonalize(df=y_data.df)


class DCbaKData(DCbaData):
    """
    Augmented consumption based accounts matrix (d_cba_k)

    The structure of this data is variable. Depending on the extension
    calcul strategy, it may be
    :class:`structure.StructureDCbaKBySector`
    or :class:`structure.StructureDCbaKByExtensionCategory`. Refer
    to these classes for the format description.
    """

    _NAME = cst.D_CBA_K
    _IS_LAZY = True

    _structure: (
        structure.StructureDCbaKBySector
        | structure.StructureDCbaKByExtensionCategory
    )

    def get_structure_type(self, **kwargs) -> type:
        """
        Determines and returns the type of structure for the d_cba_k matrix
        based on the given strategy.

        Strategy-based logic:
            - If the strategy is `cst.STRATEGY_USE_BASED`,
              the structure is of type `StructureDCbaKBySector`.
            - If the strategy is `cst.STRATEGY_GROSS_OUTPUT_BASED`,
              the structure is of type `StructureDCbaKByExtensionCategory`.`.
            - If the strategy is `cst.STRATEGY_EMBODIED_IN_IMPORT`,
              the structure is of type `StructureDCbaKByExtensionCategory`.`.
            - For any other value of "strategy," defaults to `StructureDCbaKBySector`.

        Parameters:
            **kwargs:
                A dictionary of keyword arguments. It must include:
                - "strategy" (str): A string representing the calculation strategy.

        Returns:
            type: The structure type corresponding to the provided strategy.
        """
        strategy = kwargs.get("strategy")

        match strategy:
            case cst.STRATEGY_USE_BASED:
                return structure.StructureDCbaKBySector
            case cst.STRATEGY_GROSS_OUTPUT_BASED:
                return structure.StructureDCbaKByExtensionCategory
            case cst.STRATEGY_EMBODIED_IN_IMPORT:
                return structure.StructureDCbaKByExtensionCategory
            case _:
                return structure.StructureDCbaKBySector

    def calculate(self, **kwargs):

        # Check that the calcul is relevant
        # If Y has no GFCF column(s), then d_cba_k should not be computed
        y: system_data.YData = kwargs.get("Y")
        if y and not y.has_gfcf():
            log.error(
                f"Data {y.name} has no GFCF column(s). "
                f"{self.name} should not be computed. "
                f"Consider switching to a standard system."
            )
            raise MEMissingInvestmentData(y.df.columns)

        # Call parent method
        super().calculate(**kwargs)

    def _diagonalize_y(
        self,
        y_data: system_data.YData | SyData | FyData,
    ) -> pd.DataFrame:
        y_diag = super()._diagonalize_y(y_data)
        try:
            return y_diag.drop(columns=[cst.IDX_INVESTMENT], level=1)
        except KeyError:
            log.error(f"No column '{cst.IDX_INVESTMENT}' found.")
            return y_diag


class MappingData(AbstractExtensionData):
    """
    Mapping matrix for extension data

    The structure of this data is variable. Depending on the extension
    calcul strategy, it may be
    :class:`structure.StructureDCbaBySector`
    or :class:`structure.StructureMappingDirect`
    or :class:`structure.StructureMappingIndirect`.
    Refer to these classes for the format description.
    """

    _TYPE = cst.DTYPE_FLOAT
    _NAME = cst.MAPPING
    _IS_LAZY = True

    _nature: nature.Flux
    _structure: (
        structure.StructureMappingDirect
        | structure.StructureMappingIndirect
        | structure.StructureDCbaBySector
    )

    def get_nature_type(self, **kwargs) -> type:
        return nature.Flux

    def get_structure_type(self, **kwargs) -> type:
        """
        Determines and returns the type of structure for the mapping matrix
        based on the given strategy.

        Strategy-based logic:
            - If the strategy is `cst.STRATEGY_USE_BASED`,
              the structure is of type `StructureDCbaBySector`.
            - If the strategy is `cst.STRATEGY_GROSS_OUTPUT_BASED`,
              the structure is of type `StructureMappingDirect`.
            - If the strategy is `cst.STRATEGY_EMBODIED_IN_IMPORT`,
              the structure is of type `StructureMappingIndirect`.`.
            - For any other value of "strategy," defaults to `StructureDCbaBySector`.

        Parameters:
            **kwargs:
                A dictionary of keyword arguments. It must include:
                - "strategy" (str): A string representing the calculation strategy.

        Returns:
            type: The structure type corresponding to the provided strategy.
        """
        strategy = kwargs.get("strategy")

        match strategy:
            case cst.STRATEGY_USE_BASED:
                return structure.StructureDCbaBySector
            case cst.STRATEGY_GROSS_OUTPUT_BASED:
                return structure.StructureMappingDirect
            case cst.STRATEGY_EMBODIED_IN_IMPORT:
                return structure.StructureMappingIndirect
            case _:
                return structure.StructureDCbaBySector

    def calculate(self, **kwargs):
        """
        Calculate mapping matrix.

        Case 1 - from S_x_dom, x, L, Z, Y:

        Case 2 - from M_RoW, x, L, Z, Y:

        Parameters:
            S_x_dom (SxDomData):
                The inter-industry flux matrix
            M_RoW (MRoWData):
                The multiplier of the rest of the world
            x (XData):
                The production vector of the associated system
            L (LData):
                The leontief matrix of the associated system
            Z (ZData):
                The inter-industry data of the associated system
            Y (YData):
                The final demand data of the associated system

        Raises:
            MEIncorrectArguments
                if the parameters given are incorrect
        """
        log.verbose(f"Calculate {self.name}")

        is_calcul_completed = False

        x = kwargs.get("x")
        L = kwargs.get("L")
        Z = kwargs.get("Z")
        Y = kwargs.get("Y")

        if x and L and Z and Y:
            if "S_x_dom" in kwargs.keys():
                self._calculate_from_s_x_dom(
                    S_x_dom=kwargs.get("S_x_dom"),
                    x=x,
                    L=L,
                    Z=Z,
                    Y=Y,
                )
                is_calcul_completed = True

            elif "M_RoW" in kwargs.keys():
                self._calculate_from_m_row(
                    M_RoW=kwargs.get("M_RoW"),
                    x=x,
                    L=L,
                    Z=Z,
                    Y=Y,
                )
                is_calcul_completed = True

        if not is_calcul_completed:
            raise MEIncorrectArguments(
                expected_args=[
                    ("S_x_dom", "x", "L", "Z", "Y"),
                    ("M_RoW", "x", "L", "Z", "Y"),
                ]
            )

    def _init_coeffs_and_fluxes(self) -> dict:
        """
        Initializes coefficients and fluxes for mapping computation
            - cst.S_Y: SyData data object
            - cst.S_Z: SzData data object
            - cst.F_Z: FzData data object
            - cst.F_Y: FyData data object

        This method is used to factorize the instantiation of these data
        objects.

        Returns:
            dict: Dictionary where keys are predefined data names and
                  values are the corresponding initialized data objects.
        """
        map_data = {}
        map_classes = {
            cst.S_Y: SyData,
            cst.S_Z: SzData,
            cst.F_Z: FzData,
            cst.F_Y: FyData,
        }
        for data_name, data_class in map_classes.items():
            map_data[data_name] = data_class(
                extension_name=self._id.extension_name,
                regions=self.regions,
                sectors=self.sectors,
                final_demand_categories=self.final_demand_categories,
                extension_categories=self.extension_categories,
                strategy=cst.STRATEGY_USE_BASED,
            )
        return map_data

    @staticmethod
    def _update_fluxes(
        Z: system_data.ZData,
        Y: system_data.YData,
        S_Z: SzData,
        S_Y: SyData,
        F_Z: FzData,
        F_Y: FyData,
    ):
        # Calculate F_Z
        F_Z.reset()
        F_Z.calculate(S_Z=S_Z, Z=Z)

        # Calculate F_Y
        F_Y.reset()
        F_Y.calculate(S_Y=S_Y, Y=Y)

    def _compute_multiplier(
        self,
        L: system_data.LData,
        x: system_data.XData,
        F_Z: FzData,
        Y_k: system_data.YKData = None,
    ) -> MData:
        m = MData(
            extension_name=self._id.extension_name,
            regions=self.regions,
            sectors=self.sectors,
            final_demand_categories=self.final_demand_categories,
            extension_categories=self.extension_categories,
            strategy=cst.STRATEGY_USE_BASED,
        )
        m.calculate(L=L, x=x, F_Z=F_Z)
        return m

    def _compute_d_cba(
        self,
        L: system_data.LData,
        x: system_data.XData,
        Y: system_data.YData,
        F_Z: FzData,
        F_Y: FyData,
        Y_k: system_data.YKData = None,
        S_Y: SyData = None,
    ) -> DCbaData:
        multiplier = MData(
            extension_name=self._id.extension_name,
            regions=self.regions,
            sectors=self.sectors,
            final_demand_categories=self.final_demand_categories,
            extension_categories=self.extension_categories,
            strategy=cst.STRATEGY_USE_BASED,
        )
        multiplier.calculate(L=L, x=x, F_Z=F_Z)
        d_cba = DCbaData(
            extension_name=self._id.extension_name,
            regions=self.regions,
            sectors=self.sectors,
            final_demand_categories=self.final_demand_categories,
            extension_categories=self.extension_categories,
            strategy=cst.STRATEGY_USE_BASED,
        )
        d_cba.calculate(
            M=multiplier,
            Y=Y,
            F_Y=F_Y,
        )
        return d_cba

    def _reorder_mapping_index(self, mapping: pd.DataFrame) -> pd.DataFrame:
        """
        Reorders the index of the given dataframe to put regions levels
        in first position.

        Parameters:
            mapping (pd.DataFrame):
                The DataFrame whose index needs to be reordered.

        Returns:
            pd.DataFrame : A DataFrame with its index levels reordered
        """
        # Get regions levels without the 'origin' level
        regions_levels = [
            l_ for l_ in self.regions.get_level_names() if l_ != cst.IDX_ORIGIN
        ]
        new_order = regions_levels + [
            l_ for l_ in self.df.index.names if l_ not in regions_levels
        ]
        return mapping.reorder_levels(new_order).sort_index(
            axis=0, level=regions_levels, sort_remaining=False
        )

    def _calculate_from_s_x_dom(
        self,
        S_x_dom: SxDomData,
        x: system_data.XData,
        L: system_data.LData,
        Z: system_data.ZData,
        Y: system_data.YData,
        Y_k: system_data.YKData = None,
    ):
        log.verbose(f"Calculate {self.name} from {S_x_dom.name}")

        # Loop on extension categories
        map_of_d_cba = {}
        for counter, idx_value in enumerate(S_x_dom.df.index):
            log.verbose(
                f"Step {counter + 1}/{len(S_x_dom.df.index)}: compute mapping for {idx_value}"
            )

            map_data = self._init_coeffs_and_fluxes()

            # Init S_Y and S_Z with S_x_dom values in domestic part
            # The rest is set to 0.0
            for data_ in map_data[cst.S_Y], map_data[cst.S_Z]:
                data_.set_values(0.0)
                data_.set_domestic_values(
                    np.tile(
                        S_x_dom.df.loc[[idx_value]].values.T,
                        data_.get_domestic_origin().shape[1],
                    )
                )
            # Compute d_cba and map add to the map
            self._update_fluxes(
                Z=Z,
                Y=Y,
                S_Z=map_data[cst.S_Z],
                S_Y=map_data[cst.S_Y],
                F_Z=map_data[cst.F_Z],
                F_Y=map_data[cst.F_Y],
            )
            map_of_d_cba[idx_value] = self._compute_d_cba(
                L=L,
                x=x,
                Y=Y,
                Y_k=Y_k,
                F_Y=map_data[cst.F_Y],
                F_Z=map_data[cst.F_Z],
                S_Y=map_data[cst.S_Y],
            )

        # Concatenate domestic parts of all d_cba
        log.verbose(f"Concatenate full {self.name}")
        mapping = pd.concat(
            {
                k: v.get_domestic_origin(keep_origin=False)
                for k, v in map_of_d_cba.items()
            },
            names=self.extension_categories.get_level_names(),
        )

        self.update_values(self._reorder_mapping_index(mapping=mapping))

        # Run garbage collector to free memory
        del map_data, map_of_d_cba, mapping
        gc.collect()

    def _calculate_from_m_row(
        self,
        M_RoW: MRoWData,
        x: system_data.XData,
        L: system_data.LData,
        Z: system_data.ZData,
        Y: system_data.YData,
        Y_k: system_data.YKData = None,
    ):
        log.verbose(f"Calculate {self.name} from {M_RoW.name}")

        map_data = self._init_coeffs_and_fluxes()

        # Loop on extension categories
        map_of_d_cba = {}
        for counter, idx_value in enumerate(M_RoW.df.index):
            log.verbose(
                f"Step {counter + 1}/{len(M_RoW.df.index)}: compute mapping for {idx_value}"
            )
            # Init S_Y and S_Z with M_RoW values in import part
            # The rest is set to 0.0
            for data_ in map_data[cst.S_Y], map_data[cst.S_Z]:
                data_.set_values(0.0)
                data_.set_import_values(
                    np.tile(
                        M_RoW.df.loc[[idx_value]].values.T,
                        data_.get_import_origin().shape[1],
                    )
                )

            # Compute d_cba and map add to the map
            self._update_fluxes(
                Z=Z,
                Y=Y,
                S_Z=map_data[cst.S_Z],
                S_Y=map_data[cst.S_Y],
                F_Z=map_data[cst.F_Z],
                F_Y=map_data[cst.F_Y],
            )
            map_of_d_cba[idx_value] = self._compute_d_cba(
                L=L,
                x=x,
                Y=Y,
                Y_k=Y_k,
                F_Y=map_data[cst.F_Y],
                F_Z=map_data[cst.F_Z],
                S_Y=map_data[cst.S_Y],
            )

        # Concatenate import parts of all d_cba
        log.verbose(f"Concatenate full {self.name}")
        mapping = pd.concat(
            {
                k: v.get_import_origin(keep_origin=False)
                for k, v in map_of_d_cba.items()
            },
            names=self.extension_categories.get_level_names(),
        )

        self.update_values(self._reorder_mapping_index(mapping=mapping))

        # Run garbage collector to free memory
        del map_data, map_of_d_cba, mapping
        gc.collect()


class MappingKData(MappingData):
    """
    Mapping_k matrix for extension data

    The structure of this data is variable. Depending on the extension
    calcul strategy, it may be
    :class:`structure.StructureDCbaKBySector`
    or :class:`structure.StructureMappingKDirect`
    or :class:`structure.StructureMappingKIndirect`.
    Refer to these classes for the format description.
    """

    _NAME = cst.MAPPING_K
    _IS_LAZY = True

    _structure = (
        structure.StructureMappingKDirect
        | structure.StructureMappingKIndirect
        | structure.StructureDCbaKBySector
    )

    def get_structure_type(self, **kwargs) -> type:
        """
        Determines and returns the type of structure for the mapping_k matrix
        based on the given strategy.

        Strategy-based logic:
            - If the strategy is `cst.STRATEGY_USE_BASED`,
              the structure is of type `StructureDCbaKBySector`.
            - If the strategy is `cst.STRATEGY_GROSS_OUTPUT_BASED`,
              the structure is of type `StructureMappingKDirect`.
            - If the strategy is `cst.STRATEGY_EMBODIED_IN_IMPORT`,
              the structure is of type `StructureMappingKIndirect`.`.
            - For any other value of "strategy," defaults to `StructureDCbaKBySector`.

        Parameters:
            **kwargs:
                A dictionary of keyword arguments. It must include:
                - "strategy" (str): A string representing the calculation strategy.

        Returns:
            type: The structure type corresponding to the provided strategy.
        """
        strategy = kwargs.get("strategy")

        match strategy:
            case cst.STRATEGY_USE_BASED:
                return structure.StructureDCbaKBySector
            case cst.STRATEGY_GROSS_OUTPUT_BASED:
                return structure.StructureMappingKDirect
            case cst.STRATEGY_EMBODIED_IN_IMPORT:
                return structure.StructureMappingKIndirect
            case _:
                return structure.StructureDCbaKBySector

    def calculate(self, **kwargs):
        """
        Calculate mapping matrix.

        Case 1 - from S_x_dom, x, L, Z, Y, Y_k:

        Case 2 - from M_RoW, x, L, Z, Y, Y_k:

        Parameters:
            S_x_dom (SxDomData):
                The inter-industry flux matrix
            M_RoW (MRoWData):
                The multiplier of the rest of the world
            x (XData):
                The production vector of the associated system
            L (LData):
                The leontief matrix of the associated system
            Z (ZData):
                The inter-industry data of the associated system
            Y (YData):
                The final demand data of the associated system
            Y_k (YKData):
                The investment data of the associated system

        Raises:
            MEIncorrectArguments
                if the parameters given are incorrect
        """
        log.verbose(f"Calculate {self.name}")

        is_calcul_completed = False

        x = kwargs.get("x")
        L = kwargs.get("L")
        Z = kwargs.get("Z")
        Y = kwargs.get("Y")
        Y_k = kwargs.get("Y_k")

        if x and L and Z and Y and Y_k:
            if "S_x_dom" in kwargs.keys():
                self._calculate_from_s_x_dom(
                    S_x_dom=kwargs.get("S_x_dom"),
                    x=x,
                    L=L,
                    Z=Z,
                    Y=Y,
                    Y_k=Y_k,
                )
                is_calcul_completed = True

            elif "M_RoW" in kwargs.keys():
                self._calculate_from_m_row(
                    M_RoW=kwargs.get("M_RoW"),
                    x=x,
                    L=L,
                    Z=Z,
                    Y=Y,
                    Y_k=Y_k,
                )
                is_calcul_completed = True

        if not is_calcul_completed:
            raise MEIncorrectArguments(
                expected_args=[
                    ("S_x_dom", "x", "L", "Z", "Y", "Y_k"),
                    ("M_RoW", "x", "L", "Z", "Y", "Y_k"),
                ]
            )

    def _compute_d_cba(
        self,
        L: system_data.LData,
        x: system_data.XData,
        Y: system_data.YData,
        F_Z: FzData,
        F_Y: FyData,
        Y_k: system_data.YKData = None,
        S_Y: SyData = None,
    ) -> DCbaKData:
        multiplier = MKData(
            extension_name=self._id.extension_name,
            regions=self.regions,
            sectors=self.sectors,
            final_demand_categories=self.final_demand_categories,
            extension_categories=self.extension_categories,
            strategy=cst.STRATEGY_USE_BASED,
        )
        multiplier.calculate(L=L, x=x, F_Z=F_Z, Y_k=Y_k, S_Y=S_Y)
        d_cba = DCbaKData(
            extension_name=self._id.extension_name,
            regions=self.regions,
            sectors=self.sectors,
            final_demand_categories=self.final_demand_categories,
            extension_categories=self.extension_categories,
            strategy=cst.STRATEGY_USE_BASED,
        )
        d_cba.calculate(
            M=multiplier,
            Y=Y,
            F_Y=F_Y,
        )
        return d_cba


class UnitExtensionData(AbstractExtensionData):
    """
    Unit matrix for extension data

    Refer to :class:`structure.StructureUnitBySector`  or
    :class:`structure.StructureUnitByExtensionCategory` for the
    format description.
    """

    _TYPE = cst.DTYPE_STRING
    _NAME = cst.UNIT

    _nature: nature.Unit
    _structure: (
        structure.StructureUnitBySector
        | structure.StructureUnitByExtensionCategory
    )

    def get_nature_type(self, **kwargs) -> type:
        return nature.Unit

    def get_structure_type(self, **kwargs) -> type:
        """
        Determines and returns the type of structure for the unit matrix
        based on the given strategy.

        Strategy-based logic:
            - If the strategy is `cst.STRATEGY_USE_BASED`,
              the structure is of type `StructureUnitBySector`.
            - If the strategy is `cst.STRATEGY_GROSS_OUTPUT_BASED`,
              the structure is of type `StructureUnitByExtensionCategory`.
            - If the strategy is `cst.STRATEGY_EMBODIED_IN_IMPORT`,
              the structure is of type `StructureUnitByExtensionCategory`.`.
            - For any other value of "strategy," defaults to `StructureUnitBySector`.

        Parameters:
            **kwargs:
                Keyword arguments. It must include:
                - "strategy" (str): A string representing the calculation strategy.

        Returns:
            type: The structure type corresponding to the provided strategy.
        """
        strategy = kwargs.get("strategy")

        match strategy:
            case cst.STRATEGY_USE_BASED:
                return structure.StructureUnitBySector
            case cst.STRATEGY_GROSS_OUTPUT_BASED:
                return structure.StructureUnitByExtensionCategory
            case cst.STRATEGY_EMBODIED_IN_IMPORT:
                return structure.StructureUnitByExtensionCategory
            case _:
                return structure.StructureUnitBySector
