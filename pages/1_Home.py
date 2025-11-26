"""
Home Page - Project Overview
"""

import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

st.title("Home - Project Overview")

st.info("This is the home page. Please return to the main page or select another page from the sidebar.")

st.markdown("""
### Available Pages

- **Evaporator**: Multi-effect evaporator simulation
- **Crystallization**: Batch crystallizer modeling
- **Optimization**: Process optimization with Pyomo
- **Integration**: Heat integration and economics
- **Results**: Comprehensive results dashboard
""")
