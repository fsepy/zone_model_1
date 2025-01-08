"""
Localised Fire Model Functions

This module provides functions to compute localised fire parameters such as
flame length, virtual origin, and localised flame temperature, based on
heat release rate (HRR) and other fire characteristics.
"""

import numpy as np


def flame_length(HRR: float, diam: float) -> float:
    """
    Calculate the flame length for a localised fire.

    :param HRR: Heat release rate [W].
    :param diam: Diameter of the fire [m].
    :returns: Flame length [m].
    """
    lf = (-1.02 * diam) + (0.0148 * (HRR ** 0.4))
    return lf


def virt_orig(HRR: float, diam: float) -> float:
    """
    Calculate the virtual origin for a localised fire.

    :param HRR: Heat release rate [W].
    :param diam: Diameter of the fire [m].
    :returns: Virtual origin [m].
    """
    z_o = (-1.02 * diam) + (0.00524 * (HRR ** 0.4))
    return z_o


def local_flame_temp(HRR: float, conv_fract: float, z: float, z_o: float) -> float:
    """
    Calculate the localised flame temperature at height z.

    The localised flame temperature is limited to a maximum of 900 °C.

    :param HRR: Heat release rate [W].
    :param conv_fract: Convective fraction of the heat release rate [-].
    :param z: Vertical position above floor (or reference point) [m].
    :param z_o: Virtual origin height [m].
    :returns: Flame temperature [°C].
    """
    HRR_conv = HRR * conv_fract
    local_temp = 20 + (0.25 * (HRR_conv ** 0.66667) * ((z - z_o) ** (-5 / 3)))
    local_temp = min(local_temp, 900)
    return local_temp


def fire_dia(HRR: float, HRRPUA: float) -> float:
    """
    Compute the diameter of the fire based on HRR and HRR per unit area (HRRPUA).

    :param HRR: Heat release rate [W].
    :param HRRPUA: Heat release rate per unit area [W/m^2].
    :returns: Fire diameter [m].
    """
    fire_area = HRR / HRRPUA
    radius = (fire_area / np.pi) ** 0.5
    diam = 2 * radius
    return diam


def get_localised_fire(HRR: float, HRRPUA: float, conv_fract: float, z: float) -> tuple[float, float]:
    """
    Compute flame length and local flame temperature for a localised fire.

    :param HRR: Heat release rate [W].
    :param HRRPUA: Heat release rate per unit area [W/m^2].
    :param conv_fract: Convective fraction of the heat release rate [-].
    :param z: Vertical position for temperature evaluation [m].
    :returns: A tuple ``(flame_length, local_flame_temperature)``.
    """
    diam = fire_dia(HRR, HRRPUA)
    lf = flame_length(HRR, diam)
    z_o = virt_orig(HRR, diam)
    local_temp = local_flame_temp(HRR, conv_fract, z, z_o)
    return lf, local_temp


if __name__ == "__main__":
    HRR = 2000000
    HRRPUA = 250000
    conv_fract = 0.7
    z = 1.2

    lf, local_temp = get_localised_fire(HRR, HRRPUA, conv_fract, z)
    print(lf, local_temp)
