__all__ = ["AbstractWorkflowIdentity"]

from abc import ABC
from dataclasses import dataclass
from pathlib import Path
import types

from matmat.utils import config
from matmat.core.base.identity import AbstractBaseIdentity


@dataclass(kw_only=True)
class AbstractWorkflowIdentity(AbstractBaseIdentity, ABC):
    """
    Attributes
    ----------
        path_in : str | Dict[str, str] | Dict[str, list[str]]
            Path(s) to the input data
            Example:
                {
                    "accounts": "adapters/accounts/input",
                    "shocks": "adapters/shocks/input"
                }
        path_out : str | Dict[str, str] | Dict[str, list[str]]
            Path to the output directories where the
            output data shall be stored
        export_format : str | list
            The format (or list of formats) in which the data files shall
            be exported (pickle, excel...)
        clean_path_out : bool
            Optional flag, default to None.
            If not given, then it will always be asked to the user if they
            want to clean the output path.
            If True, then the output path will be cleaned prior to the
            workflow execution. A confirmation will be required, depending
            on the CLI parameter "--no-confirm".
            If False, then the output path will not be cleaned prior to
            the workflow execution.
    """

    PREFIX_PATHS = "path_"

    path_in: str | dict[str, str] | dict[str, list[str]]
    path_out: str | dict[str, str] | dict[str, list[str]]
    export_format: str | list
    clean_path_out: bool = None

    @staticmethod
    def __append_data_dir(value):
        return str(Path(config.DATA_DIR).joinpath(value))

    def __post_init__(self):
        """
        Process paths in fields with PREFIX_PATHS prefix.

        Iterates over instance attributes and modifies paths in fields whose names
        start with PREFIX_PATHS. Converts string paths by appending data directory.
        Handles nested structures (dict, list) recursively.
        """
        for field_name, field_value in self.__dict__.items():
            if field_name.startswith(self.PREFIX_PATHS):
                if isinstance(field_value, str):
                    setattr(
                        self, field_name, self.__append_data_dir(field_value)
                    )
                elif isinstance(field_value, dict):
                    updated = types.SimpleNamespace()
                    for k, v in field_value.items():
                        if isinstance(v, str):
                            setattr(updated, k, self.__append_data_dir(v))
                        elif isinstance(v, list):
                            setattr(
                                updated,
                                k,
                                [
                                    (
                                        self.__append_data_dir(item)
                                        if isinstance(item, str)
                                        else item
                                    )
                                    for item in v
                                ],
                            )
                        elif isinstance(v, dict):
                            nested = {}
                            for nk, nv in v.items():
                                if isinstance(nv, str):
                                    nested[nk] = self.__append_data_dir(nv)
                                elif isinstance(nv, list):
                                    nested[nk] = [
                                        (
                                            self.__append_data_dir(item)
                                            if isinstance(item, str)
                                            else item
                                        )
                                        for item in nv
                                    ]
                                else:
                                    nested[nk] = nv
                            setattr(updated, k, nested)
                        else:
                            setattr(updated, k, v)
                    setattr(self, field_name, updated)
