"""
This module provides a single entry point to access the fire model
without post-processing using matplotlib.
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
from tqdm import tqdm

import zone_model_1.hrr as RHR
from zone_model_1.charring import char_depth_integral
from zone_model_1.core import (
    q_o_c_calc,
    q_o_r_calc,
    q_w,
    gas_energy_balance,
    delta_gas_temp,
    wall_rad_hf,
    fire_emissivity
)
from zone_model_1.heat_transfer_1d_plus_qinc import alpha_calc, HT_dx_dt_sub, update_wall_temp_array


def main(
        # Set initial conditions
        b: float = 4.0,  # Room breadth [m]
        d: float = 3.0,  # Room depth [m]
        h: float = 2.4,  # Room height [m]
        H_o: float = 1.8,  # Aggregate opening height [m]
        B_o: float = 0.8,  # Aggregate opening width [m]
        Tinf: float = 293.0,  # Initial ambient temperature [K]
        Tf: float = 293.0,  # Initial enclosure temperature [K]
        start_time: float = 0.0,  # Start time for time array [s]
        end_time: float = 7200.0,  # End time [s]
        wood_density: float = 450.0,
        wood_Hoc: float = 17500.0,
        ceiling_exposed: float = 0.999,

        # Heat transfer properties
        c_p: float = 1000.0,
        E_net: float = 0.8,
        rho_air: float = 1.0,

        # Fire properties
        growth_rate: float = 0.012,
        HRRPUA: float = 290.0,
        FLED: float = 570000.0,
        conv_fract: float = 0.7,

        # Wall solver properties
        k: float = 0.12,  # Thermal conductivity [W/(m·K)]
        rho: float = 750.0,  # Density [kg/m^3]
        c: float = 1090.0,  # Specific heat capacity [J/(kg·K)]
        T0_wall: float = 293.0,  # Initial wall temperature [K]
        hc: float = 35.0,  # Convective heat transfer coefficient [W/(m^2·K)]
        L: float = 0.1,  # Thickness of the plasterboard [m]
        N: int = 101,  # Number of spatial nodes
        sigma: float = 5.67e-8  # Stefan-Boltzmann constant [W/(m^2·K^4)]
):
    """
    Runs the main zone model calculation without matplotlib-based post-processing.

    :param b: Room breadth [m].
    :param d: Room depth [m].
    :param h: Room height [m].
    :param H_o: Aggregate opening height [m].
    :param B_o: Aggregate opening width [m].
    :param Tinf: Initial ambient temperature [K].
    :param Tf: Initial enclosure temperature [K].
    :param start_time: Start time for the simulation [s].
    :param end_time: End time for the simulation [s].
    :param wood_density: Density of wood [kg/m^3].
    :param wood_Hoc: Effective heat of combustion of wood [kJ/kg].
    :param ceiling_exposed: Fraction of ceiling area exposed to burning.
    :param c_p: Specific heat of air/gas [J/(kg·K)].
    :param E_net: Net wall-fire emissivity [-].
    :param rho_air: Density of air [kg/m^3].
    :param growth_rate: Fire growth rate [kW/s^2].
    :param HRRPUA: Heat release rate per unit area [kW/m^2].
    :param FLED: Fire load energy density [kJ/m^2].
    :param conv_fract: Fraction of heat release that is convective [-].
    :param k: Thermal conductivity of plasterboard [W/(m·K)].
    :param rho: Density of plasterboard [kg/m^3].
    :param c: Specific heat capacity of plasterboard [J/(kg·K)].
    :param T0_wall: Initial temperature of the plasterboard [K].
    :param hc: Convective heat transfer coefficient for the wall [W/(m^2·K)].
    :param L: Thickness of the plasterboard [m].
    :param N: Number of 1D spatial nodes through the wall thickness.
    :param sigma: Stefan-Boltzmann constant [W/(m^2·K^4)].
    :returns: A tuple containing simulation results in the following order:
              (time_arr [min], gas_temp_arr [°C], char_depth_arr [mm],
              charring_rate_arr [mm/min], MLR_arr [kg/(m^2·s)], HRR_wood_arr [W],
              HRR_contents_arr [W], HRR_total_arr [W], HRR_external_arr [W]).
    """
    # Calculate fire emissivity based on height
    Ef = fire_emissivity(h)

    # Calculate thermal diffusivity
    alpha = alpha_calc(k, rho, c)

    # Define spatial and time steps
    dx, dt = HT_dx_dt_sub(L, N, alpha)
    steps = end_time / dt
    print("Number of steps:", round(steps))

    # Initialize temperature arrays
    T = np.ones(N) * T0_wall
    T_new = T.copy()

    # Arrays to record wall temperature history
    T_history = []
    T_wall_surf = []

    # Enclosure geometry
    opening_area = H_o * B_o
    wall_area = (2.0 * (b + d) * h) - opening_area
    ceiling_area = b * d
    floor_area = b * d
    gas_volume = b * d * h

    # Fire load relationship
    HRR_time_arr, HRR_hrr_arr = RHR.time_vs_HRR(b, d, h, H_o, B_o, HRRPUA, growth_rate, FLED)
    HRR_hrr_arr = [x * 1000 for x in HRR_hrr_arr]  # Convert kW to W
    HRR_interp = interp1d(HRR_time_arr, HRR_hrr_arr, kind="linear", fill_value="extrapolate")
    HRR_VC_lim = RHR.vent_cont_HRR(opening_area, H_o) * 1000  # Ventilation-controlled limit in W

    # Initialize output arrays
    output_time_arr = []
    output_gas_temp_arr = []
    output_char_depth_arr = np.array([0])
    output_charring_rate_arr = []
    output_MLR_arr = []
    output_HRR_wood_arr = []
    output_HRR_total_arr = []
    output_HRR_ext_arr = []

    # Populate with initial values
    output_time_arr.append(0.0)
    output_gas_temp_arr.append(Tf)
    output_charring_rate_arr.append(0.0)
    output_MLR_arr.append(0.0)
    output_HRR_wood_arr.append(0.0)
    output_HRR_total_arr.append(0.0)
    output_HRR_ext_arr.append(0.0)

    # Initialize variables
    MLR = 0.0

    # Main time-stepping loop
    for i in tqdm(range(1, round(steps) + 1)):
        time_s = i * dt
        HRR_content = HRR_interp(time_s)  # W
        HRR_wood = MLR * wood_Hoc * ceiling_area * ceiling_exposed * 1000.0  # Convert kJ to W

        # Limit total HRR by ventilation
        HRR_total = min(HRR_wood + HRR_content, HRR_VC_lim)
        HRR_total = max(HRR_total, 0.0)

        # Excess HRR escapes externally
        HRR_ext = max(0.0, (HRR_wood + HRR_content) - HRR_VC_lim)

        # Fraction of HRR that is convective
        HRR_conv = HRR_total * conv_fract

        # Incident radiation on walls (fraction that is radiative, minus fire emissivity)
        q_rad_wall = wall_rad_hf(gas_volume, (1.0 - conv_fract), HRR_conv) * (1.0 - Ef)

        # Update wall temperatures
        T = update_wall_temp_array(T, T_new, T_history, alpha, dt, dx, hc, Tf, E_net, sigma, rho, c, N, q_rad_wall)
        Tw = T[0]

        # Openings: convective & radiative losses
        Q_o_c = q_o_c_calc(H_o, opening_area, c_p, Tf, Tinf)
        Q_o_r = q_o_r_calc(opening_area, Ef, Tf, Tinf=0.0)

        # Heat loss to walls
        Q_w_walls = q_w(Tf, Tw, hc, E_net) * wall_area
        Q_w_ceiling = q_w(Tf, Tw, hc, E_net) * ceiling_area
        Q_w_floor = q_w(Tf, Tw, hc, E_net) * floor_area
        Q_w_total = Q_w_walls + Q_w_ceiling + Q_w_floor

        # Gas energy balance & temperature update
        Q_gas = gas_energy_balance(HRR_conv, Q_w_total, Q_o_c, Q_o_r)
        dT_gas = delta_gas_temp(Q_gas, dt, rho_air, c_p, gas_volume)
        Tf = max(293.0, Tf + dT_gas)

        # Store results
        output_time_arr.append(time_s)
        output_gas_temp_arr.append(Tf)
        T_wall_surf.append(T[0])

        # Compute char depth
        output_time_arr_min = [x / 60.0 for x in output_time_arr]
        output_char_depth_arr = np.append(
            output_char_depth_arr,
            char_depth_integral(output_gas_temp_arr, output_time_arr_min)
        )
        # Smooth char depth array
        output_char_depth_arr = gaussian_filter1d(output_char_depth_arr, sigma=1.5)

        # Charring rate
        if Tf < (300.0 + 273.0) and time_s < 60.0:
            charring_rate = 0.0
        else:
            charring_rate = (output_char_depth_arr[i] - output_char_depth_arr[i - 1]) / (dt / 60.0)
        output_charring_rate_arr.append(charring_rate)

        # Mass loss rate
        MLR = (charring_rate / (60.0 * 1000.0)) * wood_density
        output_MLR_arr.append(MLR)

        # Store HRR data
        output_HRR_wood_arr.append(HRR_wood)
        output_HRR_total_arr.append(HRR_total)
        output_HRR_ext_arr.append(HRR_ext)

        # print(
        #     f"Solving... Step = {i}, Time = {time_s:.1f} s, "
        #     f"HRR = {HRR_conv / 1000.0:.2f} kW, Gas temp = {Tf:.2f} K, "
        #     f"Incident HF to walls = {q_rad_wall:.2f} W/m^2"
        # )

    # Plot output
    output_time_arr = [x / 60 for x in output_time_arr]
    output_gas_temp_arr = [x - 273 for x in output_gas_temp_arr]
    T_wall_surf = [x - 273 for x in T_wall_surf]
    HRR_time_arr = [x / 60 for x in HRR_time_arr]

    return (
        output_time_arr,
        output_gas_temp_arr,
        output_char_depth_arr,
        output_charring_rate_arr,
        output_MLR_arr,
        output_HRR_wood_arr,
        output_HRR_total_arr,
        output_HRR_ext_arr,
        HRR_time_arr,
        HRR_hrr_arr,
    )
