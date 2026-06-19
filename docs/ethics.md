\# ALIGNR — Research Ethics Statement



\*\*Last updated:\*\* June 19, 2026



\---



\## What is ALIGNR?



ALIGNR is a research platform studying whether structured pre-AI reflection preserves cognitive independence over 60 days. By using ALIGNR, you are voluntarily participating in a randomized research study.



\*\*Study preregistration:\*\* \[osf.io/XXXXXXX](https://osf.io) (will be registered on June 21, 2026, BEFORE any data collection or platform launch)



\---



\## What we collect



\- \*\*Numerical scores only\*\*: RAS, CII, SCS (floating point numbers, e.g. 0.7234)

\- \*\*Task category\*\*: one of five strings (technical / decision / research / creative / learning)

\- \*\*Session timestamps\*\*: date and time of each session

\- \*\*Anonymous user ID\*\*: 16-character hex derived from a one-way SHA-256 hash of your email

\- \*\*Study group assignment\*\*: "feedback" or "control" (deterministic from your user ID)



\---



\## What we never collect



\- Your pre-thinking text

\- The AI output you paste

\- Your prediction text

\- Your reflection text

\- Your real email address

\- Your IP address

\- Any personally identifiable information of any kind



\---



\## How to verify this claim



1\. Our full source code is at \[github.com/synthrakx/alignr](https://github.com/synthrakx/alignr)

2\. The database schema has no text-payload columns — open `alignr.db` in any SQLite viewer and inspect the `sessions` table yourself

3\. Run `grep -r "pre\_thinking\\|ai\_output\\|prediction" alignr/backend/` on our codebase — it returns zero storage-related matches

4\. We invite researchers to audit our privacy architecture at any time



\---



\## Study design



\- \*\*Design\*\*: Randomized A/B study (between-subjects)

\- \*\*Groups\*\*: 60% feedback group (sees RAS/CII/SCS scores after each session), 40% control group (same prompts, no scores shown)

\- \*\*Assignment\*\*: Deterministic — first 2 hex chars of your hashed user ID determine your group. Same email always gets same group. Cannot be re-rolled.

\- \*\*Duration\*\*: 60 days per participant, minimum 14 sessions for inclusion in analysis

\- \*\*Target N\*\*: 500+ registered participants, 100+ completing 14+ sessions

\- \*\*Primary outcome\*\*: RAS improvement difference between groups at Day 60

\- \*\*Statistical test\*\*: Independent samples t-test + Cohen's d, alpha = 0.05



\---



\## Hypotheses (preregistered)



\*\*H1\*\*: The feedback group will show significantly higher RAS improvement from Session 1 to Session 14 compared to the control group.



\*\*H2\*\*: The feedback group will show higher CII maintenance (less vocabulary convergence toward AI patterns) over 60 days.



\*\*H3\*\*: SCS will increase significantly over 60 days in the feedback group, indicating improving calibration of AI response prediction.



\---



\## Your rights as a participant



\- Participation is entirely voluntary

\- You may withdraw at any time by emailing synthrakx@proton.me

\- Your data will be deleted within 48 hours upon request — no questions asked

\- Results will be published as aggregate statistics only, never individual-level

\- You will never be identified in any publication

\- You may request a copy of your own numerical data at any time



\---



\## What ALIGNR is NOT



\- Not a clinical assessment or psychological evaluation

\- Not a measure of intelligence, cognitive ability, or IQ

\- Not a diagnostic tool of any kind

\- Not mental health advice or therapy

\- Not affiliated with any academic institution or regulatory body



\---



\## Limitations of our measures



These limitations are stated explicitly because honest science requires them:



\- \*\*RAS\*\* measures linguistic similarity between pre-AI text and AI output, not cognitive processes directly. Semantic similarity is a proxy, not a direct window into reasoning quality.



\- \*\*CII\*\* is a proxy measure using vocabulary diversity (type-token ratio) and sentence complexity (average word length). It is not a validated psychological instrument and should not be interpreted as a measure of intelligence or cognitive ability.



\- \*\*SCS\*\* measures prediction accuracy on semantic dimensions only. It captures how well language patterns align, not deeper epistemic states.



\- Results reflect patterns in your language use across sessions. They are research data, not personal assessments.



\- Convenience sampling via the ALIGNR platform limits generalizability. Results apply to the population of self-selected ALIGNR users, not the general population.



\---



\## Data retention



\- Numerical scores are retained for the duration of the study (60 days per participant + 24 months for analysis and replication)

\- All data is stored locally on the ALIGNR server, not on third-party clouds

\- After the study and replication period, anonymized aggregate data may be archived for future research



\---



\## Contact



\*\*Email:\*\* synthrakx@proton.me

\*\*GitHub:\*\* \[github.com/synthrakx/alignr](https://github.com/synthrakx/alignr)

\*\*Website:\*\* \[alignr.me](https://alignr.me)



\*ALIGNR is independent research. Not affiliated with any institution.\*

