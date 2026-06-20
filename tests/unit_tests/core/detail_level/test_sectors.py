import pandas as pd

from matmat.core.detail_level import core as dl
from matmat.utils import constants as cst
from tests.unit_tests.core.detail_level.base import TestDetailLevel
from tests.utils import builders


class TestSectors(TestDetailLevel):

    def test_sectors_load_from_path(self):
        """
        Test function `load_from_path` for sectors detail levels

        Expected results:
            - The read matrix in the "sectors" sheet
              matches the one exported in the Excel file
        """

        dl_sectors = dl.SectorsDL()
        dl_sectors.load_from_path(self.dl_path)

        assert dl_sectors.df.equals(self.dl_sectors)

    def test_sectors_get_level_names(self):
        """
        Test function `get_level_names` for sectors detail levels

        Expected results:
            - The level names are equal to the columns titles
        """

        dl_sectors = dl.SectorsDL()
        dl_sectors.load_from_path(self.dl_path)

        assert (
            dl_sectors.get_level_names() == self.dl_sectors.columns.to_list()
        )

    def test_get_dl_as_df(self):
        """
        Test function `get_dl_as_df` for sectors detail levels

        Expected results:
            - The df is the same as the one exported in the Excel file
        """

        dl_sectors = dl.SectorsDL()
        dl_sectors.load_from_path(self.dl_path)

        assert dl_sectors.get_dl_as_df().equals(self.dl_sectors)

    def test_get_dl_as_multi_index(self):
        """
        Test function `get_dl_as_multi_index` for sectors detail levels

        Expected results:
            - The multi index obtained matches the one obtained from the
              df exported in the Excel file
        """

        dl_sectors = dl.SectorsDL()
        dl_sectors.load_from_path(self.dl_path)

        assert dl_sectors.get_dl_as_multi_index().equals(
            pd.MultiIndex.from_frame(self.dl_sectors)
        )

    def test_init_from_index(self):
        """
        Test function `init_from_index` for sectors detail levels

        Expected results:
            - The value of the detail level is properly initialized
              from the index
        """
        sectors_index = pd.MultiIndex.from_frame(builders.get_test_sectors().df)
        dl_sectors = dl.SectorsDL.init_from_index(sectors_index)

        assert dl_sectors.get_dl_as_multi_index().equals(sectors_index)

    def test_get_dl_as_multi_index_propagated_on(self):
        """
        Test function `get_dl_as_multi_index_propagated_on` for sectors detail
        levels

        Expected results:
            - The detail level is properly propagated on each row of the
              input dataframe
        """
        dl_sectors = dl.SectorsDL(
            df=self.dl_sectors
        )
        dl_regions = dl.RegionsDL(
            df=self.dl_regions
        )

        # Build reference dataframe
        df_template = pd.DataFrame(
            index=pd.MultiIndex.from_frame(self.dl_sectors),
            columns=pd.MultiIndex.from_frame(self.dl_sectors),
            dtype=cst.DTYPE_FLOAT
        )
        templates = []
        keys = []

        for region in dl_regions.get_domestic_regions_list():
            templates.append(df_template)
            keys.append((cst.IDX_DOMESTIC, region))
        domestic_df = pd.concat(
            templates,
            keys=keys,
            names=[cst.IDX_ORIGIN, cst.IDX_REGION],
        )

        templates = []
        keys = []
        for region in dl_regions.get_import_regions_list():
            templates.append(df_template)
            keys.append((cst.IDX_IMPORT, region))
        import_df = pd.concat(
            templates,
            keys=keys,
            names=[cst.IDX_ORIGIN, cst.IDX_REGION],
        )

        df_template = pd.concat(
            [domestic_df, import_df],
        )

        assert df_template.index.equals(
            dl_sectors.get_dl_as_multi_index_propagated_on(
                df_on=dl_regions.df
            )
        )
