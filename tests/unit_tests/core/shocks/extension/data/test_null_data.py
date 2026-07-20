from matmat.core.shocks.extension.data.core import NullExtensionShockData


class TestNullExtensionShockData:

    def test_is_null(self):
        """
        Test function `is_null`
        Expected results:
            - The function shall return True
        """
        data = NullExtensionShockData()
        assert data.is_null() is True

    def test_constructor(self):
        """
        Test function `__init__`

        Instantiate an object `NullExtensionShockData` data

        Expected results:
            - data name shall be "null"
        """
        data = NullExtensionShockData()
        assert data.name == "null"
