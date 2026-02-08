import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import uuid
from datetime import datetime, timedelta
import json

# -----------------------------------------------------------------------------
# CONFIGURATION & STYLE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Entropia | Thermodynamic Knowledge",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance the "Lab" feel
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #41424b;
        text-align: center;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# THE PHYSICS ENGINE (LOGIC)
# -----------------------------------------------------------------------------

def init_state():
    """Initialize the session state with a 'Big Bang' if empty."""
    if 'particles' not in st.session_state:
        # Seed with some initial matter so the universe isn't empty
        st.session_state['particles'] = [
            {
                'id': str(uuid.uuid4()),
                'content': 'The universe tends toward disorder.',
                'created_at': datetime.now() - timedelta(hours=5),
                'mass': 1, # Generation 1
                'source': 'Big Bang'
            },
            {
                'id': str(uuid.uuid4()),
                'content': 'Knowledge requires active energy to maintain.',
                'created_at': datetime.now() - timedelta(hours=2),
                'mass': 1, 
                'source': 'Big Bang'
            }
        ]

def calculate_thermodynamics(decay_rate):
    """
    Apply the Second Law: Entropy increases with time.
    Returns a DataFrame enriched with thermodynamic properties.
    """
    if not st.session_state['particles']:
        return pd.DataFrame()

    df = pd.DataFrame(st.session_state['particles'])
    
    # Time delta in hours
    now = datetime.now()
    df['age_hours'] = df['created_at'].apply(lambda x: (now - x).total_seconds() / 3600)
    
    # Entropy Equation: E = k * time * (1 / mass)
    # Heavier particles (synthesized ideas) decay slower.
    df['entropy'] = df['age_hours'] * decay_rate * (1 / df['mass'])
    
    # Cap entropy at 100 for visualization sanity
    df['entropy'] = df['entropy'].clip(upper=100)
    
    return df

def synthesize_particles(id_a, id_b, new_insight):
    """
    Merge two particles into a new, heavier one. 
    Reduces system entropy locally.
    """
    particles = st.session_state['particles']
    
    # Find parents
    p_a = next(p for p in particles if p['id'] == id_a)
    p_b = next(p for p in particles if p['id'] == id_b)
    
    # Remove parents (Law of Conservation: Matter transforms)
    st.session_state['particles'] = [p for p in particles if p['id'] not in [id_a, id_b]]
    
    # Create new particle
    new_mass = p_a['mass'] + p_b['mass']
    new_particle = {
        'id': str(uuid.uuid4()),
        'content': new_insight,
        'created_at': datetime.now(), # Fresh creation = 0 Entropy
        'mass': new_mass,
        'source': 'Synthesis'
    }
    
    st.session_state['particles'].append(new_particle)
    return new_mass

# -----------------------------------------------------------------------------
# UI LAYOUT
# -----------------------------------------------------------------------------

def main():
    init_state()
    
    # -- Sidebar: Lab Controls --
    with st.sidebar:
        st.title("⚛️ Entropia")
        st.markdown("### The Thermodynamic Knowledge Engine")
        st.info("Ideas decay into noise (Entropy) unless you combine them into insight (Synthesis).")
        
        st.markdown("---")
        st.subheader("1. Inject Matter")
        new_thought = st.text_area("New Observation/Idea", height=100, placeholder="E.g., Chaos is a ladder...")
        if st.button("Inject into System", type="primary"):
            if new_thought.strip():
                st.session_state['particles'].append({
                    'id': str(uuid.uuid4()),
                    'content': new_thought,
                    'created_at': datetime.now(),
                    'mass': 1,
                    'source': 'User Injection'
                })
                st.rerun()
            else:
                st.error("Matter cannot be created from void (empty input).")
        
        st.markdown("---")
        st.subheader("Lab Settings")
        decay_rate = st.slider("Universal Decay Constant (k)", 1.0, 20.0, 5.0, help="Higher values make ideas rot faster.")
        
        # Data Persistence (Human-Realistic feature)
        st.markdown("---")
        st.subheader("Backup Universe")
        if st.session_state['particles']:
            json_data = json.dumps(st.session_state['particles'], default=str, indent=2)
            st.download_button("Export State JSON", json_data, "entropia_universe.json", "application/json")

    # -- Main: The Macroscope --
    
    # 1. Calculate Physics
    df = calculate_thermodynamics(decay_rate)
    
    if df.empty:
        st.warning("The universe is empty. Inject matter via the sidebar.")
        return

    # 2. Header & Metrics
    col1, col2, col3 = st.columns(3)
    avg_entropy = df['entropy'].mean()
    total_mass = df['mass'].sum()
    
    with col1:
        st.metric("System Entropy (Chaos)", f"{avg_entropy:.1f}", delta=f"{-avg_entropy/10:.1f}", delta_color="inverse")
    with col2:
        st.metric("System Mass (Knowledge)", f"{total_mass}", delta="Stable")
    with col3:
        system_temp = "🔥 Critical" if avg_entropy > 75 else "❄️ Stable" if avg_entropy < 25 else "⚠️ Warming"
        st.metric("System Status", system_temp)

    # 3. Visualization (The Einstein Twist)
    st.markdown("### 🔭 The Phase Space")
    
    # Scatter plot: X=Age, Y=Entropy. 
    # Logic: High Entropy items float to the top and turn red.
    fig = px.scatter(
        df, 
        x='age_hours', 
        y='entropy', 
        size='mass', 
        color='entropy',
        hover_data=['content', 'source'],
        color_continuous_scale=['#00cc96', '#ef553b'], # Green to Red
        range_y=[0, 110],
        title="Particle Decay Trajectory",
        labels={'age_hours': 'Time Since Creation (Hours)', 'entropy': 'Entropy (Disorder Level)'}
    )
    
    fig.update_layout(
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        font=dict(color='#fafafa'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#262730')
    )
    st.plotly_chart(fig, use_container_width=True)

    # 4. The Collider (Action Zone)
    st.markdown("### ⚡ The Hadron Collider (Synthesis)")
    st.markdown("Select two high-entropy particles to collide. Merging them creates a massive, stable insight.")

    # Create a dictionary for the multiselect to show readable names
    options = {f"{row['content'][:50]}... (Entropy: {row['entropy']:.1f})": row['id'] for index, row in df.iterrows()}
    
    selected_labels = st.multiselect(
        "Select 2 Particles to Collide:", 
        options=list(options.keys()),
        max_selections=2
    )

    if len(selected_labels) == 2:
        id_a = options[selected_labels[0]]
        id_b = options[selected_labels[1]]
        
        # Retrieve full content for context
        content_a = next(p['content'] for p in st.session_state['particles'] if p['id'] == id_a)
        content_b = next(p['content'] for p in st.session_state['particles'] if p['id'] == id_b)
        
        st.info(f"**Particle A:** {content_a}")
        st.info(f"**Particle B:** {content_b}")
        
        with st.form("synthesis_form"):
            insight = st.text_area("Synthesized Insight (What connects these two?)", placeholder="The connection is...")
            submitted = st.form_submit_button("💥 COLLIDE & SYNTHESIZE")
            
            if submitted and insight.strip():
                new_mass = synthesize_particles(id_a, id_b, insight)
                st.toast(f"Success! Created Generation {new_mass} Insight!", icon="⚛️")
                st.rerun()

    # 5. The Ledger (Data View)
    with st.expander("📂 View Particle Ledger"):
        st.dataframe(
            df[['content', 'mass', 'entropy', 'age_hours', 'source']].sort_values(by='entropy', ascending=False),
            use_container_width=True
        )

if __name__ == "__main__":
    main()
