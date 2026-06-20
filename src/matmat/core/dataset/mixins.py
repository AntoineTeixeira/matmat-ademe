"""
Presentation
************
This module contains mixins related to dataset manipulation,
to be reused throughout MatMat.

Content
*******
- Functions:
    - :class:`ToListMixin`
"""

__all__ = [
    "ToListMixin",
    "ComparisonMixin",
]

import pandas as pd

from matmat.core.data.core import AbstractData
from matmat.utils import logging as log, checks


class ToListMixin:

    def list_data(self) -> list[str]:
        """
        List the not null data

        Returns:
            list[str] : a list of string listing the data which are
            not null
        """
        list_data_not_null = []
        try:
            return self.dataset.list_data()
        except AttributeError:
            for attr_key, attr in self.__dict__.items():
                if isinstance(attr, AbstractData) and not attr.is_null():
                    if attr_key.startswith("_"):
                        list_data_not_null.append(attr_key[1:])
                    else:
                        list_data_not_null.append(attr_key)

            return list_data_not_null

    def list_null_data(self) -> list[str]:
        """
        List the null data

        Returns:
            list[str] : a list of string listing the data which are null
        """
        list_null_data = []
        try:
            return self.dataset.list_not_null_data()
        except AttributeError:
            for attr_key, attr in self.__dict__.items():
                if isinstance(attr, AbstractData) and attr.is_null():
                    if attr_key.startswith("_"):
                        list_null_data.append(attr_key[1:])
                    else:
                        list_null_data.append(attr_key)

            return list_null_data


class ComparisonMixin:

    def compare_with(self, other, threshold: float) -> dict[str, pd.DataFrame]:

        if type(self) is not type(other):
            raise TypeError(
                "Can only compare objects of same types. "
                f"Found {type(self)} and {type(other)}"
            )

        dict_diffs = {}

        for data_ref in self.dataset.data:
            if not data_ref.is_null():
                try:
                    data_test = getattr(other.dataset, data_ref.name)
                    log.verbose(f"Compare data {data_ref.name}")
                    if not data_test.is_null():
                        diff = checks.compare_dataframes(
                            df_ref=data_ref.df,
                            df_test=data_test.df,
                            threshold=threshold,
                        )
                        # Don't add empty diffs to avoid useless empty files
                        if not diff.isna().all().all():
                            dict_diffs[data_ref.name] = diff
                    else:
                        log.error(
                            f"Data {data_ref.name} is null in other "
                            f"object. Can't compare, passing..."
                        )
                except AttributeError:
                    log.debug(
                        f"Can't retrieve {data_ref.name} in other object. "
                        "Passing..."
                    )
                except TypeError:
                    log.debug(f"Can't compare {data_ref.name}. Passing...")

        return dict_diffs

    def check_zero_projections(self, projected) -> dict[str, pd.DataFrame]:

        if type(self) is not type(projected):
            raise TypeError(
                "Can only compare objects of same types. "
                f"Found {type(self)} and {type(projected)}"
            )

        dict_diffs = {}

        for data_ref in self.dataset.data:
            if not data_ref.is_null():
                try:
                    data_test = getattr(projected.dataset, data_ref.name)
                    log.verbose(f"Compare data {data_ref.name}")
                    diff = checks.compare_zero_reference(
                        df_ref=data_ref.df,
                        df_test=data_test.df,
                    )
                    # Don't add empty diffs to avoid useless empty files
                    if not diff.isna().all().all():
                        dict_diffs[data_ref.name] = diff
                except AttributeError:
                    log.debug(
                        f"Can't retrieve {data_ref.name} in projected system. "
                        "Passing..."
                    )
                except TypeError:
                    log.debug(f"Can't compare {data_ref.name}. Passing...")

        return dict_diffs
