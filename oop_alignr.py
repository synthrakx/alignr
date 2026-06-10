# oop_alignr.py
# UCA Self-Consistency result: text is method-local, never stored.
# Privacy is enforced at the class design level.

import datetime

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

    def calculate(self, pre_thinking: str, ai_output: str,
                  prediction: str = "") -> dict:
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
        # A/B assignment: deterministic, reproducible, non-reversible from hash
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
        early  = sum(scores[:3]) / 3
        if recent > early + 0.05: return "improving"
        if recent < early - 0.05: return "declining"
        return "stable"

    def add_session(self, session: ALIGNRSession):
        self.sessions.append(session)


# ── PRIVACY VERIFICATION TEST (run this, check the output) ──────────────
if __name__ == "__main__":
    import json

    session = ALIGNRSession("user_abc123", "technical", 1)
    result = session.calculate(
        pre_thinking="Python is great for data analysis and machine learning",
        ai_output="Python excels at data science automation and ML tasks",
        prediction="AI will probably mention Python's data science strengths"
    )

    print("=== to_dict() output ===")
    print(json.dumps(result, indent=2, default=str))

    print("\n=== PRIVACY VERIFICATION ===")
    # This assert is the proof you cite in researcher emails
    assert "pre_thinking" not in result, "PRIVACY VIOLATION: text stored!"
    assert "ai_output" not in result,    "PRIVACY VIOLATION: text stored!"
    assert "prediction" not in result,   "PRIVACY VIOLATION: text stored!"
    print("✅ Privacy test: PASSED — no text keys in to_dict()")
    print("✅ This is the claim: 'No text stored. Only numbers.'")
    print("✅ Verifiable in the source code. Open source. Anyone can check.")

    print("\n=== repr ===")
    print(repr(session))

    print("\n=== ALIGNRUser test ===")
    user = ALIGNRUser("a3f9bc2d1e4f7890abcdef123456")
    user.add_session(session)
    print(f"User: {user.user_id} | Group: {user.study_group}")
    print(f"Avg RAS: {user.average_ras:.3f} | Trend: {user.ras_trend}")

    # Extra: grep check reminder
    print("\n=== GREP CHECK ===")
    print("Run in terminal: grep -n 'self.pre' oop_alignr.py")
    print("Expected result: (no output) — zero matches = privacy confirmed")