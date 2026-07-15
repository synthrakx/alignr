"""
alignr/backend/database.py
ALIGNR Postgres Persistence Layer — Privacy: ZERO text columns.
Day 45 — July 15, 2026 (migrated from SQLite to Neon Postgres)
"""
import os
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL not set. "
        "Set it in your shell (local) or Render dashboard (prod)."
    )


def _connect():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db() -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            SERIAL PRIMARY KEY,
                    user_id       TEXT    UNIQUE NOT NULL,
                    study_group   TEXT    NOT NULL,
                    session_count INTEGER NOT NULL DEFAULT 0,
                    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id          SERIAL PRIMARY KEY,
                    user_id     TEXT    NOT NULL,
                    task_type   TEXT    NOT NULL,
                    ras         REAL    NOT NULL,
                    cii         REAL    NOT NULL,
                    scs         REAL,
                    session_num INTEGER NOT NULL,
                    study_group TEXT    NOT NULL,
                    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user
                    ON sessions(user_id, session_num);
            """)
        conn.commit()


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
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (user_id, study_group) VALUES (%s, %s) "
                "ON CONFLICT (user_id) DO NOTHING",
                (user_id, group)
            )
        conn.commit()
    return user_id, group


def save_session(user_id: str, task_type: str, ras: float,
                 cii: float, scs: Optional[float] = None) -> int:
    """Save numerical scores only. Returns session_num."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT session_count FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            session_num = (row[0] if row else 0) + 1
            group = assign_group(user_id)
            cur.execute("""
                INSERT INTO sessions
                    (user_id, task_type, ras, cii, scs, session_num, study_group)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, task_type, round(ras, 4), round(cii, 4),
                  round(scs, 4) if scs is not None else None, session_num, group))
            cur.execute(
                "UPDATE users SET session_count = %s WHERE user_id = %s",
                (session_num, user_id)
            )
        conn.commit()
    return session_num


def get_user_history(user_id: str) -> list[dict]:
    with _connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT ras, cii, scs, session_num, task_type, study_group, created_at
                FROM sessions WHERE user_id = %s ORDER BY session_num
            """, (user_id,))
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_research_stats() -> dict:
    with _connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT study_group,
                       COUNT(DISTINCT user_id) AS unique_users,
                       COUNT(*)                AS total_sessions,
                       ROUND(AVG(ras)::numeric, 4)  AS avg_ras,
                       ROUND(AVG(cii)::numeric, 4)  AS avg_cii,
                       ROUND(AVG(scs)::numeric, 4)  AS avg_scs
                FROM sessions GROUP BY study_group
            """)
            rows = cur.fetchall()
    return {"groups": [dict(r) for r in rows]}


if __name__ == "__main__":
    print("=" * 50)
    print("  database.py — VERIFICATION SUITE (Postgres/Neon)")
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
    assert sn >= 1
    print(f"✓ T5: Session #{sn} saved")

    history = get_user_history(uid2)
    for banned in ("pre_thinking", "ai_output", "prediction", "email"):
        assert banned not in history[0]
    print(f"✓ T6: History clean — {list(history[0].keys())}")

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'sessions'
            """)
            cols = [r[0] for r in cur.fetchall()]
    for banned in ("pre_thinking", "ai_output", "prediction"):
        assert banned not in cols
    print(f"✓ T7: Schema clean — {cols}")

    print("\n✅ ALL 7 PASSED — Privacy Layer 7 ESTABLISHED (Postgres)")