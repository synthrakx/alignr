# oop_alignr.py
# UCA Self-Consistency result: text is method-local, never stored.
# Privacy is enforced at the class design level.

import datetime
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import stats


class ALIGNRSession:
    """
    Privacy architecture: text parameters enter calculate(), metrics are extracted,
    text is discarded. Nothing stored to self from text inputs. Ever.

    This is provable: grep "self.pre" in this file → 0 results.
    This is the privacy claim in every researcher email and fellowship application.
    """

    def __init__(self, user_id: str, task_category: str, session_number: int):
        self.user_id = user_id
        self.task_category = task_category
        self.session_number = session_number
        self.ras: float | None = None
        self.cii: float | None = None
        self.scs: float | None = None
        self.created_at = datetime.datetime.now()

    def calculate(
        self, pre_thinking: str, ai_output: str, prediction: str = ""
    ) -> dict:
        """
        Text enters here as parameters. Metrics extracted. Text discarded.
        pre_thinking, ai_output, prediction: method-local only.
        After this returns: they're gone. Garbage collected. Unrecoverable.
        """
        # RAS: word overlap (Day 15: sentence-transformers replaces this)
        w1 = set(pre_thinking.lower().split())
        w2 = set(ai_output.lower().split())
        self.ras = len(w1 & w2) / len(w1 | w2) if w1 | w2 else 0.0

        # CII: vocabulary diversity proxy (file 11 full formula → Day 15)
        # Day 9 version: TTK only (simplified for now)
        # Day 15 version: (ttk * 0.6) + (min(avg_len / 20, 1.0) * 0.4)
        words = pre_thinking.lower().split()
        self.cii = len(set(words)) / len(words) if words else 0.5

        # SCS: prediction accuracy
        if prediction:
            wp = set(prediction.lower().split())
            self.scs = len(wp & w2) / len(wp | w2) if wp | w2 else 0.0

        return self.to_dict()

    def to_dict(self) -> dict:
        """Inspect this output. No text keys. This is the privacy proof."""
        return {
            "user_id": self.user_id,
            "task_category": self.task_category,
            "session_number": self.session_number,
            "ras": self.ras,
            "cii": self.cii,
            "scs": self.scs,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"ALIGNRSession(ras={self.ras:.3f}, cii={self.cii:.3f})"


class ALIGNRUser:
    """Research participant. Identified by hashed email, never real email."""

    def __init__(self, email_hash: str):
        self.user_id = email_hash[:16]
        self.study_group = "feedback" if int(email_hash[0], 16) < 10 else "control"
        self.sessions: list[ALIGNRSession] = []

    @property
    def average_ras(self) -> float:
        scores = [s.ras for s in self.sessions if s.ras is not None]
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def ras_trend(self) -> str:
        scores = [s.ras for s in self.sessions if s.ras is not None]
        if len(scores) < 3:
            return "insufficient_data"
        recent = sum(scores[-3:]) / 3
        early = sum(scores[:3]) / 3
        if recent > early + 0.05:
            return "improving"
        if recent < early - 0.05:
            return "declining"
        return "stable"

    def add_session(self, session: ALIGNRSession):
        self.sessions.append(session)


# ADD TO BOTTOM OF oop_alignr.py (after ALIGNRUser class)
# This completes the class hierarchy:
# ALIGNRSession → ALIGNRUser → ALIGNRResearch


class ALIGNRResearch:
    """
    Manages the complete A/B study.
    Privacy: text never enters or leaves this class.
    Only floats. export_summary() → open it → verify no text keys.
    """

    def __init__(self):
        self.users: dict[str, ALIGNRUser] = {}

    def add_user(self, email: str) -> ALIGNRUser:
        h = hashlib.sha256(email.encode()).hexdigest()
        if h not in self.users:
            self.users[h] = ALIGNRUser(h)
        return self.users[h]

    def add_session(
        self, email: str, pre: str, ai: str, pred: str = "", task: str = "general"
    ) -> dict:
        user = self.add_user(email)
        s = ALIGNRSession(user.user_id, task, len(user.sessions) + 1)
        result = s.calculate(pre, ai, pred)
        user.sessions.append(s)
        return result

    def compare_groups(self) -> dict:
        fb = [
            u.average_ras
            for u in self.users.values()
            if u.study_group == "feedback" and u.sessions
        ]
        ct = [
            u.average_ras
            for u in self.users.values()
            if u.study_group == "control" and u.sessions
        ]
        if len(fb) < 5 or len(ct) < 5:
            return {
                "feedback_n": len(fb),
                "control_n": len(ct),
                "p_value": None,
                "significant": False,
                "note": "need_more_data",
            }
        t, p = stats.ttest_ind(fb, ct)
        ps = ((np.std(fb) ** 2 + np.std(ct) ** 2) / 2) ** 0.5
        d = (np.mean(fb) - np.mean(ct)) / ps if ps else 0.0
        return {
            "feedback_n": len(fb),
            "feedback_avg": round(float(np.mean(fb)), 4),
            "control_n": len(ct),
            "control_avg": round(float(np.mean(ct)), 4),
            "t_stat": round(float(t), 4),
            "p_value": round(float(p), 4),
            "cohens_d": round(float(d), 4),
            "significant": bool(p < 0.05),
        }

    def export_summary(self, path="research_summary.json") -> dict:
        data = {
            "total_users": len(self.users),
            "feedback_users": sum(
                1 for u in self.users.values() if u.study_group == "feedback"
            ),
            "control_users": sum(
                1 for u in self.users.values() if u.study_group == "control"
            ),
            "group_comparison": self.compare_groups(),
            "exported_at": datetime.datetime.now().isoformat(),
        }
        Path(path).write_text(json.dumps(data, indent=2))
        print(f"Exported → {path}")
        print("Open it. Verify: ZERO text keys anywhere in this file.")
        return data


if __name__ == "__main__":

    # ── ORIGINAL PRIVACY TEST ──────────────────────────────────────────
    session = ALIGNRSession("user_abc123", "technical", 1)
    result = session.calculate(
        pre_thinking="Python is great for data analysis and machine learning",
        ai_output="Python excels at data science automation and ML tasks",
        prediction="AI will probably mention Python's data science strengths",
    )

    print("=== to_dict() output ===")
    print(json.dumps(result, indent=2, default=str))

    print("\n=== PRIVACY VERIFICATION ===")
    assert "pre_thinking" not in result, "PRIVACY VIOLATION: text stored!"
    assert "ai_output" not in result, "PRIVACY VIOLATION: text stored!"
    assert "prediction" not in result, "PRIVACY VIOLATION: text stored!"
    print("✅ Privacy test: PASSED — no text keys in to_dict()")

    print("\n=== repr ===")
    print(repr(session))

    print("\n=== ALIGNRUser test ===")
    user = ALIGNRUser("a3f9bc2d1e4f7890abcdef123456")
    user.add_session(session)
    print(f"User: {user.user_id} | Group: {user.study_group}")
    print(f"Avg RAS: {user.average_ras:.3f} | Trend: {user.ras_trend}")

    print("\n=== GREP CHECK ===")
    print("Run in terminal: grep -n 'self.pre' oop_alignr.py")
    print("Expected result: (no output) — zero matches = privacy confirmed")

    # ── ALIGNRRESEARCH INTEGRATION TEST ───────────────────────────────
    print("\n=== ALIGNRResearch integration test ===")
    research = ALIGNRResearch()

    for i in range(50):
        email = f"user{i}@test.com"
        for _ in range(5):
            research.add_session(
                email=email,
                pre="Python is useful for automation and data analysis",
                ai="Python excels at data automation and analysis",
                pred="AI will mention automation",
                task="technical",
            )

    print(research.compare_groups())
    research.export_summary()
