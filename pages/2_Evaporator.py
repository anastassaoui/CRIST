"""
Evaporator Page - Multi-Effect Evaporator Simulation
"""

import streamlit as st
import pandas as pd
import numpy as np
import config
from src.evaporateurs import MultiEffectEvaporator
from src.visualization import (
    plot_temperature_profile,
    plot_concentration_profile,
    plot_pressure_profile,
    plot_sensitivity_analysis
)
from src.auth import require_auth, add_sidebar_menu

st.set_page_config(page_title="Evaporator", page_icon="E", layout="wide")

# Require authentication
require_auth()
add_sidebar_menu('Evaporator')

# Initialize session state
if 'evaporator_results' not in st.session_state:
    st.session_state.evaporator_results = None

st.title("Multi-Effect Evaporator Simulation")
st.markdown("Configure and simulate multi-effect evaporation system for sugar cane juice concentration")

# Theory section
with st.expander("Theory: Multi-Effect Evaporation", expanded=False):
    st.markdown("""
    ## Principle of Operation

    Multi-effect evaporation reduces energy consumption by **reusing vapor** from one effect as heating medium for the next effect.
    Each effect operates at progressively lower pressure and temperature, allowing vapor from effect *i* to condense and
    heat effect *i+1*.

    ### Forward Feed Configuration

    """)
    st.latex(r"\text{Feed} \rightarrow \text{Effect 1} \rightarrow \text{Effect 2} \rightarrow \cdots \rightarrow \text{Effect n} \rightarrow \text{Product}")

    st.markdown("""
    ### Mass Balance (per effect)
    """)
    st.latex(r"F_{in} = L_{out} + V_{out}")
    st.latex(r"F_{in} \cdot x_{in} = L_{out} \cdot x_{out}")

    st.markdown("""
    Where:
    - $F_{in}$: Feed mass flow entering the effect (kg/h)
    - $L_{out}$: Concentrated liquid leaving (kg/h)
    - $V_{out}$: Vapor generated (kg/h)
    - $x_{in}, x_{out}$: Mass fractions of saccharose

    ### Energy Balance (per effect)
    """)
    st.latex(r"Q = \dot{m}_{heating} \cdot \lambda = U \cdot A \cdot \Delta T_{LM}")

    st.markdown("""
    Where:
    - $Q$: Heat duty (W)
    - $\dot{m}_{heating}$: Mass flow of heating steam/vapor (kg/s)
    - $\lambda$: Latent heat of condensation (J/kg)
    - $U$: Overall heat transfer coefficient (W/m2.K)
    - $A$: Heat transfer area (m2)
    - $\Delta T_{LM}$: Log-mean temperature difference (K)

    ### Log-Mean Temperature Difference
    """)
    st.latex(r"\Delta T_{LM} = \frac{(T_{steam} - T_{boiling,out}) - (T_{steam} - T_{boiling,in})}{\ln\left(\frac{T_{steam} - T_{boiling,out}}{T_{steam} - T_{boiling,in}}\right)}")

    st.markdown("""
    ### Boiling Point Elevation (BPE)

    Saccharose in solution raises the boiling point above that of pure water:
    """)
    st.latex(r"BPE = k \cdot x^{1.2}")

    st.markdown("""
    Where $k$ is an empirical constant and $x$ is the concentration (mass fraction).

    ### Steam Economy

    Key performance metric indicating energy efficiency:
    """)
    st.latex(r"\text{Steam Economy} = \frac{\sum V_{out}}{\dot{m}_{steam,1st effect}}")

    st.markdown("""
    **Target**: Steam economy > 2.0

    - 2 effects: ~1.8
    - 3 effects: ~2.7
    - 4 effects: ~3.6
    - 5 effects: ~4.5

    ### Implementation

    The simulator uses:
    1. **CoolProp**: Rigorous steam/water properties (saturation temperature, enthalpy, entropy)
    2. **Sequential Solution**: Solves each effect iteratively from first to last
    3. **scipy.fsolve**: Nonlinear solver for mass and energy balance convergence
    4. **Antoine Equation**: Vapor pressure of water
    5. **Empirical Correlations**: Heat transfer coefficients decrease with each effect due to lower temperatures and higher viscosity
    """)

st.markdown("---")

# Sidebar inputs
st.sidebar.header("Evaporator Configuration")

n_effects = st.sidebar.slider(
    "Number of Effects",
    min_value=2,
    max_value=5,
    value=3,
    help="Number of evaporator effects in series. More effects = higher steam economy but more capital cost. Typical range: 2-5 effects."
)

st.sidebar.subheader("Feed Conditions")

F_feed = st.sidebar.number_input(
    "Feed Flow Rate (kg/h)",
    min_value=1000.0,
    max_value=50000.0,
    value=float(config.FEED_FLOW_RATE),
    step=1000.0,
    help="Mass flow rate of sugar cane juice entering the first effect. Typical industrial range: 10,000-30,000 kg/h."
)

x_feed = st.sidebar.slider(
    "Feed Concentration (%)",
    min_value=5.0,
    max_value=30.0,
    value=config.FEED_CONCENTRATION * 100,
    step=1.0,
    help="Initial saccharose concentration in the raw juice (mass %). Typical sugar cane juice: 12-18%."
) / 100

T_feed = st.sidebar.number_input(
    "Feed Temperature (°C)",
    min_value=60.0,
    max_value=100.0,
    value=float(config.FEED_TEMPERATURE),
    step=5.0,
    help="Temperature of feed entering first effect. Pre-heating feed improves efficiency. Typical: 80-90°C."
)

st.sidebar.subheader("Operating Conditions")

P_steam = st.sidebar.number_input(
    "Steam Pressure (bar)",
    min_value=2.0,
    max_value=5.0,
    value=config.STEAM_PRESSURE / 1e5,
    step=0.5,
    help="Pressure of heating steam to first effect (absolute). Higher pressure = higher temperature but more expensive steam. Typical: 3-4 bar."
) * 1e5

P_condenser = st.sidebar.number_input(
    "Condenser Pressure (bar)",
    min_value=0.1,
    max_value=0.5,
    value=config.CONDENSER_PRESSURE / 1e5,
    step=0.05,
    help="Vacuum pressure in final effect condenser (absolute). Lower pressure = lower boiling point = higher driving force. Typical: 0.1-0.2 bar (vacuum)."
) * 1e5

x_final = st.sidebar.slider(
    "Target Final Concentration (%)",
    min_value=60.0,
    max_value=75.0,
    value=config.TARGET_CONCENTRATION * 100,
    step=1.0,
    help="Target saccharose concentration in final product. For crystallization, need 60-70% (supersaturated). Too high = viscosity problems."
) / 100

# Main content
tab1, tab2, tab3 = st.tabs(["Simulation", "Sensitivity Analysis", "Performance Metrics"])

with tab1:
    st.subheader("Run Simulation")

    if st.button("Run Evaporator Simulation", type="primary"):
        with st.spinner("Running simulation..."):
            try:
                # Create evaporator instance
                evaporator = MultiEffectEvaporator(
                    n_effects=n_effects,
                    F_feed=F_feed,
                    x_feed=x_feed,
                    T_feed=T_feed,
                    P_steam=P_steam,
                    P_condenser=P_condenser,
                    x_final=x_final
                )

                # Solve
                results = evaporator.solve_sequential()
                summary = evaporator.get_summary()

                # Store in session state
                st.session_state.evaporator_results = {
                    'effects': results,
                    'summary': summary,
                    'config': {
                        'n_effects': n_effects,
                        'F_feed': F_feed,
                        'x_feed': x_feed,
                        'T_feed': T_feed,
                        'P_steam': P_steam,
                        'P_condenser': P_condenser
                    }
                }

                st.success("Simulation completed successfully!")

            except Exception as e:
                st.error(f"Simulation failed: {e}")

    # Display results if available
    if st.session_state.evaporator_results:
        results = st.session_state.evaporator_results['effects']
        summary = st.session_state.evaporator_results['summary']

        st.markdown("### Results")

        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Final Concentration",
                f"{summary['final_concentration']*100:.1f}%",
                delta=f"+{(summary['final_concentration']-x_feed)*100:.1f}%"
            )

        with col2:
            st.metric(
                "Steam Consumption",
                f"{summary['steam_consumption']:.0f} kg/h"
            )

        with col3:
            st.metric(
                "Steam Economy",
                f"{summary['steam_economy']:.2f}",
                help="kg vapor produced / kg steam consumed"
            )

        with col4:
            st.metric(
                "Total Area",
                f"{summary['total_area']:.1f} m²"
            )

        # Results table
        st.markdown("### Effect-by-Effect Results")

        df = pd.DataFrame(results)
        df_display = df[['effect', 'F_in', 'L_out', 'V_out', 'x_out', 'T_boiling', 'P', 'Q', 'A', 'U']].copy()
        df_display['x_out'] = df_display['x_out'] * 100  # Convert to %
        df_display['P'] = df_display['P'] / 1e5  # Convert to bar
        df_display['Q'] = df_display['Q'] / 1000  # Convert to kW

        df_display.columns = [
            'Effect', 'Feed (kg/h)', 'Liquid (kg/h)', 'Vapor (kg/h)',
            'Conc. (%)', 'Temp (°C)', 'Press (bar)', 'Heat (kW)', 'Area (m²)', 'U (W/m²K)'
        ]

        st.dataframe(df_display.style.format({
            'Feed (kg/h)': '{:.0f}',
            'Liquid (kg/h)': '{:.0f}',
            'Vapor (kg/h)': '{:.0f}',
            'Conc. (%)': '{:.1f}',
            'Temp (°C)': '{:.1f}',
            'Press (bar)': '{:.2f}',
            'Heat (kW)': '{:.1f}',
            'Area (m²)': '{:.1f}',
            'U (W/m²K)': '{:.0f}'
        }), width="stretch")

        # Visualizations
        st.markdown("### Profiles")

        col1, col2 = st.columns(2)

        with col1:
            fig_temp = plot_temperature_profile(results)
            st.plotly_chart(fig_temp, width="stretch")

            fig_press = plot_pressure_profile(results)
            st.plotly_chart(fig_press, width="stretch")

        with col2:
            fig_conc = plot_concentration_profile(results)
            st.plotly_chart(fig_conc, width="stretch")

with tab2:
    st.subheader("Sensitivity Analysis")

    if st.session_state.evaporator_results:
        param = st.selectbox(
            "Parameter to vary",
            options=['P_steam', 'F_feed', 'T_feed'],
            format_func=lambda x: {
                'P_steam': 'Steam Pressure',
                'F_feed': 'Feed Flow Rate',
                'T_feed': 'Feed Temperature'
            }[x]
        )

        if st.button("Run Sensitivity Analysis"):
            with st.spinner("Running sensitivity analysis..."):
                try:
                    # Create evaporator
                    evaporator = MultiEffectEvaporator(
                        n_effects=n_effects,
                        F_feed=F_feed,
                        x_feed=x_feed,
                        T_feed=T_feed,
                        P_steam=P_steam,
                        P_condenser=P_condenser,
                        x_final=x_final
                    )

                    # Define parameter ranges
                    if param == 'P_steam':
                        values = np.linspace(2.5e5, 4.5e5, 10)
                    elif param == 'F_feed':
                        values = np.linspace(F_feed * 0.8, F_feed * 1.2, 10)
                    elif param == 'T_feed':
                        values = np.linspace(75, 95, 10)

                    # Run sensitivity
                    sens_results = evaporator.sensitivity_analysis(param, values)

                    # Extract data
                    param_vals = [r[param] for r in sens_results]
                    steam_cons = [r['steam_consumption'] for r in sens_results]
                    total_area = [r['total_area'] for r in sens_results]
                    steam_econ = [r['steam_economy'] for r in sens_results]

                    # Plot
                    outputs = {
                        'Steam Consumption (kg/h)': steam_cons,
                        'Total Area (m²)': total_area,
                        'Steam Economy': steam_econ
                    }

                    # Adjust parameter values for display
                    if param == 'P_steam':
                        param_vals = [p / 1e5 for p in param_vals]
                        param_name = 'Steam Pressure (bar)'
                    elif param == 'F_feed':
                        param_name = 'Feed Flow Rate (kg/h)'
                    elif param == 'T_feed':
                        param_name = 'Feed Temperature (°C)'

                    fig_sens = plot_sensitivity_analysis(param_name, param_vals, outputs)
                    st.plotly_chart(fig_sens, width="stretch")

                    st.success("Sensitivity analysis completed!")

                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    else:
        st.warning("Please run simulation first in the Simulation tab.")

with tab3:
    st.subheader("Performance Metrics & Comparisons")

    if st.session_state.evaporator_results:
        summary = st.session_state.evaporator_results['summary']

        # Display detailed metrics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Energy Performance")
            st.write(f"Steam Economy: **{summary['steam_economy']:.2f}**")
            st.write(f"Specific Steam: **{summary['specific_steam']:.3f}** kg steam/kg feed")
            st.write(f"Total Steam: **{summary['steam_consumption']:.0f}** kg/h")

        with col2:
            st.markdown("#### Equipment Size")
            st.write(f"Total Area: **{summary['total_area']:.1f}** m²")
            st.write(f"Average Area/Effect: **{summary['total_area']/summary['n_effects']:.1f}** m²")

        # Comparison with different configurations
        st.markdown("#### Effect of Number of Effects")

        comp_data = {
            'Number of Effects': [2, 3, 4, 5],
            'Approx. Steam Economy': [1.8, 2.7, 3.6, 4.5],
            'Relative Area': [0.7, 1.0, 1.3, 1.6]
        }

        df_comp = pd.DataFrame(comp_data)
        st.table(df_comp)

        st.info("Note: More effects = better steam economy but higher capital cost (more area)")

    else:
        st.warning("Please run simulation first.")
