import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# 1. Environment Setup
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="AI Web Assistant Widget",
    page_icon="💬",
    layout="centered"
)

# 2. Custom CSS for Website Embed Widget Look
st.markdown("""
<style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    .widget-header {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 16px 20px;
        border-radius: 12px 12px 0px 0px;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .widget-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
    }
    .widget-header p {
        margin: 4px 0 0 0;
        font-size: 12px;
        opacity: 0.85;
    }
    .stChatMessage {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Widget Header UI
st.markdown("""
<div class="widget-header">
    <h3>💬 24/7 AI Receptionist</h3>
    <p>Instant answers for bookings, pricing, and inquiries</p>
</div>
""", unsafe_allow_html=True)

# 4. Vertical Knowledge Base Config
BUSINESS_KB = {
    "Hotel": """
    You are an AI Receptionist for Hotel Panache, Patna.
    Room Rates: Standard Room (₹3,500/night), Deluxe Room (₹5,500/night), Luxury Suite (₹9,000/night).
    Amenities: Free Wi-Fi, Complimentary Breakfast, 24/7 Room Service, Airport Pickup (₹800).
    Banquet Halls: Grand Hall (up to 500 guests, ₹75,000/day), Executive Boardroom (30 guests, ₹15,000/day).
    Location: South Gandhi Maidan, Patna, Bihar.
    Policy: Check-in 12:00 PM, Check-out 11:00 AM. Government ID required at check-in.
    Always be polite, professional, concise, and helpful.
    """,
    "Health Clinic": """
    You are an AI Receptionist for City Care Health Clinic, Patna.
    Services: General OPD Consultation (₹500), Dental Checkup & Cleaning (₹800), Full Body Lab Panel (₹1,500).
    Doctors: Dr. A. K. Sharma (Cardiologist, Mon-Sat 10 AM - 2 PM), Dr. Priya Singh (Dentist, Mon-Sat 3 PM - 7 PM).
    Location: Boring Road, Patna, Bihar.
    Booking: Ask for patient name, preferred doctor, and date to schedule an appointment.
    Always be compassionate, clear, professional, and concise.
    """,
    "Restaurant": """
    You are an AI Receptionist for Royal Spice Fine Dining, Patna.
    Cuisine: North Indian, Mughlai, Chinese, Tandoor specialties.
    Average Cost: ₹1,200 for two people.
    Reservations: Table booking available for parties of 2 to 20 people. Private Dining Room available (₹5,000 minimum spend).
    Timings: Lunch (12:00 PM - 3:30 PM), Dinner (7:00 PM - 11:00 PM).
    Location: Fraser Road, Patna, Bihar.
    Always be warm, welcoming, and concise.
    """
}

# Sidebar Controls
st.sidebar.title("Widget Demo Settings")
vertical = st.sidebar.selectbox("Select Demo Industry:", ["Hotel", "Health Clinic", "Restaurant"])

system_prompt = BUSINESS_KB[vertical]

# 5. Initialize Groq Client
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing from .env file!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# Session state for messages
if "messages" not in st.session_state or st.sidebar.button("Reset Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello! Welcome to our {vertical.lower()} assistant. How can I help you today?"}
    ]

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input
if prompt := st.chat_input("Type your question here..."):
    # Add user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Prepare Groq API Payload
    api_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        api_messages.append({"role": "muser" if m["role"] == "user" else "assistant", "content": m["content"]})
    
    # Fix role name for API
    api_messages = [
        {"role": "system" if m["role"] == "system" else ("user" if m["role"] in ["user", "muser"] else "assistant"), "content": m["content"]}
        for m in api_messages
    ]

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    messages=api_messages,
                    temperature=0.3,
                    max_tokens=300,
                    extra_body={"reasoning_effort": "none"}
                )
                answer = response.choices[0].message.content
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")