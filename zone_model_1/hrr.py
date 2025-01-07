"""
Sub-routines for calculating internal HRR (Heat Release Rate).

Author
------
Danny Hopkin (danny.hopkin@ofrconsultants.com)
"""


def HRR_flash(At: float, Av: float, Hv: float) -> float:
    """
    Determine the HRR at flashover based on opening factor.

    .. math::
       Q_{fo} = 7.8 \\cdot A_t + 378 \\cdot A_v \\sqrt{H_v}

    :param At: Total surface area (excluding openings) [m^2].
    :param Av: Opening area [m^2].
    :param Hv: Opening height [m].
    :returns: HRR at flashover [kW].
    """
    Q_fo = (7.8 * At) + (378 * Av * (Hv ** 0.5))
    print(" Q_fo = ", Q_fo)
    return Q_fo


def Time_to_grow(growth_rate: float, HRR: float) -> float:
    """
    Calculate the time it takes to reach a target HRR under t-squared growth.

    .. math::
       t_{grow} = \\sqrt{\\frac{Q}{\\alpha}}

    :param growth_rate: Growth rate constant [kW/s^2].
    :param HRR: Target HRR [kW].
    :returns: Time to reach target HRR [s].
    """
    t_grow = (HRR / growth_rate) ** 0.5
    return t_grow


def FLE_grow(t_grow: float, growth_rate: float) -> float:
    """
    Calculate the fire load energy consumed during the growth phase.

    .. math::
       \\text{FLE}_{grow} = \\frac{1}{3} \\alpha \\cdot t_{grow}^3

    :param t_grow: Duration of the fire growth phase [s].
    :param growth_rate: Growth rate constant [kW/s^2].
    :returns: Energy consumed up to flashover [kJ].
    """
    FLE_growth = (1 / 3) * growth_rate * (t_grow ** 3)
    return FLE_growth


def vent_cont_HRR(Av: float, Hv: float) -> float:
    """
    Calculate the ventilation-controlled HRR.

    .. math::
       Q_{vc} = 1130 \\cdot A_v \\sqrt{H_v}

    :param Av: Opening area [m^2].
    :param Hv: Opening height [m].
    :returns: Ventilation-controlled HRR [kW].
    """
    Q_vc = 1130 * Av * (Hv ** 0.5)
    print(" Q_vc = ", Q_vc)
    return Q_vc


def fuel_cont_HRR(Af: float, HRRPUA: float) -> float:
    """
    Calculate the fuel-controlled HRR.

    .. math::
       Q_{fc} = A_f \\cdot \\text{HRRPUA}

    :param Af: Fire area [m^2].
    :param HRRPUA: Heat Release Rate per Unit Area [kW/m^2].
    :returns: Fuel-controlled HRR [kW].
    """
    Q_fc = Af * HRRPUA
    print(" Q_fc = ", Q_fc)
    return Q_fc


def steady_burn_time(FLE_grow_val: float, FLE: float, Q_max: float) -> float:
    """
    Calculate the steady burning duration in seconds.

    :param FLE_grow_val: Fire Load Energy consumed during growth phase [kJ].
    :param FLE: Total Fire Load Energy [kJ].
    :param Q_max: Maximum HRR [kW].
    :returns: Duration of steady burning [s].
    """
    t_steady = ((0.7 * FLE) - FLE_grow_val) / Q_max
    return t_steady


def decay_time(FLE: float, Q_max: float) -> float:
    """
    Calculate the decay phase duration in seconds.

    :param FLE: Total Fire Load Energy [kJ].
    :param Q_max: Maximum HRR [kW].
    :returns: Duration of decay phase [s].
    """
    t_decay = (0.6 * FLE) / Q_max
    return t_decay


def t_squared_fire(growth_rate: float, time: float) -> float:
    """
    Calculate the HRR at a given time assuming a t-squared fire growth model.

    .. math::
       Q(t) = \\alpha t^2

    :param growth_rate: Fire growth rate constant [kW/s^2].
    :param time: Time [s].
    :returns: HRR at the given time [kW].
    """
    HRR = growth_rate * (time ** 2)
    return HRR


def time_vs_HRR(b: float, d: float, h: float, H_o: float, B_o: float,
                HRRPUA: float, alpha: float, FLED: float) -> tuple[list[float], list[float]]:
    """
    Compute arrays of time vs. HRR using a piecewise approach:
    - Growth (t-squared)
    - Steady burning
    - Decay

    :param b: Room breadth [m].
    :param d: Room depth [m].
    :param h: Room height [m].
    :param H_o: Opening height [m].
    :param B_o: Opening width [m].
    :param HRRPUA: Heat release rate per unit area [kW/m^2].
    :param alpha: Growth rate [kW/s^2].
    :param FLED: Fire load energy density [kJ/m^2].
    :returns: A tuple of (HRR_time_arr, HRR_arr).

        - HRR_time_arr : List of times [s].
        - HRR_arr      : List of HRR values [kW] at those times.
    """
    # Calculate initial geometrical variables
    opening_area = H_o * B_o
    wall_area = (2 * (b + d) * h) - opening_area
    ceiling_area = b * d
    floor_area = b * d
    total_surf_area = wall_area + ceiling_area + floor_area

    # Total Fire Load Energy for entire floor area
    FLE = FLED * floor_area

    # Calculate key fire properties
    Q_fo = HRR_flash(total_surf_area, opening_area, H_o)  # [kW]
    Q_vc = vent_cont_HRR(opening_area, H_o)  # [kW]
    Q_fc = fuel_cont_HRR(floor_area, HRRPUA)  # [kW]

    # End of growth phase HRR and maximum HRR
    Q_end_grow = min(Q_fo, Q_vc, Q_fc)
    Q_max = min(Q_vc, Q_fc)

    print("Q at end of growth phase = ", Q_end_grow, "Qmax = ", Q_max)

    # Calculate time for growth, energy consumed, and durations of steady & decay phases
    t_grow = Time_to_grow(alpha, Q_end_grow)
    FLE_growth = FLE_grow(t_grow, alpha)
    t_steady = steady_burn_time(FLE_growth, FLE, Q_max)
    t_decay = decay_time(FLE, Q_max)

    # Initialise lists for output
    HRR_time_arr: list[float] = []
    HRR_arr: list[float] = []

    # Growth Phase
    for time_step in range(0, round(t_grow), 1):
        HRR_time_arr.append(float(time_step))
        HRR_arr.append(t_squared_fire(alpha, float(time_step)))

    # End of Growth Phase (add a point slightly past t_grow)
    HRR_time_arr.append(t_grow + 1)
    HRR_arr.append(Q_max)

    # Steady Burning (constant)
    HRR_time_arr.append(t_grow + t_steady)
    HRR_arr.append(Q_max)

    # Decay Phase (linearly drop to 0)
    HRR_time_arr.append(t_grow + t_steady + t_decay)
    HRR_arr.append(0.0)

    # Extend curve with a final time to ensure it goes flat to 0
    HRR_time_arr.append(14400.0)  # 4 hours in seconds
    HRR_arr.append(0.0)

    return HRR_time_arr, HRR_arr


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from sklearn.metrics import auc

    # Set initial conditions
    b = 3.6  # room breadth in [m]
    d = 2.4  # room depth in [m]
    h = 2.4  # room height in [m]
    H_o = 2  # aggregate opening height in [m]
    B_o = 1.  # aggregate opening width in [m]
    HRRPUA = 290
    alpha = 0.012
    FLED = 700000

    HRR_time_arr, HRR_arr = time_vs_HRR(b, d, h, H_o, B_o, HRRPUA, alpha, FLED)

    # Calculate area under curve to check inputs
    FLED_AUC = auc(HRR_time_arr, HRR_arr)
    # rint(FLED_AUC/ floor_area)

    fig, ax1 = plt.subplots()
    ax1.plot(HRR_time_arr, HRR_arr)
    ax1.set_xlim(0, 3600)
    plt.show()
