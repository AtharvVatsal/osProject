"""
Advanced Traffic Signal Controller - Enhanced Streamlit GUI
Real-time visualization with improved UI and informative displays
"""

import streamlit as st
import time
import pandas as pd
from traffic_controller import (
    TrafficController, SignalState, Intersection
)
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import random
import io
from typing import List

# Page configuration
st.set_page_config(
    page_title="Traffic Signal Controller System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with modern design
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Signal Box Styling - Enhanced */
    .signal-box {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .signal-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .signal-box:hover::before {
        left: 100%;
    }
    
    .red-signal {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border: 3px solid #f44336;
        box-shadow: 0 0 20px rgba(244, 67, 54, 0.3);
    }
    
    .yellow-signal {
        background: linear-gradient(135deg, #fff9c4 0%, #fff59d 100%);
        border: 3px solid #ffeb3b;
        box-shadow: 0 0 20px rgba(255, 235, 59, 0.3);
        animation: pulse-yellow 2s infinite;
    }
    
    .green-signal {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 3px solid #4caf50;
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
        animation: pulse-green 1.5s infinite;
    }
    
    .emergency-signal {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
        border: 3px solid #e91e63;
        box-shadow: 0 0 30px rgba(233, 30, 99, 0.5);
        animation: blink 0.8s infinite;
    }
    
    @keyframes blink {
        0%, 50%, 100% { opacity: 1; transform: scale(1); }
        25%, 75% { opacity: 0.7; transform: scale(0.98); }
    }
    
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.3); }
        50% { box-shadow: 0 0 30px rgba(76, 175, 80, 0.6); }
    }
    
    @keyframes pulse-yellow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 235, 59, 0.3); }
        50% { box-shadow: 0 0 30px rgba(255, 235, 59, 0.6); }
    }
    
    /* Metric Cards - Enhanced */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-running {
        background-color: #4caf50;
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    }
    
    .status-stopped {
        background-color: #f44336;
        box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Traffic Flow Indicator */
    .traffic-flow {
        padding: 1rem;
        background: white;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .flow-bar {
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(90deg, #4caf50 0%, #ffeb3b 50%, #f44336 100%);
        transition: width 0.5s ease;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
        border: none;
        padding: 0.75rem 1.5rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .info-box h4 {
        margin-top: 0;
        font-weight: 600;
    }
    
    /* Event Log Styling */
    .event-log {
        background: #1e1e1e;
        color: #0f0;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 300px;
        overflow-y: auto;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }
    
    .event-log::-webkit-scrollbar {
        width: 8px;
    }
    
    .event-log::-webkit-scrollbar-track {
        background: #2e2e2e;
        border-radius: 4px;
    }
    
    .event-log::-webkit-scrollbar-thumb {
        background: #4caf50;
        border-radius: 4px;
    }
    
    /* Vehicle Counter */
    .vehicle-counter {
        display: inline-flex;
        align-items: center;
        background: rgba(255,255,255,0.9);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .vehicle-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    /* Performance Badge */
    .perf-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 5px;
    }
    
    .perf-excellent {
        background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%);
        color: white;
    }
    
    .perf-good {
        background: linear-gradient(135deg, #ffeb3b 0%, #ffc107 100%);
        color: #333;
    }
    
    .perf-fair {
        background: linear-gradient(135deg, #ff9800 0%, #ff5722 100%);
        color: white;
    }
    
    /* Responsive Grid */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'controller' not in st.session_state:
        st.session_state.controller = None
        st.session_state.running = False
        st.session_state.start_time = None
        st.session_state.event_history = []


def export_logs_to_csv(events: List[str]) -> bytes:
    """
    Convert event logs to CSV format
    
    Args:
        events: List of event log strings
        
    Returns:
        CSV file as bytes
    """
    if not events:
        return b""
    
    # Parse events into structured data
    log_data = []
    for event in events:
        # Extract timestamp and message
        # Format: [HH:MM:SS.mmm] Message
        if '[' in event and ']' in event:
            timestamp = event[event.find('[')+1:event.find(']')]
            message = event[event.find(']')+2:].strip()
        else:
            timestamp = "N/A"
            message = event
        
        # Parse message components
        direction = ""
        state = ""
        action = ""
        
        if "is now" in message:
            parts = message.split("is now")
            direction_part = parts[0].strip()
            state = parts[1].strip() if len(parts) > 1 else ""
            
            # Extract direction
            for dir_name in ["NORTH", "SOUTH", "EAST", "WEST"]:
                if dir_name in direction_part:
                    direction = dir_name
                    break
            
            # Determine action
            if "GREEN" in state or "✓" in message:
                action = "ENTER"
            elif "RED" in state or "✗" in message:
                action = "EXIT"
            elif "YELLOW" in state or "⚠" in message:
                action = "WARN"
            elif "EMERGENCY" in state or "🚨" in message:
                action = "EMERGENCY"
        
        elif "EMERGENCY" in message or "🚨" in message:
            action = "EMERGENCY"
            for dir_name in ["NORTH", "SOUTH", "EAST", "WEST"]:
                if dir_name in message:
                    direction = dir_name
                    break
            state = "EMERGENCY"
        
        elif "STARTED" in message:
            action = "SYSTEM_START"
            state = "ACTIVE"
        
        elif "STOPPING" in message:
            action = "SYSTEM_STOP"
            state = "INACTIVE"
        
        log_data.append({
            'Timestamp': timestamp,
            'Direction': direction,
            'State': state,
            'Action': action,
            'Full_Message': message
        })
    
    # Create DataFrame
    df = pd.DataFrame(log_data)
    
    # Convert to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue().encode('utf-8')


def create_download_button_for_logs(events: List[str]):
    """
    Create a download button for event logs as CSV
    
    Args:
        events: List of event log strings
    """
    if not events:
        st.info("📭 No events to export yet")
        return
    
    csv_data = export_logs_to_csv(events)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"traffic_signal_logs_{timestamp}.csv"
    
    st.download_button(
        label="📥 Download Logs as CSV",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
        type="secondary"
    )


def create_intersection_diagram(intersection: Intersection, signals: list):
    """Create a clean, professional intersection visualization"""
    
    # Get signal states
    signal_dict = {s.direction: s for s in signals}
    
    # Create figure with clean background
    fig = go.Figure()
    
    # ========== CLEAN ROAD DESIGN ==========
    
    # Main intersection area (light gray)
    fig.add_shape(type="rect", x0=-0.7, y0=-0.7, x1=0.7, y1=0.7,
                  fillcolor="#e0e0e0", line=dict(width=0), layer='below')
    
    # Vertical road (North-South)
    fig.add_shape(type="rect", x0=-0.5, y0=-2.8, x1=0.5, y1=2.8,
                  fillcolor="#4a4a4a", line=dict(width=0), layer='below')
    
    # Horizontal road (East-West)
    fig.add_shape(type="rect", x0=-2.8, y0=-0.5, x1=2.8, y1=0.5,
                  fillcolor="#4a4a4a", line=dict(width=0), layer='below')
    
    # Lane dividers - Clean dashed lines
    # Vertical center line
    dash_y_positions = list(range(-28, 29, 4))
    for y in dash_y_positions:
        fig.add_shape(type="line", x0=0, y0=y/10, x1=0, y1=(y+2)/10,
                      line=dict(color="white", width=3), layer='below')
    
    # Horizontal center line
    dash_x_positions = list(range(-28, 29, 4))
    for x in dash_x_positions:
        fig.add_shape(type="line", x0=x/10, y0=0, x1=(x+2)/10, y1=0,
                      line=dict(color="white", width=3), layer='below')
    
    # Crosswalk stripes - Clean white rectangles
    crosswalk_positions = [
        # North
        [(-0.4+i*0.15, 0.75), (-0.3+i*0.15, 0.95)] for i in range(6)
    ] + [
        # South
        [(-0.4+i*0.15, -0.95), (-0.3+i*0.15, -0.75)] for i in range(6)
    ] + [
        # East
        [(0.75, -0.4+i*0.15), (0.95, -0.3+i*0.15)] for i in range(6)
    ] + [
        # West
        [(-0.95, -0.4+i*0.15), (-0.75, -0.3+i*0.15)] for i in range(6)
    ]
    
    for (x0, y0), (x1, y1) in crosswalk_positions:
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor="white", line=dict(width=0), layer='below', opacity=0.9)
    
    # ========== TRAFFIC SIGNALS - Clean & Modern ==========
    
    signal_config = {
        "NORTH": {"pos": (0.35, 1.5), "arrow": "▼", "offset": (0.25, 0)},
        "SOUTH": {"pos": (-0.35, -1.5), "arrow": "▲", "offset": (-0.25, 0)},
        "EAST": {"pos": (1.5, -0.35), "arrow": "◀", "offset": (0, -0.25)},
        "WEST": {"pos": (-1.5, 0.35), "arrow": "▶", "offset": (0, 0.25)}
    }
    
    for direction, config in signal_config.items():
        signal = signal_dict.get(direction)
        if not signal:
            continue
        
        x, y = config["pos"]
        arrow = config["arrow"]
        
        # Determine signal appearance
        if signal.state == SignalState.GREEN:
            color = "#00C853"  # Bright green
            glow = "rgba(0, 200, 83, 0.4)"
            size = 60
            border = "#1B5E20"
        elif signal.state == SignalState.YELLOW:
            color = "#FFD600"  # Bright yellow
            glow = "rgba(255, 214, 0, 0.4)"
            size = 60
            border = "#F57F17"
        elif signal.state == SignalState.EMERGENCY:
            color = "#FF1744"  # Bright red
            glow = "rgba(255, 23, 68, 0.6)"
            size = 70
            border = "#B71C1C"
        else:  # RED
            color = "#D32F2F"  # Red
            glow = "rgba(211, 47, 47, 0.3)"
            size = 60
            border = "#B71C1C"
        
        # Signal housing (black box)
        fig.add_shape(
            type="rect",
            x0=x-0.18, y0=y-0.25, x1=x+0.18, y1=y+0.25,
            fillcolor="#1a1a1a",
            line=dict(color="#000000", width=2),
            layer='below'
        )
        
        # Signal pole (gray)
        pole_start_y = y - 0.45 if direction in ["NORTH", "SOUTH"] else y
        pole_end_y = y - 0.25 if direction in ["NORTH", "SOUTH"] else y
        pole_start_x = x if direction in ["NORTH", "SOUTH"] else x - 0.45 if direction == "EAST" else x + 0.45
        pole_end_x = x if direction in ["NORTH", "SOUTH"] else x - 0.25 if direction == "EAST" else x + 0.25
        
        fig.add_trace(go.Scatter(
            x=[pole_start_x, pole_end_x],
            y=[pole_start_y, pole_end_y],
            mode='lines',
            line=dict(color='#505050', width=6),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Glow effect
        for glow_size in [90, 75, 60]:
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers',
                marker=dict(size=glow_size, color=glow, opacity=0.25),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Main signal light
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers',
            marker=dict(
                size=size,
                color=color,
                line=dict(width=4, color=border),
                symbol='circle'
            ),
            name=direction,
            showlegend=False,
            hovertemplate=(
                f"<b style='font-size:14px'>🚦 {direction}</b><br>"
                f"<b>State:</b> <span style='font-size:13px'>{signal.state.value}</span><br>"
                f"<b>Cycles:</b> {signal.cycle_count}<br>"
                f"<b>Time:</b> {time.time() - signal.last_state_change:.1f}s<br>"
                "<extra></extra>"
            )
        ))
        
        # Direction arrow on signal
        fig.add_annotation(
            x=x, y=y,
            text=f"<b style='font-size:18px'>{arrow}</b>",
            showarrow=False,
            font=dict(color="white", size=18, family="Arial Black"),
            bgcolor="rgba(0,0,0,0)"
        )
    
    # ========== VEHICLE INDICATORS - Cleaner Design ==========
    
    vehicle_config = {
        "NORTH": [(0.2, 2.2), (0.2, 1.9), (0.2, 1.6)],
        "SOUTH": [(-0.2, -2.2), (-0.2, -1.9), (-0.2, -1.6)],
        "EAST": [(2.2, -0.2), (1.9, -0.2), (1.6, -0.2)],
        "WEST": [(-2.2, 0.2), (-1.9, 0.2), (-1.6, 0.2)]
    }
    
    for direction, positions in vehicle_config.items():
        signal = signal_dict.get(direction)
        if not signal:
            continue
        
        density = intersection.traffic_density.get(direction, 50)
        num_vehicles = min(int((density / 100) * 3), len(positions))
        
        for i in range(num_vehicles):
            x, y = positions[i]
            
            # Vehicle appearance based on signal state
            if signal.state == SignalState.GREEN:
                vehicle_color = "#4CAF50"
                vehicle_symbol = "triangle-up"
                vehicle_size = 25
            else:
                vehicle_color = "#FF5722"
                vehicle_symbol = "square"
                vehicle_size = 22
            
            # Rotate symbol based on direction
            if direction == "SOUTH":
                vehicle_symbol = "triangle-down"
            elif direction == "EAST":
                vehicle_symbol = "triangle-left"
            elif direction == "WEST":
                vehicle_symbol = "triangle-right"
            
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers',
                marker=dict(
                    size=vehicle_size,
                    color=vehicle_color,
                    symbol=vehicle_symbol,
                    line=dict(width=2, color='#1a1a1a')
                ),
                showlegend=False,
                hovertemplate=f"<b>🚗 Vehicle</b><br>Direction: {direction}<br>Status: {'Moving' if signal.state == SignalState.GREEN else 'Waiting'}<extra></extra>"
            ))
    
    # ========== ACTIVE FLOW INDICATORS ==========
    
    flow_arrows = {
        "NORTH": (0.25, 1.0, "▼"),
        "SOUTH": (-0.25, -1.0, "▲"),
        "EAST": (1.0, -0.25, "◀"),
        "WEST": (-1.0, 0.25, "▶")
    }
    
    for direction in intersection.active_directions:
        if direction in flow_arrows:
            x, y, arrow = flow_arrows[direction]
            
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers',
                marker=dict(
                    size=50,
                    color='rgba(76, 175, 80, 0.6)',
                    symbol='circle',
                    line=dict(width=0)
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig.add_annotation(
                x=x, y=y,
                text=f"<b style='font-size:24px'>{arrow}</b>",
                showarrow=False,
                font=dict(color="#2E7D32", size=24, family="Arial Black")
            )
    
    # ========== STATUS ANNOTATION ==========
    
    active_text = ", ".join(intersection.active_directions) if intersection.active_directions else "All RED"
    
    fig.add_annotation(
        text=f"<b style='font-size:15px'>Active: {active_text}</b>",
        xref="paper", yref="paper",
        x=0.5, y=1.02,
        showarrow=False,
        font=dict(size=15, color="#1a1a1a", family="Inter"),
        bgcolor="rgba(255, 255, 255, 0.95)",
        bordercolor="#667eea",
        borderwidth=2,
        borderpad=10
    )
    
    # ========== LAYOUT ==========
    
    fig.update_layout(
        title={
            'text': "<b>🚦 Live Intersection Monitor</b>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'color': '#1a1a1a', 'family': 'Inter'}
        },
        xaxis=dict(
            range=[-3.2, 3.2],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            range=[-3.2, 3.2],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        height=600,
        showlegend=False,
        plot_bgcolor='#b3d9ff',  # Light blue sky
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=70, b=20),
        hovermode='closest'
    )
    
    return fig


def display_signal_status(signal, intersection):
    """Display individual signal status with enhanced readability"""
    state = signal.state
    
    if state == SignalState.RED:
        css_class = "red-signal"
        emoji = "🔴"
    elif state == SignalState.YELLOW:
        css_class = "yellow-signal"
        emoji = "🟡"
    elif state == SignalState.GREEN:
        css_class = "green-signal"
        emoji = "🟢"
    else:  # EMERGENCY
        css_class = "emergency-signal"
        emoji = "🚨"
    
    time_in_state = time.time() - signal.last_state_change
    density = intersection.traffic_density.get(signal.direction, 0)
    
    # Calculate progress bar width for time in state
    max_time = signal.base_green_time + signal.yellow_time + 2
    progress = min((time_in_state / max_time) * 100, 100)
    
    # Performance rating based on cycle count
    if signal.cycle_count >= 10:
        perf_badge = '<span class="perf-badge perf-excellent">⭐ Excellent</span>'
    elif signal.cycle_count >= 5:
        perf_badge = '<span class="perf-badge perf-good">✓ Good</span>'
    else:
        perf_badge = '<span class="perf-badge perf-fair">○ Fair</span>'
    
    st.markdown(f"""
        <div class="signal-box {css_class}">
            <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">{emoji}</div>
            <div class="signal-box-title">
                {signal.direction}
            </div>
            <div class="signal-box-state">
                {state.value}
            </div>
            <div class="signal-box-info">
                <div class="signal-box-metric">
                    <span style="font-weight: 700;">⏱️ Time:</span> {time_in_state:.1f}s
                </div>
                <div class="signal-box-metric">
                    <span style="font-weight: 700;">🔄 Cycles:</span> {signal.cycle_count}
                </div>
                <div style="background: rgba(0,0,0,0.15); height: 8px; border-radius: 4px; overflow: hidden; margin: 0.8rem 0;">
                    <div style="background: linear-gradient(90deg, #4caf50, #ffeb3b, #f44336); height: 100%; width: {progress}%; transition: width 0.3s;"></div>
                </div>
                <div class="signal-box-metric">
                    <span style="font-weight: 700;">🚗 Traffic:</span> {density}%
                </div>
                <div style="margin-top: 0.8rem;">
                    {perf_badge}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def create_statistics_charts(controller: TrafficController):
    """Create enhanced statistics visualization charts"""
    
    if not controller.intersections:
        return None, None, None, None
    
    intersection = controller.intersections[0]
    signals = [s for s in controller.signals if s.intersection == intersection]
    
    # ========== CHART 1: Traffic Density Gauge ==========
    density_data = []
    for direction in ["NORTH", "SOUTH", "EAST", "WEST"]:
        density = intersection.traffic_density.get(direction, 0)
        density_data.append({
            "Direction": direction,
            "Density": density,
            "Status": "Heavy" if density > 66 else "Moderate" if density > 33 else "Light"
        })
    
    df_density = pd.DataFrame(density_data)
    
    fig_density = go.Figure()
    
    # Add bars with gradient colors
    colors = ['#4caf50' if d < 33 else '#ffeb3b' if d < 66 else '#f44336' 
              for d in df_density['Density']]
    
    fig_density.add_trace(go.Bar(
        x=df_density['Direction'],
        y=df_density['Density'],
        marker=dict(
            color=colors,
            line=dict(color='#333', width=2)
        ),
        text=df_density['Density'].apply(lambda x: f"{x}%"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Density: %{y}%<br><extra></extra>'
    ))
    
    fig_density.update_layout(
        title={
            'text': "🚗 Traffic Density by Direction",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        yaxis_title="Density (%)",
        height=300,
        plot_bgcolor='rgba(0,0,0,0.02)',
        paper_bgcolor='white',
        yaxis=dict(range=[0, 110], gridcolor='rgba(0,0,0,0.1)'),
        margin=dict(t=50, b=50)
    )
    
    # ========== CHART 2: Signal Performance (Cycles) ==========
    cycle_data = pd.DataFrame([
        {
            "Direction": s.direction,
            "Cycles": s.cycle_count,
            "Avg_Wait": intersection.stats.total_wait_time / max(s.cycle_count, 1)
        }
        for s in signals
    ])
    
    fig_cycles = go.Figure()
    
    fig_cycles.add_trace(go.Bar(
        x=cycle_data['Direction'],
        y=cycle_data['Cycles'],
        name='Cycles',
        marker=dict(
            color=cycle_data['Cycles'],
            colorscale='Greens',
            line=dict(color='#1b5e20', width=2),
            showscale=True,
            colorbar=dict(title="Cycles", len=0.5)
        ),
        text=cycle_data['Cycles'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Cycles: %{y}<br><extra></extra>'
    ))
    
    fig_cycles.update_layout(
        title={
            'text': "🔄 Signal Cycles Completed",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        yaxis_title="Number of Cycles",
        height=300,
        plot_bgcolor='rgba(0,0,0,0.02)',
        paper_bgcolor='white',
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        margin=dict(t=50, b=50)
    )
    
    # ========== CHART 3: System Performance Timeline ==========
    fig_timeline = go.Figure()
    
    # Create timeline data
    timeline_data = []
    for signal in signals:
        timeline_data.append({
            'Direction': signal.direction,
            'Cycles': signal.cycle_count,
            'State': signal.state.value
        })
    
    # Pie chart of current states
    state_counts = {}
    for signal in signals:
        state = signal.state.value.split()[1]  # Get just the color name
        state_counts[state] = state_counts.get(state, 0) + 1
    
    colors_map = {'RED': '#f44336', 'YELLOW': '#ffeb3b', 'GREEN': '#4caf50', 'EMERGENCY': '#e91e63'}
    
    fig_timeline.add_trace(go.Pie(
        labels=list(state_counts.keys()),
        values=list(state_counts.values()),
        marker=dict(colors=[colors_map.get(k, '#999') for k in state_counts.keys()]),
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    ))
    
    fig_timeline.update_layout(
        title={
            'text': "🎯 Current Signal Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        height=300,
        paper_bgcolor='white',
        showlegend=True,
        margin=dict(t=50, b=20)
    )
    
    # ========== CHART 4: Wait Time Analysis ==========
    wait_data = []
    for signal in signals:
        avg_wait = intersection.stats.total_wait_time / max(intersection.stats.total_cycles, 1)
        wait_data.append({
            'Direction': signal.direction,
            'Avg_Wait': avg_wait,
            'Cycles': signal.cycle_count
        })
    
    df_wait = pd.DataFrame(wait_data)
    
    fig_wait = go.Figure()
    
    fig_wait.add_trace(go.Scatter(
        x=df_wait['Direction'],
        y=df_wait['Avg_Wait'],
        mode='lines+markers',
        marker=dict(size=15, color='#667eea', line=dict(color='#333', width=2)),
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)',
        hovertemplate='<b>%{x}</b><br>Avg Wait: %{y:.2f}s<br><extra></extra>'
    ))
    
    fig_wait.update_layout(
        title={
            'text': "⏱️ Average Wait Time",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333'}
        },
        yaxis_title="Seconds",
        height=300,
        plot_bgcolor='rgba(0,0,0,0.02)',
        paper_bgcolor='white',
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        margin=dict(t=50, b=50)
    )
    
    return fig_density, fig_cycles, fig_timeline, fig_wait


def main():
    """Main application with enhanced UI"""
    initialize_session_state()
    
    # ========== HEADER ==========
    st.markdown("""
        <div class="main-header">
            <h1>🚦 Advanced Traffic Signal Controller System</h1>
            <p>Real-Time Multi-threaded Traffic Management | OS Concepts in Action</p>
        </div>
    """, unsafe_allow_html=True)
    
    # ========== SIDEBAR CONTROLS ==========
    with st.sidebar:
        # System status indicator
        if st.session_state.running:
            status_class = "status-running"
            status_text = "RUNNING"
        else:
            status_class = "status-stopped"
            status_text = "STOPPED"
        
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <span class="status-indicator {status_class}"></span>
                <span style="font-weight: 600; font-size: 1.1rem;">{status_text}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎛️ System Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_clicked = st.button("▶️ START", disabled=st.session_state.running, type="primary", use_container_width=True)
            if start_clicked:
                st.session_state.controller = TrafficController(num_intersections=1)
                st.session_state.controller.start()
                st.session_state.running = True
                st.session_state.start_time = datetime.now()
                st.success("✅ System Started!")
                time.sleep(0.5)
                st.rerun()
        
        with col2:
            stop_clicked = st.button("⏹️ STOP", disabled=not st.session_state.running, type="secondary", use_container_width=True)
            if stop_clicked:
                if st.session_state.controller:
                    st.session_state.controller.stop()
                st.session_state.running = False
                st.warning("⏸️ System Stopped")
                time.sleep(0.5)
                st.rerun()
        
        st.divider()
        
        # Emergency controls
        if st.session_state.running:
            st.markdown("### 🚨 Emergency Vehicle")
            st.caption("Trigger priority scheduling")
            
            emergency_direction = st.selectbox(
                "Select Direction",
                ["NORTH", "SOUTH", "EAST", "WEST"],
                key="emergency_dir"
            )
            
            if st.button("🚑 Dispatch Emergency Vehicle", type="primary", use_container_width=True):
                st.session_state.controller.trigger_emergency(0, emergency_direction)
                st.success(f"🚨 Emergency vehicle dispatched from {emergency_direction}!")
                time.sleep(0.5)
                st.rerun()
            
            st.divider()
            
            # Traffic density controls
            st.markdown("### 🚗 Traffic Density Control")
            st.caption("Adjust traffic load for adaptive timing")
            
            with st.expander("Adjust Traffic Density", expanded=False):
                for direction in ["NORTH", "SOUTH", "EAST", "WEST"]:
                    density = st.slider(
                        f"{direction}",
                        0, 100, 
                        st.session_state.controller.intersections[0].traffic_density.get(direction, 50),
                        key=f"density_{direction}",
                        help=f"Current: {st.session_state.controller.intersections[0].traffic_density.get(direction, 50)}%"
                    )
                    st.session_state.controller.update_traffic_density(0, direction, density)
            
            st.divider()
            
            # System info
            st.markdown("### ℹ️ System Information")
            
            if st.session_state.start_time:
                runtime = datetime.now() - st.session_state.start_time
                hours, remainder = divmod(runtime.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <div style="font-size: 0.9rem; color: #666;">Runtime</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #333;">
                            {hours:02d}:{minutes:02d}:{seconds:02d}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # OS Concepts badge
            st.markdown("""
                <div class="info-box">
                    <h4>🎓 OS Concepts</h4>
                    <div style="font-size: 0.9rem;">
                        ✓ Multi-threading<br>
                        ✓ Mutex & Semaphores<br>
                        ✓ Synchronization<br>
                        ✓ Deadlock Prevention<br>
                        ✓ Priority Scheduling<br>
                        ✓ Race Condition Prevention
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Welcome message when stopped
            st.markdown("""
                <div class="info-box">
                    <h4>👋 Welcome!</h4>
                    <p>Click <b>START</b> above to begin the traffic signal simulation.</p>
                    <p>This system demonstrates advanced Operating System concepts through real-time traffic management.</p>
                </div>
            """, unsafe_allow_html=True)
    
    # ========== MAIN CONTENT ==========
    
    if not st.session_state.running:
        # Welcome screen with feature showcase
        st.info("👈 **Click START in the sidebar to begin the simulation**")
        
        # Feature cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 2rem; text-align: center;">🧵</div>
                    <h3 style="text-align: center; color: #667eea;">Multi-threading</h3>
                    <p style="text-align: center; font-size: 0.9rem;">4 independent signal threads running concurrently</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 2rem; text-align: center;">🔒</div>
                    <h3 style="text-align: center; color: #667eea;">Synchronization</h3>
                    <p style="text-align: center; font-size: 0.9rem;">Mutex, Semaphore & Condition Variables</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 2rem; text-align: center;">🚨</div>
                    <h3 style="text-align: center; color: #667eea;">Priority Scheduling</h3>
                    <p style="text-align: center; font-size: 0.9rem;">Emergency vehicle preemption system</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 2rem; text-align: center;">🛡️</div>
                    <h3 style="text-align: center; color: #667eea;">Deadlock Prevention</h3>
                    <p style="text-align: center; font-size: 0.9rem;">Multiple prevention strategies</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick guide
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("### 🎯 Quick Start Guide")
            st.markdown("""
                1. **Start System**: Click START button in sidebar
                2. **Observe**: Watch signals synchronize automatically
                3. **Test Emergency**: Try the emergency vehicle feature
                4. **Adjust Load**: Modify traffic density sliders
                5. **Monitor**: View real-time statistics and logs
            """)
        
        with col_b:
            st.markdown("### 📊 What You'll See")
            st.markdown("""
                - **Live Intersection**: Visual traffic signal representation
                - **Signal Status**: Real-time state of each direction
                - **Analytics**: Traffic density and performance metrics
                - **Event Log**: Detailed system activity stream
                - **Statistics**: Comprehensive performance data
            """)
    
    else:
        # ========== LIVE SYSTEM DISPLAY ==========
        
        controller = st.session_state.controller
        intersection = controller.intersections[0]
        signals = [s for s in controller.signals if s.intersection == intersection]
        
        # ========== TOP METRICS ROW ==========
        stats = controller.get_system_stats()
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric(
                label="🔄 Total Cycles",
                value=stats['total_cycles'],
                delta=f"+{len([s for s in signals if s.state == SignalState.GREEN])} active"
            )
        
        with col2:
            st.metric(
                label="⏱️ Avg Wait",
                value=stats['average_wait_time'],
                delta="Live"
            )
        
        with col3:
            st.metric(
                label="🚑 Emergencies",
                value=stats['emergency_responses'],
                delta="Handled"
            )
        
        with col4:
            st.metric(
                label="🛡️ Deadlocks Prevented",
                value=stats['deadlock_preventions'],
                delta="Protected"
            )
        
        with col5:
            st.metric(
                label="🚗 Vehicles Passed",
                value=stats['vehicles_passed'],
                delta=f"+{random.randint(3,8)} this cycle"
            )
        
        with col6:
            active_count = len(intersection.active_directions)
            st.metric(
                label="🚦 Active Signals",
                value=f"{active_count}/4",
                delta="Live"
            )
        
        st.divider()
        
        # ========== MAIN VISUALIZATION AREA ==========
        
        col_main_left, col_main_right = st.columns([2, 1])
        
        with col_main_left:
            # Enhanced intersection diagram
            fig_intersection = create_intersection_diagram(intersection, signals)
            st.plotly_chart(fig_intersection, use_container_width=True, key="intersection_viz")
            
            # Traffic flow summary
            st.markdown("### 📊 Traffic Flow Analysis")
            
            flow_cols = st.columns(4)
            for idx, direction in enumerate(["NORTH", "SOUTH", "EAST", "WEST"]):
                with flow_cols[idx]:
                    signal = next((s for s in signals if s.direction == direction), None)
                    if signal:
                        density = intersection.traffic_density.get(direction, 0)
                        
                        # Determine flow status
                        if signal.state == SignalState.GREEN:
                            flow_status = "FLOWING"
                            flow_color = "#4caf50"
                            flow_icon = "🟢"
                        elif signal.state == SignalState.YELLOW:
                            flow_status = "SLOWING"
                            flow_color = "#ffeb3b"
                            flow_icon = "🟡"
                        else:
                            flow_status = "STOPPED"
                            flow_color = "#f44336"
                            flow_icon = "🔴"
                        
                        st.markdown(f"""
                            <div class="traffic-flow">
                                <div class="traffic-flow-title">{flow_icon} {direction}</div>
                                <div class="traffic-flow-status" style="color: {flow_color};">{flow_status}</div>
                                <div class="traffic-flow-load">Load: <b>{density}%</b></div>
                                <div style="background: #e0e0e0; height: 10px; border-radius: 5px; overflow: hidden;">
                                    <div class="flow-bar" style="width: {density}%;"></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
        
        with col_main_right:
            # Signal status cards
            st.markdown("### 🚦 Signal Status")
            for signal in signals:
                display_signal_status(signal, intersection)
            
            # Active directions summary
            st.markdown("### ✅ Active Lanes")
            if intersection.active_directions:
                for direction in intersection.active_directions:
                    st.success(f"🟢 **{direction}** - GREEN LIGHT")
            else:
                st.info("🔴 All signals at RED")
        
        st.divider()
        
        # ========== ANALYTICS DASHBOARD ==========
        
        st.markdown("### 📈 System Analytics Dashboard")
        
        fig_density, fig_cycles, fig_timeline, fig_wait = create_statistics_charts(controller)
        
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(fig_density, use_container_width=True, key="chart_density")
            st.plotly_chart(fig_timeline, use_container_width=True, key="chart_timeline")
        
        with chart_col2:
            st.plotly_chart(fig_cycles, use_container_width=True, key="chart_cycles")
            st.plotly_chart(fig_wait, use_container_width=True, key="chart_wait")
        
        st.divider()
        
        # ========== PERFORMANCE INSIGHTS ==========
        
        st.markdown("### 💡 Performance Insights")
        
        insight_cols = st.columns(3)
        
        with insight_cols[0]:
            # Efficiency rating
            avg_cycles = sum(s.cycle_count for s in signals) / len(signals) if signals else 0
            efficiency = min(100, (avg_cycles / max(1, (datetime.now() - st.session_state.start_time).seconds / 10)) * 100)
            
            st.markdown(f"""
                <div class="metric-card">
                    <h4>⚡ System Efficiency</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: #4caf50; margin: 1rem 0;">
                        {efficiency:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #666;">
                        Based on cycle completion rate
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with insight_cols[1]:
            # Fairness score
            cycle_counts = [s.cycle_count for s in signals]
            if cycle_counts:
                avg = sum(cycle_counts) / len(cycle_counts)
                variance = sum((c - avg) ** 2 for c in cycle_counts) / len(cycle_counts)
                fairness = max(0, 100 - (variance ** 0.5))
            else:
                fairness = 100
            
            st.markdown(f"""
                <div class="metric-card">
                    <h4>⚖️ Fairness Score</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: #667eea; margin: 1rem 0;">
                        {fairness:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #666;">
                        Distribution balance across signals
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with insight_cols[2]:
            # Safety rating
            safety = max(0, 100 - (stats['deadlock_preventions'] * 2))
            
            st.markdown(f"""
                <div class="metric-card">
                    <h4>🛡️ Safety Rating</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: #f44336; margin: 1rem 0;">
                        {safety:.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #666;">
                        Conflict avoidance effectiveness
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # ========== EVENT LOG ==========
        
        col_log_header, col_log_download = st.columns([3, 1])
        
        with col_log_header:
            st.markdown("### 📝 System Event Log")
        
        with col_log_download:
            st.markdown("<div style='padding-top: 0.5rem;'></div>", unsafe_allow_html=True)
            # Placeholder for download button
        
        events = []
        try:
            while not intersection.event_log.empty():
                events.append(intersection.event_log.get_nowait())
        except:
            pass
        
        if events:
            # Display last 20 events in styled terminal
            event_text = "\n".join(events[-20:])
            st.markdown(f"""
                <div class="event-log">
                    <pre style="margin: 0; color: #0f0; font-size: 1rem; line-height: 1.6;">{event_text}</pre>
                </div>
            """, unsafe_allow_html=True)
            
            # Add CSV download button
            with col_log_download:
                create_download_button_for_logs(events)
        else:
            st.info("📭 No events logged yet. System is initializing...")
        
        # Auto-refresh for live updates
        time.sleep(0.5)
        st.rerun()


if __name__ == "__main__":
    main()