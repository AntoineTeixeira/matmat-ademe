import os

import pandas as pd
import numpy as np

from matmat.core.detail_level import core as dl
from matmat.core.bridge import core as bridge
from matmat.utils import constants as cst


class TestDirectBridge:

    bridge_file = "test_direct_bridge.xlsx"
    bridge_path = os.path.dirname(__file__)
    bridge_file_path = os.path.join(bridge_path, bridge_file)

    @classmethod
    def teardown_class(cls):
        try:
            os.remove(cls.bridge_file_path)
        except FileNotFoundError:
            pass

    def test_direct_bridge_diagonal(self):

        country_codes = ["AT", "BE", "DE", "LU", "FR", "PT"]
        country_names = [
            "Austria",
            "Belgium",
            "Germany",
            "Luxembourg",
            "France",
            "Portugal",
        ]

        direct_bridge_matrix = pd.DataFrame(
            {
                "code": country_codes,
                "name": country_names,
            }
        )
        direct_bridge_matrix.to_excel(
            self.bridge_file_path,
            sheet_name=dl.DetailLevelKind.REGIONS.value,
            index=False,
        )

        bridge_matrix_ref = pd.DataFrame(
            index=pd.MultiIndex.from_arrays([country_codes], names=["code"]),
            columns=pd.MultiIndex.from_arrays([country_names], names=["name"]),
            data=np.eye(len(country_codes)),
            dtype=cst.DTYPE_FLOAT,
        )

        direct_bridge = bridge.DirectBridge(
            kind=dl.DetailLevelKind.REGIONS,
            rows_level_names=["code"],
            columns_level_names=["name"],
        )
        direct_bridge.load_from_path(
            path=self.bridge_path, file_name=self.bridge_file
        )

        assert (
            direct_bridge.get_agg_matrix()
            .to_dataframe()
            .equals(bridge_matrix_ref)
        )

    def test_direct_bridge_groups(self):

        country_codes = ["AT", "BE", "DE", "LU", "FR", "PT", "USA"]
        regions = [
            "Rest Of Europe",
            "Rest Of Europe",
            "Rest Of Europe",
            "Rest Of Europe",
            "France",
            "Rest Of Europe",
            "America",
        ]

        direct_bridge_matrix = pd.DataFrame(
            {
                "code": country_codes,
                "region": regions,
            }
        )
        direct_bridge_matrix.to_excel(
            self.bridge_file_path,
            sheet_name=dl.DetailLevelKind.REGIONS.value,
            index=False,
        )

        bridge_matrix_ref = pd.DataFrame(
            index=pd.MultiIndex.from_arrays([country_codes], names=["code"]),
            columns=pd.MultiIndex.from_arrays(
                [regions], names=["regions"]
            ).drop_duplicates(),
            data=[
                [1, 0, 0],
                [1, 0, 0],
                [1, 0, 0],
                [1, 0, 0],
                [0, 1, 0],
                [1, 0, 0],
                [0, 0, 1],
            ],
            dtype=cst.DTYPE_FLOAT,
        )

        direct_bridge = bridge.DirectBridge(kind=dl.DetailLevelKind.REGIONS)
        direct_bridge.load_from_path(
            path=self.bridge_path, file_name=self.bridge_file
        )

        assert (
            direct_bridge.get_agg_matrix()
            .to_dataframe()
            .equals(bridge_matrix_ref)
        )

    def test_direct_bridge_groups_with_origin(self):

        origins = [
            "import",
            "import",
            "import",
            "import",
            "domestic",
            "import",
            "import",
        ]
        country_codes = ["AT", "BE", "DE", "LU", "FR", "PT", "USA"]
        regions = [
            "Rest Of Europe",
            "Rest Of Europe",
            "Rest Of Europe",
            "Rest Of Europe",
            "France",
            "Rest Of Europe",
            "America",
        ]

        direct_bridge_matrix = pd.DataFrame(
            {
                "origin": origins,
                "code": country_codes,
                "region": regions,
            }
        )
        direct_bridge_matrix.to_excel(
            self.bridge_file_path,
            sheet_name=dl.DetailLevelKind.REGIONS.value,
            index=False,
        )

        row_index = pd.MultiIndex.from_arrays(
            arrays=[
                [
                    "domestic",
                    "import",
                    "import",
                    "import",
                    "import",
                    "import",
                    "import",
                ],
                ["FR", "AT", "BE", "DE", "LU", "PT", "USA"],
            ],
            names=["origin", "code"],
        )
        col_index = pd.MultiIndex.from_arrays(
            arrays=[
                ["domestic", "import", "import"],
                ["France", "Rest Of Europe", "America"],
            ],
            names=["origin", "region"],
        )
        bridge_matrix_ref = pd.DataFrame(
            index=row_index,
            columns=col_index,
            data=[
                [1, 0, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 0, 1],
            ],
            dtype=cst.DTYPE_FLOAT,
        )

        direct_bridge = bridge.DirectBridge(kind=dl.DetailLevelKind.REGIONS)
        direct_bridge.load_from_path(
            path=self.bridge_path, file_name=self.bridge_file
        )

        assert (
            direct_bridge.get_agg_matrix()
            .to_dataframe()
            .equals(bridge_matrix_ref)
        )
