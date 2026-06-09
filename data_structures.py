# data_structures.py
# CRITICAL INSIGHT: this dict IS the SQLite row you'll design on Day 16
# Understanding the structure now makes database design obvious later

session = {
    "user_id": "sha256_hash_16chars",
    "date": "2026-06-08",
    "task_category": "technical",
    "ras": 0.67,
    "cii": 0.52,
    "scs": 0.44,
    # pre_thinking: NEVER HERE — privacy by design
    # ai_output:    NEVER HERE — privacy by design
}
print(session)

# Grouping by task (dashboard analytics logic)
by_task = {}
for s in [session]:
    by_task.setdefault(s["task_category"], []).append(s["ras"])
print("By task:", by_task)