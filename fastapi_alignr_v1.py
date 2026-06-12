# fastapi_alignr_v1.py
# Day 12 — ALIGNR FastAPI Backend
# The API layer that serves ALIGNR users
#
# PRIVACY: text enters in request body, is processed locally,
#          never appears in any response, never written to disk.
#
# Run:    uvicorn fastapi_alignr_v1:app --reload
# Docs:   http://localhost:8000/docs

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import sys
from pathlib import Path

# Import the class system built in Days 8-10
sys.path.insert(0, str(Path(__file__).parent))
from oop_alignr import ALIGNRResearch

# ────────────────────────────────────────────────────────────
# APP SETUP
# ────────────────────────────────────────────────────────────

app = FastAPI(
    title="ALIGNR API",
    description=(
        "Cognitive alignment research platform. "
        "Privacy: text is processed locally and discarded. "
        "Only numerical scores are returned. "
        "No text is stored. Verifiable in source code."
    ),
    version="1.0.0",
)

# CORS — allow browser-based clients to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://alignr.me"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# In-memory research store
# (Day 21: replace with SQLite via SQLAlchemy)
research = ALIGNRResearch()

# ────────────────────────────────────────────────────────────
# PYDANTIC MODELS — request/response schemas
# ────────────────────────────────────────────────────────────


class SessionRequest(BaseModel):
    """
    Text fields arrive here, are processed, then discarded.
    They are never stored, never logged, never returned.
    """

    email: EmailStr
    pre_thinking: str
    ai_output: str
    prediction: Optional[str] = ""
    task_category: Optional[str] = "general"

    @field_validator("pre_thinking", "ai_output")
    @classmethod
    def must_have_content(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Text must be at least 10 characters")
        return v.strip()

    @field_validator("task_category")
    @classmethod
    def valid_task(cls, v: str) -> str:
        valid = {"technical", "decision", "research", "general"}
        if v not in valid:
            raise ValueError(f"task_category must be one of {valid}")
        return v


class SessionResponse(BaseModel):
    """
    Response contains only numbers and metadata.
    Zero text from the user's input appears here.
    Interpretation strings are server-generated, not user-typed.
    """

    user_id: str
    session_number: int
    study_group: str
    task_category: str
    ras: Optional[float]
    cii: Optional[float]
    scs: Optional[float]
    ras_interpretation: str
    message: str


class UserResponse(BaseModel):
    user_id: str
    study_group: str
    session_count: int
    average_ras: float
    ras_trend: str


class StatsResponse(BaseModel):
    total_users: int
    feedback_users: int
    control_users: int
    total_sessions: int
    group_comparison: dict


def interpret_ras(score: Optional[float]) -> str:
    """Maps RAS float to a human-readable interpretation."""
    if score is None:
        return "insufficient_data"
    if score >= 0.75:
        return "high — your pre-thinking closely predicted the AI output"
    if score >= 0.50:
        return "moderate — some alignment between your thinking and AI"
    if score >= 0.30:
        return "developing — AI added significant new perspective"
    return "low — the AI diverged significantly from your pre-thinking"


# ────────────────────────────────────────────────────────────
# ENDPOINTS
# ────────────────────────────────────────────────────────────


@app.post("/session", response_model=SessionResponse)
async def create_session(req: SessionRequest):
    """
    Record an ALIGNR session and return alignment scores.

    Input: user's pre-thinking, AI output, and prediction.
    Processing: word-overlap RAS (Day 15: sentence-transformers).
    Output: RAS, CII, SCS scores + interpretation.

    Privacy guarantee: text fields are processed in memory and discarded.
    They do not appear in this response. They are not written to disk.
    """
    try:
        result = research.add_session(
            email=req.email,
            pre=req.pre_thinking,
            ai=req.ai_output,
            pred=req.prediction,
            task=req.task_category,
        )
        user = research.add_user(req.email)
        return SessionResponse(
            user_id=result["user_id"],
            session_number=result["session_number"],
            study_group=user.study_group,
            task_category=req.task_category,
            ras=result.get("ras"),
            cii=result.get("cii"),
            scs=result.get("scs"),
            ras_interpretation=interpret_ras(result.get("ras")),
            message=(
                "Session recorded. Your text was processed and discarded. "
                "Only the scores above are retained."
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{email_hash}", response_model=UserResponse)
async def get_user(email_hash: str):
    """
    Get a user's session history and average RAS.
    Identified by hashed email — real email never stored.
    """
    # The user is keyed by full sha256 hash inside ALIGNRResearch.
    # Find user by matching first 16 chars of hash (the user_id).
    matching_user = None
    for hash_key, user in research.users.items():
        if user.user_id == email_hash:
            matching_user = user
            break

    if matching_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found. Complete at least one session first.",
        )

    return UserResponse(
        user_id=matching_user.user_id,
        study_group=matching_user.study_group,
        session_count=len(matching_user.sessions),
        average_ras=matching_user.average_ras,
        ras_trend=matching_user.ras_trend,
    )


@app.get("/research/stats", response_model=StatsResponse)
async def get_stats():
    """
    Aggregate research statistics.
    No individual user data. Group-level analysis only.
    Used by: ALIGNR research dashboard, OSF preregistration updates.
    """
    total_sessions = sum(len(u.sessions) for u in research.users.values())
    return StatsResponse(
        total_users=len(research.users),
        feedback_users=sum(
            1 for u in research.users.values() if u.study_group == "feedback"
        ),
        control_users=sum(
            1 for u in research.users.values() if u.study_group == "control"
        ),
        total_sessions=total_sessions,
        group_comparison=research.compare_groups(),
    )


@app.get("/health")
async def health():
    """Health check. Used by Atlas watchdog on Oracle VM."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "users": len(research.users),
        "privacy": "text never stored",
    }
