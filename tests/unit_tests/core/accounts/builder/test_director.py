import os
import shutil
import json

from matmat.core.accounts import builder as acc_builder
from matmat.core.accounts.system import builder as sys_builder
from matmat.core.accounts.extension import builder as ext_builder
from matmat.core.accounts.system.strategies.calcul import EnumSystemCalcul
from matmat.core.accounts.extension.strategies.calcul import (
    EnumExtensionCalcul,
)
import matmat.utils.constants as cst

from tests.utils import builders, constants as tests_cst


class TestAccountsDirector:
    """
    Unit tests for class `AccountsDirector`.
    """

    TMP_FOLDER = "tmp_accounts"
    JSON_DICT_EXAMPLE_SYSTEM = {
        cst.KEY_BASE_YEAR: 2015,
        cst.KEY_STRATEGY: EnumSystemCalcul.STANDARD.value,
    }
    JSON_DICT_EXAMPLE_EXTENSION = {
        cst.KEY_EXTENSION_NAME: tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name,
        cst.KEY_STRATEGY: EnumExtensionCalcul.USE_BASED.value,
    }

    def test_make_from_path(self, mocker):
        """
        Test function `make_from_path`
        """
        sa_dir = acc_builder.get_director(reset=True)

        if os.path.isdir(self.TMP_FOLDER):
            shutil.rmtree(self.TMP_FOLDER)

        # Set up files to read from
        # info.json files
        os.makedirs(f"{self.TMP_FOLDER}/{cst.DIR_SYSTEM}")
        with open(
            f"{self.TMP_FOLDER}/{cst.DIR_SYSTEM}/{cst.FILE_INFO}", "w"
        ) as write_file:
            json.dump(self.JSON_DICT_EXAMPLE_SYSTEM, write_file, indent=2)

        ext_path = f"{self.TMP_FOLDER}/{cst.DIR_EXTENSIONS}/{self.JSON_DICT_EXAMPLE_EXTENSION[cst.KEY_EXTENSION_NAME]}"
        os.makedirs(ext_path)
        with open(f"{ext_path}/{cst.FILE_INFO}", "w") as write_file:
            json.dump(self.JSON_DICT_EXAMPLE_EXTENSION, write_file, indent=2)

        # detail levels files
        for path in [
            os.path.join(self.TMP_FOLDER, cst.DIR_SYSTEM),
            ext_path,
        ]:
            tests_cst.DEFAULT_REGIONS.save_to_path(path=path)
            builders.get_test_sectors().save_to_path(path=path)
            tests_cst.DEFAULT_Y_CATEGORIES.save_to_path(path=path)
        tests_cst.DEFAULT_EXTENSION_CATEGORIES.save_to_path(path=ext_path)

        spy_ss = mocker.spy(sys_builder.SystemDirector, "make_from_path")
        spy_se = mocker.spy(ext_builder.ExtensionDirector, "make_from_path")

        # Call method under test
        accounts = sa_dir.make_from_path(path=self.TMP_FOLDER, load_data=True)
        shutil.rmtree(self.TMP_FOLDER)

        spy_ss.assert_called_once_with(
            sa_dir.system_director,
            path=f"{self.TMP_FOLDER}/{cst.DIR_SYSTEM}",
            load_data=True,
        )
        assert spy_ss.spy_return is accounts.system
        spy_se.assert_called_once_with(
            sa_dir.extension_director, path=f"{ext_path}", load_data=True
        )
        assert spy_se.spy_return is accounts.get_extension(
            self.JSON_DICT_EXAMPLE_EXTENSION[cst.KEY_EXTENSION_NAME]
        )

    def test_make_from_system_and_extensions(self):
        """
        Test function `make_from_system_and_extensions`
        """
        sys_dir = sys_builder.get_director(reset=True)
        ext_dir = ext_builder.get_director(reset=True)
        acc_dir = acc_builder.get_director(reset=True)

        for director in sys_dir, ext_dir:
            director.set_regions(tests_cst.DEFAULT_REGIONS)
            director.set_sectors(builders.get_test_sectors())
            director.set_final_demand_categories(
                tests_cst.DEFAULT_Y_CATEGORIES
            )
        ext_dir.set_extension_categories(
            tests_cst.DEFAULT_EXTENSION_CATEGORIES
        )

        system = sys_dir.make_standard_system()
        extension_1 = ext_dir.make_use_based_extension(name="extension_1")
        extension_2 = ext_dir.make_gross_output_based_extension(
            name="extension_2"
        )
        extension_3 = ext_dir.make_embodied_in_import_extension(
            name="extension_3"
        )

        accounts = acc_dir.make_from_system_and_extensions(
            system=system,
            extensions={
                extension_1.name: extension_1,
                extension_2.name: extension_2,
                extension_3.name: extension_3,
            },
        )

        assert accounts.system is system
        assert len(accounts.extensions) == 3
        assert accounts.get_extension(extension_1.name) is extension_1
        assert accounts.get_extension(extension_2.name) is extension_2
        assert accounts.get_extension(extension_3.name) is extension_3
