"""
Optimization Page - Pyomo-based Process Optimization
"""

import streamlit as st
import pandas as pd
import config
from src.optimisation import EvaporatorOptimizer
from src.auth import require_auth, add_sidebar_menu

st.set_page_config(page_title="Optimization", page_icon="O", layout="wide")

# Require authentication
require_auth()
add_sidebar_menu('Optimization')

# Initialize session state
if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None
if 'n_effects_comparison' not in st.session_state:
    st.session_state.n_effects_comparison = None

st.title("Process Optimization")
st.markdown("Compare different configurations by running simulations and calculating costs")

# Theory section
with st.expander("Theory: Simulation-Based Optimization & Cost Modeling", expanded=False):
    st.markdown("""
    ## Optimization Approach

    Unlike traditional optimization (which uses external solvers), this tool uses a **simulation-based approach**:

    1. Run the working evaporator simulator for n = 2, 3, 4, 5 effects
    2. Calculate CAPEX and OPEX for each configuration
    3. Compute annualized total cost
    4. Select configuration with minimum cost

    **Advantage**: No external solvers needed, uses proven simulation code, always converges.

    ### Capital Expenditure (CAPEX)

    Equipment cost follows **economy of scale**:
    """)
    st.latex(r"\text{Cost}_{equipment} = C_{base} \cdot (\text{Size})^\alpha")

    st.markdown("""
    Where:
    - $C_{base}$: Base equipment cost (€)
    - $\text{Size}$: Equipment size (area for evaporators, volume for crystallizers)
    - $\alpha$: Cost exponent (0.6-0.7, reflects economy of scale)

    **Evaporator CAPEX**:
    """)
    st.latex(r"\text{CAPEX}_{evap} = \sum_{i=1}^{n} 15000 \cdot A_i^{0.65}")

    st.markdown("""
    **Crystallizer CAPEX**:
    """)
    st.latex(r"\text{CAPEX}_{cryst} = 25000 \cdot V^{0.6}")

    st.markdown("""
    **Heat Exchanger CAPEX** (for heat integration):
    """)
    st.latex(r"\text{CAPEX}_{HEX} = 8000 \cdot A_{HEX}^{0.7}")

    st.markdown("""
    ### Operating Expenditure (OPEX)

    **Annual steam cost**:
    """)
    st.latex(r"\text{OPEX}_{steam} = \dot{m}_{steam} \times h_{op} \times c_{steam}")

    st.markdown("""
    Where:
    - $\dot{m}_{steam}$: Steam consumption (kg/h)
    - $h_{op}$: Operating hours per year (typically 8000 h/year)
    - $c_{steam}$: Steam cost (25 Euro/tonne for 3.5 bar steam)

    **Other OPEX components**:
    - Cooling water: 0.15 €/m³
    - Electricity: 0.12 €/kWh
    - Labor: 35 €/h·operator

    ### Total Annualized Cost

    """)
    st.latex(r"\text{TAC} = f_{ann} \cdot \text{CAPEX} + \text{OPEX}_{annual}")

    st.markdown("""
    **Annualization factor** (converts capital cost to annual payment):
    """)
    st.latex(r"f_{ann} = \frac{i(1+i)^n}{(1+i)^n - 1}")

    st.markdown("""
    Where:
    - $i$: Interest rate (typically 5%)
    - $n$: Plant lifetime (typically 10 years)
    - For i=5%, n=10 years: f_ann is approximately 0.13

    ### Optimization Objective

    **Minimize steam consumption**:
    """)
    st.latex(r"\min \, \dot{m}_{steam}")

    st.markdown("""
    Favors more effects (higher steam economy) without considering capital cost.

    **Minimize total cost**:
    """)
    st.latex(r"\min \, (0.13 \cdot \text{CAPEX} + \text{OPEX}_{annual})")

    st.markdown("""
    Balances steam savings against equipment cost. Usually optimal at 3-4 effects.

    ### Trade-off

    | Number of Effects | Steam Economy | CAPEX | OPEX | Optimal? |
    |-------------------|---------------|-------|------|----------|
    | 2                 | Low (~1.8)    | Low   | High | No       |
    | 3                 | Medium (~2.7) | Medium| Medium| Often    |
    | 4                 | High (~3.6)   | High  | Low  | Often    |
    | 5                 | Very High (~4.5)| Very High | Very Low | Rarely |

    **Result**: 3 or 4 effects typically minimize total cost.

    ### Implementation

    The optimizer:
    1. Calls `MultiEffectEvaporator` directly (no external solvers)
    2. Uses EXACT same code as Evaporator page
    3. Calculates costs using correlations from `config.py`
    4. Returns simulation results + economic metrics
    """)

st.markdown("---")

# Sidebar
st.sidebar.header("Optimization Settings")

opt_objective = st.sidebar.selectbox(
    "Optimization Objective",
    options=['steam', 'cost'],
    format_func=lambda x: 'Minimize Steam Consumption' if x == 'steam' else 'Minimize Total Cost',
    help="Steam: minimize operating cost only (ignores CAPEX, favors more effects). Cost: minimize total annualized cost (balances CAPEX vs OPEX)."
)

# Main content
tab1, tab2 = st.tabs(["Single Configuration", "Optimal Number of Effects"])

with tab1:
    st.subheader("Optimize for Fixed Number of Effects")

    n_effects_opt = st.number_input(
        "Number of Effects",
        min_value=2,
        max_value=5,
        value=3,
        help="Number of evaporator effects to simulate and evaluate. The simulator will calculate steam consumption, equipment size, and costs for this configuration."
    )

    if st.button("Run Simulation", type="primary"):
        with st.spinner("Running evaporator simulation..."):
            try:
                optimizer = EvaporatorOptimizer(
                    F_feed=config.FEED_FLOW_RATE,
                    x_feed=config.FEED_CONCENTRATION,
                    T_feed=config.FEED_TEMPERATURE,
                    x_final=config.TARGET_CONCENTRATION
                )

                result = optimizer.optimize_for_n_effects(n_effects_opt, objective=opt_objective)

                st.session_state.optimization_results = result

                if result['status'] == 'optimal':
                    st.success("Simulation completed successfully!")
                else:
                    st.warning(f"Simulation status: {result['status']}")

                # Display results
                st.markdown("### Simulation Results")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Steam Consumption", f"{result['steam_consumption']:.0f} kg/h")
                with col2:
                    st.metric("Total Area", f"{result.get('total_area', 0):.1f} m²")
                with col3:
                    if opt_objective == 'cost':
                        st.metric("Annualized Cost", f"{result['objective_value']:,.0f} €/year")
                    else:
                        st.metric("Steam (objective)", f"{result['objective_value']:.0f} kg/h")

                # Effect results
                if result['effects']:
                    df = pd.DataFrame(result['effects'])
                    st.dataframe(df, width="stretch")

            except Exception as e:
                st.error(f"Simulation failed: {e}")
                import traceback
                st.code(traceback.format_exc())

with tab2:
    st.subheader("Find Optimal Number of Effects")

    st.info("This will simulate n=2, 3, 4, 5 effects and compare total annualized costs.")

    if st.button("Find Optimal Configuration"):
        with st.spinner("Running simulations for different n..."):
            try:
                optimizer = EvaporatorOptimizer(
                    F_feed=config.FEED_FLOW_RATE,
                    x_feed=config.FEED_CONCENTRATION,
                    T_feed=config.FEED_TEMPERATURE,
                    x_final=config.TARGET_CONCENTRATION
                )

                comparison = optimizer.find_optimal_number_of_effects()

                st.session_state.n_effects_comparison = comparison

                if comparison['optimal_n_effects']:
                    st.success(f"Optimal configuration: **{comparison['optimal_n_effects']} effects**")

                    # Comparison table
                    df_comp = pd.DataFrame(comparison['all_results'])
                    st.dataframe(df_comp, width="stretch")

                else:
                    st.error("All simulations failed.")

            except Exception as e:
                st.error(f"Comparison failed: {e}")
                import traceback
                st.code(traceback.format_exc())
