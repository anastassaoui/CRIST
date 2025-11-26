"""
Plotly visualization functions for Streamlit application.
All functions return plotly.graph_objects.Figure objects.
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def plot_temperature_profile(results):
    """
    Plot temperature profile across evaporator effects.

    Parameters:
    -----------
    results : list of dict
        Evaporator results for each effect

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    effects = [r['effect'] for r in results]
    temperatures = [r['T_boiling'] if 'T_boiling' in r else r.get('T', 0) for r in results]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=effects,
        y=temperatures,
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title='Temperature Profile Across Effects',
        xaxis_title='Effect Number',
        yaxis_title='Temperature (°C)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def plot_concentration_profile(results):
    """
    Plot concentration profile across evaporator effects.

    Parameters:
    -----------
    results : list of dict
        Evaporator results

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    effects = [r['effect'] for r in results]
    concentrations = [r['x_out'] * 100 for r in results]  # Convert to %

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=effects,
        y=concentrations,
        mode='lines+markers',
        name='Concentration',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(255, 127, 14, 0.2)'
    ))

    fig.update_layout(
        title='Concentration Profile Across Effects',
        xaxis_title='Effect Number',
        yaxis_title='Saccharose Concentration (%)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def plot_pressure_profile(results):
    """
    Plot pressure distribution across effects.

    Parameters:
    -----------
    results : list of dict
        Evaporator results

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    effects = [r['effect'] for r in results]
    pressures = [r['P'] / 1e5 for r in results]  # Convert to bar

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=effects,
        y=pressures,
        marker_color='#2ca02c',
        text=[f"{p:.2f} bar" for p in pressures],
        textposition='auto',
    ))

    fig.update_layout(
        title='Pressure Distribution Across Effects',
        xaxis_title='Effect Number',
        yaxis_title='Pressure (bar)',
        template='plotly_white',
        height=400
    )

    return fig


def plot_CSD(L_bins, n_distribution):
    """
    Plot crystal size distribution.

    Parameters:
    -----------
    L_bins : array
        Crystal sizes (m)
    n_distribution : array
        Number density

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Convert to microns
    L_microns = L_bins * 1e6

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=L_microns,
        y=n_distribution,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#9467bd', width=2),
        fillcolor='rgba(148, 103, 189, 0.3)'
    ))

    fig.update_layout(
        title='Crystal Size Distribution',
        xaxis_title='Crystal Size (μm)',
        yaxis_title='Number Density (nuclei/m³/μm)',
        template='plotly_white',
        height=400
    )

    return fig


def plot_CSD_comparison(strategies_results):
    """
    Compare crystal size distributions for different cooling strategies.

    Parameters:
    -----------
    strategies_results : dict
        Results for each strategy {strategy_name: (L_bins, n_dist)}

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for idx, (strategy, (L_bins, n_dist)) in enumerate(strategies_results.items()):
        L_microns = L_bins * 1e6

        fig.add_trace(go.Scatter(
            x=L_microns,
            y=n_dist,
            mode='lines',
            name=strategy.capitalize(),
            line=dict(color=colors[idx % len(colors)], width=2)
        ))

    fig.update_layout(
        title='Crystal Size Distribution Comparison',
        xaxis_title='Crystal Size (μm)',
        yaxis_title='Number Density',
        legend=dict(x=0.7, y=0.95),
        template='plotly_white',
        height=400
    )

    return fig


def plot_sensitivity_analysis(param_name, param_values, outputs):
    """
    Plot sensitivity analysis results.

    Parameters:
    -----------
    param_name : str
        Parameter name
    param_values : array
        Parameter values tested
    outputs : dict
        Output metrics {metric_name: values_array}

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()

    colors = px.colors.qualitative.Plotly

    for idx, (metric, values) in enumerate(outputs.items()):
        fig.add_trace(go.Scatter(
            x=param_values,
            y=values,
            mode='lines+markers',
            name=metric,
            line=dict(color=colors[idx % len(colors)], width=2),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=f'Sensitivity Analysis: {param_name}',
        xaxis_title=param_name,
        yaxis_title='Output Value',
        legend=dict(x=0.02, y=0.98),
        hovermode='x unified',
        template='plotly_white',
        height=500
    )

    return fig


def plot_cooling_profiles(time, temperature_profiles):
    """
    Plot cooling temperature profiles for different strategies.

    Parameters:
    -----------
    time : array
        Time points (s)
    temperature_profiles : dict
        {strategy_name: temperature_array}

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    for idx, (strategy, T_profile) in enumerate(temperature_profiles.items()):
        time_hours = time / 3600  # Convert to hours

        fig.add_trace(go.Scatter(
            x=time_hours,
            y=T_profile,
            mode='lines',
            name=strategy.capitalize(),
            line=dict(color=colors[idx % len(colors)], width=3)
        ))

    fig.update_layout(
        title='Cooling Profiles Comparison',
        xaxis_title='Time (hours)',
        yaxis_title='Temperature (°C)',
        legend=dict(x=0.7, y=0.95),
        template='plotly_white',
        height=400
    )

    return fig


def plot_supersaturation_evolution(time, S_profile):
    """
    Plot supersaturation evolution during crystallization.

    Parameters:
    -----------
    time : array
        Time points (s)
    S_profile : array
        Supersaturation values

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    time_hours = time / 3600

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time_hours,
        y=S_profile,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#d62728', width=2),
        fillcolor='rgba(214, 39, 40, 0.2)'
    ))

    # Add target supersaturation line
    fig.add_hline(y=0.05, line_dash="dash", line_color="gray",
                  annotation_text="Target S=0.05")

    fig.update_layout(
        title='Supersaturation Evolution',
        xaxis_title='Time (hours)',
        yaxis_title='Relative Supersaturation',
        template='plotly_white',
        height=400
    )

    return fig


def plot_pinch_curves(hot_streams, cold_streams):
    """
    Plot pinch diagram (composite curves).

    Parameters:
    -----------
    hot_streams : list of dict
        Hot stream data
    cold_streams : list of dict
        Cold stream data

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()

    # Simplified composite curve construction
    # Hot composite curve
    hot_temps = []
    hot_Q = []
    Q_cumulative = 0

    for stream in hot_streams:
        hot_temps.append(stream['T_in'])
        hot_Q.append(Q_cumulative)
        Q_cumulative += stream['heat_capacity'] * (stream['T_in'] - stream['T_out'])
        hot_temps.append(stream['T_out'])
        hot_Q.append(Q_cumulative)

    # Cold composite curve
    cold_temps = []
    cold_Q = []
    Q_cumulative = 0

    for stream in cold_streams:
        cold_temps.append(stream['T_in'])
        cold_Q.append(Q_cumulative)
        Q_cumulative += stream['heat_capacity'] * (stream['T_out'] - stream['T_in'])
        cold_temps.append(stream['T_out'])
        cold_Q.append(Q_cumulative)

    fig.add_trace(go.Scatter(
        x=hot_Q,
        y=hot_temps,
        mode='lines',
        name='Hot Composite',
        line=dict(color='#d62728', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=cold_Q,
        y=cold_temps,
        mode='lines',
        name='Cold Composite',
        line=dict(color='#1f77b4', width=3)
    ))

    fig.update_layout(
        title='Pinch Diagram - Composite Curves',
        xaxis_title='Heat Load (W)',
        yaxis_title='Temperature (°C)',
        legend=dict(x=0.02, y=0.98),
        template='plotly_white',
        height=500
    )

    return fig


def plot_cost_breakdown(cost_data):
    """
    Plot cost breakdown as pie chart.

    Parameters:
    -----------
    cost_data : dict
        Cost components {category: value}

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    labels = list(cost_data.keys())
    values = list(cost_data.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Set3)
    )])

    fig.update_layout(
        title='Cost Breakdown',
        template='plotly_white',
        height=400
    )

    return fig


def plot_mass_balance_sankey(flows):
    """
    Create Sankey diagram for mass flows.

    Parameters:
    -----------
    flows : list of dict
        Flow data [{source, target, value}, ...]

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Build unique nodes
    nodes = []
    for flow in flows:
        if flow['source'] not in nodes:
            nodes.append(flow['source'])
        if flow['target'] not in nodes:
            nodes.append(flow['target'])

    # Map to indices
    source_indices = [nodes.index(flow['source']) for flow in flows]
    target_indices = [nodes.index(flow['target']) for flow in flows]
    values = [flow['value'] for flow in flows]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values
        )
    )])

    fig.update_layout(
        title='Mass Balance - Sankey Diagram',
        height=500
    )

    return fig


def plot_energy_balance_sankey(heat_flows):
    """
    Create Sankey diagram for energy flows.

    Parameters:
    -----------
    heat_flows : list of dict
        Heat flow data [{source, target, value}, ...]

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    nodes = []
    for flow in heat_flows:
        if flow['source'] not in nodes:
            nodes.append(flow['source'])
        if flow['target'] not in nodes:
            nodes.append(flow['target'])

    source_indices = [nodes.index(flow['source']) for flow in heat_flows]
    target_indices = [nodes.index(flow['target']) for flow in heat_flows]
    values = [flow['value'] for flow in heat_flows]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            color='rgba(255, 127, 14, 0.8)'
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(255, 127, 14, 0.4)'
        )
    )])

    fig.update_layout(
        title='Energy Balance - Sankey Diagram',
        height=500
    )

    return fig


def create_3d_sensitivity(param1_values, param2_values, output_matrix, param1_name, param2_name, output_name):
    """
    Create 3D surface plot for two-parameter sensitivity analysis.

    Parameters:
    -----------
    param1_values : array
        First parameter values
    param2_values : array
        Second parameter values
    output_matrix : 2D array
        Output values (param1 x param2)
    param1_name : str
        First parameter name
    param2_name : str
        Second parameter name
    output_name : str
        Output metric name

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure(data=[go.Surface(
        x=param1_values,
        y=param2_values,
        z=output_matrix,
        colorscale='Viridis'
    )])

    fig.update_layout(
        title=f'3D Sensitivity: {output_name}',
        scene=dict(
            xaxis_title=param1_name,
            yaxis_title=param2_name,
            zaxis_title=output_name
        ),
        height=600
    )

    return fig


def plot_comparison_bar_chart(categories, data_dict):
    """
    Create grouped bar chart for comparing multiple datasets.

    Parameters:
    -----------
    categories : list
        Category labels
    data_dict : dict
        {series_name: values_array}

    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()

    for series_name, values in data_dict.items():
        fig.add_trace(go.Bar(
            name=series_name,
            x=categories,
            y=values
        ))

    fig.update_layout(
        title='Comparison',
        xaxis_title='Category',
        yaxis_title='Value',
        barmode='group',
        template='plotly_white',
        height=400
    )

    return fig
