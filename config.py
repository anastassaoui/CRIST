"""
Default parameters and constants for the evaporation and crystallization simulation.
All values from project specifications.
"""

# Feed specifications
FEED_FLOW_RATE = 20000  # kg/h
FEED_CONCENTRATION = 0.15  # mass fraction saccharose
FEED_TEMPERATURE = 85  # °C
FEED_PRESSURE = 1.5e5  # Pa (1.5 bar absolute)

# Target specifications
TARGET_CONCENTRATION = 0.65  # mass fraction saccharose
TARGET_CRYSTAL_SIZE = 450e-6  # m (450 μm)
TARGET_CV = 0.30  # coefficient of variation (max)
TARGET_PURITY = 0.995  # crystalline purity (min)

# Evaporator specifications
STEAM_PRESSURE = 3.5e5  # Pa (3.5 bar absolute)
STEAM_SUPERHEAT = 10  # °C
CONDENSER_PRESSURE = 0.15e5  # Pa (0.15 bar absolute)
HEAT_LOSS_FRACTION = 0.03  # 3% heat loss per effect
FOULING_RESISTANCE = 0.0002  # m²·K/W

# Heat transfer coefficients (W/m²·K)
U_COEFFICIENTS = {
    1: 2500,
    2: 2200,
    3: 1800
}

# Crystallization parameters
BATCH_SIZE = 5000  # kg/batch
CRYSTALLIZATION_TIME = 4 * 3600  # 4 hours in seconds
INITIAL_CRYSTAL_TEMP = 70  # °C
FINAL_CRYSTAL_TEMP = 35  # °C

# Solubility correlation coefficients (C* = a + bT + cT² + dT³)
SOLUBILITY_COEFFS = {
    'a': 64.18,
    'b': 0.1337,
    'c': 5.52e-3,
    'd': -9.73e-6
}

# Nucleation kinetics (B = kb * S^b * mT^j)
NUCLEATION_KB = 1.5e10  # nuclei/(m³·s)
NUCLEATION_B = 2.5
NUCLEATION_J = 0.5

# Growth kinetics (G = kg * S^g * exp(-Eg/RT))
GROWTH_KG = 2.8e-7  # m/s
GROWTH_G = 1.5
GROWTH_EG = 45000  # J/mol

# Universal constants
R_GAS = 8.314  # J/(mol·K)

# Economic parameters
COSTS = {
    'steam_3.5bar': 25,  # €/tonne
    'cooling_water': 0.15,  # €/m³
    'electricity': 0.12,  # €/kWh
    'labor': 35,  # €/h·operator
}

# Equipment cost correlations (in €)
COST_CORRELATIONS = {
    'evaporator': {'base': 15000, 'exponent': 0.65},  # C = base * A^exp
    'crystallizer': {'base': 25000, 'exponent': 0.6},  # C = base * V^exp
    'heat_exchanger': {'base': 8000, 'exponent': 0.7},  # C = base * A^exp
}

# Physical properties
WATER_MOLECULAR_WEIGHT = 18.015  # g/mol
SACCHAROSE_MOLECULAR_WEIGHT = 342.3  # g/mol
SACCHAROSE_DENSITY = 1587  # kg/m³ (crystal density)

# Cooling strategies
COOLING_STRATEGIES = ['linear', 'exponential', 'optimal']

# Optimization bounds
OPT_BOUNDS = {
    'n_effects': (2, 5),
    'steam_pressure': (2.5e5, 4.5e5),
    'final_concentration': (0.60, 0.70),
    'feed_temperature': (75, 95),
}

# Streamlit theme colors
THEME = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#d62728',
}

# Optimization approach: Just run simulations and compare results
# No external solvers or optimization libraries needed
