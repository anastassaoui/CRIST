Optimisation Module
===================

Process optimization and economic analysis.

.. automodule:: src.optimisation
   :members:
   :undoc-members:
   :show-inheritance:

EvaporatorOptimizer Class
-------------------------

Simulation-based optimization for evaporator configuration.

.. autoclass:: src.optimisation.EvaporatorOptimizer
   :members:
   :special-members: __init__
   :undoc-members:

IntegratedOptimizer Class
-------------------------

Heat integration and economic analysis for complete plant.

.. autoclass:: src.optimisation.IntegratedOptimizer
   :members:
   :special-members: __init__
   :undoc-members:

Optimization Approach
---------------------

The optimizer uses a **simulation-based approach** rather than mathematical optimization:

1. Run simulations for n=2, 3, 4, 5 effects
2. Calculate CAPEX and OPEX for each configuration
3. Compute annualized total cost
4. Select configuration with minimum cost

**Cost Equations**:

.. math::

   \\text{CAPEX} = \\sum_{i=1}^{n} C_{base} \\cdot A_i^{\\alpha}

.. math::

   \\text{OPEX}_{annual} = \\dot{m}_{steam} \\cdot h_{op} \\cdot c_{steam}

.. math::

   \\text{Total Cost} = f_{ann} \\cdot \\text{CAPEX} + \\text{OPEX}_{annual}

where:
  * C_base: Base equipment cost
  * α: Cost exponent (0.6-0.7)
  * h_op: Operating hours per year
  * c_steam: Steam cost (€/tonne)
  * f_ann: Annualization factor

Heat Integration Analysis
--------------------------

The integrated optimizer performs pinch analysis to identify heat recovery opportunities:

1. Identify hot streams (vapor from evaporators)
2. Identify cold streams (feed, crystallizer)
3. Calculate minimum temperature approach (ΔT_min = 10°C)
4. Determine recoverable heat
5. Size heat exchangers
6. Calculate economic benefit
