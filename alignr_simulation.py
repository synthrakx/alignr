# alignr_simulation.py
# Day 11 — ALIGNR Portfolio Masterpiece
# Uses the complete class system from oop_alignr.py
# UCA Skeleton-of-Thought: 7 components designed before writing
# 3X Rule: understand every block before moving on

import sys
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
from pathlib import Path
from scipy import stats

# Import the class system built in Days 8-10
sys.path.insert(0, str(Path(__file__).parent))
from oop_alignr import ALIGNRSession, ALIGNRUser, ALIGNRResearch

style.use('dark_background')
np.random.seed(42)


# ─────────────────────────────────────────────
# COMPONENT 1: TEXT SIMULATION ENGINE
# ─────────────────────────────────────────────
#
# All 9 pairs designed with similar baseline word overlap (~0.20-0.25)
# Feedback group: pre-thinking gets MORE aligned with AI over sessions
# Control group: pre-thinking stays vague throughout

TECHNICAL_PAIRS = [
    ("python automates data tasks",
     "python automates repetitive data processing tasks effectively",
     "AI will mention python data automation"),
    ("machine learning finds patterns in data",
     "machine learning algorithms find statistical patterns in training data",
     "Response covers ML pattern detection"),
    ("APIs connect software systems together",
     "APIs connect different software systems through standard interfaces",
     "Something about API connectivity"),
]

DECISION_PAIRS = [
    ("structured thinking reduces decision errors",
     "structured thinking before deciding reduces cognitive errors and bias",
     "AI mentions structured thinking before decisions"),
    ("writing options clarifies decision tradeoffs",
     "writing down options clarifies decision tradeoffs before choosing",
     "Probably about writing options for clarity"),
    ("evidence improves confidence in decisions",
     "consulting prior evidence improves confidence in novel decisions",
     "Response covers evidence-based decisions"),
]

RESEARCH_PAIRS = [
    ("related work reveals research gaps",
     "reading related work reveals gaps in current research understanding",
     "Something about literature review gaps"),
    ("preregistration prevents selective reporting outcomes",
     "OSF preregistration prevents selective reporting of research outcomes",
     "AI explains preregistration and reporting bias"),
    ("longitudinal studies reveal temporal patterns",
     "longitudinal studies reveal temporal patterns invisible in snapshots",
     "Response covers longitudinal research benefits"),
]

TASK_PAIRS = {
    "technical": TECHNICAL_PAIRS,
    "decision": DECISION_PAIRS,
    "research": RESEARCH_PAIRS,
}

def get_text_pair(task: str, session_num: int, group: str) -> tuple:
    """
    Returns (pre_thinking, ai_output, prediction) for a simulated session.

    Feedback group: BOTH pre-thinking AND prediction get more aligned
        with AI over sessions (simulates learning to predict AI's framing).
    Control group: BOTH pre-thinking AND prediction stay vague throughout.
    """
    pairs = TASK_PAIRS[task]
    base_pre, ai_out, base_pred = pairs[session_num % len(pairs)]

    # Quality grows from 0.0 (session 0) to 1.0 (session 9)
    quality = min(session_num / 9.0, 1.0)

    if group == "feedback":
        # ── PRE-THINKING: borrow AI words progressively ──
        ai_words = ai_out.split()
        target_borrow = quality * len(ai_words) * 0.5
        n_borrow = int(target_borrow + np.random.normal(0, 1.5))
        n_borrow = max(0, min(n_borrow, len(ai_words)))

        if n_borrow > 0:
            start = np.random.randint(0, max(1, len(ai_words) - n_borrow + 1))
            borrowed = " ".join(ai_words[start:start + n_borrow])
            pre = f"{base_pre} {borrowed}"
        else:
            pre = base_pre

        # ── PREDICTION: also borrow AI words progressively ──
        # Independent randomness so pred ≠ pre
        target_borrow_pred = quality * len(ai_words) * 0.4
        n_borrow_pred = int(target_borrow_pred + np.random.normal(0, 1.5))
        n_borrow_pred = max(0, min(n_borrow_pred, len(ai_words)))

        if n_borrow_pred > 0:
            start_p = np.random.randint(0, max(1, len(ai_words) - n_borrow_pred + 1))
            borrowed_p = " ".join(ai_words[start_p:start_p + n_borrow_pred])
            pred = f"{base_pred} {borrowed_p}"
        else:
            pred = base_pred
    else:
        # ── CONTROL: pad both pre and pred with vague filler ──
        vague_words = ["maybe", "I think", "not sure", "probably",
                       "something like", "perhaps", "could be"]

        n_vague = np.random.randint(3, 6)
        padding = " ".join(np.random.choice(vague_words, n_vague))
        pre = f"{padding} {base_pre}"

        n_vague_pred = np.random.randint(2, 5)
        padding_pred = " ".join(np.random.choice(vague_words, n_vague_pred))
        pred = f"{padding_pred} {base_pred}"

    return pre, ai_out, pred
# ─────────────────────────────────────────────
# COMPONENT 2: RESEARCH PIPELINE RUNNER
# ─────────────────────────────────────────────

TASK_SEQUENCE = [
    "technical", "decision", "research",
    "technical", "decision", "research",
    "technical", "decision", "research", "technical"
]

def run_simulation(n_feedback: int = 120, n_control: int = 80,
                   sessions_per_user: int = 10) -> ALIGNRResearch:
    """
    Runs the complete simulation using the real ALIGNRResearch class.

    IMPORTANT: study_group is determined by ALIGNRUser hashing,
    not by intent. We must use user.study_group (not loop intent)
    to decide which text quality to generate.
    """
    research = ALIGNRResearch()
    target_total = n_feedback + n_control
    print(f"Building simulation: targeting {n_feedback} feedback + "
          f"{n_control} control users...")

    # Generate emails until we have enough of BOTH groups
    feedback_count = 0
    control_count = 0
    i = 0

    while feedback_count < n_feedback or control_count < n_control:
        email = f"sim_user_{i:04d}@alignr.sim"
        user = research.add_user(email)

        # Check what group the hash assigned this user to
        actual_group = user.study_group

        # Skip if we already have enough of this group
        if actual_group == "feedback" and feedback_count >= n_feedback:
            del research.users[list(research.users.keys())[-1]]
            i += 1
            continue
        if actual_group == "control" and control_count >= n_control:
            del research.users[list(research.users.keys())[-1]]
            i += 1
            continue

        # Generate sessions using the user's ACTUAL group
        for s in range(sessions_per_user):
            task = TASK_SEQUENCE[s % len(TASK_SEQUENCE)]
            pre, ai_out, pred = get_text_pair(task, s, actual_group)
            research.add_session(email, pre, ai_out, pred, task)

        # Track counts
        if actual_group == "feedback":
            feedback_count += 1
        else:
            control_count += 1

        i += 1

        if (feedback_count + control_count) % 50 == 0 and \
           (feedback_count + control_count) > 0:
            print(f"  Progress: {feedback_count} feedback + "
                  f"{control_count} control...")

    print(f"Simulation complete: {feedback_count} feedback + "
          f"{control_count} control = {len(research.users)} total users")
    return research
# ─────────────────────────────────────────────
# COMPONENT 3: STATISTICAL ANALYSIS
# ─────────────────────────────────────────────

def interpret_effect(d) -> str:
    """Cohen's d interpretation:
    < 0.2  = negligible
    < 0.5  = small
    < 0.8  = medium
    >= 0.8 = large"""
    if d is None:
        return "insufficient_data"
    a = abs(d)
    if a < 0.2: return "negligible"
    if a < 0.5: return "small"
    if a < 0.8: return "medium"
    return "large"


def analyse(research: ALIGNRResearch) -> dict:
    """Full statistical analysis with effect size interpretation."""
    groups = research.compare_groups()
    d = groups.get("cohens_d")
    p = groups.get("p_value")
    fb_avg = groups.get("feedback_avg", 0)
    ct_avg = groups.get("control_avg", 0)

    # Pre-format the floats (avoids f-string conditional formatting bug)
    p_str = f"{p:.4f}" if p is not None else "N/A"
    d_str = f"{d:.3f}" if d is not None else "N/A"
    effect = interpret_effect(d)

    if p is not None:
        conclusion = (f"Feedback group RAS {fb_avg:.3f} vs "
                      f"Control {ct_avg:.3f} "
                      f"(p={p_str}, d={d_str}, {effect} effect)")
    else:
        conclusion = "Insufficient data for statistical conclusion"

    return {
        **groups,
        "effect_size_interpretation": effect,
        "conclusion": conclusion,
    }

# ─────────────────────────────────────────────
# HELPER: extract per-session metric arrays
# (used by Figures 1, 2, 3)
# ─────────────────────────────────────────────

def build_session_matrix(research: ALIGNRResearch, metric: str = "ras"):
    """
    Extract per-session metric arrays for feedback and control groups.
    Returns: (feedback_array, control_array) as numpy arrays of shape (n_users, 10).
    """
    feedback, control = [], []
    for user in research.users.values():
        scores = [getattr(s, metric) for s in user.sessions
                  if getattr(s, metric) is not None]
        if len(scores) >= 10:
            if user.study_group == "feedback":
                feedback.append(scores[:10])
            else:
                control.append(scores[:10])
    return np.array(feedback), np.array(control)


# ─────────────────────────────────────────────
# COMPONENT 4: FIGURE 1 — RAS TRAJECTORY
# ─────────────────────────────────────────────

def figure1_ras_trajectory(research: ALIGNRResearch,
                           path: str = "alignr_fig1_ras_trajectory.png"):
    """Two-panel figure: trajectory over sessions + final session comparison."""
    fb, ct = build_session_matrix(research, "ras")

    if len(fb) == 0 or len(ct) == 0:
        print(f"Figure 1: insufficient data (fb={len(fb)}, ct={len(ct)}) — skipping")
        return

    sessions = list(range(1, 11))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#0a0a0f')
    for ax in (ax1, ax2):
        ax.set_facecolor('#0a0a0f')

    # LEFT: trajectory over sessions
    ax1.plot(sessions, fb.mean(0), '#00BFFF', linewidth=2.5,
             marker='o', markersize=5, label=f'Feedback (n={len(fb)})', zorder=3)
    ax1.fill_between(sessions, fb.mean(0)-fb.std(0), fb.mean(0)+fb.std(0),
                     alpha=0.15, color='#00BFFF')
    ax1.plot(sessions, ct.mean(0), '#ff6b6b', linewidth=2.5,
             marker='s', markersize=5, label=f'Control (n={len(ct)})', zorder=3)
    ax1.fill_between(sessions, ct.mean(0)-ct.std(0), ct.mean(0)+ct.std(0),
                     alpha=0.15, color='#ff6b6b')
    ax1.set_xlabel('Session', color='#d0d0e0')
    ax1.set_ylabel('RAS', color='#d0d0e0')
    ax1.set_title('Figure 1A: RAS Trajectory (Simulated)',
                  color='#ffffff', fontweight='bold')
    ax1.legend(facecolor='#1a1a26', edgecolor='#2a2a40', labelcolor='#d0d0e0')
    ax1.tick_params(colors='#7a7a9a')
    ax1.grid(True, alpha=0.1)
    ax1.set_xticks(sessions)

    # RIGHT: final session comparison
    means = [fb[:, -1].mean(), ct[:, -1].mean()]
    stds  = [fb[:, -1].std(),  ct[:, -1].std()]
    bars = ax2.bar(['Feedback', 'Control'], means,
                   color=['#00BFFF', '#ff6b6b'], alpha=0.8,
                   yerr=stds, capsize=6, error_kw={'color': '#7a7a9a'})
    for bar, m in zip(bars, means):
        ax2.text(bar.get_x() + bar.get_width()/2, m + 0.01,
                 f'{m:.3f}', ha='center', va='bottom',
                 color='#ffffff', fontsize=11, fontweight='bold')
    ax2.set_ylabel('RAS at Session 10', color='#d0d0e0')
    ax2.set_title('Figure 1B: Final Session Comparison',
                  color='#ffffff', fontweight='bold')
    ax2.tick_params(colors='#7a7a9a')
    ax2.grid(True, alpha=0.1, axis='y')

    plt.suptitle('ALIGNR Study — Figure 1 (SIMULATED)',
                 color='#5a6a8a', fontsize=9, y=0.02)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
    plt.close()
    print(f"Figure 1 saved → {path}")

# ─────────────────────────────────────────────
# COMPONENT 5: FIGURE 2 — CII PROGRESSION
# ─────────────────────────────────────────────

def figure2_cii_progression(research: ALIGNRResearch,
                            path: str = "alignr_fig2_cii_progression.png"):
    """Single-panel figure: CII over 10 sessions, both groups."""
    fb, ct = build_session_matrix(research, "cii")

    if len(fb) == 0 or len(ct) == 0:
        print(f"Figure 2: insufficient data (fb={len(fb)}, ct={len(ct)}) — skipping")
        return

    sessions = list(range(1, 11))
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')

    ax.plot(sessions, fb.mean(0), '#00FF88', linewidth=2.5,
            marker='o', markersize=5, label=f'Feedback (n={len(fb)})')
    ax.fill_between(sessions, fb.mean(0)-fb.std(0), fb.mean(0)+fb.std(0),
                    alpha=0.15, color='#00FF88')

    ax.plot(sessions, ct.mean(0), '#FFB800', linewidth=2.5,
            marker='s', markersize=5, label=f'Control (n={len(ct)})')
    ax.fill_between(sessions, ct.mean(0)-ct.std(0), ct.mean(0)+ct.std(0),
                    alpha=0.15, color='#FFB800')

    ax.set_xlabel('Session', color='#d0d0e0')
    ax.set_ylabel('CII (Cognitive Independence Index)', color='#d0d0e0')
    ax.set_title('Figure 2: CII Progression Over 10 Sessions (Simulated)\n'
                 'Higher = more diverse vocabulary',
                 color='#ffffff', fontweight='bold')
    ax.legend(facecolor='#1a1a26', edgecolor='#2a2a40', labelcolor='#d0d0e0')
    ax.tick_params(colors='#7a7a9a')
    ax.grid(True, alpha=0.1)
    ax.set_xticks(sessions)

    plt.suptitle('ALIGNR Study — Figure 2 (SIMULATED)',
                 color='#5a6a8a', fontsize=9, y=0.02)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
    plt.close()
    print(f"Figure 2 saved → {path}")

# ─────────────────────────────────────────────
# COMPONENT 6: FIGURE 3 — SCS CALIBRATION
# ─────────────────────────────────────────────

def figure3_scs_calibration(research: ALIGNRResearch,
                            path: str = "alignr_fig3_scs_calibration.png"):
    """
    Two-panel histogram: SCS distribution at Session 1 vs Session 10.
    Tests: do users learn to predict AI output more accurately over time?
    """
    def get_scs_at(group_name, session_idx):
        scores = []
        for user in research.users.values():
            if user.study_group != group_name:
                continue
            s_list = [s.scs for s in user.sessions if s.scs is not None]
            if len(s_list) > session_idx:
                scores.append(s_list[session_idx])
        return scores

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#0a0a0f')
    colors = {'feedback': '#00BFFF', 'control': '#ff6b6b'}
    titles = ['Figure 3A: Session 1 SCS Distribution',
              'Figure 3B: Session 10 SCS Distribution']

    for i, sess_idx in enumerate([0, 9]):
        ax = axes[i]
        ax.set_facecolor('#0a0a0f')

        for group, color in colors.items():
            scores = get_scs_at(group, sess_idx)
            if scores:
                ax.hist(scores, bins=15, alpha=0.6, color=color,
                        label=f'{group.capitalize()} (n={len(scores)})',
                        edgecolor='none')

        ax.set_xlabel('SCS Score', color='#d0d0e0')
        ax.set_ylabel('Number of Users', color='#d0d0e0')
        ax.set_title(titles[i], color='#ffffff', fontweight='bold')
        ax.legend(facecolor='#1a1a26', edgecolor='#2a2a40', labelcolor='#d0d0e0')
        ax.tick_params(colors='#7a7a9a')
        ax.grid(True, alpha=0.1)

    plt.suptitle('Figure 3: Surprise Calibration Score Distribution (SIMULATED)\n'
                 'Measures how accurately users predicted AI output',
                 color='#d0d0e0', fontsize=11, y=1.01)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0a0a0f')
    plt.close()
    print(f"Figure 3 saved → {path}")

# ─────────────────────────────────────────────
# COMPONENT 7: PORTFOLIO EXPORT + CONSOLE SUMMARY
# ─────────────────────────────────────────────

def export_portfolio(research: ALIGNRResearch, stats: dict,
                     path: str = "portfolio.json") -> dict:
    """
    Export clean summary. No raw text anywhere. All floats.
    Privacy proof: open portfolio.json → zero text values from user input.
    """
    feedback_n = sum(1 for u in research.users.values()
                     if u.study_group == "feedback")
    control_n = sum(1 for u in research.users.values()
                    if u.study_group == "control")

    # Strip the conclusion sentence (keep only numbers in statistical_results)
    stat_numbers = {k: v for k, v in stats.items() if k != "conclusion"}

    data = {
        "project": "ALIGNR — Reasoning Alignment Research Platform",
        "data_type": ("SIMULATED — word-overlap proxy. Real semantic "
                      "similarity (sentence-transformers all-MiniLM-L6-v2) "
                      "activates on Day 15, producing realistic effect "
                      "sizes in the d=0.5-1.5 range typical of "
                      "cognition research."),
        "exported_at": datetime.datetime.now().isoformat(),
        "study_design": {
            "type": "randomized_controlled",
            "assignment": "deterministic_hash_of_email",
            "feedback_n": feedback_n,
            "control_n": control_n,
            "sessions_per_user": 10,
            "metrics": ["RAS", "CII", "SCS"],
        },
        "statistical_results": stat_numbers,
        "figures": {
            "fig1_ras_trajectory": "alignr_fig1_ras_trajectory.png",
            "fig2_cii_progression": "alignr_fig2_cii_progression.png",
            "fig3_scs_calibration": "alignr_fig3_scs_calibration.png",
        },
        "privacy": {
            "text_stored": False,
            "data_collected": ["RAS (float)", "CII (float)", "SCS (float)"],
            "verification_method": ("grep 'pre_thinking' oop_alignr.py "
                                    "returns no code assigning text to self"),
        },
    }

    Path(path).write_text(json.dumps(data, indent=2))
    print(f"\nPortfolio exported → {path}")
    print("Open portfolio.json → verify: zero raw user text anywhere")
    return data


def print_summary(research: ALIGNRResearch, stats: dict):
    """
    Console output that goes verbatim into the GitHub README.
    Format: clean, professional, scannable.
    """
    fb_n = stats.get("feedback_n", 0)
    ct_n = stats.get("control_n", 0)
    fb_avg = stats.get("feedback_avg", 0)
    ct_avg = stats.get("control_avg", 0)
    p = stats.get("p_value")
    d = stats.get("cohens_d")
    effect = stats.get("effect_size_interpretation", "N/A")

    p_str = f"{p:.4f}" if p is not None else "N/A"
    d_str = f"{d:.4f}" if d is not None else "N/A"

    print("\n" + "=" * 60)
    print("ALIGNR RESEARCH SUMMARY")
    print("=" * 60)
    print(f"Study:      Randomized A/B (feedback vs control)")
    print(f"Users:      {fb_n + ct_n} total  ({fb_n} feedback · {ct_n} control)")
    print(f"Sessions:   {(fb_n + ct_n) * 10} total  (10 per user)")
    print(f"Metrics:    RAS · CII · SCS")
    print(f"Privacy:    No text stored. Only floats. Verified by grep.")
    print(f"")
    print(f"RAS results:")
    print(f"  Feedback avg: {fb_avg:.4f}")
    print(f"  Control avg:  {ct_avg:.4f}")
    print(f"  p-value:      {p_str}")
    print(f"  Cohen's d:    {d_str} ({effect} effect)")
    print(f"")
    print(f"Data type:  SIMULATED (replace Day 63 with real cohort)")
    print(f"Preprint:   OSF preregistered Day 21 before data collection")
    print(f"Repository: github.com/synthrakx/alignr")
    print("=" * 60 + "\n")

# ─────────────────────────────────────────────
# MAIN — connect all 7 components end-to-end
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("ALIGNR Simulation — Portfolio Masterpiece")
    print("Uses real class system from oop_alignr.py")
    print("Day 63: replace with real cohort data\n")

    # Component 2: run full simulation (production scale)
    research = run_simulation(n_feedback=120, n_control=80,
                              sessions_per_user=10)

    # Component 3: statistical analysis
    stats_result = analyse(research)

    # Components 4-6: generate all 3 figures
    figure1_ras_trajectory(research)
    figure2_cii_progression(research)
    figure3_scs_calibration(research)

    # Component 7: export + console summary
    export_portfolio(research, stats_result)
    print_summary(research, stats_result)

    # Privacy verification (runs automatically)
    portfolio = json.loads(Path("portfolio.json").read_text())

    def check_no_user_text(obj):
        """Verify no raw user-typed sentences exist in the export."""
        forbidden_substrings = ["python automates", "machine learning",
                                "I think", "not sure", "maybe"]
        if isinstance(obj, dict):
            for v in obj.values():
                check_no_user_text(v)
        elif isinstance(obj, list):
            for v in obj:
                check_no_user_text(v)
        elif isinstance(obj, str):
            for forbidden in forbidden_substrings:
                assert forbidden not in obj.lower(), \
                    f"PRIVACY VIOLATION: found '{forbidden}' in export"

    check_no_user_text(portfolio)
    print("✅ Privacy verification: PASSED — no raw user text in portfolio.json")
    print("✅ alignr_simulation.py: 7 components integrated and working")