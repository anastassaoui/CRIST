"""
Home Page - Project Overview
"""

import streamlit as st
from src.auth import require_auth, add_sidebar_menu

st.set_page_config(page_title="Home", page_icon="H", layout="wide")

# Require authentication
require_auth()
add_sidebar_menu('Home')

st.title("Home - Project Overview")

st.markdown("""
### Available Pages

- **Evaporator**: Multi-effect evaporator simulation
- **Crystallization**: Batch crystallizer modeling
- **Optimization**: Process optimization with Pyomo
- **Integration**: Heat integration and economics
- **Results**: Comprehensive results dashboard
""")
