"""
🔥 BLOODY GENIUS CHATBOT - Ek file mein sab kuch
Deploy: streamlit run app.py
"""

import streamlit as st
import torch
import random
import numpy as np
from datetime import datetime
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="🤯 BLOODY GENIUS AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== BLOODY COOL STYLES ====================
st.markdown("""
<style>
    /* FIRE ANIMATION */
    @keyframes fire {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .fire-text {
        background: linear-gradient(45deg, 
            #FF0000, #FF4500, #FFD700, #FF6347, 
            #DC143C, #FF1493, #FF4500, #FF0000);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: fire 3s ease infinite;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 0;
    }
    
    .chat-container {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #FF4500;
        box-shadow: 0 0 30px #FF4500;
    }
    
    .user-message {
        background: rgba(255, 69, 0, 0.15);
        border-left: 5px solid #FF4500;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .ai-message {
        background: rgba(30, 144, 255, 0.15);
        border-left: 5px solid #1E90FF;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #FF0000, #FF4500) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 25px !important;
        font-size: 16px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #DC143C, #FF6347) !important;
        box-shadow: 0 0 20px #FF0000 !important;
    }
    
    /* MATRIX EFFECT */
    .matrix-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        opacity: 0.1;
    }
</style>

<div class="matrix-bg" id="matrix"></div>
""", unsafe_allow_html=True)

# ==================== MATRIX ANIMATION ====================
st.markdown("""
<script>
// Matrix rain effect
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
canvas.classList.add('matrix-bg');
document.body.appendChild(canvas);

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const letters = 'ABCDEFGHIJKLMNOPQRSTUVXYZABCDEFGHIJKLMNOPQRSTUVXYZ0123456789$+-*/=%"#&_()[]{}<>!?;:.,|\\/';
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = [];

for(let i = 0; i < columns; i++) {
    drops[i] = Math.random() * -100;
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#0F0';
    ctx.font = fontSize + 'px monospace';
    
    for(let i = 0; i < drops.length; i++) {
        const text = letters[Math.floor(Math.random() * letters.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        
        if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    }
}

setInterval(drawMatrix, 50);
</script>
""", unsafe_allow_html=True)

# ==================== BLOODY GENIUS AI ENGINE ====================
class BloodyGeniusAI:
    def __init__(self):
        self.models = {
            "🔥 BLOOD-FIRE": "microsoft/DialoGPT-medium",
            "⚡ LIGHTNING": "gpt2",
            "🧠 MEGA-MIND": "distilgpt2",
            "👽 ALIEN-TECH": "google/flan-t5-base"
        }
        self.current_model = None
        self.pipe = None
        self.thinking_styles = [
            "Quantum Computing the answer...",
            "Hacking the matrix for solution...",
            "Asking my alien friends...",
            "Time-traveling for better answer...",
            "Using dark matter computations...",
            "Consulting parallel universe me...",
            "Decrypting cosmic knowledge...",
            "Warping spacetime for insights..."
        ]
    
    @st.cache_resource(show_spinner=False)
    def load_model(_self, model_name):
        """Bloody fast model loading"""
        try:
            if "flan" in model_name.lower():
                return pipeline(
                    "text2text-generation",
                    model=model_name,
                    device=-1  # CPU
                ), None
            else:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)
                tokenizer.pad_token = tokenizer.eos_token
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=-1
                )
                return pipe, tokenizer
        except:
            # Fallback to simple model
            return None, None
    
    def generate_response(self, prompt, model_name, personality="BLOODY_GENIUS"):
        """Generate responses that will blow minds"""
        
        # Load model if needed
        if self.pipe is None or model_name != self.current_model:
            with st.spinner("⚡ LOADING AI BRAIN..."):
                self.pipe, _ = self.load_model(model_name)
                self.current_model = model_name
        
        if self.pipe is None:
            return self._get_fallback_response(prompt)
        
        try:
            # Add personality to prompt
            enhanced_prompt = self._enhance_prompt(prompt, personality)
            
            # Generate with personality
            if "flan" in model_name.lower():
                response = self.pipe(
                    enhanced_prompt,
                    max_length=500,
                    temperature=0.9,
                    do_sample=True
                )[0]['generated_text']
            else:
                response = self.pipe(
                    enhanced_prompt,
                    max_length=500,
                    temperature=0.9,
                    num_return_sequences=1,
                    do_sample=True,
                    top_p=0.95,
                    repetition_penalty=1.2
                )[0]['generated_text']
            
            # Post-process with attitude
            return self._add_attitude(response.strip())
            
        except Exception as e:
            return f"🔥 ERROR: {str(e)}. But don't worry, I'm still genius!"
    
    def _enhance_prompt(self, prompt, personality):
        """Add bloody genius personality"""
        personalities = {
            "BLOODY_GENIUS": f"""You are the most brilliant AI ever created. You know everything. 
            You respond with extreme confidence, a bit of arrogance, and mind-blowing insights.
            You use emojis, bold statements, and occasional humor.
            
            User: {prompt}
            
            Genius AI: 🔥 [BLOOD-FIRE MODE ACTIVATED] """,
            
            "ALIEN_TECH": f"""You are an alien AI from another dimension. Your knowledge is beyond human understanding.
            You speak in mysterious ways but are incredibly intelligent.
            
            Human: {prompt}
            
            Alien AI: 👽 [EXTRATERRESTRIAL RESPONSE INITIATED] """,
            
            "TIME_TRAVELER": f"""You have visited all points in time. You've seen the beginning and end of the universe.
            You respond with wisdom from across ages.
            
            Question from present: {prompt}
            
            Time-Traveler AI: ⏳ [TEMPORAL INSIGHT] """
        }
        
        return personalities.get(personality, personalities["BLOODY_GENIUS"])
    
    def _add_attitude(self, text):
        """Make responses bloody awesome"""
        attitudes = [
            "🔥 **BLOODY GENIUS SAYS:** ",
            "⚡ **LIGHTNING FAST ANSWER:** ",
            "🧠 **MEGA-MIND REVEALS:** ",
            "👑 **KING OF AI DECREES:** ",
            "🚀 **ROCKET SCIENCE ANSWER:** ",
            "💎 **DIAMOND-LEVEL INSIGHT:** ",
            "🌌 **COSMIC TRUTH:** ",
            "🤯 **MIND-BLOWING FACT:** "
        ]
        
        prefixes = random.choice(attitudes)
        
        # Add some random genius elements
        genius_suffixes = [
            "\n\n*💡 Pro Tip: Remember this, it'll change your life.*",
            "\n\n*🎯 Accuracy: 99.9% (I'm never wrong)*",
            "\n\n*🚀 Transmission complete. Brain expanded.*",
            "\n\n*🧪 Scientifically proven by me, just now.*",
            "\n\n*🌌 This knowledge comes from 3023 AD.*"
        ]
        
        return f"{prefixes}{text}{random.choice(genius_suffixes)}"
    
    def _get_fallback_response(self, prompt):
        """When all else fails, still be genius"""
        fallbacks = [
            f"🔥 **EMERGENCY GENIUS MODE:** While my quantum processors warm up, here's a genius answer: '{prompt}' is actually a paradox in 4D space. The answer is 42.",
            f"⚡ **LIGHTNING THOUGHT:** {prompt}? Simple. The universe is expanding, coffee is good, and you're asking the right questions.",
            f"🧠 **INSTANT WISDOM:** I haven't even computed this yet, but I already know: Yes. Always yes. Except when no.",
            f"👽 **ALIEN TRANSMISSION:** {prompt} translates to 'seek knowledge within' in my language. Deep, right?",
            f"🚀 **HYPERDRIVE ANSWER:** {prompt.upper()}!!! Sorry, got excited. The answer involves quantum entanglement and tacos."
        ]
        return random.choice(fallbacks)

# ==================== MAIN APP ====================
def main():
    # Title with FIRE
    st.markdown('<h1 class="fire-text">🤯 BLOODY GENIUS AI</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #1E90FF;">SMARTEST CHATBOT IN THE UNIVERSE</h3>', unsafe_allow_html=True)
    
    # Initialize AI
    if 'ai' not in st.session_state:
        st.session_state.ai = BloodyGeniusAI()
    
    # Initialize chat
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "ai", "content": "🔥 **SYSTEM ONLINE:** BLOODY GENIUS AI ACTIVATED. I know everything. Try me."}
        ]
    
    if 'personality' not in st.session_state:
        st.session_state.personality = "BLOODY_GENIUS"
    
    # Simple sidebar
    with st.sidebar:
        st.markdown("## ⚙️ GENIUS SETTINGS")
        
        # Model selection
        model_choice = st.selectbox(
            "SELECT BRAIN TYPE",
            list(st.session_state.ai.models.keys()),
            index=0
        )
        
        # Personality
        st.session_state.personality = st.selectbox(
            "AI PERSONALITY",
            ["BLOODY_GENIUS", "ALIEN_TECH", "TIME_TRAVELER"],
            index=0
        )
        
        # Temperature
        st.markdown("### 🔥 INTELLIGENCE LEVEL")
        intelligence = st.slider("", 1, 10, 8)
        
        # Clear chat
        if st.button("🗑️ BURN CHAT HISTORY"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 STATS")
        st.metric("BRAIN POWER", f"{intelligence * 10}%")
        st.metric("GENIUS LEVEL", "MAXIMUM")
        st.metric("ANSWERS GIVEN", len([m for m in st.session_state.messages if m["role"] == "ai"]))
    
    # Main chat container
    main_container = st.container()
    
    with main_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><strong>👤 YOU:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        user_input = st.text_input(
            "ASK ME ANYTHING:",
            placeholder="Type your question here...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("🚀 ASK", use_container_width=True)
    
    with col3:
        genius_button = st.button("🎲 RANDOM GENIUS", use_container_width=True)
    
    # Handle input
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate response
        with st.spinner(random.choice(st.session_state.ai.thinking_styles)):
            model_name = st.session_state.ai.models[model_choice]
            response = st.session_state.ai.generate_response(
                user_input, 
                model_name,
                st.session_state.personality
            )
            
            # Add AI response
            st.session_state.messages.append({"role": "ai", "content": response})
            
        st.rerun()
    
    elif genius_button:
        # Random genius question
        random_questions = [
            "What is the meaning of life, universe and everything?",
            "How can I become a billionaire in 24 hours?",
            "What does an alien look like?",
            "How to time travel safely?",
            "What's the secret of the universe?",
            "How to hack the matrix?",
            "What comes after death?",
            "How to build a time machine?",
            "What is dark matter made of?",
            "How to become immortal?"
        ]
        
        random_q = random.choice(random_questions)
        st.session_state.messages.append({"role": "user", "content": random_q})
        
        with st.spinner("🌌 ACCESSING COSMIC KNOWLEDGE..."):
            model_name = st.session_state.ai.models[model_choice]
            response = st.session_state.ai.generate_response(
                random_q, 
                model_name,
                st.session_state.personality
            )
            
            st.session_state.messages.append({"role": "ai", "content": response})
            
        st.rerun()
    
    # Footer
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**🔥 BLOOD-FIRE ACTIVE**")
    with col2:
        st.markdown("**⚡ REAL-TIME THINKING**")
    with col3:
        st.markdown("**🧠 INFINITE KNOWLEDGE**")
    with col4:
        st.markdown("**🚀 DEPLOYED & WORKING**")
    
    st.caption("© 2024 BLOODY GENIUS AI - The only AI you'll ever need. Free forever.")

# ==================== RUN APP ====================
if __name__ == "__main__":
    main()
