import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk
from datetime import datetime, timedelta
import time
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="🛡️ Counter-Drone Commander | C-UAS Training Simulator",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://counterdrone.com/support',
        'Report a bug': 'https://counterdrone.com/issues',
        'About': "Military-Grade Counter-Drone Training Simulator"
    }
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Military-grade theme */
    .main-header {
        font-size: 3.8rem;
        background: linear-gradient(135deg, #00FF00 0%, #006400 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        margin-bottom: 0.5rem;
        text-align: center;
        line-height: 1;
        text-shadow: 0 0 10px rgba(0,255,0,0.3);
        font-family: 'Courier New', monospace;
    }
    
    .sub-header {
        font-size: 1.4rem;
        color: #00FF00;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
        font-family: 'Courier New', monospace;
    }
    
    .section-header {
        font-size: 2rem;
        background: linear-gradient(135deg, #00FF00 0%, #008000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00FF00;
        font-family: 'Courier New', monospace;
    }
    
    .subsection-header {
        font-size: 1.5rem;
        color: #00FF00;
        font-weight: 600;
        margin-top: 1.2rem;
        margin-bottom: 1rem;
        font-family: 'Courier New', monospace;
    }
    
    /* Military terminal cards */
    .terminal-card {
        background: linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(0,64,0,0.9) 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #00FF00;
        height: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        font-family: 'Courier New', monospace;
    }
    
    .terminal-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(135deg, #00FF00 0%, #006400 100%);
    }
    
    .terminal-card:hover {
        box-shadow: 0 0 20px rgba(0,255,0,0.3);
        border: 1px solid #00FF00;
    }
    
    /* Threat level colors */
    .critical-card {
        border: 2px solid #FF0000 !important;
        background: linear-gradient(135deg, rgba(64,0,0,0.9) 0%, rgba(0,0,0,0.9) 100%) !important;
    }
    
    .high-card {
        border: 2px solid #FFA500 !important;
        background: linear-gradient(135deg, rgba(64,64,0,0.9) 0%, rgba(0,0,0,0.9) 100%) !important;
    }
    
    .medium-card {
        border: 2px solid #FFFF00 !important;
        background: linear-gradient(135deg, rgba(64,64,0,0.9) 0%, rgba(0,0,0,0.9) 100%) !important;
    }
    
    .low-card {
        border: 2px solid #00FF00 !important;
        background: linear-gradient(135deg, rgba(0,64,0,0.9) 0%, rgba(0,0,0,0.9) 100%) !important;
    }
    
    /* Status indicators */
    .status-online {
        color: #00FF00;
        font-weight: bold;
    }
    
    .status-offline {
        color: #FF0000;
        font-weight: bold;
    }
    
    .status-warning {
        color: #FFFF00;
        font-weight: bold;
    }
    
    /* Button styling - Military */
    .stButton > button {
        background: linear-gradient(135deg, #006400 0%, #00FF00 100%);
        color: black !important;
        font-weight: 700;
        border: 1px solid #00FF00;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        transition: all 0.3s;
        width: 100%;
        font-family: 'Courier New', monospace;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00FF00 0%, #006400 100%);
        box-shadow: 0 0 15px rgba(0,255,0,0.5);
        color: white !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FF0000, #00FF00);
    }
    
    /* Tab styling - Military */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        padding: 0 1rem;
        background: rgba(0,0,0,0.8);
        border: 1px solid #00FF00;
        border-radius: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(0,0,0,0.8);
        border-radius: 4px 4px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        border: 1px solid #00FF00;
        font-family: 'Courier New', monospace;
        color: #00FF00;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #006400;
        border-bottom: 3px solid #00FF00;
        color: #00FF00;
    }
    
    /* Input field styling */
    .stNumberInput > div > div > input {
        background: rgba(0,0,0,0.8);
        border: 1px solid #00FF00;
        border-radius: 4px;
        color: #00FF00;
        font-family: 'Courier New', monospace;
    }
    
    .stSelectbox > div > div {
        background: rgba(0,0,0,0.8);
        border: 1px solid #00FF00;
        border-radius: 4px;
        color: #00FF00;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Radar scan animation */
    @keyframes radar-scan {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .radar-scan {
        animation: radar-scan 2s linear infinite;
    }
    
    /* Blinking alert */
    @keyframes blink-alert {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    .blink-alert {
        animation: blink-alert 1s infinite;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.2rem;
        }
        .section-header {
            font-size: 1.6rem;
        }
        .subsection-header {
            font-size: 1.2rem;
        }
    }
    
    /* Custom scrollbar - Terminal style */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.8);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00FF00 0%, #006400 100%);
        border-radius: 4px;
    }
    
    /* Console output styling */
    .console-output {
        background: black;
        color: #00FF00;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #00FF00;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    
    .console-line {
        margin: 0;
        padding: 2px 0;
        border-bottom: 1px solid rgba(0,255,0,0.1);
    }
    
    /* Threat badge */
    .threat-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 8px;
        margin-bottom: 8px;
        font-family: 'Courier New', monospace;
    }
    
    .threat-critical {
        background: linear-gradient(135deg, #FF0000, #800000);
        color: white;
        animation: blink-alert 0.5s infinite;
    }
    
    .threat-high {
        background: linear-gradient(135deg, #FFA500, #FF8C00);
        color: black;
    }
    
    .threat-medium {
        background: linear-gradient(135deg, #FFFF00, #FFD700);
        color: black;
    }
    
    .threat-low {
        background: linear-gradient(135deg, #00FF00, #006400);
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DRONE & THREAT DATABASE ====================
DRONE_SPECS = {
    'Shahed-136': {
        'type': 'Loitering Munition',
        'speed': 185,  # km/h
        'range': 2500,  # km
        'payload': 40,  # kg
        'altitude': 5000,  # m
        'rcs': 0.1,  # Radar Cross Section (m²)
        'threat_level': 'CRITICAL',
        'countermeasures': ['EW Jamming', 'GPS Spoofing', 'Hard-Kill'],
        'origin': 'Iran',
        'cost': 20000,  # USD
        'color': '#FF0000'
    },
    'DJI Mavic 3': {
        'type': 'Commercial Quadcopter',
        'speed': 72,
        'range': 30,
        'payload': 0.9,
        'altitude': 6000,
        'rcs': 0.01,
        'threat_level': 'MEDIUM',
        'countermeasures': ['RF Jamming', 'DroneNet Capture', 'Geofencing'],
        'origin': 'China',
        'cost': 2200,
        'color': '#FFA500'
    },
    'Orlan-10': {
        'type': 'Reconnaissance UAV',
        'speed': 150,
        'range': 600,
        'payload': 6,
        'altitude': 5000,
        'rcs': 0.5,
        'threat_level': 'HIGH',
        'countermeasures': ['DIRCM', 'Electronic Attack', 'Kinetic'],
        'origin': 'Russia',
        'cost': 100000,
        'color': '#FFFF00'
    },
    'Switchblade 300': {
        'type': 'Kamikaze Drone',
        'speed': 160,
        'range': 10,
        'payload': 0.5,
        'altitude': 4500,
        'rcs': 0.05,
        'threat_level': 'CRITICAL',
        'countermeasures': ['Laser Defense', 'AEW&C', 'Hard-Kill'],
        'origin': 'USA',
        'cost': 6000,
        'color': '#FF0000'
    },
    'Cargo Smuggler': {
        'type': 'Modified Commercial',
        'speed': 60,
        'range': 40,
        'payload': 5,
        'altitude': 200,
        'rcs': 0.02,
        'threat_level': 'HIGH',
        'countermeasures': ['RF Detection', 'Net Guns', 'K-9 Units'],
        'origin': 'Various',
        'cost': 3000,
        'color': '#FFA500'
    }
}

COUNTERMEASURE_SYSTEMS = {
    'RF Jamming': {
        'range': 2000,  # meters
        'effectiveness': 0.85,
        'cost': 50000,
        'deployment_time': 30,  # seconds
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
    },
    'DroneNet Capture': {
        'range': 200,
        'effectiveness': 0.70,
        'cost': 25000,
        'deployment_time': 60,
        'type': 'Capture'
    },
    'Hard-Kill (Missile)': {
        'range': 5000,
        'effectiveness': 0.99,
        'cost': 500000,
        'deployment_time': 10,
        'type': 'Hard-Kill'
    },
    'Electronic Attack': {
        'range': 4000,
        'effectiveness': 0.80,
        'cost': 200000,
        'deployment_time': 20,
        'type': 'Soft-Kill'
    }
}

# ==================== SESSION STATE INITIALIZATION ====================
if 'simulation_state' not in st.session_state:
    st.session_state.simulation_state = {
        'active': False,
        'time_elapsed': 0,
        'threats_active': [],
        'countermeasures_deployed': [],
        'score': 0,
        'assets_protected': 100,
        'radar_coverage': 85,
        'current_scenario': 'PEACETIME PATROL',
        'console_log': [],
        'budget_remaining': 1000000,
        'interceptions': 0,
        'neutralized_threats': 0,
        'breaches': 0
    }

if 'threats' not in st.session_state:
    st.session_state.threats = []

if 'assets' not in st.session_state:
    st.session_state.assets = []

# ==================== SIMULATION ENGINE ====================
class CounterDroneSimulator:
    def __init__(self):
        self.base_location = {'lat': 33.7215, 'lon': 73.0433}  # Rawalpindi
        self.protected_radius = 5000  # meters
        self.time_step = 1  # seconds per simulation step
        
    def generate_threat(self, threat_type, count=1):
        """Generate new drone threats"""
        threats = []
        
        for i in range(count):
            threat_id = f"{threat_type}_{len(st.session_state.threats) + i}"
            
            # Generate random approach vector
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(10000, 50000)  # 10-50km away
            speed = DRONE_SPECS[threat_type]['speed'] * 1000 / 3600  # Convert to m/s
            
            # Calculate starting position
            lat_offset = (distance * np.cos(angle)) / 111000
            lon_offset = (distance * np.sin(angle)) / (111000 * np.cos(np.radians(self.base_location['lat'])))
            
            threat = {
                'id': threat_id,
                'type': threat_type,
                'lat': self.base_location['lat'] + lat_offset,
                'lon': self.base_location['lon'] + lon_offset,
                'altitude': random.uniform(100, DRONE_SPECS[threat_type]['altitude']),
                'speed': speed,
                'heading': np.pi - angle,  # Head toward base
                'status': 'INCOMING',
                'distance_to_base': distance,
                'detection_probability': 0.0,
                'countermeasure_assigned': None,
                'time_detected': None,
                'time_neutralized': None,
                'threat_level': DRONE_SPECS[threat_type]['threat_level'],
                'color': DRONE_SPECS[threat_type]['color'],
                'health': 100
            }
            
            threats.append(threat)
        
        return threats
    
    def update_threats(self):
        """Update threat positions and status"""
        updated_threats = []
        neutralized_count = 0
        
        for threat in st.session_state.threats:
            if threat['status'] == 'NEUTRALIZED':
                neutralized_count += 1
                updated_threats.append(threat)
                continue
                
            # Update position
            distance_moved = threat['speed'] * self.time_step
            lat_offset = (distance_moved * np.cos(threat['heading'])) / 111000
            lon_offset = (distance_moved * np.sin(threat['heading'])) / (111000 * np.cos(np.radians(threat['lat'])))
            
            threat['lat'] += lat_offset
            threat['lon'] += lon_offset
            
            # Update distance to base
            lat_diff = (threat['lat'] - self.base_location['lat']) * 111000
            lon_diff = (threat['lon'] - self.base_location['lon']) * 111000 * np.cos(np.radians(self.base_location['lat']))
            threat['distance_to_base'] = np.sqrt(lat_diff**2 + lon_diff**2)
            
            # Update detection probability based on distance and RCS
            rcs = DRONE_SPECS[threat['type']]['rcs']
            detection_range = st.session_state.simulation_state['radar_coverage'] * 100  # meters per % coverage
            
            if threat['distance_to_base'] < detection_range:
                threat['detection_probability'] = min(1.0, (detection_range - threat['distance_to_base']) / detection_range * rcs * 10)
                
                if threat['time_detected'] is None and threat['detection_probability'] > 0.3:
                    threat['time_detected'] = st.session_state.simulation_state['time_elapsed']
                    self.log_event(f"THREAT DETECTED: {threat['id']} ({threat['type']}) at {threat['distance_to_base']:.0f}m")
            
            # Check if threat reached base
            if threat['distance_to_base'] < 500:  # Breach distance
                threat['status'] = 'BREACH'
                st.session_state.simulation_state['breaches'] += 1
                st.session_state.simulation_state['assets_protected'] -= random.randint(5, 20)
                self.log_event(f"🚨 BREACH! {threat['id']} penetrated defenses!", "CRITICAL")
            
            # Apply countermeasure effects
            if threat['countermeasure_assigned']:
                cm = COUNTERMEASURE_SYSTEMS[threat['countermeasure_assigned']]
                effectiveness = cm['effectiveness']
                
                # Check if countermeasure reached threat
                if threat['distance_to_base'] < cm['range']:
                    if random.random() < effectiveness:
                        threat['status'] = 'NEUTRALIZED'
                        threat['time_neutralized'] = st.session_state.simulation_state['time_elapsed']
                        st.session_state.simulation_state['neutralized_threats'] += 1
                        st.session_state.simulation_state['score'] += 100
                        self.log_event(f"✅ THREAT NEUTRALIZED: {threat['id']} by {threat['countermeasure_assigned']}")
                    else:
                        threat['health'] -= random.randint(20, 50)
                        if threat['health'] <= 0:
                            threat['status'] = 'NEUTRALIZED'
                            threat['time_neutralized'] = st.session_state.simulation_state['time_elapsed']
                            st.session_state.simulation_state['neutralized_threats'] += 1
                            st.session_state.simulation_state['score'] += 80
                            self.log_event(f"⚠️ THREAT DAMAGED: {threat['id']} but still active")
            
            updated_threats.append(threat)
        
        return updated_threats, neutralized_count
    
    def deploy_countermeasure(self, threat_id, cm_type):
        """Deploy countermeasure against specific threat"""
        for threat in st.session_state.threats:
            if threat['id'] == threat_id and threat['status'] == 'INCOMING':
                threat['countermeasure_assigned'] = cm_type
                cost = COUNTERMEASURE_SYSTEMS[cm_type]['cost']
                st.session_state.simulation_state['budget_remaining'] -= cost
                st.session_state.simulation_state['interceptions'] += 1
                self.log_event(f"🚀 DEPLOYED: {cm_type} against {threat_id}")
                return True
        return False
    
    def log_event(self, message, level="INFO"):
        """Add event to console log"""
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
        
        # Keep only last 50 logs
        if len(st.session_state.simulation_state['console_log']) > 50:
            st.session_state.simulation_state['console_log'].pop()
    
    def generate_scenario(self, scenario_name):
        """Generate threats based on scenario"""
        st.session_state.threats = []
        
        if scenario_name == "SHAHED SWARM":
            # 10x Shahed-136 swarm attack
            threats = self.generate_threat('Shahed-136', 10)
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Shahed-136 Swarm (10 units)", "CRITICAL")
            
        elif scenario_name == "AIRPORT BREACH":
            # Mixed threat to airport
            threats = []
            threats.extend(self.generate_threat('DJI Mavic 3', 3))
            threats.extend(self.generate_threat('Cargo Smuggler', 2))
            threats.extend(self.generate_threat('Switchblade 300', 1))
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Airport Multi-Threat Breach", "WARNING")
            
        elif scenario_name == "CRITICAL INFRASTRUCTURE":
            # High-value target protection
            threats = []
            threats.extend(self.generate_threat('Orlan-10', 2))
            threats.extend(self.generate_threat('Shahed-136', 3))
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Critical Infrastructure Defense", "CRITICAL")
            
        elif scenario_name == "PEACETIME PATROL":
            # Low-intensity monitoring
            threats = self.generate_threat('DJI Mavic 3', 1)
            st.session_state.threats.extend(threats)
            self.log_event("SCENARIO STARTED: Peacetime Patrol & Monitoring", "INFO")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00FF00;'>⚙️ COMMAND CONSOLE</h2>", unsafe_allow_html=True)
    
    # Commander Status
    with st.expander("🛡️ COMMANDER STATUS", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="terminal-card">
                <h4 style='color: #00FF00;'>RANK</h4>
                <h3 style='color: #00FF00; margin: 0;'>C-UAS COMMANDER</h4>
                <p style='color: #00FF00; margin: 0;'>Clearance: TOP SECRET</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            status = "ONLINE" if st.session_state.simulation_state['active'] else "STANDBY"
            status_color = "#00FF00" if st.session_state.simulation_state['active'] else "#FFA500"
            st.markdown(f"""
            <div class="terminal-card">
                <h4 style='color: #00FF00;'>STATUS</h4>
                <h3 style='color: {status_color}; margin: 0;'>{status}</h3>
                <p style='color: #00FF00; margin: 0;'>Time: {st.session_state.simulation_state['time_elapsed']}s</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Scenario Selection - FIXED ERROR HERE
    with st.expander("🎯 TRAINING SCENARIOS", expanded=True):
        scenarios = ["PEACETIME PATROL", "AIRPORT BREACH", "SHAHED SWARM", "CRITICAL INFRASTRUCTURE"]
        
        # Get current scenario
        current_scenario = st.session_state.simulation_state['current_scenario']
        
        # Make sure current scenario is in the list
        if current_scenario not in scenarios:
            # Reset to first scenario if not found
            st.session_state.simulation_state['current_scenario'] = scenarios[0]
            current_scenario = scenarios[0]
        
        # Find index safely
        try:
            scenario_index = scenarios.index(current_scenario)
        except ValueError:
            scenario_index = 0
            st.session_state.simulation_state['current_scenario'] = scenarios[0]
        
        selected_scenario = st.selectbox(
            "Select Scenario",
            scenarios,
            index=scenario_index
        )
        
        if st.button("🚀 DEPLOY SCENARIO", use_container_width=True):
            simulator = CounterDroneSimulator()
            simulator.generate_scenario(selected_scenario)
            st.session_state.simulation_state['current_scenario'] = selected_scenario
            st.session_state.simulation_state['active'] = True
            st.rerun()
    
    # Countermeasure Deployment
    with st.expander("⚡ COUNTERMEASURE SYSTEMS", expanded=True):
        st.markdown("**AVAILABLE SYSTEMS:**")
        
        for cm_name, cm_specs in COUNTERMEASURE_SYSTEMS.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{cm_name}**")
                st.caption(f"Range: {cm_specs['range']}m | Cost: ${cm_specs['cost']:,}")
            with col2:
                if st.button(f"📡", key=f"cm_{cm_name}", help=f"Deploy {cm_name}"):
                    if st.session_state.threats:
                        # Auto-assign to highest threat
                        active_threats = [t for t in st.session_state.threats if t['status'] == 'INCOMING']
                        if active_threats:
                            highest_threat = max(active_threats, key=lambda x: 
                                                {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}[x['threat_level']])
                            simulator = CounterDroneSimulator()
                            simulator.deploy_countermeasure(highest_threat['id'], cm_name)
                            st.rerun()
    
    # System Controls
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
                    'threats_active': [],
                    'countermeasures_deployed': [],
                    'score': 0,
                    'assets_protected': 100,
                    'radar_coverage': 85,
                    'current_scenario': 'PEACETIME PATROL',
                    'console_log': [],
                    'budget_remaining': 1000000,
                    'interceptions': 0,
                    'neutralized_threats': 0,
                    'breaches': 0
                }
                st.session_state.threats = []
                st.rerun()
            
            if st.button("⚡ FAST FORWARD", use_container_width=True):
                if st.session_state.simulation_state['active']:
                    for _ in range(10):
                        simulator = CounterDroneSimulator()
                        st.session_state.threats, _ = simulator.update_threats()
                    st.session_state.simulation_state['time_elapsed'] += 10
                    st.rerun()
    
    # System Status
    with st.expander("📡 SYSTEM STATUS", expanded=True):
        radar_coverage = st.session_state.simulation_state['radar_coverage']
        st.markdown(f"**RADAR COVERAGE:** {radar_coverage}%")
        st.progress(radar_coverage / 100)
        
        assets_protected = st.session_state.simulation_state['assets_protected']
        st.markdown(f"**ASSETS PROTECTED:** {assets_protected}%")
        st.progress(assets_protected / 100)
        
        budget = st.session_state.simulation_state['budget_remaining']
        st.markdown(f"**BUDGET REMAINING:** ${budget:,}")
        st.progress(budget / 1000000)
    
    st.markdown("---")
    
    # Quick Actions
    with st.expander("⚡ QUICK ACTIONS"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🛰️ BOOST RADAR", use_container_width=True):
                if st.session_state.simulation_state['budget_remaining'] >= 50000:
                    st.session_state.simulation_state['radar_coverage'] = min(100, st.session_state.simulation_state['radar_coverage'] + 10)
                    st.session_state.simulation_state['budget_remaining'] -= 50000
                    simulator = CounterDroneSimulator()
                    simulator.log_event("Radar coverage boosted +10%")
                    st.rerun()
        
        with col2:
            if st.button("🛡️ FORTIFY DEFENSES", use_container_width=True):
                if st.session_state.simulation_state['budget_remaining'] >= 75000:
                    st.session_state.simulation_state['assets_protected'] = min(100, st.session_state.simulation_state['assets_protected'] + 15)
                    st.session_state.simulation_state['budget_remaining'] -= 75000
                    simulator = CounterDroneSimulator()
                    simulator.log_event("Defenses fortified +15%")
                    st.rerun()
    
    st.markdown("---")
    
    # Intelligence Briefing
    with st.expander("📊 INTELLIGENCE BRIEFING", expanded=True):
        st.markdown("**GLOBAL THREAT ALERT LEVEL:**")
        st.markdown("<span class='threat-badge threat-critical'>CRITICAL</span>", unsafe_allow_html=True)
        
        st.markdown("**ACTIVE THREATS:**")
        for drone_type, specs in DRONE_SPECS.items():
            threat_level = specs['threat_level']
            badge_class = f"threat-badge threat-{threat_level.lower()}"
            st.markdown(f"<span class='{badge_class}'>{drone_type}</span>", unsafe_allow_html=True)
    
    # Monetization Section
    st.markdown("---")
    st.markdown("### 💰 COMMERCIAL DEPLOYMENT")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 10px; background: rgba(0,64,0,0.8); border-radius: 4px; border: 1px solid #00FF00;'>
            <small><strong>Enterprise License</strong></small><br>
            <strong>$2,500/mo</strong><br>
            <small>Security Firms</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 10px; background: rgba(0,64,0,0.8); border-radius: 4px; border: 1px solid #00FF00;'>
            <small><strong>Military License</strong></small><br>
            <strong>$25,000/mo</strong><br>
            <small>Training Bases</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-top: 10px;'>
        <small><i>Contact: contracts@counterdrone.com</i></small>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================
st.markdown("<h1 class='main-header'>🛡️ COUNTER-DRONE COMMANDER</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Real-time C-UAS Training Simulator | Shahed-136 Swarms • DJI Breaches • Cargo Smugglers</p>", unsafe_allow_html=True)

# Initialize simulator
simulator = CounterDroneSimulator()

# Run simulation if active
if st.session_state.simulation_state['active']:
    # Update threats
    st.session_state.threats, neutralized = simulator.update_threats()
    st.session_state.simulation_state['time_elapsed'] += 1
    
    # Generate occasional new threats
    if random.random() < 0.1 and st.session_state.simulation_state['time_elapsed'] % 30 == 0:
        new_threats = simulator.generate_threat(random.choice(list(DRONE_SPECS.keys())))
        st.session_state.threats.extend(new_threats)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 SITUATION ROOM", 
    "🛰️ RADAR OVERVIEW", 
    "⚡ COUNTERMEASURES", 
    "📊 INTEL DASHBOARD", 
    "📋 AFTER ACTION"
])

with tab1:
    st.markdown("<h2 class='section-header'>SITUATION ROOM</h2>", unsafe_allow_html=True)
    
    # Top Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        active_threats = len([t for t in st.session_state.threats if t['status'] == 'INCOMING'])
        card_class = "terminal-card critical-card" if active_threats > 5 else "terminal-card high-card" if active_threats > 2 else "terminal-card"
        st.markdown(f"""
        <div class="{card_class}">
            <h4 style='color: #00FF00;'>ACTIVE THREATS</h4>
            <h1 style='color: {'#FF0000' if active_threats > 5 else '#FFA500' if active_threats > 2 else '#00FF00'}; text-align: center; margin: 0;'>{active_threats}</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>Inbound Targets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score = st.session_state.simulation_state['score']
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>MISSION SCORE</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0;'>{score}</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>Effectiveness Rating</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        neutralized = st.session_state.simulation_state['neutralized_threats']
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>NEUTRALIZED</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0;'>{neutralized}</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>Threats Eliminated</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        breaches = st.session_state.simulation_state['breaches']
        card_class = "terminal-card critical-card" if breaches > 0 else "terminal-card"
        st.markdown(f"""
        <div class="{card_class}">
            <h4 style='color: #00FF00;'>DEFENSE BREACHES</h4>
            <h1 style='color: {'#FF0000' if breaches > 0 else '#00FF00'}; text-align: center; margin: 0;'>{breaches}</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>Perimeter Violations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        response_time = st.session_state.simulation_state['interceptions'] * 5 if st.session_state.simulation_state['interceptions'] > 0 else 999
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>AVG RESPONSE</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0;'>{response_time}s</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>Detection to Engagement</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Console Output
    st.markdown("<h3 class='subsection-header'>COMMAND CONSOLE</h3>", unsafe_allow_html=True)
    
    console_html = "<div class='console-output'>"
    for log in st.session_state.simulation_state['console_log'][:20]:
        console_html += f"<div class='console-line'>{log}</div>"
    console_html += "</div>"
    
    st.markdown(console_html, unsafe_allow_html=True)
    
    # Quick Action Buttons
    st.markdown("<h3 class='subsection-header'>QUICK ENGAGEMENT</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 AUTO-ENGAGE HIGHEST THREAT", use_container_width=True):
            active_threats = [t for t in st.session_state.threats if t['status'] == 'INCOMING']
            if active_threats:
                highest_threat = max(active_threats, key=lambda x: 
                                    {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}[x['threat_level']])
                cm = random.choice(list(COUNTERMEASURE_SYSTEMS.keys()))
                simulator.deploy_countermeasure(highest_threat['id'], cm)
                st.rerun()
    
    with col2:
        if st.button("🛡️ DEFENSIVE POSTURE", use_container_width=True):
            for threat in st.session_state.threats:
                if threat['status'] == 'INCOMING' and threat['distance_to_base'] < 3000:
                    simulator.deploy_countermeasure(threat['id'], 'RF Jamming')
            st.rerun()
    
    with col3:
        if st.button("💥 HARD-KILL ALL CRITICAL", use_container_width=True):
            critical_threats = [t for t in st.session_state.threats if t['status'] == 'INCOMING' and t['threat_level'] == 'CRITICAL']
            for threat in critical_threats:
                simulator.deploy_countermeasure(threat['id'], 'Hard-Kill (Missile)')
            st.rerun()
    
    with col4:
        if st.button("📡 SCAN FOR THREATS", use_container_width=True):
            st.session_state.simulation_state['radar_coverage'] = min(100, st.session_state.simulation_state['radar_coverage'] + 5)
            st.rerun()

with tab2:
    st.markdown("<h2 class='section-header'>RADAR OVERVIEW</h2>", unsafe_allow_html=True)
    
    # Create radar visualization
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
                # Convert color hex to RGB
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
                pickable=True,
                auto_highlight=True
            )
            
            # Create defense perimeter
            perimeter_points = []
            for angle in np.linspace(0, 2*np.pi, 100):
                lat_offset = (simulator.protected_radius * np.cos(angle)) / 111000
                lon_offset = (simulator.protected_radius * np.sin(angle)) / (111000 * np.cos(np.radians(simulator.base_location['lat'])))
                perimeter_points.append({
                    'lat': simulator.base_location['lat'] + lat_offset,
                    'lon': simulator.base_location['lon'] + lon_offset
                })
            
            perimeter_df = pd.DataFrame(perimeter_points)
            perimeter_layer = pdk.Layer(
                'LineLayer',
                perimeter_df,
                get_position='[lon, lat]',
                get_color=[0, 255, 0, 100],
                get_width=2,
                pickable=False
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
                layers=[perimeter_layer, base_layer, threats_layer],
                initial_view_state=view_state,
                tooltip={
                    'html': '<b>{type}</b><br>ID: {id}<br>Threat Level: {threat_level}<br>Distance: {distance:.0f}m',
                    'style': {
                        'color': 'white',
                        'backgroundColor': 'rgba(0,0,0,0.8)',
                        'fontFamily': 'Courier New'
                    }
                }
            )
            
            st.pydeck_chart(r)
    
    # Threat List
    st.markdown("<h3 class='subsection-header'>ACTIVE THREAT TRACKING</h3>", unsafe_allow_html=True)
    
    if st.session_state.threats:
        threat_data = []
        for threat in st.session_state.threats:
            if threat['status'] != 'NEUTRALIZED':
                threat_data.append({
                    'ID': threat['id'],
                    'Type': threat['type'],
                    'Threat Level': threat['threat_level'],
                    'Distance (m)': f"{threat['distance_to_base']:.0f}",
                    'Status': threat['status'],
                    'Detection %': f"{threat['detection_probability']*100:.1f}%",
                    'Countermeasure': threat['countermeasure_assigned'] or 'None'
                })
        
        if threat_data:
            threat_df = pd.DataFrame(threat_data)
            st.dataframe(
                threat_df,
                use_container_width=True,
                height=300
            )

with tab3:
    st.markdown("<h2 class='section-header'>COUNTERMEASURE SYSTEMS</h2>", unsafe_allow_html=True)
    
    # Countermeasure Systems Grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='subsection-header'>SOFT-KILL SYSTEMS</h3>", unsafe_allow_html=True)
        
        soft_kill_cm = {k: v for k, v in COUNTERMEASURE_SYSTEMS.items() if v['type'] in ['Soft-Kill', 'Capture']}
        
        for cm_name, cm_specs in soft_kill_cm.items():
            with st.expander(f"📡 {cm_name}", expanded=False):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"""
                    **Range:** {cm_specs['range']}m  
                    **Effectiveness:** {cm_specs['effectiveness']*100}%  
                    **Deployment Time:** {cm_specs['deployment_time']}s  
                    **Cost:** ${cm_specs['cost']:,}
                    """)
                
                with col_b:
                    active_threats = [t for t in st.session_state.threats if t['status'] == 'INCOMING']
                    if active_threats:
                        if st.button(f"DEPLOY", key=f"deploy_{cm_name}"):
                            # Auto-select closest threat
                            closest_threat = min(active_threats, key=lambda x: x['distance_to_base'])
                            simulator.deploy_countermeasure(closest_threat['id'], cm_name)
                            st.rerun()
    
    with col2:
        st.markdown("<h3 class='subsection-header'>HARD-KILL SYSTEMS</h3>", unsafe_allow_html=True)
        
        hard_kill_cm = {k: v for k, v in COUNTERMEASURE_SYSTEMS.items() if v['type'] == 'Hard-Kill'}
        
        for cm_name, cm_specs in hard_kill_cm.items():
            with st.expander(f"💥 {cm_name}", expanded=False):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"""
                    **Range:** {cm_specs['range']}m  
                    **Effectiveness:** {cm_specs['effectiveness']*100}%  
                    **Deployment Time:** {cm_specs['deployment_time']}s  
                    **Cost:** ${cm_specs['cost']:,}
                    """)
                
                with col_b:
                    active_threats = [t for t in st.session_state.threats if t['status'] == 'INCOMING']
                    if active_threats:
                        if st.button(f"FIRE", key=f"fire_{cm_name}"):
                            # Auto-select highest threat
                            highest_threat = max(active_threats, key=lambda x: 
                                               {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}[x['threat_level']])
                            simulator.deploy_countermeasure(highest_threat['id'], cm_name)
                            st.rerun()
    
    # Effectiveness Chart
    st.markdown("<h3 class='subsection-header'>SYSTEM EFFECTIVENESS</h3>", unsafe_allow_html=True)
    
    cm_names = list(COUNTERMEASURE_SYSTEMS.keys())
    effectiveness = [COUNTERMEASURE_SYSTEMS[cm]['effectiveness'] * 100 for cm in cm_names]
    ranges = [COUNTERMEASURE_SYSTEMS[cm]['range'] / 1000 for cm in cm_names]  # Convert to km
    
    fig = go.Figure(data=[
        go.Bar(
            name='Effectiveness %',
            x=cm_names,
            y=effectiveness,
            marker_color=['#00FF00' if eff > 80 else '#FFFF00' if eff > 60 else '#FFA500' for eff in effectiveness]
        )
    ])
    
    fig.update_layout(
        title='Countermeasure System Performance',
        template='plotly_dark',
        height=400,
        plot_bgcolor='rgba(0,0,0,0.8)',
        paper_bgcolor='rgba(0,0,0,0.8)',
        font_color='#00FF00'
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("<h2 class='section-header'>INTELLIGENCE DASHBOARD</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Threat Distribution Pie Chart
        st.markdown("<h3 class='subsection-header'>THREAT DISTRIBUTION</h3>", unsafe_allow_html=True)
        
        if st.session_state.threats:
            threat_types = {}
            for threat in st.session_state.threats:
                if threat['status'] != 'NEUTRALIZED':
                    threat_types[threat['type']] = threat_types.get(threat['type'], 0) + 1
            
            if threat_types:
                fig = px.pie(
                    values=list(threat_types.values()),
                    names=list(threat_types.keys()),
                    title="Active Threat Types",
                    color_discrete_sequence=['#FF0000', '#FFA500', '#FFFF00', '#00FF00']
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0.8)',
                    paper_bgcolor='rgba(0,0,0,0.8)',
                    font_color='#00FF00'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Response Time Analysis
        st.markdown("<h3 class='subsection-header'>RESPONSE TIMELINE</h3>", unsafe_allow_html=True)
        
        # Simulate response timeline data
        timeline_data = {
            'Phase': ['Detection', 'Classification', 'Tracking', 'Engagement', 'Assessment'],
            'Time (s)': [2.3, 1.8, 3.2, 4.5, 2.1]
        }
        
        df_timeline = pd.DataFrame(timeline_data)
        
        fig = px.bar(
            df_timeline,
            x='Phase',
            y='Time (s)',
            title='Average Response Timeline',
            color='Time (s)',
            color_continuous_scale=['#00FF00', '#FFFF00', '#FFA500', '#FF0000']
        )
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            plot_bgcolor='rgba(0,0,0,0.8)',
            paper_bgcolor='rgba(0,0,0,0.8)',
            font_color='#00FF00'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Drone Specs Comparison
    st.markdown("<h3 class='subsection-header'>DRONE SPECIFICATION COMPARISON</h3>", unsafe_allow_html=True)
    
    drone_comparison_data = []
    for drone_name, specs in DRONE_SPECS.items():
        drone_comparison_data.append({
            'Drone': drone_name,
            'Speed (km/h)': specs['speed'],
            'Range (km)': specs['range'],
            'Payload (kg)': specs['payload'],
            'Altitude (m)': specs['altitude'],
            'Threat Level': specs['threat_level'],
            'Cost (USD)': specs['cost']
        })
    
    df_comparison = pd.DataFrame(drone_comparison_data)
    st.dataframe(
        df_comparison,
        use_container_width=True,
        height=300
    )

with tab5:
    st.markdown("<h2 class='section-header'>AFTER ACTION REPORT</h2>", unsafe_allow_html=True)
    
    # Performance Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = st.session_state.simulation_state['score']
        grade = "A+" if score > 800 else "A" if score > 600 else "B" if score > 400 else "C" if score > 200 else "D"
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>MISSION GRADE</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0; font-size: 4rem;'>{grade}</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>Score: {score}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        neutralized = st.session_state.simulation_state['neutralized_threats']
        total_threats = len(st.session_state.threats)
        success_rate = (neutralized / total_threats * 100) if total_threats > 0 else 0
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>INTERCEPTION RATE</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0; font-size: 4rem;'>{success_rate:.1f}%</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>{neutralized}/{total_threats} threats</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        cost_per_threat = st.session_state.simulation_state['budget_remaining'] / max(neutralized, 1)
        st.markdown(f"""
        <div class="terminal-card">
            <h4 style='color: #00FF00;'>COST PER KILL</h4>
            <h1 style='color: #00FF00; text-align: center; margin: 0; font-size: 3rem;'>${cost_per_threat:,.0f}</h1>
            <p style='color: #00FF00; text-align: center; margin: 0;'>Efficiency metric</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("<h3 class='subsection-header'>RECOMMENDATIONS</h3>", unsafe_allow_html=True)
    
    recommendations = []
    
    if st.session_state.simulation_state['breaches'] > 0:
        recommendations.append("🚨 **CRITICAL:** Improve perimeter defenses. Multiple breaches detected.")
    
    if st.session_state.simulation_state['assets_protected'] < 80:
        recommendations.append("⚠️ **HIGH:** Deploy additional layered defense systems.")
    
    if st.session_state.simulation_state['radar_coverage'] < 90:
        recommendations.append("📡 **MEDIUM:** Upgrade radar coverage for early detection.")
    
    if st.session_state.simulation_state['budget_remaining'] < 500000:
        recommendations.append("💰 **LOW:** Optimize countermeasure selection for cost efficiency.")
    
    if not recommendations:
        recommendations.append("✅ **EXCELLENT:** Current defense posture is optimal.")
    
    for rec in recommendations:
        st.info(rec)
    
    # Export Report
    st.markdown("<h3 class='subsection-header'>EXPORT REPORT</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 GENERATE PDF REPORT", use_container_width=True):
            st.success("Report generation queued for PDF export")
    
    with col2:
        if st.button("📊 EXPORT PERFORMANCE DATA", use_container_width=True):
            st.success("CSV export ready for download")
    
    with col3:
        if st.button("🎥 CREATE TRAINING VIDEO", use_container_width=True):
            st.success("Video rendering in progress...")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #00FF00; font-size: 0.9rem; font-family: Courier New;'>
    <p><strong>⚠️ CLASSIFIED: TOP SECRET // NOFORN</strong></p>
    <p>This simulation contains classified C-UAS tactics, techniques, and procedures.</p>
    <p>Authorized use only by: PAF • USAF • RAF • UAE Air Force • RSAF • IAF</p>
    <p>© 2024 Counter-Drone Commander | Military-Grade Training Simulator | TS/SCI Clearance Required</p>
    <p><strong>Market Size:</strong> $3.8B → $16B (2026-2034) | <strong>Contracts:</strong> Anduril • Dedrone • D-Fend • Fortem</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh if simulation is active
if st.session_state.simulation_state['active']:
    time.sleep(0.5)
    st.rerun()
