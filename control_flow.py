# control_flow.py — loops ARE ALIGNR's data pipeline
# Understanding this now means the Day 16 FastAPI backend clicks immediately

sessions = [
    {"day": 1, "ras": 0.34, "cii": 0.45, "task": "technical"},
    {"day": 3, "ras": 0.41, "cii": 0.43, "task": "decision"},
    {"day": 5, "ras": 0.52, "cii": 0.48, "task": "research"},
]

# For loop with trend arrow (used in ALIGNR dashboard)
for i, s in enumerate(sessions):
    trend = "↑" if i > 0 and s["ras"] > sessions[i-1]["ras"] else "→"
    print(f"Day {s['day']:2d}: RAS={s['ras']:.1%} {trend}")

# Average (used everywhere)
avg = sum(s["ras"] for s in sessions) / len(sessions)
print(f"Average RAS: {avg:.1%}")