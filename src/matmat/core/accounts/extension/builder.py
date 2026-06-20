"""
Presentation
************
This module is the builder module of the package `accounts.extension`.

This module implements a design pattern **builder** to manage instantiation
of extension objects.

The Builder design pattern is used to construct complex objects step by
step, allowing greater flexibility in the creation process. In this pattern,
the Builder class (here :class:`ExtensionBuilder`) is responsible for defining
the individual steps to build different parts of an object. It encapsulates the
construction logic, ensuring that each component of the product is created
properly.

The Director class (here :class:`ExtensionDirector`), on the other hand,
orchestrates the sequence in which these construction steps are called,
ensuring that the object is assembled in the correct order. The Director is
in charge of managing the overall construction process but delegates the
actual building work to the Builder.

To instantiate an extension object, one shall retrieve the director
singleton (though :meth:`get_director`) and use the appropriate methods.

**NOTE:** only the class :class:`ExtensionDirector` is exported to other modules
as the builder class should not be used directly.

Content
*******
- Classes:
    - ExtensionBuilder
    - :class:`ExtensionDirector`
- Functions:
    - :meth:`get_director`
"""

__all__ = ["ExtensionDirector", "get_director"]

import os
import copy

from matmat.core.base.builder import AbstractBuilder, AbstractDirector
from matmat.core.detail_level import core as dl
from matmat.core.accounts.extension.core import Extension
from matmat.core.accounts.extension.identity import ExtensionIdentity
from matmat.core.accounts.extension.dataset.core import ExtensionDataSet
from matmat.core.accounts.extension.strategies import calcul
import matmat.utils.constants as cst
import matmat.utils.logging as log

# Director singleton
# pylint: disable=C0103
extension_director = None
# pylint: enable=C0103


# pylint: disable=W0212
# (authorize access to protected members for builder class)
class ExtensionBuilder(AbstractBuilder):
    """
    This class is a builder class which permits to build the components of a
    `Extension`.

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
    _result : Extension
        The result of the building process
    """

    def __init__(self):
        """
        Constructor of `ExtensionBuilder`
        """
        self._result: Extension = Extension()

    def reset(self):
        """
        Reset built extension
        """
        self._result = Extension()

    def build_id(self, id_: ExtensionIdentity):
        """
        Build extension identity card
        """
        self._result._id = copy.deepcopy(id_)

    def get_extension(self) -> Extension:
        """
        Returns the built extension
        """
        built_extension = self._result
        self.reset()
        return built_extension

    def build_dataset(
        self,
        regions: dl.RegionsDL,
        sectors: dl.SectorsDL,
        final_demand_categories: dl.FinalDemandCategoriesDL,
        extension_categories: dl.ExtensionCategoriesDL,
    ):
        self._result.dataset = ExtensionDataSet(
            regions=regions,
            sectors=sectors,
            final_demand_categories=final_demand_categories,
            extension_name=self._result.id.name,
            extension_categories=extension_categories,
            config__extension_calcul_strategy=self._result.id.strategy,
        )

    def build_calcul_strategy(self, strategy: str):
        """
        Build extension calcul strategy

        Parameters:
            strategy (str):
                the identifier of the strategy
        """
        self._result.calcul = strategy


# pylint: enable=W0212


class ExtensionDirector(AbstractDirector):
    """
    This class manages the building steps of a `Extension` object. It
    provides a set of methods used to build various kinds of extensions.

    Attributes
    ----------
    _builder : ExtensionBuilder
        The extension builder object which provides the building methods
        for each component
    _id : ExtensionIdentity
        The id card of the extension currently built
    """

    _builder: ExtensionBuilder
    _id: ExtensionIdentity

    def init_builder(self):
        self._builder = ExtensionBuilder()

    def init_id(self):
        self._id = ExtensionIdentity(
            extension_name="undefined",
            base_year=0,
            proj_year=None,
            scenario_name=None,
            strategy=cst.STRATEGY_USE_BASED,
        )

    def make(self, name: str, strategy: str) -> Extension:
        """
        Make an extension

        Parameters:
            name (str):
                The name of the extension
            strategy (str):
                The calcul strategy
        Returns:
            Extension
        """
        log.debug(f"Make {strategy} extension '{name}'")
        self._id.extension_name = name
        self._id.strategy = strategy
        self._build_extension()
        return self._builder.get_extension()

    def make_from_path(self, path: str, load_data: bool = True) -> Extension:
        """
        Make an extension from a directory. The directory shall contain:
            - the file **info.json**
            - the detail levels file
            - the extension data files

        The extension dataset configuration depends on the strategy given
        in the info file. Then, the data matching the strategy and found in
        **path** are loaded (if load_data is True).

        Example:
        ::
            {
                "name": "ghg_combustion",
                "strategy": "by_input"
                "regions": {"domestic": ["FR"], "import": ["RoW"]},
            }

        Parameters:
            path (str):
                The path to the directory
            load_data (bool):
                True if the dataframes shall be initialized with the values
                read in the files
        """
        log.debug(f"Make Extension object from path {path}")

        self._id.load_json(
            file_path=os.path.join(path, cst.FILE_INFO),
            required_keys=[
                cst.KEY_EXTENSION_NAME,
                cst.KEY_STRATEGY,
            ],
        )

        # Initialize and load detail levels
        self._regions = dl.RegionsDL()
        self._sectors = dl.SectorsDL()
        self._final_demand_categories = dl.FinalDemandCategoriesDL()
        self._extension_categories = dl.ExtensionCategoriesDL(extension_name=self._id.name)
        self._load_detail_levels_from_path(path=path)

        self._build_extension()

        extension = self._builder.get_extension()
        if load_data:
            extension.load_from_path(path=path)
        return extension

    def make_from_id(self, id_: ExtensionIdentity) -> Extension:
        """
        Make an extension from an existing extension identity.

        The extension configuration is built according to the information
        contained in the given identity.

        Parameters:
            id_ (ExtensionIdentity):
                The identity describing the extension to build
        """
        log.debug(f"Make Extension object from id {id_.__dict__}")
        self._id = id_
        self._build_extension()
        return self._builder.get_extension()

    def make_by_output_extension(self, name: str) -> Extension:
        """
        WARNING: DEPRECATED

        Make an extension with a gross_output_based calcul strategy and
        components S_x, S_xk, F_x, F_xk, M, M_k, d_cba, d_cba_k
        """
        log.warning(
            "The method 'make_by_output_extension' is DEPRECATED "
            "and shall not be used anymore. The strategy 'by_output'"
            "has been replaced by 'gross_output_based' "
            "and 'embodied_in_import'. "
            "See the method 'make_gross_output_based_extension' instead."
        )
        return self.make(
            name=name,
            strategy=calcul.EnumExtensionCalcul.GROSS_OUTPUT.value,
        )

    def make_gross_output_based_extension(self, name: str) -> Extension:
        """
        Make an extension with a gross_output_based calcul strategy and
        components S_x, S_x_k, F_x, F_x_k, M, M_k, d_cba, d_cba_k
        """
        return self.make(
            name=name,
            strategy=calcul.EnumExtensionCalcul.GROSS_OUTPUT.value,
        )

    def make_by_input_extension(self, name: str) -> Extension:
        """
        WARNING: DEPRECATED

        Make an extension with a use_based calcul strategy and
        components S_Y, F_Y, S_Z, F_Z,
        M, M_k, d_cba, d_cba_k
        """
        log.warning(
            "The method 'make_by_input_extension' is DEPRECATED "
            "and shall not be used anymore. The strategy 'by_input'"
            "has been replaced by 'use_based'. See the method"
            "'make_use_based_extension' instead."
        )
        return self.make(
            name=name,
            strategy=calcul.EnumExtensionCalcul.USE_BASED.value,
        )

    def make_use_based_extension(self, name: str) -> Extension:
        """
        Make an extension with a use_based calcul strategy and
        components S_Y, F_Y, S_Z, F_Z, M, M_k, d_cba, d_cba_k
        """
        return self.make(
            name=name,
            strategy=calcul.EnumExtensionCalcul.USE_BASED.value,
        )

    def make_embodied_in_import_extension(self, name: str) -> Extension:
        """
        Make an extension with a use_based calcul strategy and
        components M_RoW, d_imp, M, M_k, d_cba, d_cba_k
        """
        return self.make(
            name=name,
            strategy=calcul.EnumExtensionCalcul.EMBODIED_IN_IMPORT.value,
        )

    def _build_extension(self):
        self._builder.build_id(id_=self._id)

        self._builder.build_dataset(
            regions=self._regions,
            sectors=self._sectors,
            final_demand_categories=self._final_demand_categories,
            extension_categories=self._extension_categories,
        )

        self._builder.build_calcul_strategy(self._id.strategy)


# pylint: disable=W0603
def get_director(reset: bool = False) -> ExtensionDirector:
    """
    Returns the `Extension` director singleton. If reset is True, call the
    director method reset() before returning it.
    """
    global extension_director

    if extension_director is None:
        extension_director = ExtensionDirector()
    if reset:
        extension_director.reset()
    return extension_director


# pylint: enable=W0603
