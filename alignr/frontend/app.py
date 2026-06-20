"""
alignr/frontend/app.py
ALIGNR Streamlit Frontend v2 — with consent gate.
Day 20 — June 20, 2026 (identity layer added)
Run: streamlit run alignr/frontend/app.py
"""
import hashlib
import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"
ETHICS_URL = "https://synthrakx.github.io/alignr/ethics"
GITHUB_URL = "https://github.com/synthrakx/alignr"
ORCID_URL = "https://orcid.org/0009-0009-1346-5230"


def hash_email(email: str) -> str:
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()[:16]


st.set_page_config(page_title="ALIGNR", page_icon="🧠", layout="wide")


# ── CONSENT GATE ─────────────────────────────────────────────

def show_consent_gate() -> bool:
    """Returns True only after explicit consent given.
    Gate for all data collection. No user reaches data tabs without this."""
    if st.session_state.get("consent_given"):
        return True

    st.title("🧠 ALIGNR")
    st.markdown("### Before You Begin")
    st.caption("ALIGNR is a research study. Please read and accept to participate.")

    with st.expander("📋 What is ALIGNR? (click to read)", expanded=True):
        st.markdown("""
        ALIGNR is a **voluntary research study** measuring whether structured 
        pre-AI reflection preserves cognitive independence over 60 days.
        
        **Study design:** You will be randomly assigned to one of two groups:
        - **Feedback group (60%)**: sees your RAS, CII, SCS scores after each session
        - **Control group (40%)**: same prompts, no scores shown
        
        Minimum recommended: 14 sessions over 60 days for meaningful data.
        """)

    with st.expander("🔒 What data is collected?"):
        st.markdown(f"""
        **We collect:** numerical scores only (RAS, CII, SCS), task category, 
        timestamps, and a 16-character hash of your email (irreversible — 
        we cannot recover your email from it).
        
        **We NEVER collect:** your pre-thinking text, AI output, prediction 
        text, real email address, or IP address.
        
        [Verify this in our source code →]({GITHUB_URL})
        """)

    with st.expander("🚪 Your rights"):
        st.markdown(f"""
        - Participation is completely voluntary
        - Withdraw any time: synthrakx@proton.me — data deleted within 48 hours
        - Results published as aggregate statistics only — never individual
        - Full ethics statement: [{ETHICS_URL}]({ETHICS_URL})
        """)

    with st.expander("⚠️ Limitations of our measures"):
        st.markdown("""
        - **RAS** measures linguistic similarity, not cognitive processes directly
        - **CII** is a proxy measure, not a validated psychological instrument
        - **SCS** measures prediction accuracy on semantic dimensions only
        - Results are research data, not personal assessments
        """)

    st.markdown("---")
    consent = st.checkbox(
        "✅ I understand this is a research study and I consent to participate on these terms.",
        key="consent_checkbox"
    )

    if consent:
        if st.button("Continue to ALIGNR →", type="primary"):
            st.session_state["consent_given"] = True
            st.rerun()
        return False

    st.info("Please read and accept the terms above to continue.")
    return False


# ── MAIN APP (only runs after consent) ───────────────────────

if not show_consent_gate():
    st.stop()


# Privacy banner (visible on all data tabs)
st.markdown(f"""
<div style="background:#0A1628;border:1px solid #1E3A5F;
border-radius:8px;padding:10px 16px;margin-bottom:16px;
color:#80C8FF;font-size:13px;">
🔒 Your text never leaves your device unhashed.
Only numerical scores are saved.
<a href="{GITHUB_URL}" style="color:#4FA8FF">Verify in source →</a>
| <a href="{ETHICS_URL}" style="color:#4FA8FF">Ethics statement →</a>
</div>
""", unsafe_allow_html=True)

st.title("🧠 ALIGNR")
st.caption("Reasoning Alignment Research Platform")

tab_dash, tab_sess, tab_about = st.tabs(
    ["📊 Dashboard", "➕ New Session", "ℹ️ About"]
)

# ── DASHBOARD TAB ────────────────────────────────────────────
with tab_dash:
    email = st.text_input("Your email", key="dash_email",
                          placeholder="you@example.com")
    if email:
        uid = hash_email(email)
        st.caption(f"Anonymous ID: `{uid}` — email hashed, never stored")

        r = requests.get(f"{API_BASE}/history/{uid}")

        if r.status_code == 404:
            st.info("No sessions yet. Go to ➕ New Session to start.")
        elif r.ok:
            sessions = r.json().get("sessions", [])
            df = pd.DataFrame(sessions)

            col1, col2, col3 = st.columns(3)
            col1.metric("Latest RAS",
                        f"{df['ras'].iloc[-1]:.3f}",
                        delta=f"{df['ras'].iloc[-1] - df['ras'].iloc[-2]:.3f}"
                        if len(df) > 1 else None)
            col2.metric("Latest CII", f"{df['cii'].iloc[-1]:.3f}")
            col3.metric("Latest SCS",
                        f"{df['scs'].dropna().iloc[-1]:.3f}"
                        if df["scs"].notna().any() else "N/A")

            st.subheader("Session History")
            st.dataframe(
                df[["session_num", "task_type", "ras",
                    "cii", "scs", "study_group", "created_at"]],
                use_container_width=True
            )

            if len(df) >= 2:
                st.subheader("RAS & CII Trend")
                st.line_chart(df.set_index("session_num")[["ras", "cii"]])
        else:
            st.error(f"API error: {r.status_code}")

# ── NEW SESSION TAB ──────────────────────────────────────────
with tab_sess:
    s_email = st.text_input("Email", key="sess_email",
                            placeholder="you@example.com")
    s_task = st.selectbox(
        "Task type",
        ["technical", "creative", "analytical", "research", "writing", "general"]
    )

    st.markdown("---")
    st.markdown("**Step 1:** Write your thinking BEFORE using AI")
    pre = st.text_area("Pre-thinking (minimum 5 words)",
                       height=120, key="pre")

    st.markdown("**Step 2 (optional):** Predict what the AI will say")
    pred = st.text_area("Your prediction", height=80, key="pred")

    st.info("⏸️  Now use your AI tool. Paste the AI response below.")
    ai_out = st.text_area("AI output", height=120, key="ai_out")

    if st.button("Calculate Scores", type="primary"):
        if not s_email:
            st.warning("Email is required.")
        elif not pre or len(pre.strip().split()) < 5:
            st.warning("Pre-thinking must be at least 5 words.")
        elif not ai_out or len(ai_out.strip()) < 10:
            st.warning("AI output is required (min 10 characters).")
        else:
            with st.spinner("Calculating alignment scores..."):
                try:
                    r = requests.post(f"{API_BASE}/session", json={
                        "email": s_email,
                        "pre_thinking": pre,
                        "ai_output": ai_out,
                        "prediction": pred or "",
                        "task_type": s_task,
                    }, timeout=60)

                    if r.ok:
                        res = r.json()
                        st.success("✅ Scores calculated and saved.")

                        c1, c2, c3 = st.columns(3)
                        c1.metric("RAS", f"{res.get('ras', 0):.3f}",
                                  help="Reasoning Alignment Score")
                        c2.metric("CII", f"{res.get('cii', 0):.3f}",
                                  help="Cognitive Independence Index")
                        c3.metric("SCS",
                                  f"{res.get('scs'):.3f}"
                                  if res.get("scs") else "N/A",
                                  help="Surprise Calibration Score")

                        st.caption(
                            f"Interpretation: {res.get('ras_interpretation')} | "
                            f"Group: {res.get('study_group')} | "
                            f"Session #{res.get('session_number')}"
                        )

                        if res.get("narrative"):
                            st.info(f"💡 {res['narrative']}")

                        st.caption(res.get("message", ""))
                    else:
                        st.error(f"API error {r.status_code}: {r.text}")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Is the backend running?")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Run: uvicorn fastapi_alignr_v1:app --reload")

# ── ABOUT TAB ────────────────────────────────────────────────
with tab_about:
    st.markdown(f"""
**ALIGNR** measures whether structured pre-AI reflection
preserves cognitive independence over time.

### Metrics
| Metric | Formula | Meaning |
|--------|---------|---------|
| **RAS** | cosine_similarity(encode(pre), encode(ai)) | How calibrated was your pre-thinking? |
| **CII** | (ttk × 0.6) + (min(avg_len/20, 1.0) × 0.4) | Vocabulary diversity and complexity |
| **SCS** | cosine_similarity(encode(prediction), encode(ai)) | How well did you predict the AI? |

### Study Design
- 60-day randomized controlled trial
- 60% feedback group / 40% control group
- Assignment: deterministic hash of email
- OSF preregistered before data collection

### Limitations (Important)
- **RAS** measures linguistic similarity, not cognitive processes directly
- **CII** is a proxy measure, not a validated psychological instrument
- **SCS** measures prediction accuracy on semantic dimensions only
- Results are research data, not personal assessments

### Privacy
- Zero text stored in database
- Only numerical scores saved
- Email hashed on input, never stored

### Resources
- 📋 [Full Ethics Statement]({ETHICS_URL})
- 🔓 [Source Code]({GITHUB_URL})
- 📧 Contact: synthrakx@proton.me
    """)

    st.markdown("---")
    st.markdown(f"""
### Researcher

This study is conducted by **Aman Raj**, independent researcher, Bihar, India.

- **Email:** synthrakx@proton.me
- **GitHub:** [github.com/synthrakx/alignr]({GITHUB_URL})
- **ORCID:** [0009-0009-1346-5230]({ORCID_URL})

*ALIGNR is not affiliated with any institution.*
    """)