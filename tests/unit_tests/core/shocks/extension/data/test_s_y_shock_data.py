from matmat.core.data.strategies import structure, nature
import matmat.utils.constants as cst

from tests.utils import builders


class TestSyShockData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`

        Expected results:
            - Check that the nature type is properly returned
        """
        data_ = builders.build_test_extension_shock_data(name=cst.D_S_Y)
        assert data_.get_nature_type() is nature.Coefficient

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`

        Expected results:
            - Check that the structure type is properly returned
        """
        data_ = builders.build_test_extension_shock_data(name=cst.D_S_Y)
        assert data_.get_structure_type() is structure.StructureY
