from matmat.core.data.strategies import structure, nature

import matmat.core.accounts.extension.data.core as data


class TestNullExtensionData:

    def test_get_nature_type(self):
        """
        Test function `get_nature_type`
        """
        assert data.NullExtensionData().get_nature_type() is nature.NatureNull

    def test_get_structure_type(self):
        """
        Test function `get_structure_type`
        """
        assert (
            data.NullExtensionData().get_structure_type()
            is structure.StructureNull
        )

    def test_is_null(self):
        """
        Test function `is_null`
        Expected results:
            - The function shall return True
        """
        data_ = data.NullExtensionData()
        assert data_.is_null() is True

    def test_constructor(self):
        """
        Test function `__init__`

        Instantiate an object `NullExtensionData` data

        Expected results:
            - data name shall be "null"
            - data reader shall be of type `NullReader`
        """
        data_ = data.NullExtensionData()
        assert data_.name == "null"
