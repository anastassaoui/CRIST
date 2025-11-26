"""
Simple optimization by running working simulator for different configurations.
NO external solvers, NO Pyomo, NO scipy.optimize - just the working MultiEffectEvaporator.
"""

import numpy as np
from src.evaporateurs import MultiEffectEvaporator
import config


def optimize_evaporator_by_simulation(n_effects, F_feed, x_feed, T_feed, x_final, objective='steam'):
    """
    Run the WORKING evaporator simulator and calculate costs.
    This is not optimization - just simulation + cost calculation.

    Returns realistic results using the proven MultiEffectEvaporator code.
    """

    try:
        # Use the EXACT same code as the working Evaporator page
        evaporator = MultiEffectEvaporator(
            n_effects=n_effects,
            F_feed=F_feed,
            x_feed=x_feed,
            T_feed=T_feed,
            P_steam=config.STEAM_PRESSURE,
            P_condenser=config.CONDENSER_PRESSURE,
            x_final=x_final
        )

        # Solve using the WORKING method
        results = evaporator.solve_sequential()
        summary = evaporator.get_summary()

        # Get steam consumption and total area from summary
        S_steam = summary['steam_consumption']
        total_area = summary['total_area']
        steam_economy = summary['steam_economy']

        # Calculate total evaporation from results
        total_evaporation = sum(r['V_out'] for r in results)

        # Calculate cost
        if objective == 'cost':
            # Capital cost (CAPEX)
            capital_cost = 0
            for effect in results:
                A = effect['A']
                capital_cost += config.COST_CORRELATIONS['evaporator']['base'] * \
                               (A ** config.COST_CORRELATIONS['evaporator']['exponent'])

            # Operating cost (OPEX) per year
            operating_hours = 8000
            steam_cost_annual = S_steam * operating_hours * config.COSTS['steam_3.5bar'] / 1000

            # Total annualized cost
            annualization_factor = 0.13  # 10 years, 5% interest
            objective_value = annualization_factor * capital_cost + steam_cost_annual
        else:
            # Objective is steam consumption
            objective_value = S_steam

        return {
            'status': 'optimal',
            'objective_value': objective_value,
            'steam_consumption': S_steam,
            'total_area': total_area,
            'total_evaporation': total_evaporation,
            'steam_economy': steam_economy,
            'effects': results
        }

    except Exception as e:
        print(f"Simulation failed for {n_effects} effects: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'message': str(e),
            'objective_value': float('inf'),
            'steam_consumption': 0,
            'effects': []
        }


def find_optimal_number_of_effects(F_feed, x_feed, T_feed, x_final, n_range=(2, 5)):
    """
    Run simulations for n=2,3,4,5 and pick the cheapest.
    Simple. No fancy optimization.
    """
    results = []

    for n in range(n_range[0], n_range[1] + 1):
        print(f"\nSimulating {n} effects...")

        result = optimize_evaporator_by_simulation(
            n, F_feed, x_feed, T_feed, x_final, objective='cost'
        )

        results.append({
            'n_effects': n,
            **result
        })

    return results
