"""
Integration Page - Heat Integration and Economic Analysis
"""

import streamlit as st
import pandas as pd
from src.optimisation import IntegratedOptimizer
from src.visualization import plot_pinch_curves, plot_cost_breakdown

st.set_page_config(page_title="Integration", page_icon="🔗", layout="wide")

# Initialize session state
if 'evaporator_results' not in st.session_state:
    st.session_state.evaporator_results = None
if 'crystallizer_results' not in st.session_state:
    st.session_state.crystallizer_results = None
if 'integration_results' not in st.session_state:
    st.session_state.integration_results = None

st.title("Heat Integration & Economic Analysis")
st.markdown("Pinch analysis for heat recovery and complete plant economic evaluation")

# Theory section
with st.expander("📚 Theory: Pinch Analysis & Process Integration", expanded=False):
    st.markdown("""
    ## What is Process Integration?

    Process integration combines the evaporator and crystallizer as one complete plant system, identifying opportunities
    to reuse energy between process streams. This reduces external utility consumption (steam, cooling water) and improves
    overall plant economics.

    ### Pinch Analysis Fundamentals

    **Concept**: Match hot streams (that need cooling) with cold streams (that need heating) to minimize external heating and cooling.

    **Hot Streams**: Streams that release heat
    - Vapor from evaporators (condensing at 100-140°C)
    - Hot liquid products

    **Cold Streams**: Streams that require heat
    - Feed to evaporators (needs preheating from 85°C to boiling)
    - Crystallizer feed (needs heating before cooling cycle)

    ### Heat Recovery Potential

    **Maximum recoverable heat**:
    """)
    st.latex(r"Q_{recoverable} = \min(Q_{hot,available}, Q_{cold,required})")

    st.markdown("""
    Where:
    - $Q_{hot,available}$: Total heat available from hot streams (W)
    - $Q_{cold,required}$: Total heat required by cold streams (W)

    **Minimum temperature approach** ($\\Delta T_{min}$):
    """)
    st.latex(r"\Delta T_{min} = 10 \, ^\circ \text{C}")

    st.markdown("""
    Thermodynamic constraint: hot stream temperature must be at least 10°C above cold stream for heat transfer.

    ### Heat Exchanger Network Design

    **Heat duty**:
    """)
    st.latex(r"Q = U \cdot A \cdot \Delta T_{LM}")

    st.markdown("""
    **Required area**:
    """)
    st.latex(r"A = \\frac{Q}{U \cdot \Delta T_{LM}}")

    st.markdown("""
    Where:
    - $U$: Overall heat transfer coefficient (typically 500-1000 W/m²·K)
    - $A$: Heat exchanger area (m²)
    - $\\Delta T_{LM}$: Log-mean temperature difference (K)

    **Log-mean temperature difference**:
    """)
    st.latex(r"\Delta T_{LM} = \\frac{(T_{h,in} - T_{c,out}) - (T_{h,out} - T_{c,in})}{\ln\\left(\\frac{T_{h,in} - T_{c,out}}{T_{h,out} - T_{c,in}}\\right)}")

    st.markdown("""
    ### Economic Benefits

    **Steam savings**:
    """)
    st.latex(r"\Delta \dot{m}_{steam} = \\frac{Q_{recoverable}}{\lambda_{steam}}")

    st.markdown("""
    **Annual cost savings**:
    """)
    st.latex(r"\text{Savings} = \Delta \dot{m}_{steam} \\times h_{op} \\times c_{steam}")

    st.markdown("""
    **Additional heat exchanger cost**:
    """)
    st.latex(r"\text{CAPEX}_{HEX} = 8000 \cdot A^{0.7}")

    st.markdown("""
    **Payback period**:
    """)
    st.latex(r"\\text{Payback} = \\frac{\text{CAPEX}_{HEX}}{\text{Annual Savings}}")

    st.markdown("""
    **Typical results**:
    - Heat recovery: 15-30% of total heat requirement
    - Steam savings: 500-2000 kg/h
    - Annual savings: 100,000-400,000 €/year
    - Payback: 1-3 years

    ### Complete Plant Economics

    **Total CAPEX**:
    """)
    st.latex(r"\text{CAPEX}_{total} = \text{CAPEX}_{evap} + \text{CAPEX}_{cryst} + \text{CAPEX}_{HEX}")

    st.markdown("""
    **Total Annual OPEX**:
    """)
    st.latex(r"\text{OPEX}_{total} = \text{OPEX}_{steam} + \text{OPEX}_{cooling} + \text{OPEX}_{electric} + \text{OPEX}_{labor}")

    st.markdown("""
    **Annual Revenue** (sugar sales):
    """)
    st.latex(r"\text{Revenue} = m_{sugar} \\times c_{sugar}")

    st.markdown("""
    **Annual Profit**:
    """)
    st.latex(r"\text{Profit} = \text{Revenue} - \text{OPEX}_{total}")

    st.markdown("""
    **Net Present Value** (NPV, 10 years, 5% discount):
    """)
    st.latex(r"NPV = -\text{CAPEX} + \sum_{t=1}^{10} \\frac{\text{Profit}_t}{(1+0.05)^t}")

    st.markdown("""
    **Return on Investment** (ROI):
    """)
    st.latex(r"ROI = \\frac{\text{NPV}}{\text{CAPEX}} \\times 100\\%")

    st.markdown("""
    ### Implementation

    The integration module:
    1. Identifies hot and cold streams from evaporator and crystallizer results
    2. Performs simple pinch analysis (temperature-enthalpy matching)
    3. Sizes heat exchangers using correlations
    4. Calculates complete plant CAPEX and OPEX
    5. Computes financial metrics (NPV, ROI, payback)
    6. Compares scenarios with/without heat recovery
    """)

st.markdown("---")

# Check if previous simulations exist
if not st.session_state.get('evaporator_results'):
    st.warning("Please run Evaporator simulation first (page 2)")
    st.stop()

# Sidebar
st.sidebar.header("Integration Settings")

enable_heat_recovery = st.sidebar.checkbox(
    "Enable Heat Recovery",
    value=True,
    help="Enable heat integration (pinch analysis). Hot vapor from evaporators preheats cold feed, reducing external steam consumption."
)

st.sidebar.subheader("Economic Parameters")

sugar_price = st.sidebar.number_input(
    "Sugar Sale Price (€/tonne)",
    min_value=400.0,
    max_value=800.0,
    value=600.0,
    step=50.0,
    help="Market price for refined sugar (€/tonne). Used to calculate annual revenue. Typical range: 500-700 €/tonne depending on market conditions and purity."
)

# Main content
tab1, tab2 = st.tabs(["Heat Integration", "Economic Analysis"])

with tab1:
    st.subheader("Pinch Analysis")

    if st.button("Run Heat Integration Analysis"):
        with st.spinner("Analyzing heat recovery potential..."):
            try:
                optimizer = IntegratedOptimizer(
                    st.session_state.evaporator_results,
                    st.session_state.crystallizer_results
                )

                heat_integration = optimizer.heat_integration_analysis()

                st.session_state.integration_results = heat_integration

                st.success("Heat integration analysis completed!")

                # Display results
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Heat Available", f"{heat_integration['Q_available']/1000:.0f} kW")

                with col2:
                    st.metric("Heat Required", f"{heat_integration['Q_required']/1000:.0f} kW")

                with col3:
                    st.metric("Recoverable Heat", f"{heat_integration['Q_recoverable']/1000:.0f} kW")

                st.metric("Heat Recovery %", f"{heat_integration['heat_recovery_percent']:.1f}%")

                # Pinch diagram
                if heat_integration['hot_streams'] and heat_integration['cold_streams']:
                    fig_pinch = plot_pinch_curves(
                        heat_integration['hot_streams'],
                        heat_integration['cold_streams']
                    )
                    st.plotly_chart(fig_pinch, width="stretch")

                # Heat exchanger sizing
                st.markdown("### Heat Exchanger Requirements")
                st.write(f"Required Area: **{heat_integration['A_heat_exchanger']:.1f} m²**")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
                import traceback
                st.code(traceback.format_exc())

with tab2:
    st.subheader("Economic Evaluation")

    comparison_mode = st.checkbox("Compare with and without heat recovery")

    if st.button("Run Economic Analysis"):
        with st.spinner("Calculating economics..."):
            try:
                optimizer = IntegratedOptimizer(
                    st.session_state.evaporator_results,
                    st.session_state.crystallizer_results
                )

                if comparison_mode:
                    # With and without heat recovery
                    econ_without = optimizer.economic_evaluation(with_heat_recovery=False)
                    econ_with = optimizer.economic_evaluation(with_heat_recovery=True)

                    # Comparison table
                    comp_data = {
                        'Metric': [
                            'CAPEX (€)',
                            'Annual OPEX (€/year)',
                            'Production (t/year)',
                            'Cost (€/tonne)',
                            'Payback (years)',
                            'NPV 10yr (€)'
                        ],
                        'Without Heat Recovery': [
                            econ_without['CAPEX']['total'],
                            econ_without['OPEX']['total'],
                            econ_without['production']['tonnes_per_year'],
                            econ_without['production']['cost_per_tonne'],
                            econ_without['financial']['payback_years'],
                            econ_without['financial']['NPV_10years']
                        ],
                        'With Heat Recovery': [
                            econ_with['CAPEX']['total'],
                            econ_with['OPEX']['total'],
                            econ_with['production']['tonnes_per_year'],
                            econ_with['production']['cost_per_tonne'],
                            econ_with['financial']['payback_years'],
                            econ_with['financial']['NPV_10years']
                        ]
                    }

                    df_comp = pd.DataFrame(comp_data)
                    st.dataframe(df_comp, width="stretch")

                    st.success(f"Annual Savings: **{econ_without['OPEX']['total'] - econ_with['OPEX']['total']:.0f} €/year**")

                else:
                    # Single analysis
                    econ = optimizer.economic_evaluation(with_heat_recovery=enable_heat_recovery)

                    # CAPEX breakdown
                    st.markdown("### Capital Costs (CAPEX)")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Evaporator", f"{econ['CAPEX']['evaporator']:.0f} €")
                    with col2:
                        st.metric("Crystallizer", f"{econ['CAPEX']['crystallizer']:.0f} €")
                    with col3:
                        st.metric("Heat Exchanger", f"{econ['CAPEX']['heat_exchanger']:.0f} €")
                    with col4:
                        st.metric("Total CAPEX", f"{econ['CAPEX']['total']:.0f} €")

                    # OPEX breakdown
                    st.markdown("### Operating Costs (OPEX)")
                    fig_cost = plot_cost_breakdown(econ['OPEX'])
                    st.plotly_chart(fig_cost, width="stretch")

                    # Financial metrics
                    st.markdown("### Financial Metrics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Annual Revenue", f"{econ['financial']['revenue_annual']:.0f} €")
                    with col2:
                        st.metric("Annual Profit", f"{econ['financial']['profit_annual']:.0f} €")
                    with col3:
                        st.metric("Payback Period", f"{econ['financial']['payback_years']:.1f} years")

                    st.metric("NPV (10 years, 5%)", f"{econ['financial']['NPV_10years']:.0f} €")
                    st.metric("ROI", f"{econ['financial']['ROI_percent']:.1f}%")

            except Exception as e:
                st.error(f"Economic analysis failed: {e}")
                import traceback
                st.code(traceback.format_exc())
