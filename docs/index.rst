CRIST - Evaporation & Crystallization Simulator
================================================

Welcome to CRIST's documentation!

CRIST is a comprehensive simulation tool for multi-effect evaporation and batch crystallization processes,
specifically designed for sugar production from sugar cane juice.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/evaporateurs
   modules/crystallizer
   modules/optimisation
   modules/visualization
   modules/export

Features
--------

* **Multi-Effect Evaporation**: Simulate 2-5 effect evaporators with heat integration
* **Batch Crystallization**: Population balance modeling with nucleation and growth kinetics
* **Heat Integration**: Pinch analysis for energy recovery optimization
* **Economic Analysis**: CAPEX, OPEX, NPV, and ROI calculations
* **Optimization**: Simulation-based optimization for cost minimization
* **Export**: Generate formatted Excel and PDF reports

Quick Start
-----------

1. Install dependencies::

    pip install -r requirements.txt

2. Run the Streamlit application::

    streamlit run app.py

3. Navigate through the pages:

   * **Home**: Introduction and overview
   * **Evaporator**: Multi-effect evaporation simulation
   * **Crystallizer**: Batch crystallization modeling
   * **Optimization**: Process optimization and comparison
   * **Integration**: Heat integration and economic analysis
   * **Results**: Comprehensive dashboard and export

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
