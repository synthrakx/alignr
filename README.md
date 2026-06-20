# ALIGNR

**Author:** Aman Raj ([@synthrakx](https://twitter.com/synthrakx))
**Website:** [alignr.me](https://alignr.me) *(live June 21, 2026)*
**Live API:** [alignr-production-4aae.up.railway.app](https://alignr-production-4aae.up.railway.app)
**Ethics:** [synthrakx.github.io/alignr/ethics](https://synthrakx.github.io/alignr/ethics)
**ORCID:** [0009-0009-1346-5230](https://orcid.org/0009-0009-1346-5230)
**Preregistration:** OSF — submitted June 21, 2026 before any data collection

---

## Research Question

Does structured pre-AI articulation preserve cognitive independence and reduce AI dependence over 60 days, compared to unstructured AI use?

## Three Metrics

| Metric | Formula | Measures |
|--------|---------|----------|
| RAS | cosine_similarity(encode(pre_thinking), encode(ai_output)) | Calibration of pre-AI reasoning |
| CII | (ttk * 0.6) + (min(avg_len/20, 1.0) * 0.4) | Vocabulary independence over time |
| SCS | cosine_similarity(encode(prediction), encode(ai_output)) | Surprise calibration accuracy |

Encoder: sentence-transformers/all-MiniLM-L6-v2 (384-dim embeddings)

## Study Design

- Randomized A/B: 60% feedback group (sees scores + AI narrative), 40% control (no scores)
- Assignment: Deterministic SHA-256 hash of email — same email goes to same group, always
- Duration: 60 days per participant, minimum 14 sessions for primary analysis
- Target N: 500+ registered participants
- Primary test: Independent t-test + Cohen's d, alpha = 0.05
- Preregistered: OSF before any data collection

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

Live API: https://alignr-production-4aae.up.railway.app/docs

## How to Cite

Raj, A. (2026). Does structured pre-AI articulation preserve cognitive independence? A 60-day randomized study. OSF Preregistrations. https://osf.io/[ID]

## Researcher

This study is conducted by Aman Raj, independent researcher, Bihar, India.

- Email: synthrakx@proton.me
- GitHub: github.com/synthrakx
- ORCID: 0009-0009-1346-5230

ALIGNR is not affiliated with any institution.

## License

MIT — open source. Verify every claim in the source.