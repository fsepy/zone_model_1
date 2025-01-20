"""
Simple zone model implementation based on Zhang and Li (2012).
No wall heat transfer solution.

Author
------
Danny Hopkin (danny.hopkin@ofrconsultants.com)
"""

import numpy as np


def update_wall_temp_array(
        T: np.ndarray,
        T_new: np.ndarray,
        T_history: list[np.ndarray],
        alpha: float,
        dt: float,
        dx: float,
        h: float,
        Tg: float,
        epsilon: float,
        sigma: float,
        rho: float,
        c: float,
        N: int,
        q_inc: float
) -> np.ndarray:
    """
    Update the 1D wall temperature distribution using a finite difference approach.

    The function computes a new temperature distribution for each node within
    the wall, assuming constant thermal properties. Convective and radiative
    boundary conditions are imposed at the exposed surface, and an insulated
    boundary is assumed at the opposite surface.

    :param T: Current temperature distribution [K] (1D array of length N).
    :param T_new: Array for storing updated temperature distribution [K].
    :param T_history: List to which updated temperature distributions will be appended.
    :param alpha: Thermal diffusivity [m^2/s].
    :param dt: Time step [s].
    :param dx: Spatial step [m].
    :param h: Convective heat transfer coefficient [W/(m^2·K)].
    :param Tg: Gas temperature [K].
    :param epsilon: Surface emissivity [-].
    :param sigma: Stefan-Boltzmann constant [W/(m^2·K^4)].
    :param rho: Density of wall material [kg/m^3].
    :param c: Specific heat capacity of wall material [J/(kg·K)].
    :param N: Number of nodes in the 1D discretization.
    :param q_inc: Incident radiant heat flux [W/m^2].
    :returns: Updated temperature distribution [K] (1D array of length N).
    """

    # Interior nodes: apply the heat equation
    for i in range(1, N - 1):
        T_new[i] = T[i] + alpha * dt / dx ** 2 * (T[i + 1] - 2 * T[i] + T[i - 1])

    # Boundary condition at exposed surface (x = 0)
    T_new[0] = T[0] + (
            (
                    h * (Tg - T[0])
                    + epsilon * sigma * (Tg ** 4 - T[0] ** 4)
                    + q_inc
            ) * dt / (rho * c * dx)
            + alpha * dt / dx ** 2 * (T[1] - T[0])
    )

    # Boundary condition at insulated surface (x = L)
    T_new[N - 1] = T[N - 1] + alpha * dt / dx ** 2 * (T[N - 2] - T[N - 1])

    # Update the temperature array and record the new distribution
    T = T_new.copy()
    T_history.append(T.copy())
    return T


def ht_dx_dt_sub(L: float, N: int, alpha: float) -> tuple[float, float]:
    """
    Calculate the spatial step size (dx) and time step (dt) for the wall solver.

    A stability criterion is used to compute dt for a 1D heat conduction problem
    (via finite difference).

    :param L: Total thickness of the wall [m].
    :param N: Number of spatial nodes.
    :param alpha: Thermal diffusivity [m^2/s].
    :returns: A tuple (dx, dt):
       - dx: The spatial discretization step [m].
       - dt: The time step [s].
    """
    dx = L / (N - 1)
    dt = (0.5 * dx ** 2 / alpha) / 2  # Additional factor of 2 for safety margin
    return dx, dt


def alpha_calc(k: float, rho: float, c: float) -> float:
    """
    Calculate the thermal diffusivity of the wall material.

    :param k: Thermal conductivity [W/(m·K)].
    :param rho: Density of the material [kg/m^3].
    :param c: Specific heat capacity [J/(kg·K)].
    :returns: Thermal diffusivity [m^2/s].
    """
    alpha = k / (rho * c)
    return alpha


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Define number of time steps
    time_steps = 300  # Total number of time steps

    # Define material properties and initial conditions (in Kelvin)
    k = 0.17  # Thermal conductivity (W/m*K)
    rho = 750  # Density (kg/m^3)
    c = 1090  # Specific heat capacity (J/kg*K)
    Tg = 800 + 273.15  # Gas temperature in Kelvin
    T0 = 25 + 273.15  # Initial temperature of the plasterboard in Kelvin
    h = 10  # Convective heat transfer coefficient (W/m^2*K)
    L = 0.02  # Thickness of the plasterboard (m)
    N = 50  # Number of spatial nodes
    epsilon = 0.9  # Emissivity of the plasterboard surface
    sigma = 5.67e-8  # Stefan-Boltzmann constant (W/m^2*K^4)
    q_inc = 0

    # Calculate thermal diffusivity
    alpha = alpha_calc(k, rho, c)

    # Define spatial and time steps
    dx, dt = ht_dx_dt_sub(L, N, alpha)

    # Initialise temperature array in Kelvin
    T = np.ones(N) * T0  # Initial temperature distribution
    T_new = T.copy()  # Array for updated temperatures

    # Record temperature profiles over time for visualization
    T_history = []

    # Finite difference time-stepping
    for _ in range(time_steps):
        T = update_wall_temp_array(T, T_new, T_history, alpha, dt, dx, h, Tg, epsilon, sigma, rho, c, N, q_inc)
    # ----------------------------------------------------------------------------------------------------------------------
    # Plotting the temperature distribution over time
    plt.figure(figsize=(10, 6))
    for i in range(0, time_steps, 50):  # Plot every 50th time step
        plt.plot(np.linspace(0, L, N), T_history[i], label=f'Time = {i * dt:.1f} s')
    plt.xlabel("Position within Thickness (m)")
    plt.ylabel("Temperature (K)")
    plt.title("1D Transient Temperature Distribution in Plasterboard with Radiation (Kelvin Calculations)")
    plt.legend()
    plt.grid(True)
    plt.show()
