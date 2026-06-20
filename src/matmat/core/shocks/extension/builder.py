"""
Presentation
************
This module is the builder module of the package `shocks.extension`.

This module implements a design pattern **builder** to manage instantiation
of extension shock objects.

The Builder design pattern is used to construct complex objects step by
step, allowing greater flexibility in the creation process. In this pattern,
the Builder classes (here :class:`ExtensionShockBuilder`) are
responsible for defining the individual steps to build different parts of an
object. It encapsulates the construction logic, ensuring that each component
of the product is created properly.

The Director classes (:class:`ExtensionShockDirector`), on the other hand,
orchestrate the sequence in which
these construction steps are called, ensuring that the object is assembled
in the correct order. The Director is in charge of managing the overall
construction process but delegates the actual building work to the Builder.

To instantiate a shock object, one shall retrieve the corresponding director
singleton:
    - for extension shock : use :meth:`get_director`

and use the appropriate methods.

**NOTE:** only the director class is exported to other modules as
the builder class should not be used directly.

Content
*******
- Classes:
    - ExtensionShockBuilder
    - :class:`ExtensionShockDirector`
- Functions:
    - :meth:`get_director`
"""

__all__ = [
    "ExtensionShockDirector",
    "get_director",
]

import os
import copy

from matmat.core.base.builder import AbstractBuilder, AbstractDirector
from matmat.core.detail_level import core as dl
from matmat.core.accounts.extension.core import Extension
from matmat.core.shocks.extension.core import ExtensionShock
from matmat.core.shocks.extension.identity import ExtensionShockIdentity
from matmat.core.shocks import tools as shocks_tools
from matmat.core.shocks.extension.dataset.core import ExtensionShockDataSet
from matmat.utils import tools, constants as cst, logging as log


# Directors singletons
# pylint: disable=C0103
extension_shock_director = None
# pylint: enable=C0103


class ExtensionShockBuilder(AbstractBuilder):
    """
    This class is a builder class which permits to build the components of a
    `ExtensionShock`

    NOTE: one shall call the method :meth:`build_id` prior to any other
    build methods.

    Attributes
    ----------
    _result : ExtensionShock
        The result of the building process
    """

    def __init__(self):
        """
        Constructor of `ExtensionShockBuilder`
        """
        self._result: ExtensionShock = ExtensionShock()

    def reset(self):
        """
        Reset product
        """
        self._result = ExtensionShock()

    def get_extension_shock(self) -> ExtensionShock:
        """
        Returns the built shock
        """
        built_shock = self._result
        self.reset()
        return built_shock

    def build_id(self, id_: ExtensionShockIdentity):
        """
        Build extension shock identity card
        """
        self._result._id = copy.deepcopy(id_)

    def build_dataset(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        extension_categories: dl.ExtensionCategoriesDL,
        data_list: list = None,
    ):
        self._result.dataset = ExtensionShockDataSet(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            extension_name=self._result.id.extension_name,
            extension_categories=extension_categories,
            data_list=data_list,
        )


# pylint: enable=W0212
class ExtensionShockDirector(AbstractDirector):
    """
    This class manages the building steps of a `ExtensionShock` object.
    It provides a set of methods used to build various kinds of extension
    shocks.

    Attributes
    ----------
    _builder : ExtensionShockBuilder
        The extension shock builder object which provides the building methods
        for each component
    _id : ExtensionShockIdentity
        The id card of the extension shock to build
    """

    _builder: ExtensionShockBuilder
    _id: ExtensionShockIdentity

    def init_builder(self):
        self._builder = ExtensionShockBuilder()

    def init_id(self):
        self._id = ExtensionShockIdentity(
            extension_name="undefined",
            base_year=0,
            proj_year=None,
            scenario_name=None,
        )

    def make_shock_complete(self, name: str) -> ExtensionShock:
        """
        Make an extension shock with the components dS_x_dom, dS_Y, dS_Z, M_RoW

        Parameters:
            name (str):
                The name of the extension to shock
        Returns:
            ExtensionShock
        """
        return self.make_shock_from_data_list(
            name=name, data_list=cst.LIST_OF_EXTENSION_SHOCK_DATA
        )

    def make_from_path(
        self, path: str, load_data: bool = True
    ) -> ExtensionShock:
        """
        Make an extension shock from a directory. The directory shall
        contain a file **info.json** as well
        as the shock data files.

        The files found in **path** defines the data composing the shock.
        For example, if there are two files dS_x.pkl
        and dS_Y.pkl, then the data dS_x and dS_Y will be added to the shock,
        with an input reader defined to pickle.

        Parameters:
            path (str):
                The path to the directory
            load_data (bool):
                True if the dataframes shall be initialized with the values
                read in the files (default to True)
        """
        log.debug(f"Make ExtensionShock object from path {path}")

        self._id.load_json(
            file_path=os.path.join(path, cst.FILE_INFO),
            required_keys=[cst.KEY_EXTENSION_NAME],
        )

        self._builder.build_id(id_=self._id)

        # Initialize and load detail levels
        self._regions = dl.RegionsDL()
        self._sectors = dl.SectorsDL()
        self._final_demand_categories = dl.FinalDemandCategoriesDL()
        self._extension_categories = dl.ExtensionCategoriesDL(
            extension_name=self._id.name
        )
        self._load_detail_levels_from_path(path=path)

        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
            extension_categories=self._extension_categories,
            data_list=tools.retrieve_data_list_from_path(
                path=path, data_list=cst.LIST_OF_EXTENSION_SHOCK_DATA
            ),
        )

        ext_shock = self._builder.get_extension_shock()

        if load_data:
            ext_shock.load_from_path(path)

        return ext_shock

    def make_from_id(self, id_: ExtensionShockIdentity) -> ExtensionShock:
        """
        Make an extension shock from an existing extension shock identity.

        The extension shock configuration is built according to the information
        contained in the given identity.

        Parameters:
            id_ (ExtensionShockIdentity):
                The identity describing the extension shock to build
        """
        log.debug(f"Make ExtensionShock object from id {id_.__dict__}")
        self._builder.build_id(id_=id_)
        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
            extension_categories=self._extension_categories,
        )
        return self._builder.get_extension_shock()

    def make_from_extensions(
        self, extension_from: Extension, extension_to: Extension
    ) -> ExtensionShock:
        """
        Make an extension shock from the difference between two extensions

        Parameters:
            extension_from (Extension):
                The reference extension
            extension_to (Extension):
                The projected extension

        Returns:
            ExtensionShock
        """
        log.debug(
            f"Make ExtensionShock object '{extension_from.name}' from "
            f"the difference of extensions"
        )

        self.set_regions(extension_from.regions)
        self.set_sectors(extension_from.sectors)
        self.set_final_demand_categories(
            extension_from.final_demand_categories
        )
        self.set_extension_categories(extension_from.extension_categories)
        self.set_id(
            id_=ExtensionShockIdentity(
                extension_name=extension_from.id.name,
                base_year=extension_from.id.base_year,
                proj_year=extension_to.id.base_year,
                scenario_name=extension_from.id.scenario_name,
            )
        )

        def feed_shock(shock_: ExtensionShock):
            for data_name in shock_.dataset.list_data():
                try:
                    shocks_tools.compute_shock_data(
                        shock_data=getattr(shock.dataset, data_name),
                        accounts_data_from=getattr(
                            extension_from.dataset, data_name[1:]
                        ),
                        accounts_data_to=getattr(
                            extension_to.dataset, data_name[1:]
                        ),
                    )
                except AttributeError:
                    log.debug(
                        f"No data related to '{data_name}' in extension. "
                        f"Skipping..."
                    )

        if extension_from.is_use_based():
            log.error(
                f"Construction of shock from a '{extension_from.calcul.name}' "
                f"extension is not implemented. Skipping..."
            )
            raise NotImplementedError

        if extension_from.is_gross_output_based():
            shock = self.make_shock_s_x(name=extension_from.id.name)
            feed_shock(shock)
            return shock

        if extension_from.is_embodied_in_import():
            shock = self.make_shock_m_row(name=extension_from.id.name)
            feed_shock(shock)
            return shock

        raise NotImplementedError

    def make_shock_s_x(self, name: str) -> ExtensionShock:
        """
        Make an extension shock with the components dS_x_dom

        Parameters:
            name (str):
                The name of the extension to shock
        Returns:
            ExtensionShock
        """
        data_list = [cst.D_S_X_DOM]
        return self.make_shock_from_data_list(name=name, data_list=data_list)

    def make_shock_s_y(self, name: str) -> ExtensionShock:
        """
        Make an extension shock with the components dS_Y

        Parameters:
            name (str):
                The name of the extension to shock
        Returns:
            ExtensionShock
        """
        data_list = [cst.D_S_Y]
        return self.make_shock_from_data_list(name=name, data_list=data_list)

    def make_shock_s_z(self, name: str) -> ExtensionShock:
        """
        Make an extension shock with the components dS_Z

        Parameters:
            name (str):
                The name of the extension to shock
        Returns:
            ExtensionShock
        """
        data_list = [cst.D_S_Z]
        return self.make_shock_from_data_list(name=name, data_list=data_list)

    def make_shock_m_row(self, name: str) -> ExtensionShock:
        """
        Make an extension shock with the components dM_RoW

        Parameters:
            name (str):
                The name of the extension to shock
        Returns:
            ExtensionShock
        """
        data_list = [cst.D_M_ROW]
        return self.make_shock_from_data_list(name=name, data_list=data_list)

    def make_shock_from_data_list(
        self, name: str, data_list: list
    ) -> ExtensionShock:
        self._id.extension_name = name
        self._builder.build_id(id_=self._id)
        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
            extension_categories=self._extension_categories,
            data_list=data_list,
        )
        return self._builder.get_extension_shock()


def get_director(reset: bool = False) -> ExtensionShockDirector:
    """
    Returns the `ExtensionShock` director singleton. If reset is True, call the
    director method reset() before returning it.
    """
    global extension_shock_director

    if extension_shock_director is None:
        extension_shock_director = ExtensionShockDirector()
    if reset:
        extension_shock_director.reset()
    return extension_shock_director


# pylint: enable=W0603
