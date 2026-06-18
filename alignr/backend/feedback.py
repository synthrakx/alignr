"""
alignr/backend/feedback.py
ALIGNR Narrative from scores only. Never touches user text.
Uses Ollama qwen2.5-coder:7b via HTTP — local only.
Day 17 — June 17, 2026
"""
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """Generate concise cognitive feedback from numerical session metrics only.

INPUT format: Session N | Task: <type> | RAS: <0-1> | CII: <0-1> | SCS: <0-1 or N/A>
OUTPUT: Exactly 2 sentences. Research-grounded. Specific to these numbers.
Never generic. Never say great job. Reference the actual metric values.

RAS > 0.7: pre-AI thinking closely matched output
RAS < 0.4: AI genuinely surprised user — learning likely occurred
CII > 0.6: vocabulary diversity maintained
CII < 0.4: writing may be converging toward AI patterns
SCS > 0.7: user predicted AI output accurately
SCS < 0.3: AI frequently surprises this user

CRITICAL: You only receive numbers. Never imagine or reference user text.
Respond with only the 2 sentences. No preamble. No explanation."""


def generate_feedback(ras: float, cii: float, scs,
                      session_num: int, task_type: str) -> str:
    scs_str = f"{scs:.3f}" if scs is not None else "N/A"
    prompt = (f"Session {session_num} | Task: {task_type} | "
              f"RAS: {ras:.3f} | CII: {cii:.3f} | "
              f"SCS: {scs_str}")
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 300},
        }, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except Exception as e:
        print(f"[feedback] Ollama unavailable: {e}")
        return ""


if __name__ == "__main__":
    print("=" * 50)
    print("  feedback.py — VERIFICATION SUITE")
    print("=" * 50)

    cases = [
        {"ras": 0.72, "cii": 0.54, "scs": 0.41,
         "session_num": 3,  "task_type": "technical"},
        {"ras": 0.31, "cii": 0.68, "scs": None,
         "session_num": 1,  "task_type": "creative"},
        {"ras": 0.88, "cii": 0.29, "scs": 0.91,
         "session_num": 10, "task_type": "analytical"},
    ]

    all_pass = True
    for i, c in enumerate(cases, 1):
        print(f"\nCase {i}: RAS={c['ras']} CII={c['cii']} "
              f"SCS={c['scs']} task={c['task_type']}")
        narrative = generate_feedback(**c)

        for banned in ("pre_thinking", "ai_output", "prediction"):
            if banned in narrative:
                print(f"  PRIVACY VIOLATION: '{banned}' found")
                all_pass = False

        if narrative and not (20 < len(narrative) < 600):
            print(f"  Length out of range: {len(narrative)}")
            all_pass = False

        if narrative:
            print(f"  T{i} PASS: {narrative[:120]}...")
        else:
            print(f"  T{i} WARNING: Empty response (Ollama unavailable)")

    print()
    if all_pass:
        print("ALL 3 CASES VERIFIED — scores only, no user text")
    else:
        print("FAILURES detected — check output above")