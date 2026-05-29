# OSF Preregistration — ALIGNR v2.0 Study
# Register at: osf.io/prereg BEFORE deployment (Day 21)

## Study Title
Does structured pre-AI articulation preserve cognitive independence?
A 60-day randomized study of Reasoning Alignment Score (RAS),
Cognitive Independence Index (CII), and Surprise Calibration Score (SCS).

## Hypotheses
H1: Feedback group shows significantly higher RAS improvement at Day 60
H2: Feedback group shows higher CII maintenance over 60 days
H3: SCS increases over 60 days in feedback group (calibration improving)

## Study Design
Randomized A/B controlled study.
Group A (60%, feedback): full RAS+CII+SCS scores + 2-sentence narrative
Group B (40%, control): prompts only, no scores shown
Assignment: deterministic hash(user_id)%10 < 6 = feedback

## Participants
Convenience sample via ALIGNR platform (consumer users)
Target N: 500+ registered, 100+ completing 14+ sessions per group
Duration: 60 days per participant

## Analysis Plan
Primary: Independent-samples t-test, alpha = 0.05
Secondary: Cohen's d effect sizes for all three metrics
Reported: exact p-values, means, SDs, effect sizes, CIs

## Submit to OSF on Day 21 (June 12) before deploying ALIGNR
