# from PD 7974-1:2019
import numpy as np


def Q_fo_600(A_t: float, A_v: float, H_v: float) -> float:
    return 7.8 * A_t + 378 * A_v * H_v ** 0.5


def Q_fo_500(A_t: float, A_v: float, H_v: float, h_k) -> float:
    return 610 * (h_k * A_t * A_v * H_v ** 0.5) ** 0.5


def eq_24_h_k(k_s, rho_s, c_p_s, t_f):
    return (k_s * rho_s * c_p_s / t_f) ** 0.5


def eq_31_m_dot_max(A_v, H_v) -> float:
    return 0.09 * A_v * H_v ** 0.5


def eq_33_Q_dot_max(A_v, H_v) -> float:
    """
    Ventilation-controlled HRR

    :param A_v:
    :param H_v:
    :return:
    """
    # todo: assert eq. 32
    return 1500 * A_v * H_v ** 0.5


def eq_36_t_steady(Q_fd, Q_dot_max, alpha, Q_fd_decay: float = 0.8) -> float:
    """The duration of steady state

    fuel consumed during growth phase + fuel consumed during steady state = 80 % total fuel

    fuel consumed during growth phase = (1/3) * alpha * t_v ** 3
    where t_v = (Q_dot_max / alpha) ** 0.5

    fuel consumed during steady state = t_steady * Q_dot_max

    80 % total fuel = 0.8 * Q_fd

    fuel consumed during steady state = 0.8 * Q_fd - (1/3) * alpha * t_v ** 3
    t_steady * Q_dot_max = 0.8 * Q_fd - (1/3) * alpha * t_v ** 3
    t_steady = [0.8 * Q_fd - (1/3) * alpha * t_v ** 3] / Q_dot_max

    :param Q_fd: total available fuel
    :param Q_dot_max: ventilation-controlled HRR
    :param alpha: growth factor
    :return:
    """
    t_v = (Q_dot_max / alpha) ** 0.5
    return (Q_fd_decay * Q_fd - (1 / 3) * alpha * t_v ** 3) / Q_dot_max


def eq_37_t_decay(Q_fd, Q_dot_max):
    return 0.4 * Q_fd / Q_dot_max


def calc_hrr(Q_fd, q_dot, A_t, A_v, H_v, alpha, Q_fd_decay=0.8, num_points=1000):
    """
    Calculate the fire HRR curve over time.

    Parameters:
    :param Q_fd: Total available fuel (e.g., in kJ)
    :param A_v: Ventilation area (m^2)
    :param H_v: Ventilation height (m)
    :param alpha: Growth factor (kW/s^2)
    :param Q_fd_decay: Decay fuel percentage (default is 0.8)
    :param num_points: Number of points in the time array (default is 1000)
    :return (t, Q_dot):
        t: NumPy array of time points
        Q_dot: NumPy array of HRR values corresponding to time points
    """
    # Compute peak HRR
    Q_dot_vent_max = eq_33_Q_dot_max(A_v, H_v)
    Q_dot_fuel_max = A_t * q_dot
    Q_dot_max = min(Q_dot_vent_max, Q_dot_fuel_max)

    # Compute duration of growth phase
    t_growth = (Q_dot_max / alpha) ** 0.5

    # Compute duration of steady state
    t_steady = eq_36_t_steady(Q_fd, Q_dot_max, alpha, Q_fd_decay)

    # Compute duration of decay
    t_decay = eq_37_t_decay(Q_fd, Q_dot_max)

    # Total duration
    t_total = t_growth + t_steady + t_decay

    # Generate time array with fixed intervals
    t = np.linspace(0, t_total, num_points)

    # Initialize HRR array
    Q_dot = np.zeros_like(t)

    # Growth phase: Q_dot = alpha * t^2
    mask_growth = t < t_growth
    Q_dot[mask_growth] = alpha * t[mask_growth] ** 2

    # At t = t_growth, ensure Q_dot equals Q_dot_max
    idx_t_growth = np.where(np.isclose(t, t_growth))[0]
    if idx_t_growth.size > 0:
        Q_dot[idx_t_growth] = Q_dot_max

    # Steady-state phase: Q_dot = Q_dot_max
    mask_steady = (t > t_growth) & (t <= t_growth + t_steady)
    Q_dot[mask_steady] = Q_dot_max

    # Decay phase: Linear decrease from Q_dot_max to 0 over t_decay
    mask_decay = t > t_growth + t_steady
    t_decay_phase = t[mask_decay] - (t_growth + t_steady)
    Q_dot[mask_decay] = Q_dot_max * (1 - t_decay_phase / t_decay)
    Q_dot[Q_dot < 0] = 0  # Ensure HRR doesn't go negative due to numerical errors

    return t, Q_dot


def calc_hrr_fo_capped(Q_fd, q_dot, A_t, A_v, H_v, alpha, Q_fd_decay=0.8, num_points=1000):
    """
    Calculate the fire HRR curve over time. Capped by fuel and flash over.

    Parameters:
    - Q_fd: Total available fuel (e.g., in kJ)
    - q_dot: HRR density (kW/sq.m)
    - A_t: Room floor area (m^2)
    - A_v: Ventilation area (m^2)
    - H_v: Ventilation height (m)
    - alpha: Growth factor (kW/s^2)
    - Q_fd_decay: Decay fuel percentage (default is 0.8)
    - num_points: Number of points in the time array (default is 1000)

    Returns:
    - t: NumPy array of time points
    - Q_dot: NumPy array of HRR values corresponding to time points
    """
    # Compute peak HRR
    Q_dot_fo_max = Q_fo_600(A_t, A_v, H_v)
    Q_dot_vent_max = eq_33_Q_dot_max(A_v, H_v)
    Q_dot_fuel_max = A_t * q_dot
    Q_dot_max = min(Q_dot_vent_max, Q_dot_fuel_max)

    # Compute duration of growth phase
    t_growth = (min(Q_dot_max, Q_dot_fo_max) / alpha) ** 0.5

    # Compute duration of steady state
    t_steady = eq_36_t_steady(Q_fd, Q_dot_max, alpha, Q_fd_decay)

    # Compute duration of decay
    t_decay = eq_37_t_decay(Q_fd, Q_dot_max)

    # Total duration
    t_total = t_growth + t_steady + t_decay

    # Generate time array with fixed intervals
    t = np.linspace(0, t_total, num_points)

    # Initialise HRR array
    Q_dot = np.zeros_like(t)

    # Growth phase: Q_dot = alpha * t^2
    mask_growth = t < t_growth
    Q_dot[mask_growth] = alpha * t[mask_growth] ** 2

    # At t = t_growth, ensure Q_dot equals Q_dot_max
    idx_t_growth = np.where(np.isclose(t, t_growth))[0]
    if idx_t_growth.size > 0:
        Q_dot[idx_t_growth] = Q_dot_max

    # Steady-state phase: Q_dot = Q_dot_max
    mask_steady = (t > t_growth) & (t <= t_growth + t_steady)
    Q_dot[mask_steady] = Q_dot_max

    # Decay phase: Linear decrease from Q_dot_max to 0 over t_decay
    mask_decay = t > t_growth + t_steady
    t_decay_phase = t[mask_decay] - (t_growth + t_steady)
    Q_dot[mask_decay] = Q_dot_max * (1 - t_decay_phase / t_decay)
    Q_dot[Q_dot < 0] = 0  # Ensure HRR doesn't go negative due to numerical errors

    return t, Q_dot
