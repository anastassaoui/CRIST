"""
Authentication utilities for CRIST app
"""

import streamlit as st
import streamlit_antd_components as sac


def require_auth():
    """
    Check if user is authenticated. 
    If not, redirect to main page for login.
    Call this at the start of each page.
    """
    if not st.session_state.get('authenticated', False):
        st.warning("Please login from the main page to access this content.")
        st.page_link("app.py", label="Go to Login")
        st.stop()


def add_sidebar_menu(current_page: str = None):
    """
    Add the beautiful sidebar menu to all pages.
    
    Args:
        current_page: Name of the current page to highlight in menu
    """
    # Map page names to index
    page_index_map = {
        'Home': 0,
        'Evaporator': 2,
        'Crystallization': 3,
        'Optimization': 5,
        'Integration': 6,
        'Results': 7,
    }
    
    default_index = page_index_map.get(current_page, 0)
    
    # Hide default Streamlit page navigation
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## Navigation")
        
        selected = sac.menu([
            sac.MenuItem('Home', icon='house-fill'),
            sac.MenuItem('Simulation', icon='cpu-fill', children=[
                sac.MenuItem('Evaporator', icon='droplet-fill'),
                sac.MenuItem('Crystallization', icon='gem'),
            ]),
            sac.MenuItem('Analysis', icon='graph-up', children=[
                sac.MenuItem('Optimization', icon='gear-fill'),
                sac.MenuItem('Integration', icon='link-45deg'),
            ]),
            sac.MenuItem('Results', icon='file-earmark-bar-graph-fill'),
            sac.MenuItem(type='divider'),
            sac.MenuItem('Logout', icon='box-arrow-right'),
        ], open_all=True, index=default_index)
        
        # Handle logout
        if selected == 'Logout':
            st.session_state.authenticated = False
            st.rerun()
        
        # Navigate to selected page (only if different from current)
        if selected and selected != current_page:
            if selected == 'Home':
                st.switch_page("app.py")
            elif selected == 'Evaporator':
                st.switch_page("pages/2_Evaporator.py")
            elif selected == 'Crystallization':
                st.switch_page("pages/3_Crystallization.py")
            elif selected == 'Optimization':
                st.switch_page("pages/4_Optimization.py")
            elif selected == 'Integration':
                st.switch_page("pages/5_Integration.py")
            elif selected == 'Results':
                st.switch_page("pages/6_Results.py")
        
        st.markdown("---")
        st.markdown("**CRIST Simulator**")
        st.caption("FST Settat 2024-2025")


# Keep old function for backwards compatibility
def add_logout_button():
    """Deprecated: Use add_sidebar_menu instead."""
    pass
