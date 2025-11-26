"""
Crystallization Page - Batch Crystallizer Simulation
"""

import streamlit as st
import pandas as pd
import numpy as np
import config
from src.cristallisation import BatchCrystallizer
from src.visualization import (
    plot_CSD,
    plot_cooling_profiles,
    plot_supersaturation_evolution,
    plot_comparison_bar_chart
)

st.set_page_config(page_title="Crystallization", page_icon="💎", layout="wide")

# Initialize session state
if 'crystallizer_results' not in st.session_state:
    st.session_state.crystallizer_results = None
if 'crystallizer_comparison' not in st.session_state:
    st.session_state.crystallizer_comparison = None

st.title("Batch Crystallizer Simulation")
st.markdown("Model sucrose crystal growth from supersaturated syrup using Population Balance Equations (PBE)")

# Theory section
with st.expander("📚 Theory: Batch Crystallization & Population Balance", expanded=False):
    st.markdown("""
    ## Principle of Operation

    Batch crystallization produces crystalline sugar from supersaturated syrup through **controlled cooling**.
    As temperature decreases, solubility drops, creating supersaturation that drives nucleation and crystal growth.

    ### Supersaturation Ratio
    """)
    st.latex(r"S = \frac{C}{C^*(T)} = \frac{\text{Actual concentration}}{\text{Saturation concentration at T}}")

    st.markdown("""
    Where:
    - $C$: Actual saccharose concentration (g/100g solution)
    - $C^*(T)$: Saturation (equilibrium) concentration at temperature T
    - $S > 1$: Supersaturated (crystallization occurs)
    - $S = 1$: Saturated (equilibrium)
    - $S < 1$: Undersaturated (dissolution occurs)

    ### Solubility Correlation (Saccharose in Water)
    """)
    st.latex(r"C^* = a + bT + cT^2 + dT^3")

    st.markdown("""
    Coefficients from experimental data:
    - $a = 64.18$
    - $b = 0.1337$
    - $c = 5.52 \\times 10^{-3}$
    - $d = -9.73 \\times 10^{-6}$

    ### Nucleation Kinetics

    **Primary nucleation** (birth of new crystals):
    """)
    st.latex(r"B = k_b \cdot S^b \cdot m_T^j")

    st.markdown("""
    Where:
    - $B$: Nucleation rate (nuclei/m³·s)
    - $k_b = 1.5 \\times 10^{10}$: Nucleation rate constant
    - $b = 2.5$: Supersaturation order
    - $j = 0.5$: Crystal mass order
    - $m_T$: Total crystal mass in suspension (kg)

    **Effect**: Higher supersaturation → more nuclei → smaller crystals → higher CV

    ### Growth Kinetics

    **Crystal growth rate** (how fast existing crystals grow):
    """)
    st.latex(r"G = k_g \cdot S^g \cdot \exp\left(\frac{-E_g}{RT}\right)")

    st.markdown("""
    Where:
    - $G$: Linear growth rate (m/s)
    - $k_g = 2.8 \\times 10^{-7}$: Growth rate constant
    - $g = 1.5$: Supersaturation order
    - $E_g = 45000$ J/mol: Activation energy
    - $R = 8.314$ J/(mol·K): Gas constant
    - $T$: Temperature (K)

    ### Population Balance Equation (PBE)

    Tracks the evolution of crystal size distribution (CSD) over time:
    """)
    st.latex(r"\\frac{\\partial n}{\\partial t} + G \\frac{\\partial n}{\\partial L} = 0")

    st.markdown("""
    With boundary condition (nucleation):
    """)
    st.latex(r"n(L=0, t) = \\frac{B}{G}")

    st.markdown("""
    Where:
    - $n(L,t)$: Number density of crystals of size $L$ at time $t$ (number/m³·m)
    - $L$: Characteristic crystal size (m)

    ### Moments of the Distribution

    Useful metrics derived from the CSD:

    **0th moment** (total number):
    """)
    st.latex(r"\mu_0 = \\int_0^\\infty n(L) \, dL")

    st.markdown("""
    **1st moment** (length-weighted):
    """)
    st.latex(r"\mu_1 = \\int_0^\\infty L \cdot n(L) \, dL")

    st.markdown("""
    **2nd moment** (area-weighted):
    """)
    st.latex(r"\mu_2 = \\int_0^\\infty L^2 \cdot n(L) \, dL")

    st.markdown("""
    **3rd moment** (volume/mass-weighted):
    """)
    st.latex(r"\mu_3 = \\int_0^\\infty L^3 \cdot n(L) \, dL")

    st.markdown("""
    ### Key Performance Indicators

    **Mean Crystal Size (L₅₀)**:
    """)
    st.latex(r"L_{50} = \\frac{\mu_1}{\mu_0}")

    st.markdown("""
    **Coefficient of Variation (CV)**:
    """)
    st.latex(r"CV = \\frac{\sigma}{L_{50}} = \\frac{\sqrt{\mu_2/\mu_0 - (\\mu_1/\\mu_0)^2}}{\mu_1/\\mu_0}")

    st.markdown("""
    **Mass Yield**:
    """)
    st.latex(r"\\text{Yield} = \\frac{C_{initial} - C_{final}}{C_{initial} - C^*(T_{final})}")

    st.markdown("""
    **Targets for sugar production**:
    - L₅₀ = 400-500 μm (coarse sugar)
    - CV < 30% (uniform size distribution)
    - Yield > 50% (economic viability)

    ### Cooling Strategies

    **1. Linear Cooling**:
    """)
    st.latex(r"T(t) = T_{initial} - \\frac{(T_{initial} - T_{final})}{t_{batch}} \cdot t")

    st.markdown("""
    Simple to implement, but creates high supersaturation early → excessive nucleation → small crystals

    **2. Exponential Cooling**:
    """)
    st.latex(r"T(t) = T_{final} + (T_{initial} - T_{final}) \\cdot e^{-kt}")

    st.markdown("""
    Slower cooling early, faster late. Better control of supersaturation.

    **3. Optimal Cooling**:

    Maintains constant supersaturation ratio throughout the batch, minimizing secondary nucleation
    and producing uniform, large crystals.

    ### Implementation

    The simulator uses:
    1. **Method of Moments**: Solves ODEs for moments instead of full PBE (computationally efficient)
    2. **scipy.integrate.solve_ivp**: ODE solver with adaptive time stepping
    3. **Empirical Kinetics**: Uses literature parameters for sucrose crystallization
    4. **Coupled ODEs**: Temperature profile + moment evolution + mass balance
    """)

st.markdown("---")

# Sidebar inputs
st.sidebar.header("Crystallizer Configuration")

C_initial = st.sidebar.number_input(
    "Initial Concentration (g/100g)",
    min_value=60.0,
    max_value=75.0,
    value=65.0,
    step=1.0,
    help="Initial saccharose concentration from evaporator (g solute / 100g solution). Must be supersaturated at initial T. Typical: 65-70 g/100g."
)

T_initial = st.sidebar.number_input(
    "Initial Temperature (°C)",
    min_value=60.0,
    max_value=80.0,
    value=70.0,
    step=5.0,
    help="Starting temperature of supersaturated syrup. Higher temperature = higher solubility = lower initial supersaturation. Typical: 65-75°C."
)

T_final = st.sidebar.number_input(
    "Final Temperature (°C)",
    min_value=25.0,
    max_value=50.0,
    value=35.0,
    step=5.0,
    help="Final temperature at end of batch. Lower temperature = lower solubility = more crystals precipitated. Typical: 30-40°C."
)

duration_hours = st.sidebar.number_input(
    "Batch Duration (hours)",
    min_value=1.0,
    max_value=8.0,
    value=4.0,
    step=0.5,
    help="Total time for cooling from T_initial to T_final. Longer time = slower cooling = fewer nuclei = larger crystals. Typical: 3-5 hours."
)

duration = duration_hours * 3600  # Convert to seconds

volume = st.sidebar.number_input(
    "Crystallizer Volume (m³)",
    min_value=1.0,
    max_value=50.0,
    value=5.0,
    step=1.0,
    help="Working volume of batch crystallizer vessel. Affects mass of crystals produced. Typical industrial: 5-20 m³."
)

# Main content
tab1, tab2, tab3 = st.tabs(["Simulation", "Strategy Comparison", "Equipment Sizing"])

with tab1:
    st.subheader("Single Strategy Simulation")

    strategy = st.selectbox(
        "Cooling Strategy",
        options=['linear', 'exponential', 'optimal'],
        format_func=lambda x: x.capitalize(),
        help="Linear: constant cooling rate (simple, small crystals). Exponential: slow start, fast end (medium crystals). Optimal: constant supersaturation (large, uniform crystals)."
    )

    if st.button("Run Crystallization Simulation", type="primary"):
        with st.spinner("Running simulation..."):
            try:
                # Create crystallizer
                crystallizer = BatchCrystallizer(volume, C_initial, T_initial)

                # Run simulation
                result = crystallizer.run_batch(strategy, T_final, duration)

                # Store crystallizer object and results in session state
                st.session_state.crystallizer = crystallizer
                st.session_state.crystallizer_results = result

                st.success("Simulation completed successfully!")

            except Exception as e:
                st.error(f"Simulation failed: {e}")

    # Display results
    if st.session_state.crystallizer_results:
        result = st.session_state.crystallizer_results

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Mean Crystal Size (L50)", f"{result['L50_microns']:.1f} μm")

        with col2:
            st.metric("Coefficient of Variation", f"{result['CV']*100:.1f}%")

        with col3:
            st.metric("Mass Yield", f"{result['yield']*100:.1f}%")

        with col4:
            st.metric("Final Concentration", f"{result['final_concentration']:.1f} g/100g")

        # Plots
        col1, col2 = st.columns(2)

        with col1:
            # Cooling profile
            T_profile_dict = {strategy: result['T_profile']}
            fig_cooling = plot_cooling_profiles(result['time'], T_profile_dict)
            st.plotly_chart(fig_cooling, width="stretch")

            # CSD
            if 'crystallizer' in st.session_state and st.session_state.crystallizer:
                L_bins, n_dist = st.session_state.crystallizer.calculate_CSD()
                fig_csd = plot_CSD(L_bins, n_dist)
                st.plotly_chart(fig_csd, width="stretch")

        with col2:
            # Supersaturation
            fig_S = plot_supersaturation_evolution(result['time'], result['S_profile'])
            st.plotly_chart(fig_S, width="stretch")

with tab2:
    st.subheader("Compare Cooling Strategies")

    if st.button("Run Comparison"):
        with st.spinner("Running all strategies..."):
            try:
                strategies = ['linear', 'exponential', 'optimal']
                comparison_results = {}

                for strat in strategies:
                    crystallizer = BatchCrystallizer(volume, C_initial, T_initial)
                    result = crystallizer.run_batch(strat, T_final, duration)
                    comparison_results[strat] = result

                st.session_state.crystallizer_comparison = comparison_results

                st.success("Comparison completed!")

            except Exception as e:
                st.error(f"Comparison failed: {e}")

    # Display comparison
    if 'crystallizer_comparison' in st.session_state and st.session_state.crystallizer_comparison:
        comp = st.session_state.crystallizer_comparison

        # Metrics comparison
        st.markdown("### Performance Comparison")

        df_comp = pd.DataFrame({
            'Strategy': [s.capitalize() for s in comp.keys()],
            'L50 (μm)': [comp[s]['L50_microns'] for s in comp.keys()],
            'CV (%)': [comp[s]['CV']*100 for s in comp.keys()],
            'Yield (%)': [comp[s]['yield']*100 for s in comp.keys()]
        })

        st.dataframe(df_comp.style.format({
            'L50 (μm)': '{:.1f}',
            'CV (%)': '{:.1f}',
            'Yield (%)': '{:.1f}'
        }).highlight_min(subset=['CV (%)'], color='lightgreen')
        .highlight_max(subset=['L50 (μm)', 'Yield (%)'], color='lightgreen'),
        width="stretch")

        # Cooling profiles comparison
        T_profiles = {s: comp[s]['T_profile'] for s in comp.keys()}
        time = comp['linear']['time']
        fig_cool_comp = plot_cooling_profiles(time, T_profiles)
        st.plotly_chart(fig_cool_comp, width="stretch")

        # Bar chart comparison
        metrics = {
            'L50 (μm)': [comp[s]['L50_microns'] for s in comp.keys()],
            'CV (%)': [comp[s]['CV']*100 for s in comp.keys()],
            'Yield (%)': [comp[s]['yield']*100 for s in comp.keys()]
        }

        fig_bar = plot_comparison_bar_chart(list(comp.keys()), metrics)
        st.plotly_chart(fig_bar, width="stretch")

        # Recommendation
        best_L50 = max(comp.keys(), key=lambda s: comp[s]['L50_microns'])
        best_CV = min(comp.keys(), key=lambda s: comp[s]['CV'])

        st.info(f"""
        **Recommendation**:
        - Best for large crystals: **{best_L50.capitalize()}** (L50 = {comp[best_L50]['L50_microns']:.1f} μm)
        - Best for uniform distribution: **{best_CV.capitalize()}** (CV = {comp[best_CV]['CV']*100:.1f}%)
        """)

with tab3:
    st.subheader("Crystallizer Equipment Sizing")

    # Theory section for sizing
    with st.expander("📚 Theory: Crystallizer Equipment Design", expanded=False):
        st.markdown("""
        ## Batch Crystallizer Sizing

        Equipment sizing for batch crystallizers involves calculating:
        1. Vessel volume
        2. Agitation system (power and impeller design)
        3. Cooling system (heat exchange area)
        4. Hydraulic residence time and throughput

        ### 1. Vessel Volume Calculation

        **Design basis**: 5000 kg/batch (from specifications)
        """)
        st.latex(r"V = \\frac{m_{batch}}{\\rho_{solution}}")

        st.markdown("""
        Where:
        - $m_{batch}$ = Batch mass (kg)
        - $\\rho_{solution}$ ≈ 1200 kg/m³ (concentrated sugar solution)

        **Typical**: Add 20% freeboard for safety → $V_{total} = 1.2 \\times V_{working}$

        ### 2. Agitation Power

        Crystallizers require gentle agitation to:
        - Maintain suspension and uniform supersaturation
        - Avoid crystal breakage (attrition)
        - Ensure uniform temperature distribution

        **Power correlation**:
        """)
        st.latex(r"P = N_p \\cdot \\rho \\cdot N^3 \\cdot D^5")

        st.markdown("""
        Where:
        - $N_p$ = Power number (1.5 for pitched blade turbine)
        - $\\rho$ = Solution density (kg/m³)
        - $N$ = Rotation speed (rev/s)
        - $D$ = Impeller diameter (m)

        **Design constraints**:
        - Tip speed = 2-3 m/s (avoid attrition)
        - $D_{impeller}$ = 0.33 × $D_{tank}$
        - Reynolds number > 10⁴ (turbulent regime)

        **Reynolds number**:
        """)
        st.latex(r"Re = \\frac{\\rho \\cdot N \\cdot D^2}{\\mu}")

        st.markdown("""
        Where $\\mu$ ≈ 0.01 Pa·s (viscosity of concentrated sugar solution)

        ### 3. Cooling System Sizing

        **Heat duty** (total heat to remove):
        """)
        st.latex(r"Q_{total} = m_{batch} \\cdot c_p \\cdot (T_{initial} - T_{final})")

        st.markdown("""
        Where $c_p$ ≈ 3500 J/(kg·K) for sugar solution

        **Average cooling power**:
        """)
        st.latex(r"\\dot{Q}_{avg} = \\frac{Q_{total}}{t_{batch}}")

        st.markdown("""
        **Heat exchanger area** (for jacket or internal coil):
        """)
        st.latex(r"A = \\frac{\\dot{Q}_{avg}}{U \\cdot \\Delta T_{LM}}")

        st.markdown("""
        Where:
        - $U$ = 500 W/(m²·K) (typical for jacketed vessel)
        - $\\Delta T_{LM}$ = Log-mean temperature difference

        **LMTD**:
        """)
        st.latex(r"\\Delta T_{LM} = \\frac{(T_{hot,in} - T_{cool,out}) - (T_{hot,out} - T_{cool,in})}{\\ln\\left(\\frac{T_{hot,in} - T_{cool,out}}{T_{hot,out} - T_{cool,in}}\\right)}")

        st.markdown("""
        **Cooling water** (typically 15°C inlet, 25°C outlet)

        ### 4. Residence Time & Throughput

        **Total cycle time**:
        """)
        st.latex(r"t_{cycle} = t_{batch} + t_{turnaround}")

        st.markdown("""
        Where $t_{turnaround}$ = 2 hours (emptying, cleaning, charging, heating)

        **Batches per day**:
        """)
        st.latex(r"n_{batches/day} = \\frac{24}{t_{cycle}}")

        st.markdown("""
        **Annual production**:
        """)
        st.latex(r"\\text{Production} = n_{batches/day} \\times m_{crystals/batch} \\times 330 \\, \\text{days/year}")

        st.markdown("""
        Where $m_{crystals/batch}$ = Crystallized mass per batch (depends on yield)

        **Typical industrial values**:
        - Batch time: 3-5 hours
        - Turnaround: 1.5-3 hours
        - Total cycle: 5-7 hours
        - Batches/day: 3-5
        - Annual throughput: 15,000-30,000 tonnes/year (for 5 m³ crystallizer)
        """)

    if st.session_state.crystallizer_results and 'crystallizer' in st.session_state:
        crystallizer = st.session_state.crystallizer

        st.markdown("### Equipment Sizing Results")
        st.markdown(f"**Batch Size**: {config.BATCH_SIZE} kg  |  **Working Volume**: {volume} m³")

        # Calculate all sizing parameters
        try:
            cooling_data = crystallizer.size_cooling_coil(T_cooling_water=15)
            agitation_data = crystallizer.calculate_agitation_power()
            residence_data = crystallizer.calculate_residence_time()

            # Display in columns
            st.markdown("---")

            # Vessel dimensions
            st.markdown("#### 1. Vessel Dimensions")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tank Diameter", f"{agitation_data['tank_diameter']:.2f} m")
            with col2:
                st.metric("Working Volume", f"{volume:.1f} m³")
            with col3:
                freeboard_volume = volume * 1.2
                st.metric("Total Volume (with freeboard)", f"{freeboard_volume:.1f} m³")

            # Agitation system
            st.markdown("#### 2. Agitation System")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Motor Power (with safety)", f"{agitation_data['power']:.2f} kW")
            with col2:
                st.metric("Actual Power", f"{agitation_data['power_actual']:.2f} kW")
            with col3:
                st.metric("Impeller Diameter", f"{agitation_data['impeller_diameter']:.2f} m")
            with col4:
                st.metric("Rotation Speed", f"{agitation_data['rotation_speed']:.0f} rpm")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tip Speed", f"{agitation_data['tip_speed']:.1f} m/s",
                         help="Should be 2-3 m/s to avoid crystal breakage")
            with col2:
                st.metric("Reynolds Number", f"{agitation_data['reynolds_number']:.0f}",
                         help="Should be >10,000 for turbulent mixing")

            # Cooling system
            st.markdown("#### 3. Cooling System")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Heat Exchange Area", f"{cooling_data['area']:.2f} m²")
            with col2:
                st.metric("Average Cooling Power", f"{cooling_data['Q_avg']:.1f} kW")
            with col3:
                st.metric("Total Heat Removed", f"{cooling_data['Q_total']:.0f} kJ")
            with col4:
                st.metric("LMTD", f"{cooling_data['LMTD']:.1f} K")

            # Production metrics
            st.markdown("#### 4. Production Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Batch Duration", f"{residence_data['batch_duration']:.2f} hours")
            with col2:
                st.metric("Total Cycle Time", f"{residence_data['total_cycle_time']:.2f} hours",
                         help="Includes 2 hours turnaround time")
            with col3:
                st.metric("Batches per Day", f"{residence_data['batches_per_day']:.2f}")
            with col4:
                st.metric("Annual Production", f"{residence_data['annual_throughput']:.0f} tonnes/year")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Crystals per Batch", f"{residence_data['crystals_per_batch']:.0f} kg")
            with col2:
                utilization = (residence_data['batch_duration'] / residence_data['total_cycle_time']) * 100
                st.metric("Equipment Utilization", f"{utilization:.1f}%",
                         help="Percentage of cycle time spent crystallizing")

            # Summary table
            st.markdown("---")
            st.markdown("### Design Summary")

            summary_data = {
                'Parameter': [
                    'Tank diameter',
                    'Total volume (with freeboard)',
                    'Impeller diameter',
                    'Motor power',
                    'Rotation speed',
                    'Heat exchange area',
                    'Cooling power',
                    'Batch duration',
                    'Batches per day',
                    'Annual production'
                ],
                'Value': [
                    f"{agitation_data['tank_diameter']:.2f}",
                    f"{freeboard_volume:.2f}",
                    f"{agitation_data['impeller_diameter']:.2f}",
                    f"{agitation_data['power']:.2f}",
                    f"{agitation_data['rotation_speed']:.0f}",
                    f"{cooling_data['area']:.2f}",
                    f"{cooling_data['Q_avg']:.2f}",
                    f"{residence_data['batch_duration']:.2f}",
                    f"{residence_data['batches_per_day']:.2f}",
                    f"{residence_data['annual_throughput']:.0f}"
                ],
                'Unit': [
                    'm',
                    'm³',
                    'm',
                    'kW',
                    'rpm',
                    'm²',
                    'kW',
                    'hours',
                    '-',
                    'tonnes/year'
                ]
            }

            df_summary = pd.DataFrame(summary_data)
            st.table(df_summary)

            # Store sizing data in session state for export
            st.session_state.crystallizer_results['sizing'] = {
                'cooling': cooling_data,
                'agitation': agitation_data,
                'residence': residence_data,
                'tank_diameter': agitation_data['tank_diameter'],
                'total_volume': freeboard_volume
            }

        except Exception as e:
            st.error(f"Sizing calculation failed: {e}")
            import traceback
            st.code(traceback.format_exc())

    else:
        st.warning("Please run a crystallization simulation first in the Simulation tab.")
