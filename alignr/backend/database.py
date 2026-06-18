"""
alignr/backend/database.py
ALIGNR SQLite Persistence Layer — Privacy: ZERO text columns.
Day 16 — June 16, 2026
"""
import sqlite3
import hashlib
from pathlib import Path
from typing import Optional

DB_PATH = Path("alignr_data/alignr.db")


def init_db() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       TEXT    UNIQUE NOT NULL,
                study_group   TEXT    NOT NULL,
                session_count INTEGER NOT NULL DEFAULT 0,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT    NOT NULL,
                task_type   TEXT    NOT NULL,
                ras         REAL    NOT NULL,
                cii         REAL    NOT NULL,
                scs         REAL,
                session_num INTEGER NOT NULL,
                study_group TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_user
                ON sessions(user_id, session_num);
        """)


def hash_email(email: str) -> str:
    """Convert email to 16-char hex user_id. Email is NEVER stored."""
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()[:16]


def assign_group(user_id: str) -> str:
    """Deterministic. Same user_id → same group every time, forever."""
    return "feedback" if int(user_id[:2], 16) % 10 < 6 else "control"


def register_user(email: str) -> tuple[str, str]:
    """Hash email immediately. Never stored. Returns (user_id, group)."""
    user_id = hash_email(email)
    group = assign_group(user_id)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, study_group) VALUES (?, ?)",
            (user_id, group)
        )
    return user_id, group


def save_session(user_id: str, task_type: str, ras: float,
                 cii: float, scs: Optional[float] = None) -> int:
    """Save numerical scores only. Returns session_num."""
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT session_count FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        session_num = (row[0] if row else 0) + 1
        group = assign_group(user_id)
        conn.execute("""
            INSERT INTO sessions
                (user_id, task_type, ras, cii, scs, session_num, study_group)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, task_type, round(ras, 4), round(cii, 4),
              round(scs, 4) if scs is not None else None, session_num, group))
        conn.execute(
            "UPDATE users SET session_count = ? WHERE user_id = ?",
            (session_num, user_id)
        )
    return session_num


def get_user_history(user_id: str) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT ras, cii, scs, session_num, task_type, study_group, created_at
            FROM sessions WHERE user_id = ? ORDER BY session_num
        """, (user_id,)).fetchall()
    return [dict(r) for r in rows]


def get_research_stats() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT study_group,
                   COUNT(DISTINCT user_id) AS unique_users,
                   COUNT(*)                AS total_sessions,
                   ROUND(AVG(ras), 4)      AS avg_ras,
                   ROUND(AVG(cii), 4)      AS avg_cii,
                   ROUND(AVG(scs), 4)      AS avg_scs
            FROM sessions GROUP BY study_group
        """).fetchall()
    return {"groups": [dict(r) for r in rows]}


if __name__ == "__main__":
    print("=" * 50)
    print("  database.py — VERIFICATION SUITE")
    print("=" * 50)
    init_db()
    print("✓ T1: DB initialized")

    uid = hash_email("researcher@mit.edu")
    assert "@" not in uid and len(uid) == 16
    assert hash_email("researcher@mit.edu") == uid
    print(f"✓ T2: Hash consistent → {uid}")

    g1, g2 = assign_group(uid), assign_group(uid)
    assert g1 == g2
    print(f"✓ T3: Group deterministic → {g1}")

    uids = [f"{i:02x}{'0'*14}" for i in range(256)]
    fb_pct = sum(1 for u in uids if assign_group(u) == "feedback") / 256 * 100
    assert 50 <= fb_pct <= 70
    print(f"✓ T4: Group split {fb_pct:.1f}% feedback")

    uid2, grp = register_user("test@alignr.me")
    sn = save_session(uid2, "technical", 0.723, 0.541, 0.412)
    assert sn == 1
    print(f"✓ T5: Session #{sn} saved")

    history = get_user_history(uid2)
    for banned in ("pre_thinking", "ai_output", "prediction", "email"):
        assert banned not in history[0]
    print(f"✓ T6: History clean — {list(history[0].keys())}")

    with sqlite3.connect(DB_PATH) as conn:
        cols = [r[1] for r in conn.execute(
            "PRAGMA table_info(sessions)").fetchall()]
    for banned in ("pre_thinking", "ai_output", "prediction"):
        assert banned not in cols
    print(f"✓ T7: Schema clean — {cols}")

    print("\n✅ ALL 7 PASSED — Privacy Layer 7 ESTABLISHED")