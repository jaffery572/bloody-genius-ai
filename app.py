import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk
from datetime import datetime, timedelta
import time
import random
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="🛡️ Counter-Drone Commander | C-UAS Training Simulator",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 3.8rem;
        background: linear-gradient(135deg, #00FF00 0%, #006400 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        margin-bottom: 0.5rem;
        text-align: center;
        line-height: 1;
        font-family: 'Courier New', monospace;
    }
    
    .terminal-card {
        background: linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(0,64,0,0.9) 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #00FF00;
        height: 100%;
        font-family: 'Courier New', monospace;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #006400 0%, #00FF00 100%);
        color: black !important;
        font-weight: 700;
        border: 1px solid #00FF00;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        width: 100%;
        font-family: 'Courier New', monospace;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== DRONE DATABASE ====================
DRONE_SPECS = {
    'Shahed-136': {
        'type': 'Loitering Munition',
        'speed': 185,
        'range': 2500,
        'payload': 40,
        'altitude': 5000,
        'threat_level': 'CRITICAL',
        'countermeasures': ['EW Jamming', 'GPS Spoofing', 'Hard-Kill'],
        'color': '#FF0000'
    },
    'DJI Mavic 3': {
        'type': 'Commercial Quadcopter',
        'speed': 72,
        'range': 30,
        'payload': 0.9,
        'altitude': 6000,
        'threat_level': 'MEDIUM',
        'countermeasures': ['RF Jamming', 'DroneNet Capture', 'Geofencing'],
        'color': '#FFA500'
    },
    'Orlan-10': {
        'type': 'Reconnaissance UAV',
        'speed': 150,
        'range': 600,
        'payload': 6,
        'altitude': 5000,
        'threat_level': 'HIGH',
        'countermeasures': ['DIRCM', 'Electronic Attack', 'Kinetic'],
        'color': '#FFFF00'
    }
}

COUNTERMEASURE_SYSTEMS = {
    'RF Jamming': {
        'range': 2000,
        'effectiveness': 0.85,
        'cost': 50000,
        'deployment_time': 30,
        'type': 'Soft-Kill'
    },
    'GPS Spoofing': {
        'range': 3000,
        'effectiveness': 0.75,
        'cost': 80000,
        'deployment_time': 45,
        'type': 'Soft-Kill'
    },
    'Laser Defense': {
        'range': 1000,
        'effectiveness': 0.95,
        'cost': 300000,
        'deployment_time': 5,
        'type': 'Hard-Kill'
    }
}

# ==================== SESSION STATE ====================
if 'simulation_state' not in st.session_state:
    st.session_state.simulation_state = {
        'active': False,
        'time_elapsed': 0,
        'score': 0,
        'assets_protected': 100,
        'radar_coverage': 85,
        'current_scenario': 'PEACETIME PATROL',
        'console_log': [],
        'budget_remaining': 1000000,
        'neutralized_threats': 0,
        'breaches': 0
    }

if 'threats' not in st.session_state:
    st.session_state.threats = []

# ==================== SIMULATION ENGINE ====================
class CounterDroneSimulator:
    def __init__(self):
        self.base_location = {'lat': 33.7215, 'lon': 73.0433}
        self.protected_radius = 5000
        self.time_step = 1
        
    def generate_threat(self, threat_type, count=1):
        threats = []
        
        for i in range(count):
            threat_id = f"{threat_type}_{len(st.session_state.threats) + i}"
            
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(10000, 50000)
            speed = DRONE_SPECS[threat_type]['speed'] * 1000 / 3600
            
            lat_offset = (distance * np.cos(angle)) / 111000
            lon_offset = (distance * np.sin(angle)) / (111000 * np.cos(np.radians(self.base_location['lat'])))
            
            threat = {
                'id': threat_id,
                'type': threat_type,
                'lat': self.base_location['lat'] + lat_offset,
                'lon': self.base_location['lon'] + lon_offset,
                'altitude': random.uniform(100, DRONE_SPECS[threat_type]['altitude']),
                'speed': speed,
                'heading': np.pi - angle,
                'status': 'INCOMING',
                'distance_to_base': distance,
                'countermeasure_assigned': None,
                'threat_level': DRONE_SPECS[threat_type]['threat_level'],
                'color': DRONE_SPECS[threat_type]['color'],
                'health': 100
            }
            
            threats.append(threat)
        
        return threats
    
    def update_threats(self):
        updated_threats = []
        neutralized_count = 0
        
        for threat in st.session_state.threats:
            if threat['status'] == 'NEUTRALIZED':
                neutralized_count += 1
                updated_threats.append(threat)
                continue
                
            distance_moved = threat['speed'] * self.time_step
            lat_offset = (distance_moved * np.cos(threat['heading'])) / 111000
            lon_offset = (distance_moved * np.sin(threat['heading'])) / (111000 * np.cos(np.radians(threat['lat'])))
            
            threat['lat'] += lat_offset
            threat['lon'] += lon_offset
            
            lat_diff = (threat['lat'] - self.base_location['lat']) * 111000
            lon_diff = (threat['lon'] - self.base_location['lon']) * 111000 * np.cos(np.radians(self.base_location['lat']))
            threat['distance_to_base'] = np.sqrt(lat_diff**2 + lon_diff**2)
            
            if threat['distance_to_base'] < 500:
                threat['status'] = 'BREACH'
                st.session_state.simulation_state['breaches'] += 1
                st.session_state.simulation_state['assets_protected'] -= random.randint(5, 20)
                self.log_event(f"🚨 BREACH! {threat['id']} penetrated defenses!", "CRITICAL")
            
            if threat['countermeasure_assigned']:
                cm = COUNTERMEASURE_SYSTEMS[threat['countermeasure_assigned']]
                effectiveness = cm['effectiveness']
                
                if threat['distance_to_base'] < cm['range']:
                    if random.random() < effectiveness:
                        threat['status'] = 'NEUTRALIZED'
                        st.session_state.simulation_state['neutralized_threats'] += 1
                        st.session_state.simulation_state['score'] += 100
                        self.log_event(f"✅ THREAT NEUTRALIZED: {threat['id']} by {threat['countermeasure_assigned']}")
            
            updated_threats.append(threat)
        
        return updated_threats, neutralized_count
    
    def deploy_countermeasure(self, threat_id, cm_type):
        for threat in st.session_state.threats:
            if threat['id'] == threat_id and threat['status'] == 'INCOMING':
                threat['countermeasure_assigned'] = cm_type
                cost = COUNTERMEASURE_SYSTEMS[cm_type]['cost']
                st.session_state.simulation_state['budget_remaining'] -= cost
                self.log_event(f"🚀 DEPLOYED: {cm_type} against {threat_id}")
                return True
        return False
    
    def log_event(self, message, level="INFO"):
        timestamp = f"[{st.session_state.simulation_state['time_elapsed']:04d}s]"
        
        if level == "CRITICAL":
            log_entry = f"{timestamp} 🔥 {message}"
        elif level == "WARNING":
            log_entry = f"{timestamp} ⚠️ {message}"
        elif level == "SUCCESS":
            log_entry = f"{timestamp} ✅ {message}"
        else:
            log_entry = f"{timestamp} ℹ️ {message}"
            
        st.session_state.simulation_state['console_log'].insert(0, log_entry)
        
        if len(st.session_state.simulation_state['console_log']) > 50:
            st.session_state.simulation_state['console_log'].pop()
    
    def generate_scenario(self, scenario_name):
        st.session_state.threats = []
        
        if scenario_name == "SHAHED SWARM":
            threats = self.generate_threat('Shahed-136', 5)
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Shahed-136 Swarm (5 units)", "CRITICAL")
            
        elif scenario_name == "AIRPORT BREACH":
            threats = []
            threats.extend(self.generate_threat('DJI Mavic 3', 2))
            threats.extend(self.generate_threat('Orlan-10', 1))
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Airport Multi-Threat Breach", "WARNING")
            
        elif scenario_name == "CRITICAL INFRASTRUCTURE":
            threats = []
            threats.extend(self.generate_threat('Orlan-10', 2))
            threats.extend(self.generate_threat('Shahed-136', 2))
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Critical Infrastructure Defense", "CRITICAL")
            
        elif scenario_name == "PEACETIME PATROL":
            threats = self.generate_threat('DJI Mavic 3', 1)
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Peacetime Patrol & Monitoring", "INFO")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00FF00;'>⚙️ COMMAND CONSOLE</h2>", unsafe_allow_html=True)
    
    with st.expander("🛡️ COMMANDER STATUS", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="terminal-card">
                <h4 style='color: #00FF00;'>RANK</h4>
                <h3 style='color: #00FF00; margin: 0;'>C-UAS COMMANDER</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            status = "ONLINE" if st.session_state.simulation_state['active'] else "STANDBY"
            status_color = "#00FF00" if st.session_state.simulation_state['active'] else "#FFA500"
            st.markdown(f"""
            <div class="terminal-card">
                <h4 style='color: #00FF00;'>STATUS</h4>
                <h3 style='color: {status_color}; margin: 0;'>{status}</h3>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("🎯 TRAINING SCENARIOS", expanded=True):
        scenarios = ["PEACETIME PATROL", "AIRPORT BREACH", "SHAHED SWARM", "CRITICAL INFRASTRUCTURE"]
        
        current_scenario = st.session_state.simulation_state['current_scenario']
        
        # FIX: Check if current scenario exists in list
        if current_scenario not in scenarios:
            current_scenario = scenarios[0]
            st.session_state.simulation_state['current_scenario'] = current_scenario
        
        selected_scenario = st.selectbox(
            "Select Scenario",
            scenarios,
            index=scenarios.index(current_scenario)
        )
        
        if st.button("🚀 DEPLOY SCENARIO", use_container_width=True):
            simulator = CounterDroneSimulator()
            simulator.generate_scenario(selected_scenario)
            st.session_state.simulation_state['current_scenario'] = selected_scenario
            st.session_state.simulation_state['active'] = True
            st.rerun()
    
    with st.expander("⚡ COUNTERMEASURE SYSTEMS", expanded=True):
        for cm_name, cm_specs in COUNTERMEASURE_SYSTEMS.items():
            if st.button(f"📡 {cm_name}", use_container_width=True):
                if st.session_state.threats:
                    active_threats = [t for t in st.session_state.threats if t['status'] == 'INCOMING']
                    if active_threats:
                        highest_threat = max(active_threats, key=lambda x: 
                                            {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}[x['threat_level']])
                        simulator = CounterDroneSimulator()
                        simulator.deploy_countermeasure(highest_threat['id'], cm_name)
                        st.rerun()
    
    with st.expander("🔧 SYSTEM CONTROLS", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ START SIM", use_container_width=True):
                st.session_state.simulation_state['active'] = True
                st.rerun()
            
            if st.button("⏸️ PAUSE", use_container_width=True):
                st.session_state.simulation_state['active'] = False
                st.rerun()
        
        with col2:
            if st.button("🔄 RESET", use_container_width=True):
                st.session_state.simulation_state = {
                    'active': False,
                    'time_elapsed': 0,
                    'score': 0,
                    'assets_protected': 100,
                    'radar_coverage': 85,
                    'current_scenario': 'PEACETIME PATROL',
                    'console_log': [],
                    'budget_remaining': 1000000,
                    'neutralized_threats': 0,
                    'breaches': 0
                }
                st.session_state.threats = []
                st.rerun()
    
    with st.expander("📡 SYSTEM STATUS", expanded=True):
        radar_coverage = st.session_state.simulation_state['radar_coverage']
        st.markdown(f"**RADAR COVERAGE:** {radar_coverage}%")
        st.progress(radar_coverage / 100)
        
        assets_protected = st.session_state.simulation_state['assets_protected']
        st.markdown(f"**ASSETS PROTECTED:** {assets_protected}%")
        st.progress(assets_protected / 100)
        
        budget = st.session_state.simulation_state['budget_remaining']
        st.markdown(f"**BUDGET:** ${budget:,}")

# ==================== MAIN CONTENT ====================
st.markdown("<h1 class='main-header'>🛡️ COUNTER-DRONE COMMANDER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00FF00;'>Real-time C-UAS Training Simulator</p>", unsafe_allow_html=True)

# Initialize simulator
simulator = CounterDroneSimulator()

# Run simulation if active
if st.session_state.simulation_state['active']:
    st.session_state.threats, neutralized = simulator.update_threats()
    st.session_state.simulation_state['time_elapsed'] += 1

# Create tabs
tab1, tab2, tab3 = st.tabs(["🎯 SITUATION ROOM", "🛰️ RADAR OVERVIEW", "📊 INTEL DASHBOARD"])

with tab1:
    st.markdown("<h2 style='color: #00FF00;'>SITUATION ROOM</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_threats = len([t for t in st.session_state.threats if t['status'] == 'INCOMING'])
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>ACTIVE THREATS</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0;'>{active_threats}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score = st.session_state.simulation_state['score']
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>MISSION SCORE</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0;'>{score}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        neutralized = st.session_state.simulation_state['neutralized_threats']
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>NEUTRALIZED</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0;'>{neutralized}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        breaches = st.session_state.simulation_state['breaches']
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>BREACHES</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0;'>{breaches}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Console Output
    st.markdown("<h3 style='color: #00FF00;'>COMMAND CONSOLE</h3>", unsafe_allow_html=True)
    
    console_html = "<div style='background: black; color: #00FF00; padding: 1rem; border-radius: 4px; border: 1px solid #00FF00; height: 200px; overflow-y: auto; font-family: Courier New;'>"
    for log in st.session_state.simulation_state['console_log'][:10]:
        console_html += f"<div style='margin: 2px 0;'>{log}</div>"
    console_html += "</div>"
    
    st.markdown(console_html, unsafe_allow_html=True)

with tab2:
    st.markdown("<h2 style='color: #00FF00;'>RADAR OVERVIEW</h2>", unsafe_allow_html=True)
    
    if st.session_state.threats:
        # Prepare data for map
        base_data = pd.DataFrame([{
            'lat': simulator.base_location['lat'],
            'lon': simulator.base_location['lon'],
            'size': 100,
            'color': [0, 255, 0, 180]
        }])
        
        threats_data = []
        for threat in st.session_state.threats:
            if threat['status'] != 'NEUTRALIZED':
                color_hex = threat['color'].lstrip('#')
                rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                
                threats_data.append({
                    'lat': threat['lat'],
                    'lon': threat['lon'],
                    'size': 50,
                    'color': list(rgb) + [200],
                    'id': threat['id'],
                    'type': threat['type'],
                    'threat_level': threat['threat_level'],
                    'distance': threat['distance_to_base']
                })
        
        if threats_data:
            threats_df = pd.DataFrame(threats_data)
            
            # Create layers
            base_layer = pdk.Layer(
                'ScatterplotLayer',
                base_data,
                get_position='[lon, lat]',
                get_color='color',
                get_radius='size',
                pickable=True
            )
            
            threats_layer = pdk.Layer(
                'ScatterplotLayer',
                threats_df,
                get_position='[lon, lat]',
                get_color='color',
                get_radius='size',
                pickable=True
            )
            
            # Set view state
            view_state = pdk.ViewState(
                latitude=simulator.base_location['lat'],
                longitude=simulator.base_location['lon'],
                zoom=10,
                pitch=0
            )
            
            # Render map
            r = pdk.Deck(
                layers=[base_layer, threats_layer],
                initial_view_state=view_state,
                tooltip={
                    'html': '<b>{type}</b><br>Distance: {distance:.0f}m',
                    'style': {
                        'color': 'white',
                        'backgroundColor': 'rgba(0,0,0,0.8)'
                    }
                }
            )
            
            st.pydeck_chart(r)
    
    # Threat List
    st.markdown("<h3 style='color: #00FF00;'>ACTIVE THREATS</h3>", unsafe_allow_html=True)
    
    if st.session_state.threats:
        threat_data = []
        for threat in st.session_state.threats:
            if threat['status'] != 'NEUTRALIZED':
                threat_data.append({
                    'ID': threat['id'],
                    'Type': threat['type'],
                    'Threat Level': threat['threat_level'],
                    'Distance (m)': f"{threat['distance_to_base']:.0f}",
                    'Status': threat['status']
                })
        
        if threat_data:
            threat_df = pd.DataFrame(threat_data)
            st.dataframe(threat_df, use_container_width=True)

with tab3:
    st.markdown("<h2 style='color: #00FF00;'>INTELLIGENCE DASHBOARD</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Drone Specs
        st.markdown("<h3 style='color: #00FF00;'>DRONE SPECIFICATIONS</h3>", unsafe_allow_html=True)
        
        drone_data = []
        for drone_name, specs in DRONE_SPECS.items():
            drone_data.append({
                'Drone': drone_name,
                'Speed (km/h)': specs['speed'],
                'Range (km)': specs['range'],
                'Threat Level': specs['threat_level'],
                'Cost (USD)': 'Classified'
            })
        
        df_drones = pd.DataFrame(drone_data)
        st.dataframe(df_drones, use_container_width=True)
    
    with col2:
        # Countermeasure Systems
        st.markdown("<h3 style='color: #00FF00;'>COUNTERMEASURE SYSTEMS</h3>", unsafe_allow_html=True)
        
        cm_data = []
        for cm_name, specs in COUNTERMEASURE_SYSTEMS.items():
            cm_data.append({
                'System': cm_name,
                'Range (m)': specs['range'],
                'Effectiveness': f"{specs['effectiveness']*100}%",
                'Cost (USD)': f"${specs['cost']:,}"
            })
        
        df_cm = pd.DataFrame(cm_data)
        st.dataframe(df_cm, use_container_width=True)

# Auto-refresh if simulation is active
if st.session_state.simulation_state['active']:
    time.sleep(1)
    st.rerun()
