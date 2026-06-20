"""
Presentation
************
This module is the builder module of the package `shocks.system`.

This module implements a design pattern **builder** to manage instantiation
of system shock objects.

The Builder design pattern is used to construct complex objects step by
step, allowing greater flexibility in the creation process. In this pattern,
the Builder classes (here :class:`SystemShockBuilder`) are
responsible for defining the individual steps to build different parts of an
object. It encapsulates the construction logic, ensuring that each component
of the product is created properly.

The Director classes (here :class:`SystemShockDirector`), on the other hand,
orchestrate the sequence in which
these construction steps are called, ensuring that the object is assembled
in the correct order. The Director is in charge of managing the overall
construction process but delegates the actual building work to the Builder.

To instantiate a shock object, one shall retrieve the corresponding director
singleton:
    - for system shock : use :meth:`get_director`

and use the appropriate methods.

**NOTE:** only the director class is exported to other modules as
the builder class should not be used directly.

Content
*******
- Classes:
    - SystemShockBuilder
    - :class:`SystemShockDirector`
- Functions:
    - :meth:`get_director`
"""

__all__ = [
    "SystemShockDirector",
    "get_director",
]

import os
import copy

from matmat.core.base.builder import AbstractBuilder, AbstractDirector
from matmat.core.detail_level import core as dl
from matmat.core.accounts.system.core import System
from matmat.core.shocks.system.core import SystemShock
from matmat.core.shocks.system.identity import SystemShockIdentity
from matmat.core.shocks import tools as shocks_tools
from matmat.core.shocks.system.dataset.core import SystemShockDataSet
from matmat.utils import tools, constants as cst, logging as log


# Directors singletons
# pylint: disable=C0103
system_shock_director = None
# pylint: enable=C0103


# pylint: disable=W0212
# (authorize access to protected members of a class for builder class)
class SystemShockBuilder(AbstractBuilder):
    """
    This class is a builder class which permits to build the components of
    a `SystemShock`

    NOTE: one shall call the method :meth:`build_id` prior to any other
    build methods.

    Attributes
    ----------
    _result : SystemShock
        The result of the building process
    """

    def __init__(self):
        """
        Constructor of `SystemShockBuilder`
        """
        self._result: SystemShock = SystemShock()

    def reset(self):
        """
        Reset builder to default values
        """
        self._result = SystemShock()

    def get_system_shock(self) -> SystemShock:
        """
        Returns the built shock and reset the product
        """
        built_shock = self._result
        self.reset()
        return built_shock

    def build_id(self, id_: SystemShockIdentity):
        """
        Build system shock identity card
        """
        self._result._id = copy.deepcopy(id_)

    def build_dataset(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        data_list: list = None,
    ):
        self._result.dataset = SystemShockDataSet(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            data_list=data_list,
        )


class SystemShockDirector(AbstractDirector):
    """
    This class manages the building steps of a `SystemShock` object. It
    provides a set of methods used to build various kinds of system shocks.

    Attributes
    ----------
    _builder : SystemShockBuilder
        The system shock builder object which provides the building methods
        for each component
    _id : SystemShockIdentity
        The id card of the system shock to build
    """

    _builder: SystemShockBuilder
    _id: SystemShockIdentity

    def init_builder(self):
        self._builder = SystemShockBuilder()

    def init_id(self):
        self._id = SystemShockIdentity(
            base_year=0,
            proj_year=None,
            scenario_name=None,
        )

    def make_from_path(self, path: str, load_data: bool = True) -> SystemShock:
        """
        Make a system shock from a directory. The directory shall
        contain a file **info.json** as well as the shock data files.

        The files found in **path** defines the data composing the shock.
        For example, if there are two files dA.pkl and imp_dom_ratio.pkl,
        then the data dA and imp_dom_ratio will be added to the shock,
        with an input reader defined to pickle.

        Parameters:
            path (str):
                The path to the directory
            load_data (bool):
                True if the dataframes shall be initialized with the values
                read in the files (default to True)
        """
        log.debug(f"Make SystemShock object from path {path}")

        self.id.load_json(
            file_path=os.path.join(path, cst.FILE_INFO),
            required_keys=[cst.KEY_BASE_YEAR],
        )

        self._builder.build_id(id_=self.id)

        # Initialize and load detail levels
        self._regions = dl.RegionsDL()
        self._sectors = dl.SectorsDL()
        self._final_demand_categories = dl.FinalDemandCategoriesDL()
        self._load_detail_levels_from_path(path=path)

        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
            data_list=tools.retrieve_data_list_from_path(
                path=path, data_list=cst.LIST_OF_SYSTEM_SHOCK_DATA
            ),
        )

        system_shock = self._builder.get_system_shock()

        if load_data:
            system_shock.load_from_path(path)

        return system_shock

    def make_from_id(self, id_: SystemShockIdentity) -> SystemShock:
        """
        Make a system shock from an existing system shock identity.

        The system shock configuration is built according to the information
        contained in the given identity.

        Parameters:
            id_ (SystemShockIdentity):
                The identity describing the system shock to build
        """
        log.debug(f"Make SystemShock object from id {id_.__dict__}")
        self._builder.build_id(id_=id_)
        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
        )
        return self._builder.get_system_shock()

    def make_from_systems(
        self, system_from: System, system_to: System
    ) -> SystemShock:
        """
        Make a system shock from the difference between two systems

        Parameters:
            system_from (System):
                The reference system
            system_to (System):
                The projected system

        Returns:
            SystemShock
        """
        log.debug("Make SystemShock object from the difference of systems")

        self.set_regions(system_from.regions)
        self.set_sectors(system_from.sectors)
        self.set_final_demand_categories(system_from.final_demand_categories)
        self.set_id(
            id_=SystemShockIdentity(
                base_year=system_from.id.base_year,
                proj_year=system_to.id.base_year,
                scenario_name=system_from.id.scenario_name,
            )
        )

        def feed_shock(shock_: SystemShock):
            for data_name in shock_.dataset.list_data():
                try:
                    shocks_tools.compute_shock_data(
                        shock_data=getattr(shock.dataset, data_name),
                        accounts_data_from=getattr(
                            system_from.dataset, data_name[1:]
                        ),
                        accounts_data_to=getattr(
                            system_to.dataset, data_name[1:]
                        ),
                    )
                except AttributeError:
                    log.debug(
                        f"No data related to '{data_name}' in system. "
                        f"Skipping..."
                    )

        if system_from.is_standard():
            shock = self.make_shock_standard()
            feed_shock(shock)
            return shock

        if system_from.is_exo_invest_matrix():
            shock = self.make_shock_exo()
            feed_shock(shock)
            return shock

        if system_from.is_endo_invest_matrix():
            log.error(
                f"Construction of shock from a '{system_from.calcul.name}' "
                f"system is not implemented. Skipping..."
            )
            # TODO: shock on dK
            raise NotImplementedError

        raise NotImplementedError

    def make_shock_complete(self) -> SystemShock:
        """
        Make a system shock with the components dA, dK, dY, dY_k, dZ,
        imp_dom_ratio

        Returns:
            SystemShock
        """
        return self.make_shock_from_data_list(
            data_list=cst.LIST_OF_SYSTEM_SHOCK_DATA
        )

    def make_shock_standard(self) -> SystemShock:
        """
        Make a system shock with the components dA, dY, imp_dom_ratio

        Returns:
            SystemShock
        """
        data_list = [cst.D_A, cst.D_Y]
        return self.make_shock_from_data_list(data_list)

    def make_shock_exo(self) -> SystemShock:
        """
        Make a system shock with the components dA, dY, dY_k

        Returns:
            SystemShock
        """
        data_list = [cst.D_A, cst.D_Y, cst.D_Y_K]
        return self.make_shock_from_data_list(data_list)

    def make_shock_y(self) -> SystemShock:
        """
        Make a system shock with the components dY

        Returns:
            SystemShock
        """
        data_list = [cst.D_Y]
        return self.make_shock_from_data_list(data_list)

    def make_shock_y_k(self) -> SystemShock:
        """
        Make a system shock with the components dY_k

        Returns:
            SystemShock
        """
        data_list = [cst.D_Y_K]
        return self.make_shock_from_data_list(data_list)

    def make_shock_a(self) -> SystemShock:
        """
        Make a system shock with the components dA

        Returns:
            SystemShock
        """
        data_list = [cst.D_A]
        return self.make_shock_from_data_list(data_list)

    def make_shock_k(self) -> SystemShock:
        """
        Make a system shock with the components dK

        Returns:
            SystemShock
        """
        data_list = [cst.D_K]
        return self.make_shock_from_data_list(data_list)

    def make_shock_from_data_list(self, data_list: list) -> SystemShock:
        self._builder.build_id(id_=self.id)
        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
            data_list=data_list,
        )
        return self._builder.get_system_shock()


# pylint: disable=W0603
def get_director(reset: bool = False) -> SystemShockDirector:
    """
    Returns the `SystemShock` director singleton. If reset is True, call the
    director method reset() before returning it.
    """
    global system_shock_director

    if system_shock_director is None:
        system_shock_director = SystemShockDirector()
    if reset:
        system_shock_director.reset()
    return system_shock_director


# pylint: enable=W0603
