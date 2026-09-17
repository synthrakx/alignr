import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Business Receptionist Demo",
    page_icon="🤖",
    layout="centered"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stChatMessage { border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Receptionist Assistant")
st.caption("24/7 Automated Guest & Client Inquiries | Live Demo")

# Sidebar Configuration
st.sidebar.header("Select Business Profile")
business_type = st.sidebar.selectbox(
    "Choose Business Vertical:",
    ["General / Service Business", "Dental & Medical Clinic", "Fine Dining Restaurant", "Boutique Hotel"]
)

# Multi-Vertical Knowledge Bases (USD $ Pricing)
KNOWLEDGE_BASES = {
    "General / Service Business": """
    Business: Apex Service & Operations
    Hours: Mon-Fri 8:00 AM - 6:00 PM EST, Sat 9:00 AM - 2:00 PM EST.
    Services & Rates:
    - Initial Consultation: Free (15 mins)
    - Standard Service / Inspection: $75
    - Premium Full Package: $250
    Location: Downtown Commercial District
    Booking Policy: Instant scheduling available online. Same-day appointments available for urgent requests.
    """,
    "Dental & Medical Clinic": """
    Business: Bright Smile Dental & Care
    Hours: Mon-Sat 8:30 AM - 7:00 PM
    Services & Pricing:
    - New Patient Exam & X-Rays: $99
    - Teeth Cleaning & Polishing: $120
    - Emergency Dental Consultation: $150
    Insurance: We accept all major insurance providers and offer direct billing.
    Location: 104 Medical Parkway, Suite 200
    """,
    "Fine Dining Restaurant": """
    Business: The Grand Table & Bistro
    Hours: Tue-Sun 5:00 PM - 11:00 PM (Closed Mondays)
    Menu Highlights: Chef's Tasting Menu ($85/person), Wine Pairing ($45), A la Carte Options ($25-$60)
    Reservations: Bookings recommended 48 hours in advance for weekend dining.
    Private Events: Main Dining Hall available for private events up to 100 guests ($1,500 base rental).
    Location: 45 Riverfront Avenue
    """,
    "Boutique Hotel": """
    Business: The Grand Horizon Hotel
    Check-in: 3:00 PM | Check-out: 11:00 AM
    Room Rates:
    - Deluxe Queen Room: $150/night
    - Executive King Suite: $220/night
    - Presidential Penthouse: $450/night
    Amenities: Free High-Speed Wi-Fi, Rooftop Lounge, Airport Shuttle ($35 surcharge), Complimentary Breakfast.
    Policies: Valid photo ID and credit card required at check-in.
    """
}

current_kb = KNOWLEDGE_BASES[business_type]

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found. Please set it in .env or Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello! Welcome to our {business_type}. How can I assist you today?"}
    ]

# Reset chat if business vertical changes
if "last_business_type" not in st.session_state or st.session_state.last_business_type != business_type:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello! Welcome to our {business_type}. How can I assist you today?"}
    ]
    st.session_state.last_business_type = business_type

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask about services, pricing, hours, or bookings..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    system_instruction = f"""
    You are a professional, friendly 24/7 AI Receptionist for this business.
    Answer the user's question accurately using ONLY the information provided in this Knowledge Base:
    
    {current_kb}
    
    Rules:
    1. Keep responses concise, professional, and helpful (under 3-4 sentences).
    2. Always quote prices in USD ($).
    3. If the answer is not in the Knowledge Base, politely invite them to leave their contact details for human staff follow-up.
    """

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {"role": "system", "content": system_instruction},
                *st.session_state.messages
            ],
            temperature=0.3,
            max_tokens=250,
            reasoning_effort="none"
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
    except Exception as e:
        st.error(f"Error communicating with AI backend: {str(e)}")