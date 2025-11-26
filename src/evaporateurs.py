"""
Multi-effect evaporator simulation and analysis.
Includes sequential solving, sensitivity analysis, and steam economy calculations.
"""

import numpy as np
from scipy.optimize import fsolve
from src.thermodynamique import (
    get_saturation_temperature,
    get_latent_heat,
    boiling_point_elevation,
    solution_enthalpy,
    heat_transfer_coefficient_evaporator,
    check_mass_balance,
    check_energy_balance
)
import config


class EvaporatorEffect:
    """
    Single evaporator effect with mass and energy balances.
    """

    def __init__(self, effect_number, P_vapor):
        """
        Initialize evaporator effect.

        Parameters:
        -----------
        effect_number : int
            Effect number (1, 2, 3, ...)
        P_vapor : float
            Vapor pressure in this effect (Pa)
        """
        self.effect_number = effect_number
        self.P_vapor = P_vapor

        # State variables
        self.F_in = None  # Feed flow rate (kg/h)
        self.x_in = None  # Feed concentration (mass fraction)
        self.T_in = None  # Feed temperature (°C)
        self.L_out = None  # Liquid outlet flow rate (kg/h)
        self.V_out = None  # Vapor outlet flow rate (kg/h)
        self.x_out = None  # Liquid outlet concentration (mass fraction)
        self.T_boiling = None  # Boiling temperature (°C)
        self.Q_heating = None  # Heat duty (W)
        self.A_heat_transfer = None  # Heat transfer area (m²)
        self.U = None  # Overall heat transfer coefficient (W/(m²·K))

    def solve_effect(self, F_in, x_in, T_in, T_heating_medium):
        """
        Solve mass and energy balances for this effect given heating medium temperature.

        Parameters:
        -----------
        F_in : float
            Feed flow rate (kg/h)
        x_in : float
            Feed concentration (mass fraction)
        T_in : float
            Feed temperature (°C)
        T_heating_medium : float
            Temperature of heating steam/vapor (°C)

        Returns:
        --------
        dict : Results dictionary with L_out, V_out, x_out, T_boiling, Q, A
        """
        self.F_in = F_in
        self.x_in = x_in
        self.T_in = T_in

        # Calculate boiling point with BPE
        T_sat = get_saturation_temperature(self.P_vapor)
        BPE = boiling_point_elevation(x_in, self.P_vapor)
        self.T_boiling = T_sat + BPE

        # For sequential solution, we need to estimate vapor flow
        # This requires solving coupled mass and energy balances

        def residuals(vars):
            """Residual function for mass and energy balance."""
            V_out, x_out = vars

            # Mass balance
            L_out = F_in - V_out
            if L_out <= 0:
                return [1e10, 1e10]

            # Component balance
            mass_balance_error = F_in * x_in - L_out * x_out

            # Energy balance
            # Convert flow rates to kg/s
            F_in_s = F_in / 3600
            V_out_s = V_out / 3600
            L_out_s = L_out / 3600

            # Enthalpies
            h_feed = solution_enthalpy(T_in, x_in)
            h_liquid_out = solution_enthalpy(self.T_boiling, x_out)
            h_vapor_out = get_latent_heat(self.P_vapor) + h_liquid_out  # Approximation

            # Heat required
            Q_required = (L_out_s * h_liquid_out + V_out_s * h_vapor_out - F_in_s * h_feed)

            # Heat provided (estimate based on U and driving force)
            U_est = heat_transfer_coefficient_evaporator(self.T_boiling, x_out, self.effect_number)
            delta_T = T_heating_medium - self.T_boiling

            if delta_T <= 0:
                return [1e10, 1e10]

            # Assume area based on typical values
            A_est = Q_required / (U_est * delta_T) if U_est * delta_T > 0 else 1e10

            # Energy balance error (should be small if consistent)
            energy_error = Q_required - U_est * A_est * delta_T

            return [mass_balance_error, energy_error / 10000]  # Scale energy error

        # Initial guess: 30% evaporation, concentration increases
        V_guess = F_in * 0.3
        x_guess = min(x_in * F_in / (F_in - V_guess), 0.7)

        try:
            solution = fsolve(residuals, [V_guess, x_guess], full_output=True)
            V_out, x_out = solution[0]
            info = solution[1]

            # Check if solution converged
            if info['fvec'].max() > 0.01:
                # Didn't converge well, use simple estimate
                V_out = F_in * 0.25
                x_out = x_in * F_in / (F_in - V_out)

        except:
            # Fallback: simple estimate
            V_out = F_in * 0.25
            x_out = x_in * F_in / (F_in - V_out)

        # Calculate outputs
        self.V_out = V_out
        self.L_out = F_in - V_out
        self.x_out = min(x_out, 0.75)  # Cap concentration

        # Recalculate BPE with final concentration
        BPE_final = boiling_point_elevation(self.x_out, self.P_vapor)
        self.T_boiling = T_sat + BPE_final

        # Heat duty
        F_in_s = F_in / 3600
        V_out_s = self.V_out / 3600
        L_out_s = self.L_out / 3600

        h_feed = solution_enthalpy(T_in, x_in)
        h_liquid_out = solution_enthalpy(self.T_boiling, self.x_out)
        lambda_vapor = get_latent_heat(self.P_vapor)
        h_vapor_out = h_liquid_out + lambda_vapor

        self.Q_heating = (L_out_s * h_liquid_out + V_out_s * h_vapor_out - F_in_s * h_feed)

        # Heat transfer calculation
        self.U = heat_transfer_coefficient_evaporator(self.T_boiling, self.x_out, self.effect_number)
        delta_T = T_heating_medium - self.T_boiling

        if delta_T > 0 and self.U > 0:
            self.A_heat_transfer = self.Q_heating / (self.U * delta_T)
        else:
            self.A_heat_transfer = 0

        # Apply heat loss
        self.Q_heating *= (1 + config.HEAT_LOSS_FRACTION)

        return {
            'L_out': self.L_out,
            'V_out': self.V_out,
            'x_out': self.x_out,
            'T_boiling': self.T_boiling,
            'Q': self.Q_heating,
            'A': self.A_heat_transfer,
            'U': self.U
        }


class MultiEffectEvaporator:
    """
    Multi-effect evaporator system with co-current flow configuration.
    """

    def __init__(self, n_effects, F_feed, x_feed, T_feed, P_steam, P_condenser, x_final):
        """
        Initialize multi-effect evaporator.

        Parameters:
        -----------
        n_effects : int
            Number of effects
        F_feed : float
            Feed flow rate (kg/h)
        x_feed : float
            Feed concentration (mass fraction)
        T_feed : float
            Feed temperature (°C)
        P_steam : float
            Steam pressure (Pa)
        P_condenser : float
            Condenser pressure (Pa)
        x_final : float
            Target final concentration (mass fraction)
        """
        self.n_effects = n_effects
        self.F_feed = F_feed
        self.x_feed = x_feed
        self.T_feed = T_feed
        self.P_steam = P_steam
        self.P_condenser = P_condenser
        self.x_final = x_final

        # Create pressure profile (linear distribution)
        self.pressures = np.linspace(P_steam * 0.7, P_condenser, n_effects)

        # Create effects
        self.effects = [EvaporatorEffect(i + 1, self.pressures[i]) for i in range(n_effects)]

        # Results
        self.results = None
        self.steam_consumption = None
        self.total_area = None
        self.steam_economy = None

    def solve_sequential(self):
        """
        Solve multi-effect evaporator using sequential method (effect by effect).

        Returns:
        --------
        dict : Complete results for all effects
        """
        results = []

        # Steam temperature
        T_steam = get_saturation_temperature(self.P_steam) + config.STEAM_SUPERHEAT

        F_current = self.F_feed
        x_current = self.x_feed
        T_current = self.T_feed

        for i, effect in enumerate(self.effects):
            # Heating medium temperature
            if i == 0:
                T_heating = T_steam
            else:
                # Use vapor from previous effect
                T_heating = self.effects[i - 1].T_boiling

            # Solve effect
            result = effect.solve_effect(F_current, x_current, T_current, T_heating)

            results.append({
                'effect': i + 1,
                'F_in': F_current,
                'x_in': x_current,
                'T_in': T_current,
                'L_out': result['L_out'],
                'V_out': result['V_out'],
                'x_out': result['x_out'],
                'T_boiling': result['T_boiling'],
                'P': self.pressures[i],
                'Q': result['Q'],
                'A': result['A'],
                'U': result['U']
            })

            # Update for next effect
            F_current = result['L_out']
            x_current = result['x_out']
            T_current = result['T_boiling']

        self.results = results

        # Calculate steam consumption (kg/h)
        Q_first_effect = results[0]['Q']  # W
        lambda_steam = get_latent_heat(self.P_steam)  # J/kg
        self.steam_consumption = (Q_first_effect / lambda_steam) * 3600  # kg/h

        # Total heat transfer area
        self.total_area = sum([r['A'] for r in results])

        # Total vapor produced
        total_vapor = sum([r['V_out'] for r in results])

        # Steam economy
        self.steam_economy = total_vapor / self.steam_consumption if self.steam_consumption > 0 else 0

        return results

    def get_summary(self):
        """
        Get summary of evaporator performance.

        Returns:
        --------
        dict : Performance metrics
        """
        if self.results is None:
            raise ValueError("Must solve system first")

        return {
            'n_effects': self.n_effects,
            'final_concentration': self.results[-1]['x_out'],
            'steam_consumption': self.steam_consumption,
            'total_area': self.total_area,
            'steam_economy': self.steam_economy,
            'specific_steam': self.steam_consumption / self.F_feed,  # kg steam / kg feed
        }

    def sensitivity_analysis(self, parameter, values):
        """
        Perform sensitivity analysis by varying a parameter.

        Parameters:
        -----------
        parameter : str
            Parameter to vary ('P_steam', 'x_final', 'F_feed', 'T_feed')
        values : array-like
            Values to test

        Returns:
        --------
        list : Results for each parameter value
        """
        sensitivity_results = []

        original_value = getattr(self, parameter)

        for value in values:
            # Set parameter
            setattr(self, parameter, value)

            # Re-initialize if needed
            if parameter == 'P_steam':
                self.pressures = np.linspace(value * 0.7, self.P_condenser, self.n_effects)
                self.effects = [EvaporatorEffect(i + 1, self.pressures[i]) for i in range(self.n_effects)]

            # Solve
            self.solve_sequential()
            summary = self.get_summary()

            sensitivity_results.append({
                parameter: value,
                **summary
            })

        # Restore original value
        setattr(self, parameter, original_value)

        return sensitivity_results
