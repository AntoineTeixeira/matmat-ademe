def check_specific_call_with_args(
    function_spy, call_number: int, args: list, kwargs: dict
):
    """
    Check that the call number {call_number} has been made with the expected arguments.

    *NOTE: this function is developed here as it is not natively included in Pytest mocker fixture*

    Parameters:
        function_spy:
            The spy on the function (fixture mocker of Pytest)
        call_number (int):
            The call number of the function (the first call is 1)
        args (list):
            The list of expected positional arguments
        kwargs (dict):
            The dictionary of expected named arguments
    Raises:
        AssertionError:
            If one the expected arguments does not match
    """
    assert call_number <= function_spy.call_count
    for index, argument in enumerate(args):
        value_to_compare = function_spy.call_args_list[call_number - 1].args[
            index
        ]
        try:
            assert value_to_compare is argument
        except AssertionError as e:
            # If equality by reference does not work, then
            # If value is primitive, try equality with '=='
            if type(argument) in [str, int, float, bool]:
                assert value_to_compare == argument
            # Else try equality with 'equals'
            else:
                assert value_to_compare.equals(argument)
    for key, value in kwargs.items():
        value_to_compare = function_spy.call_args_list[call_number - 1].kwargs[
            key
        ]
        try:
            assert value_to_compare is value
        except AssertionError as e:
            # If equality by reference does not work, then
            # If value is primitive, try equality with '=='
            if type(value) in [str, int, float, bool]:
                assert value_to_compare == value
            # Else try equality with 'equals'
            else:
                assert value_to_compare.equals(value)
