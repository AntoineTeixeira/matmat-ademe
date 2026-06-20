"""
Presentation
************
This module contains mixins to be reused throughout MatMat.

Content
*******
- Functions:
    - :class:`JsonMixin`
    - :class:`CopyMixin`
"""

__all__ = [
    "JsonMixin",
    "CopyMixin",
]

import copy
import os
import json
import types

from matmat.utils import checks
import matmat.utils.logging as log


class JsonMixin:
    """
    Mixin Json.
    Implements methods to deal with JSON data.
    """
    @classmethod
    def load_from_json(cls, file_path: str):
        log.debug(f"Make identity from JSON file {file_path}")
        with open(file_path, "r", encoding="utf-8") as json_file:
            json_dict = json.load(json_file)
        return cls(**json_dict)

    def load_json(
        self,
        file_path: str,
        required_keys: list,
        allow_stranger_keys: bool = False,
    ):
        log.debug(f"Load JSON file {file_path}")

        with open(file_path, "r", encoding="utf-8") as json_file:
            json_dict = json.load(json_file)

        for key in required_keys:
            checks.check_dict_key(json_dict, key)

        if not allow_stranger_keys:
            # Collect all attributes defined in the class and its parents
            allowed_keys = set()
            for cls in type(self).mro():  # mro() = Method Resolution Order
                allowed_keys.update(getattr(cls, "__annotations__", {}).keys())
            for k in json_dict.keys():
                if k not in allowed_keys:
                    raise AttributeError(f"JSON contains unknown attribute '{k}' "
                                         f"not defined in {type(self).__name__}"
                                         f"\nThe defined attributes are:"
                                         f" {allowed_keys}")

        for k, v in json_dict.items():
            log.debug(f"Set {k} to {v}")
            setattr(self, k, v)

    def to_json_file(self, folder_path: str, file_name: str):
        """
        Export the attributes to a JSON file

        Parameters:
            folder_path (str):
                The path to the directory where the file shall be exported
            file_name (str):
                The name of the file
        """
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)

        json_dict = self.to_json_dict()

        with open(
            os.path.join(folder_path, file_name), "w", encoding="utf-8"
        ) as write_file:
            json.dump(json_dict, write_file, indent=2)

    def to_json_dict(self):
        """
        Generate a dictionary from the attributes.
        Remove the leading underscore from the attributes if necessary

        Returns:
            dict
        """
        def serialize(attribute):
            if isinstance(attribute, types.SimpleNamespace):
                return vars(attribute)
            return attribute

        json_dict = {}
        for key, value in self.__dict__.items():
            clean_key = key[1:] if key[0] == "_" else key
            json_dict[clean_key] = serialize(value)

        return json_dict


class CopyMixin:
    """
    Mixin Copy.
    Define a copy() method to perform a deepcopy of an object.
    """

    def copy(self):
        """
        Returns a deepcopy of the object
        """
        return copy.deepcopy(self)
