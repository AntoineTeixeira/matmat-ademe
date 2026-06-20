"""
Presentation
************
This module is the builder module of the package `accounts.system`.

This module implements a design pattern **builder** to manage instantiation
of system objects.

The Builder design pattern is used to construct complex objects step by
step, allowing greater flexibility in the creation process. In this pattern,
the Builder class (here :class:`SSBuilder`) is responsible for defining the
individual steps to build different parts of an object. It encapsulates the
construction logic, ensuring that each component of the product is created
properly.

The Director class (here :class:`SystemDirector`), on the other hand,
orchestrates the sequence in which these construction steps are called,
ensuring that the object is assembled in the correct order. The Director is
in charge of managing the overall construction process but delegates the
actual building work to the Builder.

To instantiate a system object, one shall retrieve the director
singleton (though :meth:`get_director`) and use the appropriate methods.

**NOTE:** only the class :class:`SystemDirector` is exported to other modules
as the builder class should not be used directly.

Content
*******
- Classes:
    - SSBuilder
    - :class:`SystemDirector`
- Functions:
    - :meth:`get_director`
"""

__all__ = ["SystemDirector", "get_director"]

import os
import copy

from matmat.core.base.builder import AbstractBuilder, AbstractDirector
from matmat.core.detail_level import core as dl
from matmat.core.accounts.system.core import System
from matmat.core.accounts.system.identity import SystemIdentity
from matmat.core.accounts.system.strategies import calcul
import matmat.core.accounts.system.dataset.core as dataset
import matmat.utils.constants as cst
import matmat.utils.logging as log

# Director singleton
# pylint: disable=C0103
system_director = None
# pylint: enable=C0103


# pylint: disable=W0212
# (authorize access to protected members of a class for builder class)
class SystemBuilder(AbstractBuilder):
    """
    This class is a builder class which permits to build the components of
    a `System`

    Notes
    -----
    The build methods shall be called in the following order:
        - build_id
        - build_dataset
        - build_calcul_strategy
    because:
        - build_dataset needs the id to be set
        - build_calcul_strategy needs the dataset to be set

    Attributes
    ----------
    _result : System
        The result of the building process
    """

    def __init__(self):
        """
        Constructor of `SSBuilder`
        """
        # System product
        self._result: System = System()

    def build_id(self, id_: SystemIdentity):
        """
        Build system identity card
        """
        self._result._id = copy.deepcopy(id_)

    def reset(self):
        """
        Reset built system
        """
        self._result = System()

    def get_system(self) -> System:
        """
        Returns the built system and reset the product
        """
        built_system = self._result
        self.reset()
        return built_system

    def build_dataset(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
    ):
        self._result.dataset = dataset.SystemDataSet(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            config__system_calcul_strategy=self._result.id.strategy,
        )

    def build_calcul_strategy(self, calcul_strategy: str):
        """
        Build system calcul strategy

        Parameters:
            calcul_strategy (str):
                the identifier of the calcul strategy
        """
        self._result.calcul = calcul_strategy


# pylint: enable=W0212


class SystemDirector(AbstractDirector):
    """
    This class manages the building steps of a `System` object.
    It provides a set of methods used to build various kinds of systems.

    Attributes
    ----------
    _builder : SystemBuilder
        The system builder object which provides the building methods for
        each component
    _id : SystemIdentity
        The identity card of the system to build
    """

    _builder: SystemBuilder
    _id: SystemIdentity

    def init_builder(self):
        self._builder = SystemBuilder()

    def init_id(self):
        self._id = SystemIdentity(
            strategy=calcul.EnumSystemCalcul.STANDARD.value,
            base_year=0,
            proj_year=None,
            scenario_name=None,
        )

    def make(self, strategy: str) -> System:
        """
        Make a system

        Parameters:
            strategy (str):
                The calcul strategy
        """
        log.debug(f"Make {strategy} system")
        self._id.strategy = strategy
        self._build_system()
        return self._builder.get_system()

    def make_from_path(self, path: str, load_data: bool = True) -> System:
        """
        Make a system from a directory. The directory shall contain a
        file **info.json** as well as the system data files.

        The system dataset configuration depends on the strategy given
        in the info file. Then, the data matching the strategy and found in
        **path** are loaded (if load_data is True).

        Parameters:
            path (str):
                The path to the directory
            load_data (bool):
                True if the dataframes shall be initialized with the values
                read in the files
        """
        log.debug(f"Make System object from path {path}")

        self._id.load_json(
            file_path=os.path.join(path, cst.FILE_INFO),
            required_keys=[
                cst.KEY_STRATEGY,
                cst.KEY_BASE_YEAR,
            ],
        )

        # Initialize and load detail levels
        self._regions = dl.RegionsDL()
        self._sectors = dl.SectorsDL()
        self._final_demand_categories = dl.FinalDemandCategoriesDL()
        self._load_detail_levels_from_path(path=path)

        self._build_system()

        system = self._builder.get_system()
        if load_data:
            system.load_from_path(path=path)
        return system

    def make_from_id(self, id_: SystemIdentity) -> System:
        """
        Make a system from an existing system identity.

        The system configuration is built according to the information
        contained in the given identity.

        Parameters:
            id_ (SystemIdentity):
                The identity describing the system to build
        """
        log.debug(f"Make System object from id {id_.__dict__}")
        self._id = id_
        self._build_system()
        return self._builder.get_system()

    def make_standard_system(self) -> System:
        """
        Make a system with a standard calcul strategy and components
        A, L, x, Y, Z

        Returns:
            System
        """
        return self.make(strategy=calcul.EnumSystemCalcul.STANDARD.value)

    def make_exo_invest_matrix_system(self):
        """
        Make a system with an exo_invest_matrix calcul strategy
        and components A, L, x, Y, Z, K, L_k, Y_k

        Returns:
            System
        """
        return self.make(
            strategy=calcul.EnumSystemCalcul.EXO_INVEST_MATRIX.value
        )

    def make_endo_invest_matrix_system(self):
        """
        Make a system with an endo_invest_matrix calcul strategy
        and components A, L, x, Y, Z, K, L_k, Y_k

        Returns:
            System
        """
        return self.make(
            strategy=calcul.EnumSystemCalcul.ENDO_INVEST_MATRIX.value
        )

    def _build_system(self):
        self._builder.build_id(id_=self._id)

        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
        )

        self._builder.build_calcul_strategy(self._id.strategy)


# pylint: disable=W0603
def get_director(reset: bool = False) -> SystemDirector:
    """
    Returns the `System` director singleton. If reset is True, call the
    director method reset() before returning it.
    """
    global system_director

    if system_director is None:
        system_director = SystemDirector()
    if reset:
        system_director.reset()
    return system_director


# pylint: enable=W0603
