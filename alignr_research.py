# alignr_research.py
# Day 10 — Simulation + Figure 1 for arXiv preprint
# NOTE: This uses SIMULATED data clearly labeled as such.
# Day 63: replace with real cohort data.
# UCA Skeleton-of-Thought: 3 components designed first, built in order.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
from scipy import stats

style.use('dark_background')
np.random.seed(42)

# ── COMPONENT 1: SIMULATION ──────────────────────────────────────────────
N_FEEDBACK = 60
N_CONTROL  = 40
N_SESSIONS = 10

def simulate_ras_trajectory(n, base, improvement, noise=0.07):
    """Simulate RAS scores across sessions per user."""
    all_sessions = []
    for _ in range(n):
        personal_base = base + np.random.normal(0, 0.04)
        session_scores = []
        for s in range(N_SESSIONS):
            score = personal_base + improvement * s + np.random.normal(0, noise)
            session_scores.append(float(np.clip(score, 0.0, 1.0)))
        all_sessions.append(session_scores)
    return np.array(all_sessions)

# Hypothesis: feedback group improves faster (pre-AI reflection helps)
feedback = simulate_ras_trajectory(N_FEEDBACK, base=0.42, improvement=0.018)
control  = simulate_ras_trajectory(N_CONTROL,  base=0.41, improvement=0.008)

fb_mean = feedback.mean(axis=0)
fb_std  = feedback.std(axis=0)
ct_mean = control.mean(axis=0)
ct_std  = control.std(axis=0)

# ── COMPONENT 2: STATISTICAL COMPARISON ─────────────────────────────────
# compare_groups: final session scores only (session 10)
fb_final = feedback[:, -1]
ct_final = control[:, -1]

t_stat, p_value = stats.ttest_ind(fb_final, ct_final)
pooled_std = ((np.std(fb_final)**2 + np.std(ct_final)**2) / 2) ** 0.5
cohens_d = (np.mean(fb_final) - np.mean(ct_final)) / pooled_std if pooled_std else 0.0

result = {
    "feedback_n":   N_FEEDBACK,
    "feedback_avg": round(float(np.mean(fb_final)), 4),
    "control_n":    N_CONTROL,
    "control_avg":  round(float(np.mean(ct_final)), 4),
    "t_stat":       round(float(t_stat), 4),
    "p_value":      round(float(p_value), 4),
    "cohens_d":     round(float(cohens_d), 4),
    "significant":  bool(p_value < 0.05),
    "data_type":    "SIMULATED — replace with real data Day 63",
}

print("compare_groups() result:")
for k, v in result.items():
    print(f"  {k}: {v}")

# ── COMPONENT 3: FIGURE 1 ────────────────────────────────────────────────
sessions = list(range(1, N_SESSIONS + 1))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('#0a0a0f')

# Subplot 1: RAS trajectory over sessions
ax1 = axes[0]
ax1.set_facecolor('#0a0a0f')
ax1.plot(sessions, fb_mean, color='#00BFFF', linewidth=2.5, marker='o',
         markersize=5, label=f'Feedback (n={N_FEEDBACK})', zorder=3)
ax1.fill_between(sessions, fb_mean-fb_std, fb_mean+fb_std,
                 alpha=0.15, color='#00BFFF')
ax1.plot(sessions, ct_mean, color='#ff6b6b', linewidth=2.5, marker='s',
         markersize=5, label=f'Control (n={N_CONTROL})', zorder=3)
ax1.fill_between(sessions, ct_mean-ct_std, ct_mean+ct_std,
                 alpha=0.15, color='#ff6b6b')
ax1.set_xlabel('Session Number', color='#d0d0e0', fontsize=11)
ax1.set_ylabel('Reasoning Alignment Score (RAS)', color='#d0d0e0', fontsize=11)
ax1.set_title('RAS Trajectory Over 10 Sessions\n(Simulated data — replace Day 63)',
              color='#ffffff', fontsize=12, fontweight='bold')
ax1.legend(facecolor='#1a1a26', edgecolor='#2a2a40',
           labelcolor='#d0d0e0', fontsize=10)
ax1.tick_params(colors='#7a7a9a')
ax1.set_xticks(sessions)
ax1.grid(True, alpha=0.1, color='#2a2a40')

# Subplot 2: Final session comparison bar chart
ax2 = axes[1]
ax2.set_facecolor('#0a0a0f')
groups = ['Feedback', 'Control']
means  = [float(np.mean(fb_final)), float(np.mean(ct_final))]
stds   = [float(np.std(fb_final)),  float(np.std(ct_final))]
colors = ['#00BFFF', '#ff6b6b']
bars = ax2.bar(groups, means, color=colors, alpha=0.8,
               yerr=stds, capsize=6, error_kw={'color': '#7a7a9a'})
ax2.set_ylabel('RAS at Session 10', color='#d0d0e0', fontsize=11)
ax2.set_title(f'Final Session Comparison\np={result["p_value"]:.4f} · d={result["cohens_d"]:.3f}',
              color='#ffffff', fontsize=12, fontweight='bold')
for bar, mean in zip(bars, means):
    ax2.text(bar.get_x() + bar.get_width()/2, mean + 0.01,
             f'{mean:.3f}', ha='center', va='bottom',
             color='#ffffff', fontsize=11, fontweight='bold')
ax2.tick_params(colors='#7a7a9a')
ax2.set_facecolor('#0a0a0f')
ax2.grid(True, alpha=0.1, color='#2a2a40', axis='y')

plt.suptitle('ALIGNR Study — Figure 1 (SIMULATED DATA)',
             color='#7a7a9a', fontsize=10, y=0.02)
plt.tight_layout()
plt.savefig('alignr_figure1_simulated.png', dpi=150,
            bbox_inches='tight', facecolor='#0a0a0f')
print("\n✅ alignr_figure1_simulated.png saved")
print("Open it. Ask: does this look like research output?")
print("This chart is Figure 1 of your arXiv preprint.")
print("Day 63: re-run with real cohort data → publish.")