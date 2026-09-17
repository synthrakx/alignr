import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Business Receptionist | Live Demo",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS: Hide Streamlit Clutter & Upgrade Theme
st.markdown("""
    <style>
    /* Hide Streamlit Header, Footer, and Fork Button */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp > header {display: none;}
    
    /* Background & Global Colors */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Live Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.85rem;
        color: #38BDF8;
        margin-bottom: 12px;
    }
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #22C55E;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    /* Chat Message Bubbles */
    .stChatMessage {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Top Header
st.markdown('<div class="status-badge"><span class="status-dot"></span> 24/7 AI Receptionist Active</div>', unsafe_allow_html=True)
st.title("Automated AI Receptionist")
st.caption("Interactive Client & Guest Assistant | Instant USD Knowledge Retrieval")

# Sidebar Configuration
st.sidebar.title("🏢 Business Profile")
st.sidebar.markdown("Switch business profiles to test vertical-specific AI knowledge bases:")

business_type = st.sidebar.selectbox(
    "Select Industry Demo:",
    ["General / Service Business", "Dental & Medical Clinic", "Fine Dining Restaurant", "Boutique Hotel"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 🌟 What this demo proves:
- **Instant Response:** Sub-second answer speeds.
- **Zero Hallucinations:** Strictly follows Knowledge Base facts.
- **24/7 Coverage:** Handles bookings & inquiries automatically.
""")

# Knowledge Bases (USD Pricing)
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
    st.error("⚠️ GROQ_API_KEY not found. Please set it in .env or Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# Session State Management
if "messages" not in st.session_state or "last_business_type" not in st.session_state or st.session_state.last_business_type != business_type:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello! Welcome to **{business_type}**. How can I assist you with our services, pricing, or bookings today?"}
    ]
    st.session_state.last_business_type = business_type

# Display Message History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Quick Test Buttons
col1, col2, col3 = st.columns(3)
prompt_input = None

if col1.button("💰 What are your prices?"):
    prompt_input = "What are your services and prices?"
elif col2.button("🕒 What are your hours?"):
    prompt_input = "What are your hours and location?"
elif col3.button("📅 How do I book?"):
    prompt_input = "How do I book an appointment or reservation?"

# Chat Input
user_chat = st.chat_input("Ask about services, pricing, hours, or bookings...")
if user_chat:
    prompt_input = user_chat

if prompt_input:
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

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
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ],
            temperature=0.3,
            max_tokens=300
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
    except Exception as e:
        st.error(f"Error communicating with AI backend: {str(e)}")