from matmat.core.shocks.system.data.core import NullSystemShockData


class TestNullSystemShockData:

    def test_is_null(self):
        """
        Test function `is_null`
        Expected results:
            - The function shall return True
        """
        data = NullSystemShockData()
        assert data.is_null() is True

    def test_constructor(self):
        """
        Test function `__init__`

        Instantiate an object `NullSystemShockData` data

        Expected results:
            - data name shall be "null"
        """
        data = NullSystemShockData()
        assert data.name == "null"
