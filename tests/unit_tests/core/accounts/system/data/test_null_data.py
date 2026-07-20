from matmat.core.accounts.system.data.core import NullSystemData
from matmat.core.data.strategies import structure, nature


class TestNullSystemData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert NullSystemData().get_nature_type() is nature.NatureNull

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert NullSystemData().get_structure_type() is structure.StructureNull

    def test_is_null(self):
        """
        Test function `is_null`
        Expected results:
            - The function shall return True
        """
        data = NullSystemData()
        assert data.is_null() is True

    def test_constructor(self):
        """
        Test function `__init__`

        Instantiate an object `NullSystemData` data

        Expected results:
            - data name shall be "null"
            - data reader shall be of type `NullReader`
        """
        data = NullSystemData()
        assert data.name == "null"
