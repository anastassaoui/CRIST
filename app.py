"""
Evaporation and Crystallization Simulator
Main Streamlit Application Entry Point

Run with: streamlit run app.py
"""

import streamlit as st
import config

# Page configuration
st.set_page_config(
    page_title="Evaporation & Crystallization Simulator",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧪</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'evaporator_results' not in st.session_state:
    st.session_state.evaporator_results = None

if 'crystallizer_results' not in st.session_state:
    st.session_state.crystallizer_results = None

if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None

if 'integration_results' not in st.session_state:
    st.session_state.integration_results = None

# Main page content
st.title("Evaporation & Crystallization Simulator")
st.markdown("### Multi-Effect Evaporator and Batch Crystallizer Design Tool")

st.markdown("---")

# Welcome message
st.info("Select a page from the sidebar to begin simulation and optimization.")

# Project overview
with st.expander("📖 About This Project", expanded=True):
    st.markdown("""
    ## Overview

    This application simulates and optimizes an **integrated sugar production process** from sugar cane juice to crystalline sugar.
    The process involves two major unit operations working in sequence:

    ### 1. Multi-Effect Evaporation

    **Purpose**: Concentrate dilute sugar cane juice (15% saccharose) to supersaturated syrup (65% saccharose)

    **Theory**: Multi-effect evaporators reuse vapor from one effect as heating steam for the next effect, dramatically
    reducing steam consumption. Each effect operates at progressively lower pressure and temperature.

    **Mass Balance**:
    """)

    st.latex(r"F_{in} = L_{out} + V_{out}")
    st.latex(r"F_{in} \cdot x_{in} = L_{out} \cdot x_{out}")

    st.markdown("""
    **Energy Balance**:
    """)

    st.latex(r"Q = \dot{m}_{steam} \cdot \lambda_{steam} = U \cdot A \cdot \Delta T_{LM}")

    st.markdown("""
    Where:
    - $F_{in}$: Feed flow rate (kg/h)
    - $L_{out}$: Liquid product flow rate (kg/h)
    - $V_{out}$: Vapor flow rate (kg/h)
    - $x$: Concentration (mass fraction)
    - $U$: Overall heat transfer coefficient (W/m²·K)
    - $A$: Heat transfer area (m²)
    - $\lambda$: Latent heat of vaporization (J/kg)

    **Steam Economy** = kg vapor produced / kg steam consumed (target: >2.0)

    ---

    ### 2. Batch Crystallization

    **Purpose**: Produce uniform, high-quality sugar crystals from supersaturated syrup

    **Theory**: Controlled cooling creates supersaturation, driving nucleation and crystal growth.
    Population Balance Equations (PBE) track the evolution of crystal size distribution over time.

    **Nucleation Rate**:
    """)

    st.latex(r"B = k_b \cdot S^b \cdot m_T^j")

    st.markdown("""
    **Growth Rate**:
    """)

    st.latex(r"G = k_g \cdot S^g \cdot \exp\left(\frac{-E_g}{RT}\right)")

    st.markdown("""
    **Supersaturation Ratio**:
    """)

    st.latex(r"S = \frac{C}{C^*} = \frac{\text{Actual concentration}}{\text{Saturation concentration}}")

    st.markdown("""
    Where:
    - $B$: Nucleation rate (nuclei/m³·s)
    - $G$: Crystal growth rate (m/s)
    - $S$: Supersaturation ratio (dimensionless)
    - $m_T$: Total crystal mass (kg)
    - $E_g$: Activation energy (J/mol)
    - $R$: Gas constant = 8.314 J/(mol·K)
    - $T$: Temperature (K)

    **Target**: Mean crystal size (L₅₀) = 450 μm, CV < 30%

    ---

    ### 3. Process Integration & Optimization

    **Heat Integration**: Uses pinch analysis to identify opportunities for heat recovery.
    Hot vapor from evaporators can preheat cold feed streams, reducing external heating requirements.

    **Economic Optimization**: Finds the configuration that minimizes total annualized cost:
    """)

    st.latex(r"\text{Total Cost} = f_{ann} \cdot \text{CAPEX} + \text{OPEX}_{annual}")

    st.markdown("""
    Where:
    - CAPEX = Capital expenditure (equipment costs)
    - OPEX = Operating expenditure (steam, cooling water, electricity, labor)
    - $f_{ann}$ = Annualization factor (depends on interest rate and plant lifetime)

    **Cost Correlations**:
    """)

    st.latex(r"\text{Equipment Cost} = C_{base} \cdot (\text{Size})^{\alpha}")

    st.markdown("""
    Where $\\alpha$ = 0.6-0.7 (economy of scale exponent)

    ---

    ## Implementation Details

    **Thermodynamics**: CoolProp library provides rigorous steam/water properties (enthalpy, entropy, saturation conditions)

    **Solvers**:
    - Evaporator: Sequential solution with scipy.fsolve for nonlinear equations
    - Crystallizer: ODE integration with scipy.integrate.solve_ivp
    - Optimization: Simulation-based comparison (no external solvers needed)

    **Visualization**: All plots use Plotly for interactive, zoomable, exportable graphics

    **Export**: Generate professional Excel (multi-sheet) and PDF reports with all results
    """)

# Navigation guide
st.markdown("### Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Evaporator**
    Simulate multi-effect evaporators with:
    - Sequential mass & energy balances
    - Steam economy calculations
    - Sensitivity analysis
    """)

with col2:
    st.markdown("""
    **Crystallization**
    Model crystal growth with:
    - Population balance equations
    - Multiple cooling strategies
    - CSD analysis
    """)

with col3:
    st.markdown("""
    **Optimization**
    Find optimal design using:
    - Pyomo models
    - IPOPT solver
    - Cost minimization
    """)

st.markdown("---")

# Quick start guide
with st.expander("Quick Start Guide"):
    st.markdown("""
    ### Getting Started

    1. **Evaporator Page**:
       - Set number of effects (2-5)
       - Configure feed conditions
       - Run simulation
       - View results and profiles

    2. **Crystallization Page**:
       - Choose cooling strategy
       - Set batch parameters
       - Compare strategies
       - Analyze crystal size distribution

    3. **Optimization Page**:
       - Select optimization objective
       - Set parameter bounds
       - Run Pyomo optimization
       - View optimal configuration

    4. **Integration Page**:
       - Enable heat recovery
       - Perform pinch analysis
       - Calculate economics
       - Compare scenarios

    5. **Results Page**:
       - View comprehensive dashboard
       - Export results
       - Generate reports

    **Note**: Results from each page are stored in session state and can be accessed across pages.
    """)

# Current session status
st.markdown("### Current Session Status")

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    if st.session_state.evaporator_results:
        st.success("Evaporator: Complete")
    else:
        st.warning("Evaporator: Not run")

with status_col2:
    if st.session_state.crystallizer_results:
        st.success("Crystallizer: Complete")
    else:
        st.warning("Crystallizer: Not run")

with status_col3:
    if st.session_state.optimization_results:
        st.success("Optimization: Complete")
    else:
        st.warning("Optimization: Not run")

with status_col4:
    if st.session_state.integration_results:
        st.success("Integration: Complete")
    else:
        st.warning("Integration: Not run")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
<p>Evaporation & Crystallization Simulator | FST Settat | 2024-2025</p>
</div>
""", unsafe_allow_html=True)
