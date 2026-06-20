import json

import matmat.utils.constants as cst


def dump_dict(dict_: dict,
              path: str = ".",
              json_file: str = cst.FILE_INFO):
    with open(f"{path}/{json_file}", "w", encoding="utf-8") as write_file:
        json.dump(dict_, write_file, indent=2)
