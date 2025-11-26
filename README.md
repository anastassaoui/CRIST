# Evaporation & Crystallization Simulator

Multi-page Streamlit web application for designing and optimizing an integrated multiple-effect evaporation and crystallization unit for sugar production.

## Project Overview

This application simulates and optimizes a complete sugar production process:
- **Multi-Effect Evaporation**: Concentrate sugar cane juice from 15% to 65%
- **Batch Crystallization**: Produce high-quality sugar crystals
- **Process Optimization**: Minimize costs using Pyomo and Google OR-Tools
- **Heat Integration**: Maximize energy recovery through pinch analysis

## Technology Stack

- **Thermodynamics**: CoolProp, thermo
- **Optimization**: Pyomo with Google OR-Tools (CBC solver)
- **Visualization**: Plotly (interactive charts)
- **Framework**: Streamlit
- **Scientific Computing**: NumPy, SciPy, Pandas

## Installation

### 1. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install All Dependencies (Including Solver)

```bash
pip install -r requirements.txt
```

**That's it!** Google OR-Tools (which includes the CBC solver) will be installed automatically via pip. No additional setup needed!

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at http://localhost:8501

## Project Structure

```
CRIST/
├── src/                        # Core simulation modules
│   ├── thermodynamique.py      # CoolProp/thermo wrappers
│   ├── evaporateurs.py         # Multi-effect evaporator
│   ├── cristallisation.py      # Batch crystallizer
│   ├── optimisation.py         # Optimization orchestration
│   └── visualization.py        # Plotly chart generation
│
├── models/                     # Pyomo optimization models
│   ├── evaporator_model.py
│   ├── crystallizer_model.py
│   └── integrated_model.py
│
├── pages/                      # Streamlit pages
│   ├── 1_Home.py
│   ├── 2_Evaporator.py
│   ├── 3_Crystallization.py
│   ├── 4_Optimization.py
│   ├── 5_Integration.py
│   └── 6_Results.py
│
├── app.py                      # Main entry point
├── config.py                   # Default parameters
└── requirements.txt            # Python dependencies
```

## Usage Guide

### 1. Evaporator Simulation (Page 2)

- Set number of effects (2-5)
- Configure feed conditions
- Run simulation
- View temperature, concentration, and pressure profiles
- Perform sensitivity analysis

### 2. Crystallization (Page 3)

- Choose cooling strategy (linear, exponential, optimal)
- Set batch parameters
- Compare strategies
- Analyze crystal size distribution (CSD)

### 3. Optimization (Page 4)

- Select optimization objective (steam or cost)
- Run Pyomo optimization with IPOPT
- Find optimal number of effects
- Compare configurations

### 4. Integration (Page 5)

- Perform pinch analysis
- Enable/disable heat recovery
- Calculate CAPEX, OPEX, ROI
- Compare economics with/without heat recovery

### 5. Results Dashboard (Page 6)

- View comprehensive results
- Export to Excel (planned)
- Generate PDF reports (planned)

## Default Process Specifications

**Feed:**
- Flow rate: 20,000 kg/h
- Concentration: 15% saccharose
- Temperature: 85°C
- Pressure: 1.5 bar

**Target:**
- Final concentration: 65% saccharose
- Crystal size: 450 μm
- CV: < 30%
- Purity: > 99.5%

**Steam:**
- Pressure: 3.5 bar
- Superheat: 10°C

## Features

- Interactive parameter input through GUI
- Real-time simulation with thermodynamic rigor
- Multiple cooling strategy comparison
- Sensitivity analysis
- Economic evaluation (CAPEX, OPEX, NPV, ROI)
- Interactive Plotly visualizations
- Session state management across pages

## Troubleshooting

### Solver Not Found Error

If optimization fails with "solver not found":
1. Reinstall OR-Tools: `pip install --upgrade ortools`
2. Restart the Streamlit app
3. Check installed solvers by running:
   ```python
   from src.solver_utils import get_available_solvers
   print(get_available_solvers())
   ```

### CoolProp Import Errors

If CoolProp fails to import:
1. Reinstall: `pip uninstall CoolProp && pip install CoolProp`
2. On Windows, you may need: `pip install CoolProp==6.4.1`

### Streamlit Session State Issues

If results don't persist across pages:
1. Restart the app
2. Clear browser cache
3. Check that simulations completed successfully

### Docker Build Issues

When building Docker image:
- Make sure all packages in requirements.txt are pip-installable
- OR-Tools works perfectly in Docker containers (no special configuration needed)

## Development

### Adding New Features

1. Add backend logic to `src/` modules
2. Add Pyomo models to `models/` if optimization needed
3. Add visualization functions to `src/visualization.py`
4. Update Streamlit pages in `pages/`
5. Update config.py for new parameters

### Extending Visualizations

All visualization functions in `src/visualization.py` return `plotly.graph_objects.Figure` objects. To add new charts:

```python
import plotly.graph_objects as go

def plot_new_metric(data):
    fig = go.Figure()
    # Add traces
    fig.add_trace(...)
    # Configure layout
    fig.update_layout(...)
    return fig
```

Then use in Streamlit:
```python
fig = plot_new_metric(data)
st.plotly_chart(fig, use_container_width=True)
```

## Future Enhancements

- Dockerization for easy deployment
- Excel and PDF export functionality
- Real-time optimization progress tracking
- Multi-user session management
- Database integration for results storage
- Advanced pinch analysis tools

## License

This project is for educational purposes as part of FST Settat coursework.

## Contact

Filière Procédés et Ingénierie Chimique (PIC)
Université Hassan 1 - FST Settat
Année Universitaire 2024-2025

---

**Note**: All solvers install automatically via pip! Just run `pip install -r requirements.txt` and you're ready to go.
