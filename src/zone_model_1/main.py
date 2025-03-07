"""
This module provides a single entry point to access the fire model
without post-processing using matplotlib.
"""

import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
from tqdm import tqdm
import pandas as pd

import zone_model_1.hrr as RHR
from zone_model_1.char_regression import char_reg_HRR, char_density
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
from zone_model_1.heat_transfer_1d_plus_qinc import alpha_calc, ht_dx_dt_sub, update_wall_temp_array


def main(
        # Set initial conditions
        b: float = 3.4,  # Room breadth [m]
        d: float = 3.4,  # Room depth [m]
        h: float = 2.5,  # Room height [m]
        H_o: float = 1.8,  # Aggregate opening height [m]
        B_o: float = 0.7,  # Aggregate opening width [m]
        T_inf: float = 293.0,  # Initial outside ambient temperature [K]
        T_f: float = 293.0,  # Initial enclosure temperature [K]

        # Properties of the wood for combustion analysis
        wood_density: float = 450.0,
        wood_Hoc: float = 15500.0,
        ceiling_exposed: float = 1.74,
        regress: float = 0.7,
        char_HoC: float = 32000,

        # Heat transfer properties of gas
        c_p: float = 1000.0,
        E_net: float = 0.7,
        rho_air: float = 1.204,

        # Fire properties
        growth_rate: float = 0.012,
        HRRPUA: float = 290.0,
        FLED: float = 780000.0,
        FLED_combustion_eff: float = 0.8,
        conv_fract: float = 0.6,

        # Boundary solver properties
        # Walls
        k: float = 0.12,  # Thermal conductivity [W/(m·K)]
        rho: float = 750.0,  # Density [kg/m^3]
        c: float = 1090.0,  # Specific heat capacity [J/(kg·K)]
        T0_wall: float = 293.0,  # Initial wall temperature [K]
        L: float = 0.05,  # Thickness of the plasterboard [m]
        N: int = 51,  # Number of spatial nodes

        # Ceiling
        k_ceil: float = 0.12,  # Thermal conductivity [W/(m·K)]
        rho_ceil: float = 450.0,  # Density [kg/m^3]
        c_ceil: float = 1530.0,  # Specific heat capacity [J/(kg·K)]
        T0_ceil: float = 293.0,  # Initial wall temperature [K]
        L_ceil: float = 0.15,  # Thickness of the plasterboard [m]
        N_ceil: int = 101,  # Number of spatial nodes

        # floor
        k_floor: float = 1.6,  # Thermal conductivity [W/(m·K)]
        rho_floor: float = 2300.0,  # Density [kg/m^3]
        c_floor: float = 900.0,  # Specific heat capacity [J/(kg·K)]
        T0_floor: float = 293.0,  # Initial wall temperature [K]
        L_floor: float = 0.2,  # Thickness of the plasterboard [m]
        N_floor: int = 101,  # Number of spatial nodes

        # General
        hc: float = 35.0,  # Convective heat transfer coefficient [W/(m^2·K)]
        sigma: float = 5.67e-8  # Stefan-Boltzmann constant [W/(m^2·K^4)]
):
    """
    Runs the main zone model calculation without matplotlib-based post-processing.

    :param b: Room breadth [m].
    :param d: Room depth [m].
    :param h: Room height [m].
    :param H_o: Aggregate opening height [m].
    :param B_o: Aggregate opening width [m].
    :param T_inf: Initial ambient temperature [K].
    :param T_f: Initial enclosure temperature [K].
    :param wood_density: Density of wood [kg/m^3].
    :param wood_Hoc: Effective heat of combustion of wood [kJ/kg].
    :param ceiling_exposed: Fraction of ceiling area exposed to burning.
    :param regress: char regression rate [mm/min].
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
    alpha_wall = alpha_calc(k, rho, c)
    alpha_ceil = alpha_calc(k_ceil, rho_ceil, c_ceil)
    alpha_floor = alpha_calc(k_floor, rho_floor, c_floor)

    # Initialize temperature arrays for boundaries
    # Walls
    T = np.ones(N) * T0_wall
    T_new = T.copy()

    # Ceiling
    T_ceil = np.ones(N_ceil) * T0_ceil
    T_ceil_new = T_ceil.copy()

    # Floor
    T_floor = np.ones(N_floor) * T0_floor
    T_floor_new = T_floor.copy()

    # Arrays to record boundary temperature history
    T_history = []
    T_ceil_history = []
    T_floor_history = []

    # Enclosure geometry
    opening_area = H_o * B_o
    wall_area = (2.0 * (b + d) * h) - opening_area
    ceiling_area = b * d
    floor_area = b * d
    gas_volume = b * d * h

    # Fire load relationship
    HRR_prescribed = 'yes'
    # Calculate HRR with time
    HRR_time_arr, HRR_hrr_arr, ceiling_ignition_time, start_dec, end_dec = RHR.time_vs_hrr(b, d, h, H_o, B_o, HRRPUA, growth_rate, FLED * FLED_combustion_eff, conv_fract)

    # Option to prescribe HRR with time
    if HRR_prescribed =='yes':
        df_input_HRR = pd.read_excel("Input.xlsx")
        HRR_time_arr = df_input_HRR['Time_s']
        HRR_time_arr = HRR_time_arr.tolist()
        HRR_hrr_arr = df_input_HRR['HRR_kW']
        start_dec = 3585
        end_dec = 5400


    HRR_hrr_arr = [x * 1000 for x in HRR_hrr_arr]  # Convert kW to W
    HRR_interp = interp1d(HRR_time_arr, HRR_hrr_arr, kind="linear", fill_value="extrapolate")
    HRR_VC_lim = RHR.vent_cont_hrr(opening_area, H_o) * 1000  # Ventilation-controlled limit in W

    # Check end time
    end_time = HRR_time_arr[-1]

    # Char surface regression interp
    char_reg_time_arr = [0, start_dec, end_dec, end_time]
    char_reg_rate_arr = [0, 0, regress, regress]
    char_reg_interp = interp1d(char_reg_time_arr, char_reg_rate_arr, kind="linear", fill_value="extrapolate")

    # Define spatial and time steps
    dx_wall, dt1 = ht_dx_dt_sub(L, N, alpha_wall)
    dx_ceil, dt2 = ht_dx_dt_sub(L_ceil, N_ceil, alpha_ceil)
    dx_floor, dt3 = ht_dx_dt_sub(L_floor, N_floor, alpha_floor)
    dt = min(dt1, dt2, dt3)

    steps = end_time / dt
    print("Number of steps:", round(steps))

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
    output_gas_temp_arr.append(T_f)
    output_charring_rate_arr.append(0.0)
    output_MLR_arr.append(0.0)
    output_HRR_wood_arr.append(0.0)
    output_HRR_total_arr.append(0.0)
    output_HRR_ext_arr.append(0.0)

    # Initialize variables
    MLR = 0.0
    char_rho = 0

    # Main time-stepping loop
    for i in tqdm(range(1, round(steps) + 1)):
        time_s = i * dt
        HRR_content = HRR_interp(time_s)  # W

        # Lookup char regression rate
        Reg_rate = char_reg_interp(time_s) / (60 * 1000)

        if time_s > ceiling_ignition_time:
            HRR_char_reg = char_reg_HRR(char_rho, Reg_rate, char_HoC * 1000) * ceiling_area * ceiling_exposed
            HRR_struct = MLR * wood_Hoc * ceiling_area * ceiling_exposed * 1000.0  # Convert kW to W
            HRR_wood = HRR_struct + HRR_char_reg

        else:
            HRR_wood = 0

        # Limit total HRR by ventilation
        HRR_total = min(HRR_wood + HRR_content, HRR_VC_lim)
        HRR_total = max(HRR_total, 0.0)

        # Excess HRR escapes externally
        HRR_ext = max(0.0, (HRR_wood + HRR_content) - HRR_VC_lim)

        # Fraction of HRR that is convective
        HRR_conv = HRR_total * conv_fract

        # Incident radiation on walls (fraction that is radiative, minus fire emissivity)
        q_rad_wall = wall_rad_hf(gas_volume, (1.0 - conv_fract), HRR_conv) #* (1.0 - Ef)

        # Update boundary temperatures
        # Walls
        T = update_wall_temp_array(T, T_new, T_history, alpha_wall, dt, dx_wall, hc, T_f, E_net, sigma, rho, c, N, q_rad_wall)
        Ts_wall = T[0]

        # ceiling
        T_ceil = update_wall_temp_array(T_ceil, T_ceil_new, T_ceil_history, alpha_ceil, dt, dx_ceil, hc, T_f, E_net, sigma, rho_ceil, c_ceil, N_ceil, q_rad_wall)
        Ts_ceil = T_ceil[0]

        # floor
        T_floor = update_wall_temp_array(T_floor, T_floor_new, T_floor_history, alpha_floor, dt, dx_floor, hc, T_f, E_net, sigma, rho_floor, c_floor, N_floor, q_rad_wall)
        Ts_floor = T_floor[0]

        # Openings: convective & radiative losses
        Q_o_c = q_o_c_calc(H_o, opening_area, c_p, T_f, T_inf)
        Q_o_r = q_o_r_calc(opening_area, Ef, T_f, Tinf=0.0)

        # Heat loss to walls
        Q_w_walls = q_w(T_f, Ts_wall, hc, E_net) * wall_area
        Q_w_ceiling = q_w(T_f, Ts_ceil, hc, E_net) * ceiling_area
        Q_w_floor = q_w(T_f, Ts_floor, hc, E_net) * floor_area
        Q_w_total = Q_w_walls + Q_w_ceiling + Q_w_floor

        # Gas energy balance & temperature update
        Q_gas = gas_energy_balance(HRR_conv, Q_w_total, Q_o_c, Q_o_r)
        dT_gas = delta_gas_temp(Q_gas, dt, rho_air, c_p, gas_volume)
        T_f = max(293.0, T_f + dT_gas)

        # Store results
        output_time_arr.append(time_s)
        output_gas_temp_arr.append(T_f)

        # Compute char depth
        output_time_arr_min = [x / 60.0 for x in output_time_arr]
        output_char_depth_arr = np.append(
            output_char_depth_arr,
            char_depth_integral(output_gas_temp_arr, output_time_arr_min)
        )
        # Smooth char depth array
        output_char_depth_arr = gaussian_filter1d(output_char_depth_arr, sigma=1.5)

        if time_s < ceiling_ignition_time:
            charring_rate = 0.0
        else:
            charring_rate = (output_char_depth_arr[i] - output_char_depth_arr[i - 1]) / (dt / 60.0)
            # Update char density
            char_rho = char_density(output_char_depth_arr[i])
        output_charring_rate_arr.append(charring_rate)

        # Mass loss rate
        MLR = (charring_rate / (60.0 * 1000.0)) * wood_density
        output_MLR_arr.append(MLR)

        # Store HRR data
        output_HRR_wood_arr.append(HRR_wood)
        output_HRR_total_arr.append(HRR_total)
        output_HRR_ext_arr.append(HRR_ext)

    # Plot output
    output_time_arr = [x / 60 for x in output_time_arr]
    output_gas_temp_arr = [x - 273 for x in output_gas_temp_arr]
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
