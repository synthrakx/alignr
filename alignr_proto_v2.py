# alignr_proto_v2.py — JSON storage with PRIVACY VERIFICATION
# After running this: open the JSON file and look at it with your own eyes
import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("alignr_sessions.json")


def word_overlap_ras(t1: str, t2: str) -> float:
    w1, w2 = set(t1.lower().split()), set(t2.lower().split())
    return len(w1 & w2) / len(w1 | w2) if w1 | w2 else 0.0


pre = input("Pre-thinking: ")
pred = input("Prediction: ")
ai = input("AI output: ")
task = input("Task type [technical/decision/research]: ")

ras = word_overlap_ras(pre, ai)
scs = word_overlap_ras(pred, ai)

record = {
    "date": datetime.now().isoformat(),
    "task": task,
    "ras": round(ras, 4),
    "scs": round(scs, 4),
    # pre_thinking:  NOT here by design
    # ai_output:     NOT here by design
    # prediction:    NOT here by design
}

sessions = json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else []
sessions.append(record)
DATA_FILE.write_text(json.dumps(sessions, indent=2))

print(f"\nRAS: {ras:.1%} | SCS: {scs:.1%}")
print("\nNOW: open alignr_sessions.json in your editor")
print("VERIFY with your own eyes: no pre_thinking key anywhere in the file")
print("This is ALIGNR's privacy claim — provable, not just stated")
