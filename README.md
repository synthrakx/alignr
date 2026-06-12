# ALIGNR
## AI Cognitive Alignment Trainer

**Status:** Day 11 of 90 — building in public. Launching June 28, 2026.

> How well does your thinking align with AI? Track it over 60 days.

ALIGNR measures cognitive alignment between your pre-AI reasoning and
AI-generated outputs using semantic similarity. Part of a real research
study on human-AI cognitive development.

---

## Research Output (Simulated — Day 11)

The portfolio simulation runs the complete ALIGNR system end-to-end
with 200 simulated users × 10 sessions = 2,000 sessions.

**Summary:**

- Study: Randomized A/B (feedback vs control)
- Users: 200 total (120 feedback, 80 control)
- Sessions: 2,000 total (10 per user)
- Metrics: RAS, CII, SCS
- Privacy: No text stored. Only floats. Verified by grep.

**RAS results:**

- Feedback group avg: 0.6865
- Control group avg: 0.3660
- p-value: 0.0000
- Cohen's d: 13.03 (large effect)
- Significant: True

**Data type:** SIMULATED — replace with real cohort data on Day 63.
**Preprint:** OSF preregistered Day 21, before any real data collection.

**Note on effect size:** The d=13 is inflated because the simulation
uses word-overlap as a proxy. Real semantic similarity
(sentence-transformers all-MiniLM-L6-v2) activates on Day 15, which
will produce realistic effect sizes in the d=0.5-1.5 range typical of
cognition research.

### Figures

- **Figure 1:** RAS Trajectory — feedback vs control over 10 sessions
- **Figure 2:** CII Progression — vocabulary diversity over time
- **Figure 3:** SCS Calibration — prediction accuracy distribution

Run the simulation locally with: python alignr_simulation.py

---

## Research Basis

- CHI 2026: Pre-AI reflection improves critical thinking outcomes
- Microsoft Research ExtendAI (CHI 2025): Articulating reasoning first = better augmentation
- Academy of Management Journal (2026): Cognitive alignment in human-AI collaboration

---

## Privacy — Verifiable, Not Just Claimed

Your text is never stored. Only alignment scores (numbers) are kept.

**Architectural enforcement:**

- Text parameters are method-local inside ALIGNRSession.calculate()
- After calculation, text falls out of scope and is garbage collected
- Nothing assigned to self from text inputs
- Verifiable in source: searching for self.pre in oop_alignr.py returns no code assigning text to self

**Data export proof:**

- portfolio.json contains only counts, averages, p-values, effect sizes
- Zero raw user sentences in the export
- 2,000+ text inputs processed in tests, zero persisted

Analysis runs on local AI (Ollama) — nothing sent to OpenAI.

---

## Architecture

- **ALIGNRSession** — one interaction, metrics extracted, text discarded
- **ALIGNRUser** — one participant, identified by SHA-256 email hash
- **ALIGNRResearch** — the entire study, group comparison, export

The class hierarchy lives in oop_alignr.py. The portfolio simulation
that uses it end-to-end lives in alignr_simulation.py.

---

## Built By

SYNTHRAKX | synthrakx@proton.me | May 2026

GitHub: github.com/synthrakx/alignr