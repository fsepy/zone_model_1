"""
Simple zone model implementation based on Zhang and Li (2012).

Author
------
Danny Hopkin (danny.hopkin@ofrconsultants.com)
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

import hrr as RHR
from charring import char_depth_integral
from heat_transfer_1d_plus_qinc import alpha_calc, HT_dx_dt_sub, update_wall_temp_array


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
    Ef = 1 - np.exp(-1.1 * h)
    return Ef


if __name__ == "__main__":
    # Set initial conditions
    b = 4  # room breadth in [m]
    d = 3  # room depth in [m]
    h = 2.4  # room height in [m]
    H_o = 1.8  # aggregate opening height in [m]
    B_o = 0.8  # aggregate opening width in [m]
    Tinf = 293  # Initial environment temperature condition in [K]
    Tf = 293  # Initial enclosure temperature condition in [K]
    Start_time = 0  # set start time for time array in [s]
    End_time = 7200
    wood_density = 450
    wood_Hoc = 17500
    ceiling_exposed = 0.999

    # Heat transfer properties
    c_p = 1000
    Ef = fire_emissivity(h)
    E_net = 0.8
    rho_air = 1

    # Fire properties
    growth_rate = 0.012
    HRRPUA = 290
    FLED = 570000
    conv_fract = 0.7

    # Define material properties and initial conditions for wall solver
    k = 0.12  # Thermal conductivity (W/m*K)
    rho = 750  # Density (kg/m^3)
    c = 1090  # Specific heat capacity (J/kg*K)
    T0_wall = 293  # Initial temperature of the plasterboard in Kelvin
    hc = 35  # Convective heat transfer coefficient (W/m^2*K)
    L = 0.1  # Thickness of the plasterboard (m)
    N = 101  # Number of spatial nodes
    sigma = 5.67e-8  # Stefan-Boltzmann constant (W/m^2*K^4)

    # Calculate thermal diffusivity
    alpha = alpha_calc(k, rho, c)

    # Define spatial and time steps
    dx, dt = HT_dx_dt_sub(L, N, alpha)
    steps = End_time / dt
    print(round(steps))

    # Initialise temperature array in Kelvin
    T = np.ones(N) * T0_wall  # Initial temperature distribution
    T_new = T.copy()  # Array for updated temperatures

    # Record temperature profiles over time for visualization
    T_history = []
    T_wall_surf = []

    # Calculate initial geometrical variables
    opening_area = H_o * B_o
    wall_area = (2 * (b + d) * h) - opening_area
    ceiling_area = b * d
    floor_area = b * d
    gas_volume = b * d * h

    # Define relationship between HRR and time
    HRR_time_arr, HRR_hrr_arr = RHR.time_vs_HRR(b, d, h, H_o, B_o, HRRPUA, growth_rate, FLED)
    HRR_hrr_arr = [x * 1000 for x in HRR_hrr_arr]  # Convert to Watts
    HRR_interp = interp1d(HRR_time_arr, HRR_hrr_arr)  # Interpolation function
    HRR_VC_lim = RHR.vent_cont_HRR(opening_area, H_o) * 1000

    # Create output storage arrays
    output_time_arr = []
    output_gas_temp_arr = []
    output_char_depth_arr = np.array([0])
    output_charring_rate_arr = []
    output_MLR_arr = []
    output_HRR_wood_arr = []
    output_HRR_total_arr = []
    output_HRR_ext_arr = []

    # Populate storage arrays with initial values
    output_time_arr.append(0)
    output_gas_temp_arr.append(Tf)
    output_charring_rate_arr.append(0)
    output_MLR_arr.append(0)
    output_HRR_wood_arr.append(0)
    output_HRR_total_arr.append(0)
    output_HRR_ext_arr.append(0)

    # Initialisation variables
    MLR = 0

    # Resolve energy balance
    for i in range(1, round(steps) + 1, 1):
        time = i * dt
        HRR_content = HRR_interp(time)
        HRR_wood = MLR * wood_Hoc * ceiling_area * ceiling_exposed * 1000

        HRR_total = HRR_wood + HRR_content
        HRR_total = min(HRR_total, HRR_VC_lim)
        HRR_total = max(HRR_total, 0)

        HRR_ext = max(0, (HRR_wood + HRR_content) - HRR_VC_lim)

        HRR = HRR_total * conv_fract

        q_rad_wall = wall_rad_hf(gas_volume, (1 - conv_fract), HRR) * (1 - Ef)

        T = update_wall_temp_array(T, T_new, T_history, alpha, dt, dx, hc, Tf, E_net, sigma, rho, c, N, q_rad_wall)
        Tw = T[0]

        Q_o_c = q_o_c_calc(H_o, opening_area, c_p, Tf, Tinf)
        Q_o_r = q_o_r_calc(opening_area, Ef, Tf, Tinf=0)
        Q_w_walls = q_w(Tf, Tw, hc, E_net) * wall_area
        Q_w_ceiling = q_w(Tf, Tw, hc, E_net) * ceiling_area
        Q_w_floor = q_w(Tf, Tw, hc, E_net) * floor_area
        Q_w = Q_w_walls + Q_w_ceiling + Q_w_floor

        Q_gas = gas_energy_balance(HRR, Q_w, Q_o_c, Q_o_r)
        dT_gas = delta_gas_temp(Q_gas, dt, rho_air, c_p, gas_volume)
        Tf = Tf + dT_gas
        Tf = max(293, Tf)

        output_time_arr.append(time)
        output_gas_temp_arr.append(Tf)
        T_wall_surf.append(T[0])

        # Get char depth
        output_time_arr_min = [x / 60 for x in output_time_arr]
        output_char_depth_arr = np.append(output_char_depth_arr,
                                          char_depth_integral(output_gas_temp_arr, output_time_arr_min))
        output_char_depth_arr = gaussian_filter1d(output_char_depth_arr, sigma=1.5)

        if Tf < 300 + 273 and time < 60:
            charring_rate = 0
        else:
            charring_rate = (output_char_depth_arr[i] - output_char_depth_arr[i - 1]) / (dt / 60)
        output_charring_rate_arr.append(charring_rate)

        MLR = (charring_rate / (60 * 1000)) * wood_density
        output_MLR_arr.append(MLR)
        output_HRR_wood_arr.append(HRR_wood)
        output_HRR_total_arr.append(HRR_total)
        output_HRR_ext_arr.append(HRR_ext)

        print(
            "Solving..........   Step = ", i, " Time = ", time, " s", " HRR = ", HRR / 1000, " Gas temp = ", Tf,
            'Incident HF to walls = ', q_rad_wall
        )

    # Plot output
    output_time_arr = [x / 60 for x in output_time_arr]
    output_gas_temp_arr = [x - 273 for x in output_gas_temp_arr]
    T_wall_surf = [x - 273 for x in T_wall_surf]
    HRR_time_arr = [x / 60 for x in HRR_time_arr]

    fig, ax1 = plt.subplots()
    ax1.plot(output_time_arr, output_gas_temp_arr, label='Gas')
    ax1.set_xlabel('Time [min]')
    ax1.set_ylabel('Temperature [$^o$C]')
    ax1.legend(framealpha=1, frameon=True)
    ax1.grid(which='major', color='#666666', linestyle='dotted')
    ax1.minorticks_on()
    fig.tight_layout()

    fig, ax2 = plt.subplots()
    ax2.plot(output_time_arr, output_char_depth_arr, label='Char')
    ax2.set_xlabel('Time [min]')
    ax2.set_ylabel('Char depth [mm]')
    fig.tight_layout()

    fig, ax3 = plt.subplots()
    ax3.plot(output_time_arr, output_charring_rate_arr, label='Char')
    ax3.set_xlabel('Time [min]')
    ax3.set_ylabel('Charring rate [mm/min]')
    fig.tight_layout()

    fig, ax4 = plt.subplots()
    ax4.plot(output_time_arr, output_MLR_arr, label='Char')
    ax4.set_xlabel('Time [min]')
    ax4.set_ylabel('MLR [kg/m$^2$/s]')
    fig.tight_layout()

    fig, ax5 = plt.subplots()
    ax5.plot(output_time_arr, output_HRR_wood_arr, label='wood')
    ax5.plot(HRR_time_arr, HRR_hrr_arr, label='contents')
    ax5.plot(output_time_arr, output_HRR_total_arr, label='total internal')
    ax5.plot(output_time_arr, output_HRR_ext_arr, label='total external')
    ax5.set_xlabel('Time [min]')
    ax5.set_ylabel('HRR [W]')
    ax5.legend(framealpha=1, frameon=True)
    ax5.set_xlim(0, (End_time / 60))
    fig.tight_layout()

    plt.show()
