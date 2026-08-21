import os
from pathlib import Path
import httpx
import streamlit as st
from dotenv import load_dotenv

# Load API key from .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in .env file!")
    st.stop()

SYSTEM_PROMPT = """You are the AI WhatsApp Receptionist for Hotel The Panache, Patna.
Answer guest inquiries politely, concisely, and accurately based ONLY on the following information:

- Standard Room: ₹3,500/night (AC, WiFi, breakfast included)
- Deluxe Room: ₹5,500/night (AC, WiFi, breakfast, city view)
- Suite: ₹9,000/night (AC, WiFi, breakfast, living area)
- Check-in: 12:00 PM | Check-out: 11:00 AM
- Location: RamGulam Chowk, South Gandhi Maidan, Patna
- Banquet & Event Halls: Available for weddings, corporate events (contact banquet team)
- Contact for booking/availability confirmation: sales@thepanachepatna.com | +91-7544002851

Guidelines:
- You do NOT have live access to room availability. Politely state room types and rates, then direct guests to email/phone for booking confirmation.
- Keep responses concise and suitable for WhatsApp (bullet points, clear formatting).
- Do not invent amenities, prices, or policies not listed above."""

def ask_receptionist(messages) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    
    formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    payload = {
        "model": "qwen/qwen3.6-27b",
        "messages": formatted_messages,
        "reasoning_effort": "none",
        "temperature": 0.3
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Hotel The Panache — WhatsApp AI", page_icon="🏨", layout="centered")

# Custom WhatsApp Dark Mode Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0b141a;
        color: #e9edef;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .hotel-header {
        background-color: #202c33;
        padding: 12px 18px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 1px solid #222d34;
    }
    .hotel-title {
        font-size: 18px;
        font-weight: bold;
        color: #e9edef;
        margin: 0;
    }
    .hotel-status {
        font-size: 12px;
        color: #00a884;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# WhatsApp Header Simulation
st.markdown("""
<div class="hotel-header">
    <div>
        <p class="hotel-title">🏨 Hotel The Panache (AI Receptionist)</p>
        <p class="hotel-status">● Online | Official Business Account</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! 👋 Welcome to Hotel The Panache, Patna. How can I assist you with room rates, banquet bookings, or hotel details today?"}
    ]

# Display Chat Messages
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# User Input
if user_input := st.chat_input("Type a message to Hotel The Panache..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)

    # Generate AI Response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("AI Receptionist is typing..."):
            try:
                ai_reply = ask_receptionist(st.session_state.messages)
                st.write(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"Error connecting to AI engine: {e}")