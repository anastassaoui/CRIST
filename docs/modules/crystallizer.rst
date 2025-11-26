Crystallizer Module
===================

Batch crystallization simulation using population balance equations.

.. automodule:: src.crystallizer
   :members:
   :undoc-members:
   :show-inheritance:

BatchCrystallizer Class
-----------------------

Population balance model for batch cooling crystallization of sucrose.

.. autoclass:: src.crystallizer.BatchCrystallizer
   :members:
   :special-members: __init__
   :undoc-members:

Nucleation and Growth Kinetics
-------------------------------

The crystallizer uses empirical kinetics models:

**Nucleation Rate**:

.. math::

   B = k_b \\cdot S^b \\cdot m_T^j

where:
  * B: nucleation rate (nuclei/m³·s)
  * S: supersaturation ratio
  * m_T: total crystal mass (kg)
  * k_b, b, j: kinetic parameters

**Growth Rate**:

.. math::

   G = k_g \\cdot S^g \\cdot \\exp\\left(\\frac{-E_g}{RT}\\right)

where:
  * G: growth rate (m/s)
  * E_g: activation energy (J/mol)
  * R: gas constant (J/mol·K)
  * T: temperature (K)
  * k_g, g: kinetic parameters

Cooling Strategies
------------------

The module supports multiple cooling strategies:

* **Linear**: Constant cooling rate
* **Exponential**: Exponential temperature decay
* **Optimal**: Optimized cooling profile to minimize CV
