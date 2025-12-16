"""
Results Page - Comprehensive Results Dashboard
"""

import streamlit as st
import pandas as pd
import traceback
from datetime import datetime
from src.export import create_excel_report, create_pdf_report
from src.auth import require_auth, add_sidebar_menu

st.set_page_config(page_title="Results", page_icon="R", layout="wide")

# Require authentication
require_auth()
add_sidebar_menu('Results')

# Initialize session state
if 'evaporator_results' not in st.session_state:
    st.session_state.evaporator_results = None
if 'crystallizer_results' not in st.session_state:
    st.session_state.crystallizer_results = None
if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None
if 'integration_results' not in st.session_state:
    st.session_state.integration_results = None

st.title("Results Dashboard")
st.markdown("Comprehensive overview of all simulations")

st.markdown("---")

# Check session state
has_evap = st.session_state.get('evaporator_results') is not None
has_cryst = st.session_state.get('crystallizer_results') is not None
has_opt = st.session_state.get('optimization_results') is not None
has_integ = st.session_state.get('integration_results') is not None

# Status overview
st.markdown("### Simulation Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if has_evap:
        st.success("Evaporator: Complete")
    else:
        st.error("Evaporator: Not run")

with col2:
    if has_cryst:
        st.success("Crystallizer: Complete")
    else:
        st.error("Crystallizer: Not run")

with col3:
    if has_opt:
        st.success("Optimization: Complete")
    else:
        st.error("Optimization: Not run")

with col4:
    if has_integ:
        st.success("Integration: Complete")
    else:
        st.error("Integration: Not run")

st.markdown("---")

# Evaporator results
if has_evap:
    st.markdown("## Evaporator Results")

    results = st.session_state.evaporator_results
    summary = results['summary']

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Number of Effects", summary['n_effects'])
    with col2:
        st.metric("Final Concentration", f"{summary['final_concentration']*100:.1f}%")
    with col3:
        st.metric("Steam Economy", f"{summary['steam_economy']:.2f}")
    with col4:
        st.metric("Total Area", f"{summary['total_area']:.1f} m²")

    with st.expander("Detailed Effect Data"):
        df = pd.DataFrame(results['effects'])
        st.dataframe(df, width="stretch")

# Crystallizer results
if has_cryst:
    st.markdown("## Crystallizer Results")

    result = st.session_state.crystallizer_results

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Strategy", result['strategy'].capitalize())
    with col2:
        st.metric("L50", f"{result['L50_microns']:.1f} μm")
    with col3:
        st.metric("CV", f"{result['CV']*100:.1f}%")
    with col4:
        st.metric("Yield", f"{result['yield']*100:.1f}%")

# Integration results
if has_integ:
    st.markdown("## Heat Integration Results")

    integ = st.session_state.integration_results

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Heat Recoverable", f"{integ['Q_recoverable']/1000:.0f} kW")
    with col2:
        st.metric("Recovery %", f"{integ['heat_recovery_percent']:.1f}%")
    with col3:
        st.metric("HEX Area", f"{integ['A_heat_exchanger']:.1f} m²")

# Export options
st.markdown("---")
st.markdown("## Export Results")

col1, col2 = st.columns(2)

with col1:
    if st.button("Export to Excel", type="primary", use_container_width=True):
        with st.spinner("Generating Excel report..."):
            try:
                excel_file = create_excel_report(
                    st.session_state.evaporator_results,
                    st.session_state.crystallizer_results,
                    st.session_state.optimization_results,
                    st.session_state.integration_results
                )

                st.download_button(
                    label="Download Excel Report",
                    data=excel_file,
                    file_name=f"process_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.success("Excel report generated successfully!")
            except Exception as e:
                st.error(f"Failed to generate Excel report: {e}")
                st.code(traceback.format_exc())

with col2:
    if st.button("Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                pdf_file = create_pdf_report(
                    st.session_state.evaporator_results,
                    st.session_state.crystallizer_results,
                    st.session_state.optimization_results,
                    st.session_state.integration_results
                )

                st.download_button(
                    label="Download PDF Report",
                    data=pdf_file,
                    file_name=f"process_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("PDF report generated successfully!")
            except Exception as e:
                st.error(f"Failed to generate PDF report: {e}")
                st.code(traceback.format_exc())

# Summary
st.markdown("---")
st.markdown("## Process Summary")

if has_evap and has_cryst:
    st.success("Complete simulation data available for comprehensive analysis")

    # Key takeaways
    st.markdown("### Key Performance Indicators")

    kpi_data = []

    if has_evap:
        kpi_data.append({
            'KPI': 'Steam Economy',
            'Value': f"{summary['steam_economy']:.2f}",
            'Unit': 'kg vapor/kg steam',
            'Status': 'Good' if summary['steam_economy'] > 2.0 else 'Needs improvement'
        })

    if has_cryst:
        target_met = abs(result['L50_microns'] - 450) < 50
        kpi_data.append({
            'KPI': 'Crystal Size Target',
            'Value': f"{result['L50_microns']:.1f}",
            'Unit': 'μm',
            'Status': 'Met' if target_met else 'Not met'
        })

        cv_ok = result['CV'] < 0.3
        kpi_data.append({
            'KPI': 'Size Distribution CV',
            'Value': f"{result['CV']*100:.1f}",
            'Unit': '%',
            'Status': 'Good' if cv_ok else 'High'
        })

    if kpi_data:
        df_kpi = pd.DataFrame(kpi_data)
        st.table(df_kpi)

else:
    st.warning("Run Evaporator and Crystallizer simulations to see complete summary")
