\# Spec: nlp\_engine.py — ALIGNR v2.0 Metrics Engine



\## What to build

A Python module that calculates three cognitive metrics from user text.



\## Why

ALIGNR v2.0 measures: RAS (cosine similarity), CII (independence index),

SCS (surprise calibration). Three metrics give research statistical power.



\## Success criteria

1\. calculate\_ras(pre, ai) returns dict with ras, cas\_pct, interpretation

2\. calculate\_cii(text, history) returns float 0.0-1.0

3\. calculate\_scs(prediction, ai) returns dict with scs, surprise\_level

4\. All 4 unit tests pass (similar/unrelated/short-input/novelty)

5\. No text in any returned dict (numbers only — privacy by design)



\## Privacy constraint (non-negotiable)

pre\_thinking, ai\_output, prediction: method-local, never stored to self

Only floats stored to database. Verifiable via SQLite Viewer inspection.



\## Tech

sentence-transformers all-MiniLM-L6-v2 (RAS + SCS)

Word-level features for CII (no ML model needed for MVP)

numpy + sklearn.metrics.pairwise



\## Not in scope (backlog)

ML-based CII, anti-gaming system, browser extension

