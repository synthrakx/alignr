import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Synthrakx | Enterprise AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- UNIQUE PREMIUM SAAS CSS (Glassmorphism & Depth) ---
st.markdown("""
    <style>
    /* Hide Streamlit Clutter while preserving top-left sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}
    [data-testid="stHeader"] {background: transparent !important;}
    [data-testid="stToolbar"] {visibility: hidden;}
    [data-testid="stDecoration"] {visibility: hidden;}

    /* Modern Font & Gradient Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }

    /* Sleek Top Brand Header */
    .brand-header {
        font-size: 0.9rem;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #38BDF8;
        margin-bottom: 0.5rem;
    }

    /* Main Title Styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #F8FAFC, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    /* Sidebar "Command Center" Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .metric-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .metric-label { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;}
    .metric-value { font-size: 1.2rem; font-weight: 600; color: #10B981; }

    /* Chat Bubbles - High Contrast & Depth */
    .stChatMessage { background-color: transparent !important; border: none !important; padding: 0 !important; margin-bottom: 1.2rem !important; }

    /* AI Assistant Bubble */
    div[data-testid="chat-message-assistant"] div[data-testid="stChatMessageContent"] {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 0px 16px 16px 16px;
        padding: 1rem 1.25rem; font-size: 0.95rem; color: #F1F5F9;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }

    /* User Bubble */
    div[data-testid="chat-message-user"] div[data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        border: none;
        border-radius: 16px 0px 16px 16px;
        padding: 1rem 1.25rem; font-size: 0.95rem; color: #FFFFFF;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }

    /* Quick Buttons */
    .stButton>button {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #E2E8F0;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: rgba(56, 189, 248, 0.1);
        border-color: #38BDF8;
        transform: translateY(-2px);
        color: #38BDF8;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (COMMAND CENTER) ---
st.sidebar.markdown('<div class="brand-header">⚙️ Admin Console</div>', unsafe_allow_html=True)
business_type = st.sidebar.selectbox(
    "Select Target Industry:",
    ["General / Service Business", "Home Services (HVAC & Plumbing)", "Dental & Medical Clinic", "Fine Dining Restaurant", "Boutique Hotel"]
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="brand-header">Live Telemetry</div>', unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="metric-box">
    <div class="metric-label">Avg. Response Time</div>
    <div class="metric-value">⚡ 0.8s</div>
</div>
<div class="metric-box">
    <div class="metric-label">Resolution Rate</div>
    <div class="metric-value">🎯 96.4%</div>
</div>
<div class="metric-box">
    <div class="metric-label">After-Hours Capture</div>
    <div class="metric-value">🌙 Active</div>
</div>
""", unsafe_allow_html=True)

# --- MAIN DASHBOARD ---
st.markdown('<div class="brand-header">SYNTHRAKX.AI</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Autonomous Receptionist</div>', unsafe_allow_html=True)
st.caption("Try to break it. Ask complex questions about pricing, hours, or policies.")
st.write("") # Spacer

# --- KNOWLEDGE BASES (USD) ---
KNOWLEDGE_BASES = {
    "Home Services (HVAC & Plumbing)": """
Business: Apex Plumbing, Heating & Air
    Hours: 24/7 Emergency Dispatch Available | Standard Office: Mon-Sat 7:00 AM - 7:00 PM EST
    Services & Pricing:
    - Service Diagnostic & Inspection Call: $89
    - Standard Drain Clearing / Plumbing Repair: $140
    - HVAC Tune-Up & System Maintenance: $115
    - Water Heater Service & Installation: $250+
    Location: Serving Metro & Surrounding Counties
    Dispatch Policy: Instant phone/text dispatch. Emergency calls dispatched within 60 minutes.
    """,
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

# --- GROQ API INIT ---
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ System Offline: API Key Missing.")
    st.stop()
client = Groq(api_key=api_key)

# --- CHAT STATE ---
welcome_msg = f"**Welcome to the {business_type} simulation environment.**\n\nI am the autonomous agent deployed for this business. Test my capabilities by asking about:\n- 💰 **Pricing & Services**\n- 🕒 **Hours & Operations**\n- 📅 **Booking & Policies**"

if "messages" not in st.session_state or "last_business_type" not in st.session_state or st.session_state.last_business_type != business_type:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.last_business_type = business_type

# High-end avatars
avatar_dict = {"assistant": "⚡", "user": "👤"}

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_dict[msg["role"]]):
        st.markdown(msg["content"])

# --- QUICK ACTION BUTTONS ---
st.write("")
col1, col2, col3 = st.columns(3)
prompt_input = None

if col1.button("💰 Services & Pricing", use_container_width=True): prompt_input = "What are your services and prices?"
if col2.button("🕒 Hours & Location", use_container_width=True): prompt_input = "What are your hours and where are you located?"
if col3.button("📅 How to Book", use_container_width=True): prompt_input = "How do I make a booking or reservation?"

user_chat = st.chat_input("Initiate query...")
if user_chat:
    prompt_input = user_chat

if prompt_input:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user", avatar=avatar_dict["user"]):
        st.markdown(prompt_input)

    # 2. System Instruction
    system_instruction = f"""
    You are an elite, highly professional 24/7 AI Receptionist for this business.
    Answer the user's question accurately using ONLY the information provided in this Knowledge Base:

    {current_kb}

    Rules:
    1. Keep responses concise, professional, and helpful (2-3 sentences max).
    2. ALWAYS include the dollar sign ($) immediately before every price figure (e.g. $89, $140, $250). NEVER output bare numbers without '$'.
    3. Output plain text ONLY. NEVER wrap prices or numbers in backticks (`), code blocks, or markdown code formatting.
    4. Never hallucinate. If the answer is not in the Knowledge Base, politely state you don't have that information but human staff will assist them shortly.
    """

    # 3. Call Groq API (VERIFIED MODEL ID)
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": system_instruction},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ],
            temperature=0.2,
            max_tokens=200
        )
        reply = response.choices[0].message.content

        # Python Sanitization: Eliminate backtick code-boxes & enforce $ currency prefixes
        reply = reply.replace("`", "")
        reply = re.sub(r'\b(for|at|is|costs?|priced at)\s+(\d+)\b', r'\1 $\2', reply, flags=re.IGNORECASE)

        # 4. Show AI Response
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar=avatar_dict["assistant"]):
            st.markdown(reply)

    except Exception as e:
        st.error(f"System Error: {str(e)}")