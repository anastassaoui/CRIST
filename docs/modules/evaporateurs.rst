Evaporateur Module
==================

Multi-effect evaporation simulation for sugar cane juice concentration.

.. automodule:: src.evaporateurs
   :members:
   :undoc-members:
   :show-inheritance:

MultiEffectEvaporator Class
----------------------------

The main class for simulating multi-effect evaporators.

.. autoclass:: src.evaporateurs.MultiEffectEvaporator
   :members:
   :special-members: __init__
   :undoc-members:

Key Methods
-----------

solve_sequential()
~~~~~~~~~~~~~~~~~~
Solves the multi-effect evaporator system sequentially, effect by effect.

Returns a list of dictionaries containing:

* ``T_boiling``: Boiling temperature (°C)
* ``P``: Pressure (Pa)
* ``F_in``: Feed flow rate (kg/h)
* ``x_in``: Feed concentration (mass fraction)
* ``L_out``: Liquid product flow rate (kg/h)
* ``V_out``: Vapor flow rate (kg/h)
* ``x_out``: Product concentration (mass fraction)
* ``Q``: Heat duty (W)
* ``A``: Heat transfer area (m²)

get_summary()
~~~~~~~~~~~~~
Returns a summary dictionary with overall evaporator performance:

* ``n_effects``: Number of effects
* ``final_concentration``: Final product concentration
* ``steam_consumption``: Steam consumption (kg/h)
* ``total_area``: Total heat transfer area (m²)
* ``steam_economy``: kg vapor per kg steam
* ``specific_steam``: Steam consumption per kg water evaporated
