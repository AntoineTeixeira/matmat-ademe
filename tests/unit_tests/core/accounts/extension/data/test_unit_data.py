from matmat.core.data.strategies import structure, nature
import matmat.utils.constants as cst

import tests.utils.builders as builders
from tests.utils import constants as tests_cst


class TestUnitExtensionData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert (
            builders.build_test_extension_unit().get_nature_type()
            is nature.Unit
        )

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            builders.build_test_extension_unit().get_structure_type(
                strategy=cst.STRATEGY_USE_BASED
            )
            is structure.StructureUnitBySector
        )
        assert (
            builders.build_test_extension_unit().get_structure_type(
                strategy=cst.STRATEGY_GROSS_OUTPUT_BASED
            )
            is structure.StructureUnitByExtensionCategory
        )
        assert (
            builders.build_test_extension_unit().get_structure_type(
                strategy=cst.STRATEGY_EMBODIED_IN_IMPORT
            )
            is structure.StructureUnitByExtensionCategory
        )
