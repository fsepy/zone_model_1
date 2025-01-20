"""
Simple zone model implementation based on Zhang and Li (2012).

Author
------
Danny Hopkin (danny.hopkin@ofrconsultants.com)
"""

import numpy as np


def q_o_c_calc(H_o: float, A_o: float, c_p: float, Tf: float, Tinf: float) -> float:
    """
    Calculate heat loss due to convective flow from openings (q_o_c).

    :param H_o: Opening height [m].
    :param A_o: Opening area [m^2].
    :param c_p: Specific heat of gas [J/(kg·K)].
    :param Tf: Gas temperature [K].
    :param Tinf: Ambient (external) temperature [K].
    :returns: Convective heat loss through the opening [W].
    """
    q_o_c = 0.5 * A_o * c_p * (Tf - Tinf) * np.sqrt(H_o)
    return q_o_c


def q_o_r_calc(A_o: float, Ef: float, Tf: float, Tinf: float) -> float:
    """
    Calculate heat loss by radiation through openings (q_o_r).

    :param A_o: Opening area [m^2].
    :param Ef: Emissivity of the fire [-].
    :param Tf: Gas (fire) temperature [K].
    :param Tinf: Ambient (external) temperature [K].
    :returns: Radiative heat loss through the opening [W].
    """
    q_o_r = A_o * Ef * 5.67e-8 * ((Tf ** 4) - (Tinf ** 4))
    return q_o_r


def q_w(Tf: float, Tw: float, hc: float, E_net: float) -> float:
    """
    Calculate heat flux to the wall (q_w) in [W/m^2].

    This includes both convection and radiation:

    :param Tf: Gas temperature [K].
    :param Tw: Wall surface temperature [K].
    :param hc: Convection coefficient for the wall [W/(m^2·K)].
    :param E_net: Net emissivity of both wall and fire [-].
    :returns: Heat flux [W/m^2] to the wall.
    """
    q_w_conv = hc * (Tf - Tw)
    q_w_rad = E_net * 5.67e-8 * ((Tf ** 4) - (Tw ** 4))
    return q_w_conv + q_w_rad


def gas_energy_balance(HRR: float, Q_w: float, Q_o_c: float, Q_o_r: float) -> float:
    """
    Compute net energy stored in the gas by enclosure energy balance.

    :param HRR: Fire heat release rate [W].
    :param Q_w: Total heat loss to walls [W].
    :param Q_o_c: Total convective losses from openings [W].
    :param Q_o_r: Total radiative losses from openings [W].
    :returns: Net heat stored in the gas [W].
    """
    Q_gas = HRR - (Q_w + Q_o_c + Q_o_r)
    return Q_gas


def delta_gas_temp(Q_gas: float, dt: float, rho_air: float, c_p: float, V_gas: float) -> float:
    """
    Calculate the change in lumped gas temperature.

    :param Q_gas: Net heat input to the gas [W].
    :param dt: Time step [s].
    :param rho_air: Density of air [kg/m^3].
    :param c_p: Specific heat of air [J/(kg·K)].
    :param V_gas: Volume of the gas in the enclosure [m^3].
    :returns: Temperature increment [K].
    """
    dT_gas = (Q_gas * dt) / (rho_air * c_p * V_gas)
    return dT_gas


def wall_rad_hf(gas_volume: float, rad_fraction: float, HRR: float) -> float:
    """
    Calculate the radiant heat flux to the walls.

    Approximates the enclosure volume as a sphere to find the characteristic
    path length of radiation:

    :param gas_volume: Volume of the gas in the enclosure [m^3].
    :param rad_fraction: Fraction of HRR that is radiative [-].
    :param HRR: Total heat release rate [W].
    :returns: Radiant heat flux [W/m^2].
    """
    rad_path_len = ((gas_volume * 3) / (4 * np.pi)) ** (1 / 3)
    q_rad = (rad_fraction * HRR) / (4 * np.pi * (rad_path_len ** 2))
    return q_rad


def fire_emissivity(h: float) -> float:
    """
    Calculate fire emissivity as a function of characteristic height.

    :param h: Characteristic fire height [m].
    :returns: Fire emissivity [-].
    """
    return 1 - np.exp(-1.1 * h)
