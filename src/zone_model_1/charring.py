"""
Charring functions according to prEN 1995-1-2.

Author
------
Danny Hopkin (danny.hopkin@ofrconsultants.com)
"""

import numpy as np

try:
    from scipy.integrate import simpson as simps
except ImportError:
    # Fallback for older versions of SciPy
    from scipy.integrate import simps


def char_depth_integral(Temp: list[float], time: list[float]) -> float:
    """
    Compute the char depth by integrating temperature over time.

    This function calculates the char depth (d_char) based on the integral of
    squared temperatures over time, according to a simplified model:

    :param Temp: List of temperature values [K] at discrete time steps.
    :param time: List of time values [min] corresponding to the temperature values.
    :returns: The computed char depth [mm].
    """
    # Square the temperature values
    T_squared = [x ** 2 for x in Temp]
    # Numerical integration using Simpson’s rule
    simps_T_squared = simps(T_squared, time)
    # Compute char depth
    d_char = (simps_T_squared / 1.35e5) ** (1 / 1.6)
    return d_char


def standard_fire_curve(time_min: float) -> float:
    """
    Calculate the standard fire curve temperature at a given time.

    Uses the standard parametric function given in EN 1991-1-2 for fire
    temperatures over time. The result is:

    .. math::
       T_{SFC} = 345 \\cdot \\log_{10}(8 \\cdot t + 1) + 293

    :param time_min: Time in minutes since the start of the fire.
    :returns: Temperature [K] at the given time according to the standard fire curve.
    """
    return (345.0 * np.log10((8.0 * time_min) + 1.0)) + 293.0


if __name__ == "__main__":
    N = 60
    time_list = list(range(1, N + 1))
    temp_list = [standard_fire_curve(x) for x in time_list]
    integral = char_depth_integral(temp_list, time_list)
    assert abs(char_depth_integral(temp_list, time_list) - 49.617272031154265) < 1e-6, 'Unmatched char depth integral'
    print(integral)
