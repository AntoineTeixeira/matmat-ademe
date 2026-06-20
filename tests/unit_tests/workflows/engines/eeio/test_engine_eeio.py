import os
import shutil
import pytest

from matmat.workflows.engines.eeio.core import EngineEEIO
from matmat.workflows.engines.eeio.identity import EngineEEIOIdentity
from matmat.core.detail_level import core as dl
from matmat.core.accounts import builder as a_builder
from matmat.utils import constants as cst

from tests.utils import constants as tests_cst


class TestEngineEEIO:

    # Constants
    TMP_INPUT_DIR = "./tmp_input"
    TMP_OUTPUT_DIR = "./tmp_output"
    BRIDGE_FILE = "bridge_matrices.xlsx"

    # Class variables
    id_: EngineEEIOIdentity

    @pytest.fixture(autouse=True)
    def setup(
        self,
        accounts_3,
        accounts_shock_1,
        bridge_regions_from_1_to_3,
        bridge_sectors_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
    ):
        self.generate_id()
        # Export accounts
        accounts_3.save_to_path(
            os.path.join(self.TMP_INPUT_DIR, EngineEEIO.KEY_ACCOUNTS),
            export_format=cst.FORMAT_PICKLE,
        )
        # Export shocks
        accounts_shock_1.save_to_path(
            os.path.join(self.TMP_INPUT_DIR, EngineEEIO.KEY_SHOCK),
            export_format=cst.FORMAT_PICKLE,
        )
        # Export bridges
        for bridge_ in (
            bridge_regions_from_1_to_3,
            bridge_sectors_from_1_to_3,
            bridge_fdc_from_1_to_3,
        ):
            bridge_.save_to_path(
                path=os.path.join(self.TMP_INPUT_DIR, EngineEEIO.KEY_BRIDGES),
                file_name=self.BRIDGE_FILE,
            )
        for ext_name in accounts_shock_1.extensions_shocks.keys():
            bridge_ext_cats_from_1_to_3.save_to_path(
                path=os.path.join(self.TMP_INPUT_DIR, EngineEEIO.KEY_BRIDGES),
                file_name=self.BRIDGE_FILE,
                sheet_name=ext_name,
            )

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.TMP_INPUT_DIR, ignore_errors=True)
        shutil.rmtree(cls.TMP_OUTPUT_DIR, ignore_errors=True)

    @classmethod
    def generate_id(cls):
        cls._id = EngineEEIOIdentity(
            path_in={
                EngineEEIO.KEY_ACCOUNTS: os.path.abspath(
                    os.path.join(cls.TMP_INPUT_DIR, EngineEEIO.KEY_ACCOUNTS)
                ),
                EngineEEIO.KEY_SHOCK: os.path.abspath(
                    os.path.join(cls.TMP_INPUT_DIR, EngineEEIO.KEY_SHOCK)
                ),
                EngineEEIO.KEY_BRIDGES: os.path.abspath(
                    os.path.join(
                        cls.TMP_INPUT_DIR,
                        EngineEEIO.KEY_BRIDGES,
                        cls.BRIDGE_FILE,
                    )
                ),
            },
            path_out=os.path.abspath(cls.TMP_OUTPUT_DIR),
            export_format=[cst.FORMAT_PICKLE],
            system_calcul_strategy=cst.STRATEGY_STANDARD,
            extension_names=[
                tests_cst.EXT_NAME_USE_BASED,
                tests_cst.EXT_NAME_GROSS_OUTPUT_BASED,
                tests_cst.EXT_NAME_EMBODIED_IN_IMPORT,
            ],
        )

    @staticmethod
    def set_input_data(
        engine: EngineEEIO,
        accounts_3,
        accounts_shock_1,
        bridge_regions_from_1_to_3,
        bridge_sectors_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
    ):
        engine.input_data[engine.KEY_ACCOUNTS] = accounts_3
        engine.input_data[engine.KEY_SHOCK] = accounts_shock_1
        engine.input_data[engine.KEY_BRIDGES] = {
            dl.DetailLevelKind.SECTORS.value: bridge_sectors_from_1_to_3,
            dl.DetailLevelKind.REGIONS.value: bridge_regions_from_1_to_3,
            dl.DetailLevelKind.FINAL_DEMAND_CATEGORIES.value: bridge_fdc_from_1_to_3,
            dl.DetailLevelKind.EXTENSION_CATEGORIES.value: {
                name: bridge_ext_cats_from_1_to_3.copy()
                for name in accounts_shock_1.extensions_shocks.keys()
            },
        }
        # Update sheet_name in ext_cats bridges
        for name, bridge_ in engine.get_input_data(
            [engine.KEY_BRIDGES, dl.DetailLevelKind.EXTENSION_CATEGORIES.value]
        ).items():
            bridge_.sheet_name = name

    @staticmethod
    def set_processed_data(
        engine: EngineEEIO,
        accounts_3,
        accounts_shock_3,
    ):
        engine.processed_data[engine.KEY_ACCOUNTS] = accounts_3.copy()
        engine.processed_data[engine.KEY_SHOCK] = accounts_shock_3.copy()

    @staticmethod
    def set_calculated_data(
        engine: EngineEEIO,
        accounts_3,
    ):
        engine.calculated_data[engine.KEY_ACCOUNTS] = accounts_3.copy()

    def test_load(self, mocker):
        """
        Test method `load`
        """

        spy_load_accounts = mocker.spy(EngineEEIO, "_load_accounts")
        spy_load_shock = mocker.spy(EngineEEIO, "_load_shock")
        spy_load_bridges = mocker.spy(EngineEEIO, "_load_bridges")

        engine = EngineEEIO(id_=self._id)
        engine.load()

        spy_load_accounts.assert_called_once()
        spy_load_shock.assert_called_once()
        spy_load_bridges.assert_called_once()

    def test_load_accounts(self, accounts_3):
        """
        Test method '_load_accounts'
        """
        engine = EngineEEIO(id_=self._id)
        engine._load_accounts()
        assert engine.get_input_data(engine.KEY_ACCOUNTS).equals(accounts_3)

    def test_load_shock(self, accounts_shock_1):
        """
        Test method '_load_shock'
        """
        engine = EngineEEIO(id_=self._id)
        engine._load_shock()
        assert engine.get_input_data(engine.KEY_SHOCK).equals(accounts_shock_1)

    def test_load_bridges(
        self,
        accounts_shock_1,
        bridge_regions_from_1_to_3,
        bridge_sectors_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
    ):
        """
        Test method '_load_bridges'
        """
        engine = EngineEEIO(id_=self._id)
        engine._load_bridges()
        assert engine.i_bridge_regions.equals(bridge_regions_from_1_to_3)
        assert engine.i_bridge_sectors.equals(bridge_sectors_from_1_to_3)
        assert engine.i_bridge_final_demand_categories.equals(
            bridge_fdc_from_1_to_3
        )
        for name in accounts_shock_1.extensions_shocks.keys():
            assert engine.get_i_bridge_extension_categories(
                extension_name=name
            ).equals(bridge_ext_cats_from_1_to_3)

    def test_process(
        self,
        accounts_3,
        accounts_shock_1,
        bridge_regions_from_1_to_3,
        bridge_sectors_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
        mocker,
    ):
        """
        Test method 'process'
        """
        spy_disaggregate_shock = mocker.spy(EngineEEIO, "_disaggregate_shock")
        spy_apply_calcul_strategies = mocker.spy(
            EngineEEIO, "_apply_calcul_strategies"
        )

        engine = EngineEEIO(id_=self._id)

        # Set inputs
        self.set_input_data(
            engine,
            accounts_3,
            accounts_shock_1,
            bridge_regions_from_1_to_3,
            bridge_sectors_from_1_to_3,
            bridge_fdc_from_1_to_3,
            bridge_ext_cats_from_1_to_3,
        )

        # Call function under test
        engine.process()

        spy_disaggregate_shock.assert_called_once()
        spy_apply_calcul_strategies.assert_called_once()

    def test_disaggregate_shock(
        self,
        accounts_shock_1,
        bridge_regions_from_1_to_3,
        bridge_sectors_from_1_to_3,
        bridge_fdc_from_1_to_3,
        bridge_ext_cats_from_1_to_3,
    ):
        """
        Test method '_disaggregate_shock'
        """
        engine = EngineEEIO(id_=self._id)

        # Set inputs
        self.set_input_data(
            engine,
            None,
            accounts_shock_1,
            bridge_regions_from_1_to_3,
            bridge_sectors_from_1_to_3,
            bridge_fdc_from_1_to_3,
            bridge_ext_cats_from_1_to_3,
        )

        # Call function under test
        engine._disaggregate_shock()

        # Compute reference
        test_shock = accounts_shock_1.copy()
        test_shock.disaggregate(bridge_regions_from_1_to_3)
        test_shock.disaggregate(bridge_sectors_from_1_to_3)
        test_shock.disaggregate(bridge_fdc_from_1_to_3)
        for ext_shock in test_shock.list_extensions_shocks():
            ext_shock.disaggregate(
                bridge_ext_cats_from_1_to_3, match_extension_name=False
            )

        # Compare
        assert test_shock.equals(engine.get_processed_data(engine.KEY_SHOCK))

    def test_apply_calcul_strategies(self, accounts_3):
        """
        Test method '_apply_calcul_strategies'
        """
        engine = EngineEEIO(id_=self._id)

        # Set inputs
        engine.input_data[engine.KEY_ACCOUNTS] = accounts_3.copy()

        # Call function under test
        engine._apply_calcul_strategies()

        assert (
            engine.get_processed_data(engine.KEY_ACCOUNTS).system.calcul.name
            == self._id.system_calcul_strategy
        )

    def test_calculate(self, accounts_3, accounts_shock_3, mocker):
        """
        Test method 'calculate'
        """
        spy_shock_accounts = mocker.spy(EngineEEIO, "_shock_accounts")
        spy_calculate_accounts = mocker.spy(EngineEEIO, "_calculate_accounts")

        engine = EngineEEIO(id_=self._id)

        # Set inputs
        self.set_processed_data(engine, accounts_3, accounts_shock_3)

        # Call function under test
        engine.calculate()

        spy_shock_accounts.assert_called_once()
        spy_calculate_accounts.assert_called_once()

    def test_shock_accounts(self, accounts_3, accounts_shock_3):
        """
        Test method '_shock_accounts'
        """
        engine = EngineEEIO(id_=self._id)

        # Set inputs
        self.set_processed_data(engine, accounts_3, accounts_shock_3)

        # Call function under test
        engine._shock_accounts()

        # Compute reference
        test_accounts = accounts_3.copy()
        test_shock = accounts_shock_3.copy()
        test_accounts.reset_for_shock()
        test_accounts.shock(shock=test_shock)

        # Compare
        assert test_accounts.equals(
            engine.get_calculated_data(engine.KEY_ACCOUNTS)
        )

    def test_calculate_accounts(self, accounts_3):
        """
        Test method '_calculate_accounts'
        """
        engine = EngineEEIO(id_=self._id)

        # Set inputs
        self.set_calculated_data(engine, accounts_3)

        # Call function under test
        engine._calculate_accounts()

        # Compute reference
        test_accounts = accounts_3.copy()
        test_accounts.calculate()

        # Compare
        assert test_accounts.equals(
            engine.get_calculated_data(engine.KEY_ACCOUNTS)
        )

    def test_save(self, accounts_3):
        """
        Test method 'save'
        """
        engine = EngineEEIO(id_=self._id)

        # Set inputs
        engine.calculated_data[engine.KEY_ACCOUNTS] = accounts_3.copy()

        # Call function under test
        engine.save()

        # Read exported accounts
        test_accounts = a_builder.get_director(reset=True).make_from_path(
            path=self._id.path_out
        )

        # Compare
        assert test_accounts.equals(
            engine.get_calculated_data(engine.KEY_ACCOUNTS)
        )
