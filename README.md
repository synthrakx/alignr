# ALIGNR

**Author:** Aman Raj ([@synthrakx](https://twitter.com/synthrakx))

**Platform:** [alignr.streamlit.app](https://alignr.streamlit.app)

**Live API:** [alignr-giaz.onrender.com](https://alignr-giaz.onrender.com)

**Ethics:** [synthrakx.github.io/alignr/ethics](https://synthrakx.github.io/alignr/ethics)

**ORCID:** [0009-0009-1346-5230](https://orcid.org/0009-0009-1346-5230)

**Preregistration:** [osf.io/y86mg](https://osf.io/y86mg) — registered June 23, 2026, before any data collection

**Protocol Log:** [osf.io/mv4u7](https://osf.io/mv4u7) — Protocol Clarification & Correction Log

---

## Research Question

Does structured pre-AI articulation preserve cognitive independence and reduce AI dependence over 60 days, compared to unstructured AI use?

## Three Metrics

| Metric | Formula | Measures |
|--------|---------|----------|
| RAS | cosine_similarity(encode(pre_thinking), encode(ai_output)) | Calibration of pre-AI reasoning |
| CII | (ttk * 0.6) + (min(avg_len/20, 1.0) * 0.4) | Vocabulary independence over time |
| SCS | cosine_similarity(encode(prediction), encode(ai_output)) | Surprise calibration accuracy |

Encoder: sentence-transformers/all-MiniLM-L6-v2 (384-dim embeddings) / Path B Direct ONNX Runtime

## Study Design

- Randomized A/B: ~60% feedback group (sees numerical scores), ~40% control (no scores)
- Assignment: Deterministic SHA-256 hash of email — same email goes to same group, always
- Duration: 60 days per participant, 14 sessions max (hard cap enforced server-side)
- Primary test: Independent t-test comparing Session 14 RAS between groups + Cohen's d, alpha = 0.05
- Supplementary: Bootstrap resampling (1,000 iterations, 95% CI)
- Preregistered: [osf.io/y86mg](https://osf.io/y86mg) | Protocol Log: [osf.io/mv4u7](https://osf.io/mv4u7)

## Privacy Architecture

No text is stored at any point. Only numerical scores.

| Stored | Never stored |
|--------|--------------|
| RAS, CII, SCS (floats) | pre_thinking text |
| task_type, timestamp | ai_output text |
| 16-char SHA-256 hash of email | prediction text |
| study_group assignment | email, IP, any PII |

Full ethics statement: [synthrakx.github.io/alignr/ethics](https://synthrakx.github.io/alignr/ethics)

## Quick Start

git clone https://github.com/synthrakx/alignr
cd alignr
pip install -r requirements.txt
uvicorn fastapi_alignr_v1:app --reload
streamlit run alignr/frontend/app.py

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /user/register | Register user (email hashed, never stored) |
| POST | /session | Submit session, receive RAS/CII/SCS scores |
| GET | /history/{user_id} | Retrieve numerical session history |
| GET | /research/stats | Aggregate statistics for both groups |
| GET | /health | Database and service health check |

Live API Docs: https://alignr-giaz.onrender.com/docs

## How to Cite

BibTeX:

    @misc{raj2026alignr,
      title  = {Does structured pre-AI articulation preserve cognitive independence?
                A 60-day randomized study},
      author = {Raj, Aman},
      year   = {2026},
      month  = {June},
      url    = {https://osf.io/y86mg},
      note   = {Preregistered at osf.io/y86mg. Platform: alignr.streamlit.app}
    }

APA: Raj, A. (2026, June 23). *ALIGNR: Longitudinal Study of Cognitive Alignment in Human-AI Interaction*. OSF. https://osf.io/y86mg

## Researcher

This study is conducted by Aman Raj, independent researcher, Bihar, India.

- Email: synthrakx@proton.me
- GitHub: github.com/synthrakx
- ORCID: [0009-0009-1346-5230](https://orcid.org/0009-0009-1346-5230)

ALIGNR is not affiliated with any institution.

## License

MIT — open source. Verify every claim in the source.

---