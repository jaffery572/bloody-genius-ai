import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Counter-Drone Commander",
    page_icon="🚁",
    layout="wide"
)

# ==================== SIMPLE CSS ====================
st.markdown("""
<style>
    .metric-card {
        background: #0a0a0a;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #00ff00;
        text-align: center;
        margin: 10px;
    }
    .metric-value {
        color: #00ff00;
        font-size: 36px;
        font-weight: bold;
    }
    .metric-label {
        color: #00ff00;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'simulation_state' not in st.session_state:
    st.session_state.simulation_state = {
        'active': False,
        'time': 0,
        'score': 0,
        'threats': 0,
        'neutralized': 0,
        'breaches': 0,
        'radar': 85,
        'budget': 1000000
    }

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("⚙️ COMMAND CONSOLE")
    
    # Status
    status = "🟢 ONLINE" if st.session_state.simulation_state['active'] else "🔴 OFFLINE"
    st.markdown(f"**Status:** {status}")
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.simulation_state['active'] = True
            st.rerun()
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.simulation_state['active'] = False
            st.rerun()
    
    # Scenarios
    st.markdown("---")
    st.subheader("🎯 SCENARIOS")
    
    scenario = st.selectbox(
        "Choose Scenario",
        ["Peacetime Patrol", "Airport Defense", "Swarm Attack", "Critical Infrastructure"]
    )
    
    if st.button("🚀 Deploy Scenario", use_container_width=True):
        # Generate threats based on scenario
        threats = random.randint(1, 10) if scenario == "Swarm Attack" else random.randint(1, 5)
        st.session_state.simulation_state['threats'] = threats
        st.session_state.simulation_state['active'] = True
        st.success(f"Scenario '{scenario}' deployed with {threats} threats")
        st.rerun()
    
    # Countermeasures
    st.markdown("---")
    st.subheader("⚡ COUNTERMEASURES")
    
    if st.button("📡 RF Jamming", use_container_width=True):
        if st.session_state.simulation_state['threats'] > 0:
            neutralized = min(random.randint(1, 3), st.session_state.simulation_state['threats'])
            st.session_state.simulation_state['threats'] -= neutralized
            st.session_state.simulation_state['neutralized'] += neutralized
            st.session_state.simulation_state['score'] += neutralized * 100
            st.session_state.simulation_state['budget'] -= 50000
            st.success(f"Neutralized {neutralized} threats with RF Jamming")
            st.rerun()
    
    if st.button("🎯 Laser Defense", use_container_width=True):
        if st.session_state.simulation_state['threats'] > 0:
            neutralized = min(random.randint(1, 2), st.session_state.simulation_state['threats'])
            st.session_state.simulation_state['threats'] -= neutralized
            st.session_state.simulation_state['neutralized'] += neutralized
            st.session_state.simulation_state['score'] += neutralized * 150
            st.session_state.simulation_state['budget'] -= 300000
            st.success(f"Neutralized {neutralized} threats with Laser Defense")
            st.rerun()
    
    if st.button("🛡️ Hard-Kill", use_container_width=True):
        if st.session_state.simulation_state['threats'] > 0:
            neutralized = min(random.randint(1, 3), st.session_state.simulation_state['threats'])
            st.session_state.simulation_state['threats'] -= neutralized
            st.session_state.simulation_state['neutralized'] += neutralized
            st.session_state.simulation_state['score'] += neutralized * 200
            st.session_state.simulation_state['budget'] -= 500000
            st.success(f"Neutralized {neutralized} threats with Hard-Kill")
            st.rerun()
    
    # Reset
    if st.button("🔄 Reset Simulation", use_container_width=True, type="secondary"):
        st.session_state.simulation_state = {
            'active': False,
            'time': 0,
            'score': 0,
            'threats': 0,
            'neutralized': 0,
            'breaches': 0,
            'radar': 85,
            'budget': 1000000
        }
        st.rerun()

# ==================== MAIN DASHBOARD ====================
st.title("🛡️ COUNTER-DRONE COMMANDER")
st.markdown("---")

# Top Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.simulation_state['threats']}</div>
        <div class="metric-label">ACTIVE THREATS</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.simulation_state['neutralized']}</div>
        <div class="metric-label">NEUTRALIZED</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.simulation_state['breaches']}</div>
        <div class="metric-label">BREACHES</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.simulation_state['score']}</div>
        <div class="metric-label">SCORE</div>
    </div>
    """, unsafe_allow_html=True)

# Charts and Data
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 SYSTEM STATUS")
    
    # Radar Coverage
    st.markdown(f"**Radar Coverage:** {st.session_state.simulation_state['radar']}%")
    st.progress(st.session_state.simulation_state['radar'] / 100)
    
    # Budget
    st.markdown(f"**Budget:** ${st.session_state.simulation_state['budget']:,}")
    budget_percent = max(0, min(100, st.session_state.simulation_state['budget'] / 1000000 * 100))
    st.progress(budget_percent / 100)
    
    # Time
    st.markdown(f"**Simulation Time:** {st.session_state.simulation_state['time']}s")

with col2:
    st.subheader("📈 THREAT DISTRIBUTION")
    
    # Create a simple chart
    threat_data = pd.DataFrame({
        'Threat Type': ['Shahed-136', 'DJI Mavic', 'Orlan-10', 'Others'],
        'Count': [random.randint(1, 5), random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)]
    })
    st.bar_chart(threat_data.set_index('Threat Type'))

# Console Log
st.markdown("---")
st.subheader("📟 COMMAND CONSOLE")

# Create console
console_text = ""
if st.session_state.simulation_state['active']:
    console_text += f"[{st.session_state.simulation_state['time']}s] System: Simulation ACTIVE\n"
    
if st.session_state.simulation_state['threats'] > 0:
    console_text += f"[{st.session_state.simulation_state['time']}s] Alert: {st.session_state.simulation_state['threats']} threats detected\n"
    
if st.session_state.simulation_state['neutralized'] > 0:
    console_text += f"[{st.session_state.simulation_state['time']}s] Success: {st.session_state.simulation_state['neutralized']} threats neutralized\n"
    
if st.session_state.simulation_state['breaches'] > 0:
    console_text += f"[{st.session_state.simulation_state['time']}s] WARNING: {st.session_state.simulation_state['breaches']} breaches detected\n"

console_text += f"[{st.session_state.simulation_state['time']}s] Status: {'SIMULATION RUNNING' if st.session_state.simulation_state['active'] else 'SIMULATION PAUSED'}"

st.code(console_text, language='bash')

# Drone Database
st.markdown("---")
st.subheader("📋 DRONE DATABASE")

drone_data = pd.DataFrame({
    'Drone': ['Shahed-136', 'DJI Mavic 3', 'Orlan-10', 'Switchblade 300', 'Cargo Smuggler'],
    'Type': ['Loitering Munition', 'Commercial Quadcopter', 'Recon UAV', 'Kamikaze Drone', 'Modified Commercial'],
    'Speed (km/h)': [185, 72, 150, 160, 60],
    'Range (km)': [2500, 30, 600, 10, 40],
    'Threat Level': ['CRITICAL', 'MEDIUM', 'HIGH', 'CRITICAL', 'HIGH']
})

st.dataframe(drone_data, use_container_width=True)

# Simulation Logic
if st.session_state.simulation_state['active']:
    # Increment time
    st.session_state.simulation_state['time'] += 1
    
    # Occasionally add new threats
    if random.random() < 0.1:
        new_threats = random.randint(0, 2)
        st.session_state.simulation_state['threats'] += new_threats
        if new_threats > 0:
            st.session_state.simulation_state['breaches'] += 1
    
    # Auto-refresh
    time.sleep(1)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*Counter-Drone Commander Simulator v1.0 | Ready for Deployment*")
