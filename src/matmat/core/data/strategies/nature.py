"""
Overview
********
This module defines the different possible nature strategies for a data.
It defines an abstract class :class:`AbstractDataNature`, which is the
contract to be implemented, and then a set of subclasses to define the
concrete implementations of natures.

To simplify integration and maintenance, each nature is
encapsulated within a dedicated strategy class. A data object contains
a nature object responsible for the definition of the data nature.
The specific implementation of the nature depends on the nature
strategy class chosen.

Contents
********
- Classes:
  - :class:`AbstractDataNature`
  - :class:`NatureNull`
  - :class:`Flux`
  - :class:`Coefficient`
  - :class:`Unit`
"""

__all__ = [
    "AbstractDataNature",
    "NatureNull",
    "Flux",
    "Coefficient",
    "Unit",
]

from abc import ABC, abstractmethod

import pandas as pd

from matmat.core.bridge import core as bridge
from matmat.core.data.strategies.structure import AbstractDataStructure
from matmat.utils.errors import (
    MEAggregationOperationNotPossible,
)


class AbstractDataNature(ABC):
    """
    Abstract class for data nature strategy. It defines the contract to
    be implemented by subclasses.
    """

    @abstractmethod
    def aggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Aggregate a dataframe w.r.t. its structure and the
        given bridge matrix

        Parameters:
            df (pd.DataFrame):
                The dataframe to aggregate
            structure (AbstractDataStructure):
                The structure of the data to aggregate
            bridge_ (bridge.Bridge):
                The bridge to apply
        Returns:
            pd.DataFrame : the aggregated dataframe
        """

    @abstractmethod
    def disaggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Disaggregate a dataframe w.r.t. its structure and the
        given bridge matrix

        Parameters:
            df (pd.DataFrame):
                The dataframe to disaggregate
            structure (AbstractDataStructure):
                The structure of the data to disaggregate
            bridge_ (bridge.Bridge):
                The bridge to apply
        Returns:
            pd.DataFrame : the disaggregated dataframe
        """


class NatureNull(AbstractDataNature):
    """
    A null nature.
    This class overrides all methods to do nothing.
    """

    def aggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Returns the input dataframe unchanged
        """
        return df

    def disaggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Returns the input dataframe unchanged
        """
        return df


class Flux(AbstractDataNature):
    """
    The flux nature.

    A flux can only be aggregated, and not disaggregated.
    """

    def aggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Aggregate this flux dataframe by calling the associated method of the
        given structure

        Parameters:
            df (pd.DataFrame):
                Input data to be aggregated.
            structure (AbstractDataStructure):
                The structure of the data to aggregate
            bridge_ (bridge.Bridge):
                The bridge to apply

        Returns:
            pd.DataFrame:
                The aggregated dataframe

        Raises:
            NotImplementedError:
                Raised if the bridge type is unknown
        """
        return structure.apply_bridge_to_df(df=df, bridge_=bridge_)

    def disaggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Raises an error because a flux cannot be disaggregated

        Parameters:
            df (pd.DataFrame):
                The dataframe to disaggregate
            structure (AbstractDataStructure):
                The structure of the data to disaggregate
            bridge_: (bridge.Bridge):
                The bridge to apply
        Raises:
            MEAggregationOperationNotPossible
        """
        raise MEAggregationOperationNotPossible(
            operation="disaggregation", nature=self.__class__.__name__
        )


class Coefficient(AbstractDataNature):
    """
    The coefficient nature.

    A coefficient can only be disaggregated, and not aggregated.
    """

    def aggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Raises an error because a coefficient cannot be aggregated

        Parameters:
            df (pd.DataFrame):
                The dataframe to aggregate
            structure (AbstractDataStructure):
                The structure of the data to aggregate
            bridge_: (bridge.Bridge):
                The bridge to apply
        Raises:
            MEAggregationOperationNotPossible
        """
        raise MEAggregationOperationNotPossible(
            operation="aggregation", nature=self.__class__.__name__
        )

    def disaggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Disaggregate this coefficient dataframe by calling the associated
        method of the given structure

        Parameters:
            df (pd.DataFrame):
                Input data to be disaggregated.
            structure (AbstractDataStructure):
                The structure of the data to disaggregate
            bridge_ (bridge.Bridge):
                The bridge to apply

        Returns:
            pd.DataFrame:
                The disaggregated dataframe

        Raises:
            NotImplementedError:
                Raised if the bridge type is unknown
        """
        return structure.apply_bridge_to_df(df=df, bridge_=bridge_)


class Unit(AbstractDataNature):
    """
    The unit nature.

    A unit can be aggregated or disaggregated. However, there shall be
    consistency between the units aggregated / disaggregated together.

    The configuration parameter ALLOW_HETEROGENEOUS_AGGREGATION permits
    to allow or not the aggregation of data with different units.
    """

    def aggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Aggregate this flux dataframe by calling the aggregate method of the
        given structure

        Parameters:
            df (pd.DataFrame):
                Input data to be aggregated.
            structure (AbstractDataStructure):
                The structure of the data to aggregate
            bridge_ (bridge.Bridge):
                The bridge to apply

        Returns:
            pd.DataFrame:
                The aggregated dataframe

        Raises:
            NotImplementedError:
                Raised if the bridge type is unknown
        """
        return structure.apply_bridge_to_df(df=df, bridge_=bridge_)

    def disaggregate(
        self,
        df: pd.DataFrame,
        structure: AbstractDataStructure,
        bridge_: bridge.Bridge,
    ) -> pd.DataFrame:
        """
        Disaggregate this unit dataframe by calling the aggregate
        method of the given structure

        Parameters:
            df (pd.DataFrame):
                Input data to be disaggregated.
            structure (AbstractDataStructure):
                The structure of the data to disaggregate
            bridge_ (bridge.Bridge):
                The bridge to apply

        Returns:
            pd.DataFrame:
                The disaggregated dataframe

        Raises:
            NotImplementedError:
                Raised if the bridge type is unknown
        """
        return structure.apply_bridge_to_df(df=df, bridge_=bridge_)
