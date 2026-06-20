"""
Presentation
************
This module contains the definition of the extension calcul strategy classes.

There are different ways of performing operations on an extension, depending
on the data at disposal, and on the objectives of the analysis. To ease the
integration and maintenance of these various ways of computation,
the concept of strategy is encapsulated into a dedicated class. An extension
object contains a strategy object which performs the calculations. Depending
on the class of the strategy object, these calculations have different
implementations.

**How to add a new calcul strategy?**
    1. Define a class deriving
       from :class:`AbstractExtensionCalcul`
    2. Implement the abstract methods
    3. Update the enumeration class :class:`EnumExtensionCalcul` w.r.t. the
       new class
    4. Update unit tests (see **tests/unit_tests/core/extension/strategies**)
       with the new strategy

The following section presents the different extension strategy classes.

Content
*******
- Classes:
    - :class:`EnumExtensionCalcul`
    - :class:`AbstractExtensionCalcul`
    - :class:`UseBased`
    - :class:`GrossOutputBased`
"""

__all__ = [
    "EnumExtensionCalcul",
    "AbstractExtensionCalcul",
    "UseBased",
    "GrossOutputBased",
    "EmbodiedInImport",
]

from enum import Enum, verify, UNIQUE
from abc import ABC, abstractmethod

from matmat.core.accounts.extension.dataset.core import ExtensionDataSet
from matmat.core.accounts.system.dataset.core import SystemDataSet
from matmat.utils.errors import MENotEnoughData, MEUnknownStrategy
from matmat.utils import constants as cst, logging as log


# noinspection PyPep8Naming
# pylint: disable=C0103, R0913, R0914
# C0103: some variables / parameters names are not lowercase because they match
#        MatMat literature case
# R0913, R0914: it is necessary to pass many arguments to have one single
#               interface for the calcul strategy
class AbstractExtensionCalcul(ABC):
    """
    This abstract class represents an extension calcul strategy. It
    defines the abstract methods that must be implemented by the concrete
    extension strategy classes.
    """

    NAME: str

    @property
    def name(self):
        return self.NAME

    @abstractmethod
    def calculate(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the extension fluxes and coefficients.
        """

    @abstractmethod
    def calculate_m(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate multiplier M.
        """

    @abstractmethod
    def calculate_mk(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate multiplier M_k.
        """

    @abstractmethod
    def calculate_d_cba(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the consumption based accounts.
        """

    @abstractmethod
    def calculate_d_cba_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the augmented consumption based accounts.
        """

    @abstractmethod
    def calculate_mapping(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the mapping matrix
        """

    @abstractmethod
    def calculate_mapping_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the mapping matrix
        """

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
    def reset_for_shock(
        self,
        *,
        extension_dataset: ExtensionDataSet,
    ):
        """
        Reset the extension data in preparation for a shock. The data which
        shall be reset depends on the extension strategy.
        """

    def is_shock_applicable(self, shock_data_name: str) -> bool:
        """
        Check if a shock data is applicable to the extension.

        Parameters:
            shock_data_name (str):
                The name of the shock data to verify against the list of
                shockable data.

        Returns:
            bool : True if the shock data is compatible with the list of
                   shockable data, False otherwise.
        """
        # [:1] to slice the leading "d" from the data name
        # Example: "dM_RoW" becomes "M_RoW"
        return shock_data_name[1:] in self.list_shockable_data()


# noinspection PyPep8Naming
class UseBased(AbstractExtensionCalcul):
    """
    Extension calcul strategy based on use
    """

    NAME: str = cst.STRATEGY_USE_BASED

    @staticmethod
    def list_shockable_data() -> list:
        return [cst.S_Y, cst.S_Z]

    def calculate(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the extension fluxes and coefficients.

        Each data is computed in a dedicated method. For example, S_Y is
        computed in the method :meth:`_calculate_s_y`. This permits to
        override specific steps by subclasses if necessary, to implement
        specific equations.

        1. Calculate S_Z or F_Z (depending on the input data)
        2. Calculate S_Y or F_Y (depending on the input data)
        """
        self._calculate_z_data(
            system_dataset=system_dataset, extension_dataset=extension_dataset
        )
        self._calculate_y_data(
            system_dataset=system_dataset, extension_dataset=extension_dataset
        )

    def calculate_m(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate multiplier M.

        1. Calculate M from F_Z, x, and L
        """
        if not (
            system_dataset.L.is_domestic_region_empty()
            or system_dataset.x.is_df_empty()
            or extension_dataset.F_Z.is_df_empty()
        ):
            extension_dataset.M.calculate(
                F_Z=extension_dataset.F_Z,
                x=system_dataset.x,
                L=system_dataset.L,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    system_dataset.L.name,
                    extension_dataset.F_Z.name,
                    system_dataset.x.name,
                ],
                all_data=True,
            )

    def calculate_mk(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate M from F_Z, S_Y, Y_k, x and L_k
        """
        if not (
            system_dataset.L_k.is_domestic_region_empty()
            or system_dataset.x.is_df_empty()
            or extension_dataset.F_Z.is_df_empty()
            or extension_dataset.S_Y.is_df_empty()
            or system_dataset.Y_k.is_df_empty()
        ):
            extension_dataset.M_k.calculate(
                F_Z=extension_dataset.F_Z,
                x=system_dataset.x,
                L=system_dataset.L_k,
                S_Y=extension_dataset.S_Y,
                Y_k=system_dataset.Y_k,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    system_dataset.L_k.name,
                    system_dataset.x.name,
                    extension_dataset.F_Z.name,
                    extension_dataset.S_Y.name,
                    system_dataset.Y_k.name,
                ],
                all_data=True,
            )

    def calculate_d_cba(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the consumption based accounts from M, Y, and F_Y

        Raises:
            MENotEnoughData
                if one of M, Y, F_Y is empty
        """
        if not (
            extension_dataset.M.is_df_empty()
            or system_dataset.Y.is_df_empty()
            or extension_dataset.F_Y.is_df_empty()
        ):
            extension_dataset.d_cba.calculate(
                M=extension_dataset.M,
                Y=system_dataset.Y,
                F_Y=extension_dataset.F_Y,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.M.name,
                    system_dataset.Y.name,
                    extension_dataset.F_Y.name,
                ],
                all_data=True,
            )

    def calculate_d_cba_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the augmented consumption based accounts from M_k, Y, and F_Y

        Raises:
            MENotEnoughData
                if one of M_k, Y, F_Y is empty
        """
        if not (
            extension_dataset.M_k.is_df_empty()
            or system_dataset.Y.is_df_empty()
            or extension_dataset.F_Y.is_df_empty()
        ):
            extension_dataset.d_cba_k.calculate(
                M=extension_dataset.M_k,
                Y=system_dataset.Y,
                F_Y=extension_dataset.F_Y,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.M_k.name,
                    system_dataset.Y.name,
                    extension_dataset.F_Y.name,
                ],
                all_data=True,
            )

    def calculate_mapping(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        log.error(
            f"No need to calculate mapping in a '{self.NAME}' extension "
            f"as it is equal to {extension_dataset.d_cba.name}."
        )

    def calculate_mapping_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        log.error(
            f"No need to calculate mapping_k in a '{self.NAME}' extension "
            f"as it is equal to {extension_dataset.d_cba_k.name}."
        )

    def reset_for_shock(
        self,
        *,
        extension_dataset: ExtensionDataSet,
    ):
        """
        Reset the following extension data in preparation for a shock:
            - F_Y
            - F_Z
        """
        extension_dataset.F_Y.reset()
        extension_dataset.F_Z.reset()

    @staticmethod
    def _calculate_f_z(
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        If F_Z is empty, calculate F_Z from S_Z and Z
        """
        if extension_dataset.F_Z.is_df_empty():
            extension_dataset.F_Z.calculate(
                S_Z=extension_dataset.S_Z, Z=system_dataset.Z
            )

    @staticmethod
    def _calculate_s_z(
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        If S_Z is empty, calculate S_Z from F_Z and Z
        """
        if extension_dataset.S_Z.is_df_empty():
            extension_dataset.S_Z.calculate(
                F_Z=extension_dataset.F_Z, Z=system_dataset.Z
            )

    def _calculate_z_data(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate F_Z or S_Z, depending on what input is available.

        Raises:
            MENotEnoughData
                if F_Z and S_Z are empty
        """
        if not (
            extension_dataset.F_Z.is_df_empty()
            and extension_dataset.S_Z.is_df_empty()
        ):
            self._calculate_s_z(
                system_dataset=system_dataset,
                extension_dataset=extension_dataset,
            )
            self._calculate_f_z(
                system_dataset=system_dataset,
                extension_dataset=extension_dataset,
            )
        else:
            raise MENotEnoughData(list_of_data=["F_Z", "S_Z"])

    @staticmethod
    def _calculate_f_y(
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        If F_Y is empty, calculate  from S_Y and Y
        """
        if extension_dataset.F_Y.is_df_empty():
            extension_dataset.F_Y.calculate(
                S_Y=extension_dataset.S_Y, Y=system_dataset.Y
            )

    @staticmethod
    def _calculate_s_y(
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        If S_Y is empty, calculate S_Y from F_Y and Y
        """
        if extension_dataset.S_Y.is_df_empty():
            extension_dataset.S_Y.calculate(
                F_Y=extension_dataset.F_Y, Y=system_dataset.Y
            )

    def _calculate_y_data(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate F_Y or S_Y, depending on what input is available.

        Raises:
            MENotEnoughData
                if F_Y and S_Y are empty
        """
        if not (
            extension_dataset.F_Y.is_df_empty()
            and extension_dataset.S_Y.is_df_empty()
        ):
            self._calculate_s_y(
                system_dataset=system_dataset,
                extension_dataset=extension_dataset,
            )
            self._calculate_f_y(
                system_dataset=system_dataset,
                extension_dataset=extension_dataset,
            )
        else:
            raise MENotEnoughData(list_of_data=["F_Y", "S_Y"])


# noinspection PyPep8Naming
class GrossOutputBased(AbstractExtensionCalcul):
    """
    Extension calcul strategy based on gross output
    """

    NAME: str = cst.STRATEGY_GROSS_OUTPUT_BASED

    @staticmethod
    def list_shockable_data() -> list:
        return [cst.S_X_DOM]

    def calculate(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the extension fluxes and coefficients

        1. Calculate S_x_dom or F_x_dom (depending on the input data)
        """
        self._calculate_x_data(
            system_dataset=system_dataset,
            extension_dataset=extension_dataset,
        )

    def calculate_m(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate multiplier M.

        1. Calculate M from S_x_dom and L
        """
        if not (
            system_dataset.L.is_domestic_region_empty()
            or extension_dataset.S_x_dom.is_df_empty()
        ):
            extension_dataset.M.calculate(
                S_x_dom=extension_dataset.S_x_dom, L=system_dataset.L
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    system_dataset.L.name,
                    extension_dataset.S_x_dom.name,
                ],
                all_data=True,
            )

    def calculate_mk(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate M_k from S_x_dom and Lk_dom
        """
        if not (
            system_dataset.L_k.is_domestic_region_empty()
            or extension_dataset.S_x_dom.is_df_empty()
        ):
            extension_dataset.M_k.calculate(
                S_x_dom=extension_dataset.S_x_dom, L=system_dataset.L_k
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    system_dataset.L_k.name,
                    extension_dataset.S_x_dom.name,
                ],
                all_data=True,
            )

    def calculate_d_cba(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the consumption based accounts from M and Y.

        Raises:
            MENotEnoughData
                if one of M, Y is empty
        """
        if not (
            extension_dataset.M.is_df_empty() or system_dataset.Y.is_df_empty()
        ):
            extension_dataset.d_cba.calculate(
                M=extension_dataset.M,
                Y=system_dataset.Y,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[extension_dataset.M.name, system_dataset.Y.name],
                all_data=True,
            )

    def calculate_d_cba_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the augmented consumption based accounts from M_k and Y.

        Raises:
            MENotEnoughData
                if one of M_k, Y is empty
        """
        if not (
            extension_dataset.M_k.is_df_empty()
            or system_dataset.Y.is_df_empty()
        ):
            extension_dataset.d_cba_k.calculate(
                M=extension_dataset.M_k, Y=system_dataset.Y
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.M_k.name,
                    system_dataset.Y.name,
                ],
                all_data=True,
            )

    def calculate_mapping(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        if not (
            extension_dataset.S_x_dom.is_df_empty()
            or system_dataset.x.is_df_empty()
            or system_dataset.L.is_df_empty()
            or system_dataset.Z.is_df_empty()
            or system_dataset.Y.is_df_empty()
        ):
            extension_dataset.mapping.calculate(
                S_x_dom=extension_dataset.S_x_dom,
                x=system_dataset.x,
                L=system_dataset.L,
                Z=system_dataset.Z,
                Y=system_dataset.Y,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.S_x_dom.name,
                    system_dataset.x.name,
                    system_dataset.L.name,
                    system_dataset.Z.name,
                    system_dataset.Y.name,
                ],
                all_data=True,
            )

    def calculate_mapping_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        if not (
            extension_dataset.S_x_dom.is_df_empty()
            or system_dataset.x.is_df_empty()
            or system_dataset.L.is_df_empty()
            or system_dataset.Z.is_df_empty()
            or system_dataset.Y.is_df_empty()
            or system_dataset.Y_k.is_df_empty()
        ):
            extension_dataset.mapping_k.calculate(
                S_x_dom=extension_dataset.S_x_dom,
                x=system_dataset.x,
                L=system_dataset.L_k,
                Z=system_dataset.Z,
                Y=system_dataset.Y,
                Y_k=system_dataset.Y_k,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.S_x_dom.name,
                    system_dataset.x.name,
                    system_dataset.L.name,
                    system_dataset.Z.name,
                    system_dataset.Y.name,
                    system_dataset.Y_k.name,
                ],
                all_data=True,
            )

    def reset_for_shock(
        self,
        *,
        extension_dataset: ExtensionDataSet,
    ):
        """
        Reset the following extension data in preparation for a shock:
            - F_x_dom
        """
        extension_dataset.F_x_dom.reset()

    @staticmethod
    def _calculate_f_x_dom(
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        If F_x_dom is empty, calculate F_x_dom from S_x_dom and x
        """
        if extension_dataset.F_x_dom.is_df_empty():
            extension_dataset.F_x_dom.calculate(
                S_x_dom=extension_dataset.S_x_dom, x=system_dataset.x
            )

    @staticmethod
    def _calculate_s_x_dom(
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        If S_x_dom is empty, calculate S_x_dom from F_x_dom and x
        """
        if extension_dataset.S_x_dom.is_df_empty():
            extension_dataset.S_x_dom.calculate(
                F_x_dom=extension_dataset.F_x_dom, x=system_dataset.x
            )

    def _calculate_x_data(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate F_x_dom or S_x_dom, depending on
        what inputs are available

        Raises:
            MENotEnoughData
                if F_x_dom and S_x_dom are empty
        """
        if not (
            extension_dataset.F_x_dom.is_df_empty()
            and extension_dataset.S_x_dom.is_df_empty()
        ):
            self._calculate_s_x_dom(
                system_dataset=system_dataset,
                extension_dataset=extension_dataset,
            )
            self._calculate_f_x_dom(
                system_dataset=system_dataset,
                extension_dataset=extension_dataset,
            )
        else:
            raise MENotEnoughData(list_of_data=["F_x_dom", "S_x_dom"])


class EmbodiedInImport(AbstractExtensionCalcul):
    """
    Extension calcul strategy when embodied in import
    """

    NAME: str = cst.STRATEGY_EMBODIED_IN_IMPORT

    @staticmethod
    def list_shockable_data() -> list:
        return [cst.M_ROW]

    def calculate(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate:
            - d_imp from M_RoW and x
            - or M_RoW from d_imp and x
        """
        if not (
            extension_dataset.M_RoW.is_df_empty()
            or system_dataset.x.is_df_empty()
        ):
            extension_dataset.d_imp.calculate(
                M_RoW=extension_dataset.M_RoW,
                x=system_dataset.x,
            )
        elif not (
            extension_dataset.d_imp.is_df_empty()
            or system_dataset.x.is_df_empty()
        ):
            extension_dataset.M_RoW.calculate(
                d_imp=extension_dataset.d_imp,
                x=system_dataset.x,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[(cst.M_ROW, cst.X), (cst.D_IMP, cst.X)],
                all_data=False,
            )

    def calculate_m(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate M from M_RoW, A, and L
        """
        if not (
            system_dataset.L.is_domestic_region_empty()
            or system_dataset.A.is_import_region_empty()
            or extension_dataset.M_RoW.is_df_empty()
        ):
            extension_dataset.M.calculate(
                L=system_dataset.L,
                A=system_dataset.A,
                M_RoW=extension_dataset.M_RoW,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    system_dataset.L.name,
                    system_dataset.A.name,
                    extension_dataset.M_RoW.name,
                ],
                all_data=True,
            )

    def calculate_mk(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate M from M_RoW, A, K and L_k
        """
        if not (
            system_dataset.L_k.is_domestic_region_empty()
            or system_dataset.A.is_import_region_empty()
            or system_dataset.K.is_import_region_empty()
            or extension_dataset.M_RoW.is_df_empty()
        ):
            extension_dataset.M_k.calculate(
                L=system_dataset.L_k,
                A=system_dataset.A,
                K=system_dataset.K,
                M_RoW=extension_dataset.M_RoW,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    system_dataset.L_k.name,
                    system_dataset.A.name,
                    system_dataset.K.name,
                    extension_dataset.M_RoW.name,
                ],
                all_data=True,
            )

    def calculate_d_cba(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the consumption based accounts from M, Y and M_RoW.

        Raises:
            MENotEnoughData
                if one of M, Y, M_RoW is empty
        """
        if not (
            extension_dataset.M.is_df_empty()
            or system_dataset.Y.is_df_empty()
            or extension_dataset.M_RoW.is_df_empty()
        ):
            extension_dataset.d_cba.calculate(
                M=extension_dataset.M,
                Y=system_dataset.Y,
                M_RoW=extension_dataset.M_RoW,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.M.name,
                    system_dataset.Y.name,
                    extension_dataset.M_RoW.name,
                ],
                all_data=True,
            )

    def calculate_d_cba_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        """
        Calculate the augmented consumption based accounts from M_k, Y
        and M_RoW.

        Raises:
            MENotEnoughData
                if one of M_k, Y, M_RoW is empty
        """
        if not (
            extension_dataset.M_k.is_df_empty()
            or system_dataset.Y.is_df_empty()
            or extension_dataset.M_RoW.is_df_empty()
        ):
            extension_dataset.d_cba_k.calculate(
                M=extension_dataset.M_k,
                Y=system_dataset.Y,
                M_RoW=extension_dataset.M_RoW,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.M_k.name,
                    system_dataset.Y.name,
                    extension_dataset.M_RoW.name,
                ],
                all_data=True,
            )

    def calculate_mapping(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        if not (
            extension_dataset.M_RoW.is_df_empty()
            or system_dataset.x.is_df_empty()
            or system_dataset.L.is_df_empty()
            or system_dataset.Z.is_df_empty()
            or system_dataset.Y.is_df_empty()
        ):
            extension_dataset.mapping.calculate(
                M_RoW=extension_dataset.M_RoW,
                x=system_dataset.x,
                L=system_dataset.L,
                Z=system_dataset.Z,
                Y=system_dataset.Y,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.M_RoW.name,
                    system_dataset.x.name,
                    system_dataset.L.name,
                    system_dataset.Z.name,
                    system_dataset.Y.name,
                ],
                all_data=True,
            )

    def calculate_mapping_k(
        self,
        *,
        extension_dataset: ExtensionDataSet,
        system_dataset: SystemDataSet,
    ):
        if not (
            extension_dataset.M_RoW.is_df_empty()
            or system_dataset.x.is_df_empty()
            or system_dataset.L.is_df_empty()
            or system_dataset.Z.is_df_empty()
            or system_dataset.Y.is_df_empty()
            or system_dataset.Y_k.is_df_empty()
        ):
            extension_dataset.mapping_k.calculate(
                M_RoW=extension_dataset.M_RoW,
                x=system_dataset.x,
                L=system_dataset.L_k,
                Z=system_dataset.Z,
                Y=system_dataset.Y,
                Y_k=system_dataset.Y_k,
            )
        else:
            raise MENotEnoughData(
                list_of_data=[
                    extension_dataset.M_RoW.name,
                    system_dataset.x.name,
                    system_dataset.L.name,
                    system_dataset.Z.name,
                    system_dataset.Y.name,
                    system_dataset.Y_k.name,
                ],
                all_data=True,
            )

    def reset_for_shock(
        self,
        *,
        extension_dataset: ExtensionDataSet,
    ):
        # Nothing to reset
        pass


@verify(UNIQUE)
class EnumExtensionCalcul(Enum):
    """
    Enumeration of extension calcul strategies:
        - use based
        - gross output based
        - embodied in import
    """

    USE_BASED = UseBased.NAME
    GROSS_OUTPUT = GrossOutputBased.NAME
    EMBODIED_IN_IMPORT = EmbodiedInImport.NAME

    @classmethod
    def map_enum_to_classes(cls) -> dict:
        return {
            cls.USE_BASED: UseBased,
            cls.GROSS_OUTPUT: GrossOutputBased,
            cls.EMBODIED_IN_IMPORT: EmbodiedInImport,
        }

    def build_strategy(self) -> AbstractExtensionCalcul:
        """
        Build the extension calcul strategy w.r.t. the enumeration member.

        Returns:
            AbstractExtensionCalcul : the extension calcul strategy
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
