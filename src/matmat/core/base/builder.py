"""
Presentation
************
This module contains the definition of abstract builder classes

Content
*******
- Classes:
    - :class:`AbstractBuilder`
    - :class:`AbstractDirector`
"""

__all__ = [
    "AbstractBuilder",
    "AbstractDirector",
]

from abc import ABC, abstractmethod
from typing import Literal, cast

from matmat.core.base.identity import AbstractBaseIdentity
from matmat.core.detail_level import core as dl


class AbstractBuilder(ABC):
    """
    Abstract base class for a Builder in the Builder design pattern.

    A Builder is responsible for constructing parts of a complex product.
    This class defines the interface and common functionality for all
    concrete Builders.
    """

    @abstractmethod
    def build_id(self, id_: AbstractBaseIdentity):
        """
        Set the identity of the product.

        Parameters:
            id_ (AbstractBaseIdentity): The identity to assign to the product.
        """
        raise NotImplementedError

    @abstractmethod
    def build_dataset(self, **kwargs):
        """
        Build the dataset for the product.

        Additional parameters may be required depending on the concrete Builder.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self):
        """
        Reset the product of the builder.
        """
        raise NotImplementedError


class AbstractDirector(ABC):
    """
    Abstract base class for a Director in the Builder design pattern.

    A Director is responsible for constructing complex products using
    a Builder instance. This class defines the interface and common
    functionality for all concrete Directors.

    Attributes:
        _builder (AbstractBuilder):
            The builder instance used to construct the product.
        _id (AbstractBaseIdentity):
            The identity of the product being built.
        _regions (dl.RegionsDL):
            Regions represented in the product.
        _sectors (dl.SectorsDL):
            Dataframe specifying the sectors represented in the product.
        _final_demand_categories (dl.FinalDemandCategoriesDL):
            Categories and subcategories of final demand.
        _extension_categories (dl.ExtensionCategoriesDL):
            Dataframe specifying the extension categories of the product.
    """

    _builder: AbstractBuilder
    _id: AbstractBaseIdentity

    def __init__(self):
        """
        Initialize the Director.

        This method initializes the builder and product identity,
        and sets the regions, sectors, and final demand categories to None.
        """
        # Builder instantiation
        self.init_builder()

        # Identity initialization
        self.init_id()

        # Index parameters
        self._regions: dl.RegionsDL = None
        self._sectors: dl.SectorsDL = None
        self._final_demand_categories: dl.FinalDemandCategoriesDL = None
        self._extension_categories: dl.ExtensionCategoriesDL = None

    @abstractmethod
    def init_builder(self):
        """
        Initialize the builder instance for the Director.

        Must be implemented by subclasses to instantiate the appropriate builder
        """
        raise NotImplementedError

    @abstractmethod
    def init_id(self):
        """
        Initialize the identity of the product to build.

        Must be implemented by subclasses to initialize the identity fields
        """
        raise NotImplementedError

    @abstractmethod
    def make_from_id(self, id_: AbstractBaseIdentity):
        """
        Construct the product using a given identity.

        Parameters:
            id_ (AbstractBaseIdentity):
                The identity used to build the product.
        """
        raise NotImplementedError

    @abstractmethod
    def make_from_path(self, path: str, load_data: bool = True):
        """
        Construct the product from a data source path.

        Parameters:
            path (str):
                Path to the data source.
            load_data (bool):
                Whether to load data immediately. (Default to True)
        """
        raise NotImplementedError

    def _load_detail_levels_from_path(self, path: str):
        """
        Call the `load_from_path` method of all the detail level
        objects

        Parameters:
            path (str):
                Path to the directory containing the "detail_levels" file
        """
        for dl_ in self.detail_levels:
            # Raise an error if missing sheets for sectors, regions,
            # final_demand_categories
            # Ignore errors for extension_categories
            dl_.load_from_path(
                path=path,
                missing_sheet_policy=cast(
                    Literal["ignore", "raise"],
                    (
                        "ignore"
                        if dl_.kind is dl.DetailLevelKind.EXTENSION_CATEGORIES
                        else "raise"
                    ),
                ),
            )

    @property
    def id(self):
        """
        Get the identity of the current product.
        """
        return self._id

    @property
    def detail_levels(self):
        """
        Iterate over all the detail level objects
        """
        for k, v in self.__dict__.items():
            if isinstance(v, dl.AbstractDetailLevel):
                yield v

    @property
    def regions(self):
        return self._regions

    @property
    def sectors(self):
        return self._sectors

    @property
    def final_demand_categories(self):
        return self._final_demand_categories

    @property
    def extension_categories(self):
        return self._extension_categories

    def reset(self):
        """
        Reset the Director to its initial state.

        Resets the builder, re-initializes the product identity,
        and clears regions, sectors, and final demand categories.
        """
        self._builder.reset()
        self.init_id()
        self._regions = None
        self._sectors = None
        self._final_demand_categories = None
        self._extension_categories = None

    def set_id(self, id_: AbstractBaseIdentity):
        """
        Set the identity of the product to build.

        Parameters:
            id_ (AbstractBaseIdentity):
                The identity card of the product
        """
        self._id = id_

    def set_regions(self, regions: dl.RegionsDL):
        """
        Set the regions of the product to build.

        A regions dataframe shall follow this structure:

        +----------+----------+
        | *origin* | *region* |
        +----------+----------+
        | domestic |     -    -
        +----------+----------+
        | domestic |     -    -
        +----------+----------+
        |  [...]   |     -    -
        +----------+----------+
        | import   |     -    -
        +----------+----------+
        | import   |     -    -
        +----------+----------+
        |  [...]   |     -    -
        +----------+----------+

        There may be no import part.

        Parameters:
            regions (dl.RegionsDL):
                The regions of the product
        """
        self._regions = regions

    def set_sectors(self, sectors: dl.SectorsDL):
        """
        Set the sectors of the product to build.

        A sectors dataframe shall follow this structure:

        +------------+----------------+----------+
        | *category* | *sub_category* | *sector* |
        +------------+----------------+----------+
        |     -      |        -       |    -     |
        +------------+----------------+----------+
        |     -      |        -       |    -     |
        +------------+----------------+----------+
        |     -      |        -       |    -     |
        +------------+----------------+----------+

        Parameters:
            sectors (dl.SectorsDL):
                The sectors of the product
        """
        self._sectors = sectors

    def set_final_demand_categories(
        self, final_demand_categories: dl.FinalDemandCategoriesDL
    ):
        """
        Set the categories and subcategories of the final demand
        of the product to build.

        Parameters:
            final_demand_categories (dl.FinalDemandCategoriesDL):
                The categories and subcategories of the final demand
        """
        self._final_demand_categories = final_demand_categories

    def set_extension_categories(self, categories: dl.ExtensionCategoriesDL):
        """
        Set the extension categories of the product to build.

        Parameters:
            categories (dl.ExtensionCategoriesDL):
                The categories represented in the extension product
        """
        self._extension_categories = categories
