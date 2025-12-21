"""
AI Chatbot Module for CRIST Application
Uses Groq API for fast LLM inference
"""

import os
import streamlit as st
from typing import List, Dict, Optional

# Try to import groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def get_groq_api_key() -> Optional[str]:
    """Get Groq API key from environment variables or secrets.toml"""
    # First try environment variables (for Docker/Render deployment)
    api_key = os.environ.get('GROQ_API_KEY')
    
    if api_key:
        return api_key
    
    # Fall back to secrets.toml (for local development)
    try:
        return st.secrets["groq"]["api_key"]
    except (KeyError, FileNotFoundError):
        return None


def get_groq_client() -> Optional["Groq"]:
    """Initialize and return Groq client"""
    if not GROQ_AVAILABLE:
        return None
    
    api_key = get_groq_api_key()
    if not api_key:
        return None
    
    return Groq(api_key=api_key)


# System prompt that provides context about the CRIST application
SYSTEM_PROMPT = """You are an intelligent AI assistant for the CRIST Evaporation & Crystallization Simulator application. 
This application is a process engineering tool developed at FST Settat (2024-2025) for sugar production simulation.

## About the Application

The CRIST simulator helps chemical engineers simulate and optimize an integrated sugar production process from sugar cane juice to crystalline sugar. The process involves:

### 1. Multi-Effect Evaporation
- **Purpose**: Concentrate dilute sugar cane juice (15% saccharose) to supersaturated syrup (65% saccharose)
- Multi-effect evaporators reuse vapor from one effect as heating steam for the next effect
- This dramatically reduces steam consumption
- Each effect operates at progressively lower pressure and temperature
- Key equations: Mass balance (F_in = L_out + V_out), Energy balance (Q = m_steam × λ_steam = U × A × ΔT_LM)
- Steam Economy target: >2.0 (kg vapor produced / kg steam consumed)

### 2. Batch Crystallization
- **Purpose**: Produce uniform, high-quality sugar crystals from supersaturated syrup
- Uses controlled cooling to create supersaturation, driving nucleation and crystal growth
- Population Balance Equations (PBE) track the evolution of crystal size distribution
- Nucleation Rate: B = k_b × S^b × m_T^j
- Growth Rate: G = k_g × S^g × exp(-E_g/RT)
- Target: Mean crystal size (L₅₀) = 450 μm, CV < 30%

### 3. Process Integration & Optimization
- Heat Integration using pinch analysis for heat recovery opportunities
- Economic Optimization to minimize total annualized cost (CAPEX + OPEX)

## Application Pages
- **Home**: Project overview and theory
- **Evaporator**: Multi-effect evaporator simulation (2-5 effects)
- **Crystallization**: Batch crystallizer modeling with cooling strategies
- **Optimization**: Process optimization for cost minimization
- **Integration**: Heat integration and economic analysis
- **Results**: Comprehensive results dashboard with export options

## Technical Details
- Uses CoolProp library for rigorous steam/water thermodynamic properties
- Uses scipy for nonlinear equation solving and ODE integration
- All plots are interactive using Plotly
- Can export results to Excel and PDF

## Your Role
- Help users understand the simulation parameters and results
- Explain chemical engineering concepts related to evaporation and crystallization
- Guide users through the application features
- Answer questions about mass/energy balances, thermodynamics, and process optimization
- Provide recommendations for process parameters

Always be helpful, accurate, and explain concepts clearly. If you don't know something specific about the application, be honest about it.
"""


def initialize_chat_history():
    """Initialize chat history in session state if not exists"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_model' not in st.session_state:
        st.session_state.chat_model = "llama-3.3-70b-versatile"


def get_chat_response(
    user_message: str,
    chat_history: List[Dict[str, str]],
    model: str = "llama-3.3-70b-versatile"
) -> str:
    """
    Get a response from Groq API
    
    Args:
        user_message: The user's message
        chat_history: List of previous messages
        model: The LLM model to use
        
    Returns:
        The assistant's response text
    """
    client = get_groq_client()
    
    if not client:
        return "❌ **Error**: Groq API key not configured. Please set GROQ_API_KEY environment variable or add it to secrets.toml"
    
    # Build messages list with system prompt and chat history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Add chat history (limit to last 20 messages to avoid context overflow)
    for msg in chat_history[-20:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"❌ **Error**: {str(e)}"


def clear_chat_history():
    """Clear the chat history"""
    st.session_state.chat_history = []


def add_message(role: str, content: str):
    """Add a message to chat history"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({
        "role": role,
        "content": content
    })


# Available models on Groq
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant", 
    "llama-3.2-90b-vision-preview",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]


def render_chat_interface():
    """Render the chat interface component"""
    initialize_chat_history()
    
    # Check if Groq is available
    if not GROQ_AVAILABLE:
        st.error("❌ The `groq` package is not installed. Please run `pip install groq`")
        return
    
    # Check if API key is configured
    if not get_groq_api_key():
        st.warning("""
        ⚠️ **Groq API Key Not Configured**
        
        To use the AI Assistant, please configure your Groq API key:
        
        **Option 1: Environment Variable (Recommended for deployment)**
        ```
        GROQ_API_KEY=your_api_key_here
        ```
        
        **Option 2: secrets.toml (For local development)**
        Add to `.streamlit/secrets.toml`:
        ```toml
        [groq]
        api_key = "your_api_key_here"
        ```
        
        Get your free API key at [console.groq.com](https://console.groq.com)
        """)
        return
    
    # Model selection in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("##### AI Model")
        selected_model = st.selectbox(
            "Model",
            AVAILABLE_MODELS,
            index=0,
            help="Select the AI model to use",
            label_visibility="collapsed"
        )
        st.session_state.chat_model = selected_model
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"{len(st.session_state.chat_history)} messages")
        with col2:
            if st.button("Clear", use_container_width=True, type="secondary"):
                clear_chat_history()
                st.rerun()
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        # Display existing messages
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about the CRIST simulator..."):
        # Add user message to history and display
        add_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_response(
                    prompt,
                    st.session_state.chat_history[:-1],  # Exclude the just-added user message
                    st.session_state.chat_model
                )
            st.markdown(response)
        
        # Add assistant response to history
        add_message("assistant", response)
