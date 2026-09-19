"""
analysis/primary_analysis.py

ALIGNR -- Primary Confirmatory Analysis
Corrected per the Protocol Clarification & Correction Log posted to the
OSF project on [DATE]. See README.md / docs/index.md for the link.

WHAT CHANGED AND WHY
---------------------
The previous version of this file computed a Session-1-to-Session-14
within-participant CHANGE SCORE and compared that between groups. That
is not what the registration's own "Primary Statistical Test" section
specifies. This file now computes exactly what is registered as primary:

    Independent-samples t-test comparing Session 14 RAS between the
    feedback group and the control group, alpha = 0.05, with Cohen's d
    as the effect-size estimate.

The Session 1->14 trajectory (the language used in the H1 narrative) is
retained below as a clearly-labeled SECONDARY / descriptive analysis.
It is reported, but no confirmatory claim is drawn from it alone.

A bootstrap-resampling supplement (1,000 iterations, 95% CI) is
included per Dr. Maria Antoniak's suggestion. This is a robustness
check on the primary result, not a replacement for it.

STATISTICAL NOTE: this uses scipy's default Student's t-test
(equal_var=True), matching an unmodified reading of "independent
t-test" in the registration. The registration does not specify
Welch's vs Student's. If variance homogeneity looks violated in real
data, a Levene's test + Welch's correction can be added as a further
supplementary check -- but that would itself need its own dated
addendum, the same way this file's correction did. Don't silently
switch it.

INCLUSION CRITERIA (per registration)
--------------------------------------
Only participants with >= 14 completed sessions are "completers" and
enter the primary analysis population. Everyone else is reported as a
descriptive count only, not included in the test.

ASSIGNMENT RATIO NOTE
-----------------------
alignr/backend/study_groups.py's hash-prefix assignment produces a true
split of ~60.94% feedback / ~39.06% control (156 of 256 possible
two-hex-char prefixes), not an exact 60/40. This file reports the real
observed ratio rather than assuming 60/40. See Correction Log, item 3.
No change was made to the assignment function itself -- see the log
for why.
"""

import os
import sys

import numpy as np
import pandas as pd
import psycopg2
from scipy import stats


COMPLETER_THRESHOLD = 14   # sessions required for inclusion in primary analysis
PRIMARY_SESSION = 14       # the session number the confirmatory test runs on
ALPHA = 0.05
BOOTSTRAP_ITERATIONS = 1000
BOOTSTRAP_CI = 0.95


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")
    return psycopg2.connect(database_url)


def load_sessions() -> pd.DataFrame:
    """One row per session, joined to each participant's assigned group."""
    query = """
        SELECT
            s.user_id,
            u.study_group,
            s.session_number,
            s.ras,
            s.cii,
            s.scs,
            s.timestamp
        FROM sessions s
        JOIN users u ON u.user_id = s.user_id
        ORDER BY s.user_id, s.session_number;
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
    return df


def get_completer_population(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict to participants with >= COMPLETER_THRESHOLD sessions."""
    session_counts = df.groupby("user_id")["session_number"].count()
    completers = session_counts[session_counts >= COMPLETER_THRESHOLD].index
    non_completers = session_counts[session_counts < COMPLETER_THRESHOLD]

    print(f"Registered participants with >=1 session: {df['user_id'].nunique()}")
    print(f"Completers (>= {COMPLETER_THRESHOLD} sessions): {len(completers)}")
    print(f"Non-completers (excluded from primary analysis): {len(non_completers)}")

    return df[df["user_id"].isin(completers)].copy()


def run_primary_test(completers_df: pd.DataFrame) -> dict:
    """THE REGISTERED PRIMARY TEST -- Session 14 RAS, feedback vs control."""
    # Column normalization for schema drift
    if "session_num" in completers_df.columns and "session_number" not in completers_df.columns:
        completers_df["session_number"] = completers_df["session_num"]

    session_14 = completers_df[completers_df["session_number"] == PRIMARY_SESSION]
    feedback = session_14[session_14["study_group"] == "feedback"]["ras"].dropna()
    control = session_14[session_14["study_group"] == "control"]["ras"].dropna()

    if len(feedback) < 2 or len(control) < 2:
        return {"status": "insufficient_data", "feedback_n": len(feedback), "control_n": len(control)}

    t_stat, p_value = stats.ttest_ind(feedback, control)  # default: equal_var=True
    pooled_sd = np.sqrt((feedback.std(ddof=1) ** 2 + control.std(ddof=1) ** 2) / 2)
    cohens_d = (feedback.mean() - control.mean()) / pooled_sd if pooled_sd > 0 else 0.0

    return {
        "status": "complete",
        "feedback_n": int(len(feedback)),
        "control_n": int(len(control)),
        "feedback_mean_ras": round(float(feedback.mean()), 4),
        "control_mean_ras": round(float(control.mean()), 4),
        "t_statistic": round(float(t_stat), 4),
        "p_value": round(float(p_value), 6),
        "cohens_d": round(float(cohens_d), 4),
        "significant_at_alpha_05": bool(p_value < ALPHA),
    }


def run_bootstrap_supplement(completers_df: pd.DataFrame) -> dict:
    """SUPPLEMENTARY, NOT PRIMARY -- Antoniak's bootstrap robustness check."""
    session_14 = completers_df[completers_df["session_number"] == PRIMARY_SESSION]
    feedback = session_14[session_14["study_group"] == "feedback"]["ras"].dropna().values
    control = session_14[session_14["study_group"] == "control"]["ras"].dropna().values

    if len(feedback) < 2 or len(control) < 2:
        return {"status": "insufficient_data"}

    rng = np.random.default_rng(seed=42)
    diffs = np.empty(BOOTSTRAP_ITERATIONS)
    for i in range(BOOTSTRAP_ITERATIONS):
        fb_sample = rng.choice(feedback, size=len(feedback), replace=True)
        ctrl_sample = rng.choice(control, size=len(control), replace=True)
        diffs[i] = fb_sample.mean() - ctrl_sample.mean()

    lower_pct = (1 - BOOTSTRAP_CI) / 2 * 100
    upper_pct = (1 + BOOTSTRAP_CI) / 2 * 100

    return {
        "status": "complete",
        "iterations": BOOTSTRAP_ITERATIONS,
        "mean_difference": round(float(diffs.mean()), 4),
        "ci_lower": round(float(np.percentile(diffs, lower_pct)), 4),
        "ci_upper": round(float(np.percentile(diffs, upper_pct)), 4),
    }


def run_secondary_trajectory_analysis(completers_df: pd.DataFrame) -> dict:
    """
    SECONDARY / DESCRIPTIVE -- the Session 1 -> 14 change-score comparison
    the old file mistakenly treated as primary. Kept and reported, but
    not confirmatory.
    """
    def improvement(group_df):
        sorted_df = group_df.sort_values("session_number")
        first = sorted_df.iloc[0]["ras"]
        last = sorted_df[sorted_df["session_number"] == PRIMARY_SESSION]["ras"]
        if last.empty:
            return None
        return float(last.iloc[0] - first)

    results = (
        completers_df.groupby(["user_id", "study_group"])
        .apply(improvement)
        .reset_index(name="ras_change")
        .dropna(subset=["ras_change"])
    )

    feedback = results[results["study_group"] == "feedback"]["ras_change"]
    control = results[results["study_group"] == "control"]["ras_change"]

    if len(feedback) < 2 or len(control) < 2:
        return {"status": "insufficient_data"}

    t_stat, p_value = stats.ttest_ind(feedback, control)

    return {
        "status": "complete (secondary/descriptive -- not the confirmatory test)",
        "feedback_n": int(len(feedback)),
        "control_n": int(len(control)),
        "feedback_mean_change": round(float(feedback.mean()), 4),
        "control_mean_change": round(float(control.mean()), 4),
        "t_statistic": round(float(t_stat), 4),
        "p_value": round(float(p_value), 6),
    }


def report_assignment_ratio(df: pd.DataFrame) -> dict:
    """Document the true observed split against the known ~60.94/~39.06 theoretical one."""
    counts = df.drop_duplicates("user_id")["study_group"].value_counts()
    total = counts.sum()
    return {
        "theoretical_feedback_pct": 60.9375,
        "theoretical_control_pct": 39.0625,
        "observed_feedback_pct": round(float(counts.get("feedback", 0) / total * 100), 4) if total else None,
        "observed_control_pct": round(float(counts.get("control", 0) / total * 100), 4) if total else None,
    }


def main():
    df = load_sessions()
    if df.empty:
        print("No session data yet. Nothing to analyze.")
        sys.exit(0)

    completers_df = get_completer_population(df)

    print("\n=== PRIMARY TEST (registered confirmatory analysis) ===")
    for k, v in run_primary_test(completers_df).items():
        print(f"  {k}: {v}")

    print("\n=== SUPPLEMENTARY: bootstrap resampling ===")
    for k, v in run_bootstrap_supplement(completers_df).items():
        print(f"  {k}: {v}")

    print("\n=== SECONDARY / DESCRIPTIVE: Session 1->14 trajectory ===")
    for k, v in run_secondary_trajectory_analysis(completers_df).items():
        print(f"  {k}: {v}")

    print("\n=== Assignment ratio (documented, not silently assumed) ===")
    for k, v in report_assignment_ratio(df).items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()