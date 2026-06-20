import os
import json
import shutil

from matmat.core.shocks import builder as shock_builder
from matmat.core.shocks.system.builder import SystemShockDirector
from matmat.core.shocks.extension.builder import ExtensionShockDirector
import matmat.utils.constants as cst

from tests.utils import builders, constants as tests_cst


class TestAccountsShockDirector:
    """
    Unit tests for class `AccountsShockDirector`.
    """

    TMP_FOLDER = "tmp_shocks"
    JSON_DICT_EXAMPLE_SYSTEM = {
        cst.KEY_BASE_YEAR: 2015,
    }
    JSON_DICT_EXAMPLE_EXTENSION = {
        cst.KEY_EXTENSION_NAME: tests_cst.DEFAULT_EXTENSION_CATEGORIES._sheet_name,
    }

    def test_make_from_path(self, mocker):
        """
        Test function `make_from_path`
        """
        ss_dir = shock_builder.get_director(reset=True)

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

        spy_sss = mocker.spy(SystemShockDirector, "make_from_path")
        spy_ses = mocker.spy(ExtensionShockDirector, "make_from_path")
        shock = ss_dir.make_from_path(path=self.TMP_FOLDER, load_data=True)
        shutil.rmtree(self.TMP_FOLDER)

        spy_sss.assert_called_once_with(
            ss_dir.system_shock_director,
            path=f"{self.TMP_FOLDER}/{cst.DIR_SYSTEM}",
            load_data=True,
        )
        assert spy_sss.spy_return is shock.system_shock

        spy_ses.assert_called_once_with(
            ss_dir.extension_shock_director, path=ext_path, load_data=True
        )
        assert spy_ses.spy_return is shock.get_extension_shock(
            self.JSON_DICT_EXAMPLE_EXTENSION[cst.KEY_EXTENSION_NAME]
        )
