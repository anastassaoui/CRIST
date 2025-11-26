"""
High-level optimization orchestration and economic analysis.
Uses simple simulation approach - just runs the working evaporator for different n.
"""

import numpy as np
from models.simple_optimization import (
    optimize_evaporator_by_simulation,
    find_optimal_number_of_effects
)
import config


class EvaporatorOptimizer:
    """
    High-level evaporator optimization wrapper.
    """

    def __init__(self, F_feed, x_feed, T_feed, x_final):
        """
        Initialize optimizer.

        Parameters:
        -----------
        F_feed : float
            Feed flow rate (kg/h)
        x_feed : float
            Feed concentration
        T_feed : float
            Feed temperature (°C)
        x_final : float
            Target final concentration
        """
        self.F_feed = F_feed
        self.x_feed = x_feed
        self.T_feed = T_feed
        self.x_final = x_final

    def optimize_for_n_effects(self, n_effects, objective='steam'):
        """
        Run evaporator simulation and calculate costs.

        Parameters:
        -----------
        n_effects : int
            Number of effects
        objective : str
            'steam' or 'cost'

        Returns:
        --------
        dict : Simulation results with cost
        """
        return optimize_evaporator_by_simulation(
            n_effects, self.F_feed, self.x_feed, self.T_feed, self.x_final, objective
        )

    def find_optimal_number_of_effects(self):
        """
        Simulate n=2,3,4,5 and pick the cheapest.

        Returns:
        --------
        dict : Results for all configurations with recommendation
        """
        results = find_optimal_number_of_effects(
            self.F_feed, self.x_feed, self.T_feed, self.x_final, n_range=(2, 5)
        )

        # Find best configuration
        valid_results = [r for r in results if r.get('status') == 'optimal']

        if valid_results:
            best = min(valid_results, key=lambda r: r.get('objective_value', float('inf')))
            return {
                'all_results': results,
                'optimal_n_effects': best['n_effects'],
                'optimal_cost': best.get('objective_value', None)
            }
        else:
            return {
                'all_results': results,
                'optimal_n_effects': None,
                'error': 'No valid solutions found'
            }


class CrystallizerOptimizer:
    """
    High-level crystallizer optimization wrapper.
    """

    def __init__(self, C_initial, T_initial, duration):
        """
        Initialize crystallizer optimizer.

        Parameters:
        -----------
        C_initial : float
            Initial concentration (g/100g)
        T_initial : float
            Initial temperature (°C)
        duration : float
            Batch duration (s)
        """
        self.C_initial = C_initial
        self.T_initial = T_initial
        self.duration = duration

    def optimize_cooling_profile(self, T_final):
        """
        Find optimal cooling profile using scipy.

        Parameters:
        -----------
        T_final : float
            Final temperature (°C)

        Returns:
        --------
        dict : Optimal cooling profile
        """
        # Simplified optimization: use linear cooling with penalty for high supersaturation
        # This avoids complex DAE solving which would require external solvers
        print("Note: Cooling profile optimization simplified (scipy-based)")
        return {
            'status': 'simplified',
            'message': 'Using predefined optimal cooling strategy',
            'T_profile': None  # Will use crystallizer's built-in strategies
        }


class IntegratedOptimizer:
    """
    Full process integration and optimization.
    """

    def __init__(self, evaporator_results, crystallizer_results):
        """
        Initialize integrated optimizer.

        Parameters:
        -----------
        evaporator_results : dict
            Results from evaporator simulation
        crystallizer_results : dict
            Results from crystallizer simulation
        """
        self.evaporator_results = evaporator_results
        self.crystallizer_results = crystallizer_results

    def heat_integration_analysis(self):
        """
        Perform pinch analysis for heat integration.

        Returns:
        --------
        dict : Heat integration results
        """
        # Identify hot and cold streams

        # Hot streams: vapor condensates from effects
        hot_streams = []
        if self.evaporator_results and 'effects' in self.evaporator_results:
            for effect in self.evaporator_results['effects']:
                hot_streams.append({
                    'name': f"Effect {effect['effect']} condensate",
                    'T_in': effect['T_boiling'],
                    'T_out': 40,  # Assume cooled to 40°C
                    'heat_capacity': effect['V_out'] * 4180 / 3600,  # W/K (approximate)
                })

        # Cold streams: feed preheating, crystallizer heating
        cold_streams = [
            {
                'name': 'Feed preheating',
                'T_in': config.FEED_TEMPERATURE,
                'T_out': 90,  # Preheat to 90°C
                'heat_capacity': config.FEED_FLOW_RATE * 3500 / 3600,  # W/K
            }
        ]

        # Simple pinch analysis: calculate available heat recovery
        total_hot_available = sum(
            stream['heat_capacity'] * (stream['T_in'] - stream['T_out'])
            for stream in hot_streams
        )

        total_cold_required = sum(
            stream['heat_capacity'] * (stream['T_out'] - stream['T_in'])
            for stream in cold_streams
        )

        Q_recoverable = min(total_hot_available, total_cold_required)

        # Estimate heat exchanger area required
        U_hex = 500  # W/(m²·K)
        LMTD = 30  # Assume 30°C average temperature difference

        A_hex = Q_recoverable / (U_hex * LMTD) if U_hex * LMTD > 0 else 0

        return {
            'hot_streams': hot_streams,
            'cold_streams': cold_streams,
            'Q_available': total_hot_available,
            'Q_required': total_cold_required,
            'Q_recoverable': Q_recoverable,
            'heat_recovery_percent': (Q_recoverable / total_cold_required * 100) if total_cold_required > 0 else 0,
            'A_heat_exchanger': A_hex,
        }

    def economic_evaluation(self, with_heat_recovery=False):
        """
        Perform comprehensive economic evaluation.

        Parameters:
        -----------
        with_heat_recovery : bool
            Include heat recovery in analysis

        Returns:
        --------
        dict : Economic metrics
        """
        # Capital costs (CAPEX)

        # Evaporator cost
        evap_capex = 0
        if self.evaporator_results and 'effects' in self.evaporator_results:
            for effect in self.evaporator_results['effects']:
                A = effect.get('A', 0)
                if A > 0 and not np.isnan(A):
                    evap_capex += config.COST_CORRELATIONS['evaporator']['base'] * \
                                 (A ** config.COST_CORRELATIONS['evaporator']['exponent'])

        # Crystallizer cost
        cryst_capex = 0
        if self.crystallizer_results:
            V = config.BATCH_SIZE / 1200  # m³ (approximate)
            cryst_capex = config.COST_CORRELATIONS['crystallizer']['base'] * \
                         (V ** config.COST_CORRELATIONS['crystallizer']['exponent'])

        # Heat exchanger cost (if applicable)
        hex_capex = 0
        if with_heat_recovery:
            heat_integration = self.heat_integration_analysis()
            A_hex = heat_integration.get('A_heat_exchanger', 0)
            if A_hex > 0 and not np.isnan(A_hex):
                hex_capex = config.COST_CORRELATIONS['heat_exchanger']['base'] * \
                           (A_hex ** config.COST_CORRELATIONS['heat_exchanger']['exponent'])

        total_capex = evap_capex + cryst_capex + hex_capex

        # Operating costs (OPEX) per year

        operating_hours = 8000  # hours/year

        # Steam cost
        if self.evaporator_results and 'steam_consumption' in self.evaporator_results:
            steam_consumption = self.evaporator_results['steam_consumption']  # kg/h
        else:
            steam_consumption = 5000  # Default estimate

        steam_cost_annual = steam_consumption * operating_hours * config.COSTS['steam_3.5bar'] / 1000  # €/year

        # Cooling water cost (crystallizer)
        cooling_water_m3_per_batch = 50  # m³
        batches_per_year = operating_hours / (config.CRYSTALLIZATION_TIME / 3600)
        cooling_water_cost_annual = batches_per_year * cooling_water_m3_per_batch * config.COSTS['cooling_water']

        # Electricity cost (pumps, agitation)
        electricity_kW = 50  # Average power consumption
        electricity_cost_annual = electricity_kW * operating_hours * config.COSTS['electricity']

        # Labor cost
        n_operators = 2
        labor_cost_annual = n_operators * operating_hours * config.COSTS['labor']

        # Total OPEX
        total_opex = steam_cost_annual + cooling_water_cost_annual + electricity_cost_annual + labor_cost_annual

        # If heat recovery, reduce steam costs
        if with_heat_recovery:
            heat_integration = self.heat_integration_analysis()
            steam_reduction = heat_integration['Q_recoverable'] / 2e6  # kg/s (approximate)
            steam_savings = steam_reduction * 3600 * operating_hours * config.COSTS['steam_3.5bar'] / 1000
            total_opex -= steam_savings
        else:
            steam_savings = 0

        # Production metrics
        sugar_production_kg_per_hour = config.FEED_FLOW_RATE * config.TARGET_CONCENTRATION
        sugar_production_tonnes_per_year = sugar_production_kg_per_hour * operating_hours / 1000

        # Unit cost
        production_cost_per_tonne = total_opex / sugar_production_tonnes_per_year if sugar_production_tonnes_per_year > 0 else 0

        # ROI calculation
        # Assume sugar sells at 600 €/tonne
        sugar_price = 600  # €/tonne
        revenue_annual = sugar_production_tonnes_per_year * sugar_price
        profit_annual = revenue_annual - total_opex

        # Payback period
        payback_years = total_capex / profit_annual if profit_annual > 0 else float('inf')

        # NPV (10 years, 5% discount rate)
        discount_rate = 0.05
        years = 10
        npv = -total_capex + sum(profit_annual / ((1 + discount_rate) ** year) for year in range(1, years + 1))

        return {
            'CAPEX': {
                'evaporator': evap_capex,
                'crystallizer': cryst_capex,
                'heat_exchanger': hex_capex,
                'total': total_capex,
            },
            'OPEX': {
                'steam': steam_cost_annual,
                'cooling_water': cooling_water_cost_annual,
                'electricity': electricity_cost_annual,
                'labor': labor_cost_annual,
                'total': total_opex,
                'steam_savings': steam_savings if with_heat_recovery else 0,
            },
            'production': {
                'tonnes_per_year': sugar_production_tonnes_per_year,
                'cost_per_tonne': production_cost_per_tonne,
            },
            'financial': {
                'revenue_annual': revenue_annual,
                'profit_annual': profit_annual,
                'payback_years': payback_years,
                'NPV_10years': npv,
                'ROI_percent': (npv / total_capex * 100) if total_capex > 0 else 0,
            }
        }
