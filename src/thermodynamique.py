"""
Thermodynamic property calculations using CoolProp and thermo.
Provides wrapper functions for water/steam properties and sugar solution correlations.
"""

import numpy as np
from CoolProp.CoolProp import PropsSI


def get_water_properties(T=None, P=None, Q=None, property_name='H'):
    """
    Get thermodynamic properties of water/steam using CoolProp.

    Parameters:
    -----------
    T : float, optional
        Temperature in °C
    P : float, optional
        Pressure in Pa
    Q : float, optional
        Quality (0=saturated liquid, 1=saturated vapor)
    property_name : str
        Property to retrieve: 'H' (enthalpy J/kg), 'S' (entropy J/kg/K),
        'D' (density kg/m³), 'V' (viscosity Pa·s), 'L' (thermal conductivity W/m/K)

    Returns:
    --------
    float : Requested property value
    """
    # Convert temperature to Kelvin if provided
    T_K = T + 273.15 if T is not None else None

    # Determine input pair
    if P is not None and Q is not None:
        # Saturated conditions
        return PropsSI(property_name, 'P', P, 'Q', Q, 'Water')
    elif P is not None and T_K is not None:
        # Temperature and pressure specified
        return PropsSI(property_name, 'P', P, 'T', T_K, 'Water')
    elif T_K is not None and Q is not None:
        # Temperature and quality
        return PropsSI(property_name, 'T', T_K, 'Q', Q, 'Water')
    else:
        raise ValueError("Must provide either (P, Q), (P, T), or (T, Q)")


def get_saturation_temperature(P):
    """
    Get saturation temperature of water at given pressure.

    Parameters:
    -----------
    P : float
        Pressure in Pa

    Returns:
    --------
    float : Saturation temperature in °C
    """
    T_sat_K = PropsSI('T', 'P', P, 'Q', 0, 'Water')
    return T_sat_K - 273.15


def get_saturation_pressure(T):
    """
    Get saturation pressure of water at given temperature.

    Parameters:
    -----------
    T : float
        Temperature in °C

    Returns:
    --------
    float : Saturation pressure in Pa
    """
    T_K = T + 273.15
    return PropsSI('P', 'T', T_K, 'Q', 0, 'Water')


def get_latent_heat(P):
    """
    Get latent heat of vaporization at given pressure.

    Parameters:
    -----------
    P : float
        Pressure in Pa

    Returns:
    --------
    float : Latent heat in J/kg
    """
    h_vap = PropsSI('H', 'P', P, 'Q', 1, 'Water')
    h_liq = PropsSI('H', 'P', P, 'Q', 0, 'Water')
    return h_vap - h_liq


def boiling_point_elevation(x_saccharose, P=101325):
    """
    Calculate boiling point elevation (BPE) for saccharose solution using Dühring correlation.

    Parameters:
    -----------
    x_saccharose : float
        Mass fraction of saccharose (0-1)
    P : float, optional
        Pressure in Pa (default: 1 atm)

    Returns:
    --------
    float : Boiling point elevation in °C
    """
    # Get pure water boiling point at this pressure
    T_water = get_saturation_temperature(P)

    # Dühring correlation for sugar solutions
    # BPE increases with concentration
    # Empirical correlation: BPE ≈ k * x * (1 + a*x)
    # For saccharose solutions
    k = 0.5  # Base coefficient
    a = 1.2  # Nonlinearity factor

    BPE = k * x_saccharose * 100 * (1 + a * x_saccharose)

    return BPE


def solution_enthalpy(T, x_saccharose):
    """
    Calculate specific enthalpy of saccharose solution.

    Parameters:
    -----------
    T : float
        Temperature in °C
    x_saccharose : float
        Mass fraction of saccharose (0-1)

    Returns:
    --------
    float : Specific enthalpy in J/kg
    """
    # Get pure water enthalpy
    h_water = get_water_properties(T=T, P=101325, property_name='H')

    # Heat capacity of saccharose (approximate)
    cp_saccharose = 1250  # J/(kg·K)

    # Mixing enthalpy (negative, exothermic dissolution)
    h_mix = -50000 * x_saccharose * (1 - x_saccharose)  # J/kg

    # Solution enthalpy (mass-weighted average plus mixing term)
    h_solution = (1 - x_saccharose) * h_water + x_saccharose * cp_saccharose * T + h_mix

    return h_solution


def solution_heat_capacity(T, x_saccharose):
    """
    Calculate specific heat capacity of saccharose solution.

    Parameters:
    -----------
    T : float
        Temperature in °C
    x_saccharose : float
        Mass fraction of saccharose (0-1)

    Returns:
    --------
    float : Specific heat capacity in J/(kg·K)
    """
    # Heat capacity of water
    cp_water = 4180  # J/(kg·K) - approximate, varies slightly with T

    # Heat capacity of saccharose
    cp_saccharose = 1250  # J/(kg·K)

    # Mass-weighted average
    cp_solution = (1 - x_saccharose) * cp_water + x_saccharose * cp_saccharose

    return cp_solution


def solution_density(T, x_saccharose):
    """
    Calculate density of saccharose solution.

    Parameters:
    -----------
    T : float
        Temperature in °C
    x_saccharose : float
        Mass fraction of saccharose (0-1)

    Returns:
    --------
    float : Density in kg/m³
    """
    # Water density at temperature
    rho_water = get_water_properties(T=T, P=101325, property_name='D')

    # Saccharose density
    rho_saccharose = 1587  # kg/m³

    # Volume-weighted calculation (more accurate for solutions)
    # 1/rho = x/rho_saccharose + (1-x)/rho_water
    rho_solution = 1 / (x_saccharose / rho_saccharose + (1 - x_saccharose) / rho_water)

    return rho_solution


def heat_transfer_coefficient_evaporator(T, x_saccharose, effect_number):
    """
    Estimate overall heat transfer coefficient for evaporator effect.
    Accounts for reduced coefficient with concentration and effect number.

    Parameters:
    -----------
    T : float
        Temperature in °C
    x_saccharose : float
        Mass fraction of saccharose (0-1)
    effect_number : int
        Effect number (1, 2, 3, ...)

    Returns:
    --------
    float : Overall heat transfer coefficient U in W/(m²·K)
    """
    from config import U_COEFFICIENTS, FOULING_RESISTANCE

    # Base U value for this effect
    U_base = U_COEFFICIENTS.get(effect_number, 1800)

    # Reduction factor for concentration (higher concentration = lower U)
    concentration_factor = 1 - 0.3 * x_saccharose

    # Account for fouling resistance
    U_fouled = 1 / (1/U_base + FOULING_RESISTANCE)

    U_effective = U_fouled * concentration_factor

    return U_effective


def check_mass_balance(m_in, m_out, tolerance=0.001):
    """
    Check if mass balance closes within tolerance.

    Parameters:
    -----------
    m_in : float or array-like
        Inlet mass flow(s)
    m_out : float or array-like
        Outlet mass flow(s)
    tolerance : float
        Relative tolerance (default: 0.1%)

    Returns:
    --------
    tuple : (bool, float) - (balance_ok, relative_error)
    """
    total_in = np.sum(m_in)
    total_out = np.sum(m_out)

    if total_in == 0:
        return False, float('inf')

    relative_error = abs(total_in - total_out) / total_in
    balance_ok = relative_error < tolerance

    return balance_ok, relative_error


def check_energy_balance(Q_in, Q_out, tolerance=0.01):
    """
    Check if energy balance closes within tolerance.

    Parameters:
    -----------
    Q_in : float or array-like
        Inlet energy flow(s) in W
    Q_out : float or array-like
        Outlet energy flow(s) in W
    tolerance : float
        Relative tolerance (default: 1%)

    Returns:
    --------
    tuple : (bool, float) - (balance_ok, relative_error)
    """
    total_in = np.sum(Q_in)
    total_out = np.sum(Q_out)

    if total_in == 0:
        return False, float('inf')

    relative_error = abs(total_in - total_out) / total_in
    balance_ok = relative_error < tolerance

    return balance_ok, relative_error
