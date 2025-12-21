"""
AI Assistant - CRIST Chatbot
Interactive AI-powered assistant for the Evaporation & Crystallization Simulator
"""

import streamlit as st
from streamlit_chat import message
from src.auth import require_auth, add_sidebar_menu
from src.chatbot import (
    GROQ_AVAILABLE, 
    initialize_chat_history,
    add_message,
    get_chat_response,
    get_groq_api_key,
    clear_chat_history,
    AVAILABLE_MODELS
)

st.set_page_config(
    page_title="AI Assistant - CRIST",
    page_icon="",
    layout="wide"
)

# Require authentication
require_auth()
add_sidebar_menu('AI Assistant')

# Page header
st.title("AI Assistant")
st.caption("Your intelligent guide to the CRIST Simulator")

st.markdown("---")

# Initialize chat
initialize_chat_history()

# Check if Groq is available
if not GROQ_AVAILABLE:
    st.error("The `groq` package is not installed. Please run `pip install groq`")
    st.stop()

# Check if API key is configured
if not get_groq_api_key():
    st.warning("""
    **Groq API Key Not Configured**
    
    To use the AI Assistant, please configure your Groq API key:
    
    **Option 1**: Set `GROQ_API_KEY` environment variable  
    **Option 2**: Add to `.streamlit/secrets.toml`:
    ```toml
    [groq]
    api_key = "your_api_key_here"
    ```
    
    Get your free API key at [console.groq.com](https://console.groq.com)
    """)
    st.stop()

# Sidebar controls
with st.sidebar:
    st.markdown("---")
    st.markdown("**AI Model**")
    selected_model = st.selectbox(
        "Model",
        AVAILABLE_MODELS,
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.chat_model = selected_model
    
    if st.button("Clear Chat", use_container_width=True):
        clear_chat_history()
        st.rerun()
    
    st.caption(f"{len(st.session_state.chat_history)} messages")

# Display chat messages using streamlit-chat
chat_container = st.container()

with chat_container:
    for i, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"user_{i}")
        else:
            message(msg["content"], is_user=False, key=f"assistant_{i}")

# Chat input
user_input = st.chat_input("Ask me anything about the CRIST simulator...")

if user_input:
    # Add user message
    add_message("user", user_input)
    
    # Get response
    with st.spinner("Thinking..."):
        response = get_chat_response(
            user_input,
            st.session_state.chat_history[:-1],
            st.session_state.get('chat_model', 'llama-3.3-70b-versatile')
        )
    
    # Add assistant response
    add_message("assistant", response)
    st.rerun()

# Quick questions section
st.markdown("---")
st.markdown("**Quick Questions**")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("What is steam economy?", use_container_width=True):
        add_message("user", "What is steam economy and how can I improve it?")
        response = get_chat_response(
            "What is steam economy and how can I improve it?",
            st.session_state.chat_history[:-1],
            st.session_state.get('chat_model', 'llama-3.3-70b-versatile')
        )
        add_message("assistant", response)
        st.rerun()

with col2:
    if st.button("Explain crystallization", use_container_width=True):
        add_message("user", "Explain how batch crystallization works")
        response = get_chat_response(
            "Explain how batch crystallization works",
            st.session_state.chat_history[:-1],
            st.session_state.get('chat_model', 'llama-3.3-70b-versatile')
        )
        add_message("assistant", response)
        st.rerun()

with col3:
    if st.button("How to reduce costs?", use_container_width=True):
        add_message("user", "How can I reduce operating costs in sugar production?")
        response = get_chat_response(
            "How can I reduce operating costs in sugar production?",
            st.session_state.chat_history[:-1],
            st.session_state.get('chat_model', 'llama-3.3-70b-versatile')
        )
        add_message("assistant", response)
        st.rerun()
