import os

from matmat.core.data.strategies import structure, nature
import matmat.utils.constants as cst

import tests.utils.builders as builders
from tests.utils import constants as tests_cst


class TestUnitSystemData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert (
            builders.build_test_system_unit().get_nature_type() is nature.Unit
        )

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_system_unit().get_structure_type()
            is structure.StructureUnitBySector
        )

    def test_load_from_excel(self):
        """
        Test function `load_from_path`

        Expected results:
            - Create an excel file from a dataframe (df_ref) and check
              that the function `initialize` applied
              to this file set the dataframe to the dataframe (df_ref)
        """
        path_to_init_dir = "./"
        unit_ref = builders.build_test_system_unit()
        path_to_init_file = f"{path_to_init_dir}/{unit_ref.name}.xlsx"
        builders.randomize_string_df(unit_ref.df)
        df_ref = unit_ref.df
        df_ref.to_excel(path_to_init_file)

        unit_test = builders.build_test_system_unit()
        unit_test.load_from_path(path=path_to_init_dir)

        os.remove(path_to_init_file)

        assert unit_test.equals(unit_ref)

    def test_load_from_csv(self):
        """
        Test function `load_from_path`

        Expected results:
            - Create a csv file from a dataframe (df_ref) and check
              that the function `initialize` applied
              to this file set the dataframe to the dataframe (df_ref)
        """
        path_to_init_dir = "./"
        unit_ref = builders.build_test_system_unit()
        path_to_init_file = f"{path_to_init_dir}/{unit_ref.name}.csv"
        builders.randomize_string_df(unit_ref.df)
        df_ref = unit_ref.df
        df_ref.to_csv(path_to_init_file)

        unit_test = builders.build_test_system_unit()
        unit_test.load_from_path(path=path_to_init_dir)

        os.remove(path_to_init_file)

        assert unit_test.equals(unit_ref)
