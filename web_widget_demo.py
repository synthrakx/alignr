import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Receptionist Demo",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Premium SaaS UI/UX CSS Overhaul
st.markdown("""
    <style>
    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global Theme */
    .stApp { background-color: #0B1120; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    /* Live Status Badge */
    .status-badge {
        display: inline-flex; align-items: center; background-color: #064E3B; 
        border: 1px solid #047857; border-radius: 999px; padding: 4px 12px; 
        font-size: 0.75rem; font-weight: 600; color: #34D399; margin-bottom: 1rem;
    }
    .status-dot { height: 6px; width: 6px; background-color: #10B981; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px #10B981;}
    
    /* Chat Bubbles - SaaS Style */
    .stChatMessage { background-color: transparent !important; border: none !important; padding: 0 !important; margin-bottom: 1.5rem !important; }
    div[data-testid="stChatMessageContent"] { 
        background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; 
        padding: 1rem 1.25rem; font-size: 0.95rem; line-height: 1.5; color: #F1F5F9; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    /* Make user messages slightly different to distinguish */
    div[data-testid="chat-message-user"] div[data-testid="stChatMessageContent"] { background-color: #0F172A; border-color: #3B82F6; }
    
    /* Sidebar Polish */
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="status-badge"><span class="status-dot"></span> Online & Ready</div>', unsafe_allow_html=True)
st.title("✨ AI Receptionist")
st.caption("Test how the AI handles your customers 24/7. Switch industries in the sidebar.")

# --- SIDEBAR ---
st.sidebar.title("⚙️ Demo Controls")
business_type = st.sidebar.selectbox(
    "1. Select Industry:",
    ["General / Service Business", "Dental & Medical Clinic", "Fine Dining Restaurant", "Boutique Hotel"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Why Businesses Upgrade:**
*   **0s Wait Time:** Instant answers.
*   **100% Accurate:** Only uses your data.
*   **24/7 Booking:** Never miss a midnight lead.
""")

# --- KNOWLEDGE BASES (USD) ---
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

# --- GROQ API INIT ---
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY missing. Contact developer.")
    st.stop()
client = Groq(api_key=api_key)

# --- CHAT STATE ---
welcome_msg = f"👋 **Welcome to the {business_type} demo!**\n\nI am the AI assistant. Test me by asking about:\n- 💰 **Pricing & Services**\n- 🕒 **Business Hours**\n- 📅 **Booking Policies**\n\nHow can I help you today?"

if "messages" not in st.session_state or "last_business_type" not in st.session_state or st.session_state.last_business_type != business_type:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.last_business_type = business_type

# Avatars for UI
avatar_dict = {"assistant": "✨", "user": "👤"}

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_dict[msg["role"]]):
        st.markdown(msg["content"])

# --- CHAT INPUT & LOGIC ---
prompt_input = st.chat_input("Type your question here...")

# Quick Action Buttons (Placed right above input to act as suggestions)
st.write("") # Spacer
col1, col2, col3 = st.columns(3)
if col1.button("💰 Services & Pricing", use_container_width=True): prompt_input = "What are your services and prices?"
if col2.button("🕒 Hours & Location", use_container_width=True): prompt_input = "What are your hours and where are you located?"
if col3.button("📅 How to Book", use_container_width=True): prompt_input = "How do I make a booking or reservation?"

if prompt_input:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user", avatar=avatar_dict["user"]):
        st.markdown(prompt_input)

    # 2. System Instruction
    system_instruction = f"""
    You are a professional, friendly 24/7 AI Receptionist for this business.
    Answer the user's question accurately using ONLY the information provided in this Knowledge Base:
    
    {current_kb}
    
    Rules:
    1. Keep responses concise, professional, and helpful (2-3 sentences max).
    2. Always quote prices exactly as shown in USD ($).
    3. If the answer is not in the Knowledge Base, politely state you don't have that information but human staff will assist them shortly.
    """

    # 3. Call Groq API (FIXED MODEL ID)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Extremely fast, reliable, current Groq model
            messages=[
                {"role": "system", "content": system_instruction},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ],
            temperature=0.2,
            max_tokens=200
        )
        reply = response.choices[0].message.content
        
        # 4. Show AI Response
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar=avatar_dict["assistant"]):
            st.markdown(reply)
            
    except Exception as e:
        st.error(f"Backend Error: {str(e)}")