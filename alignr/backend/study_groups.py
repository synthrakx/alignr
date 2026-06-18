"""
alignr/backend/study_groups.py
Wraps database.assign_group() — single source of truth for A/B assignment.
Day 17 — June 17, 2026
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import assign_group


def is_feedback_group(user_id: str) -> bool:
    return assign_group(user_id) == "feedback"


def get_group_label(user_id: str) -> str:
    return "F" if is_feedback_group(user_id) else "C"


def simulate_cohort(n: int = 100) -> dict:
    uids = [hashlib.sha256(f"u{i}@alignr.me".encode()).hexdigest()[:16]
            for i in range(n)]
    fb = sum(1 for u in uids if is_feedback_group(u))
    return {"n": n, "feedback": fb, "control": n - fb, "pct": fb / n * 100}


if __name__ == "__main__":
    # T1: Deterministic — 10 calls, same result
    uid = hashlib.sha256(b"test@alignr.me").hexdigest()[:16]
    results = [assign_group(uid) for _ in range(10)]
    assert len(set(results)) == 1
    print(f"✓ T1: 10 calls → always '{results[0]}'")

    # T2: Distribution check
    stats = simulate_cohort(100)
    assert 45 <= stats["pct"] <= 75
    print(f"✓ T2: {stats['feedback']} feedback / {stats['control']} control "
          f"({stats['pct']:.1f}%)")

    # T3: Visual 10-user sample
    print("\n  10-user sample:")
    for i in range(10):
        u = hashlib.sha256(f"user{i}@alignr.me".encode()).hexdigest()[:16]
        print(f"  User {i:02d}: [{get_group_label(u)}] {assign_group(u)}")

    print("\n✅ ALL 3 TESTS PASSED")