import pybamm
from utils.desired_decimal_point_generator import (
    desired_decimal_point_generator
)


# implementation by @tinosulzer
class FunctionLike:
    "Behaves like a function but saves fun and parameter"

    def __init__(self, fun, parameter):
        self.fun = fun
        self.parameter = parameter

    def __call__(self, *args):
        return self.parameter * self.fun(*args)


def parameter_value_generator(
    chemistry,
    parameter,
    lower_bound=None,
    upper_bound=None,
):
    """
    Generates random values for a given parameter and
    for a given chemistry.
    Parameters:
        chemistry: dict
        parameter: str
        lower_bound: numerical
        upper_bound: numerical
    Returns:
        params: pybamm.ParameterValues
    """
    params = pybamm.ParameterValues(chemistry=chemistry)

    if callable(params[parameter]):
        base_value = 1
        new_parameter_value = desired_decimal_point_generator(
            lower_bound if lower_bound is not None else base_value*0.5,
            upper_bound if upper_bound is not None else base_value*2,
            2
        )
        params[parameter] = FunctionLike(
            params[parameter], new_parameter_value
        )
    else:
        base_value = params[parameter]
        new_parameter_value = desired_decimal_point_generator(
            lower_bound if lower_bound is not None else base_value*0.5,
            upper_bound if upper_bound is not None else base_value*2,
            2
        )
        params[parameter] = new_parameter_value

    return params
