# fastapi_alignr_v1.py
# Day 17 — ALIGNR FastAPI Backend (wired to SQLite + feedback)
# Run:  uvicorn fastapi_alignr_v1:app --reload
# Docs: http://localhost:8000/docs

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "alignr" / "backend"))

from database import (
    init_db, hash_email, assign_group,
    register_user, save_session,
    get_user_history, get_research_stats,
)
from study_groups import is_feedback_group
from feedback import generate_feedback

sys.path.insert(0, str(Path(__file__).parent))
from backend.nlp_engine import calculate_ras, calculate_cii, calculate_scs

# Init DB on startup
init_db()

app = FastAPI(
    title="ALIGNR API",
    description=(
        "Cognitive alignment research platform. "
        "Privacy: text processed locally and discarded. "
        "Only numerical scores returned and stored."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://localhost:8501",
                   "https://alignr.me"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Pydantic Models ──────────────────────────────────────────

class SessionRequest(BaseModel):
    email: str
    pre_thinking: str
    ai_output: str
    prediction: Optional[str] = ""
    task_type: Optional[str] = "general"


class SessionResponse(BaseModel):
    user_id: str
    session_number: int
    study_group: str
    task_type: str
    ras: Optional[float]
    cii: Optional[float]
    scs: Optional[float]
    ras_interpretation: str
    narrative: Optional[str]
    message: str


class RegisterRequest(BaseModel):
    email: str


class RegisterResponse(BaseModel):
    user_id: str
    study_group: str


class HistoryResponse(BaseModel):
    user_id: str
    sessions: list[dict]


class StatsResponse(BaseModel):
    groups: list[dict]


def interpret_ras(score: Optional[float]) -> str:
    if score is None:
        return "insufficient_data"
    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "moderate"
    if score >= 0.30:
        return "developing"
    return "low"


# ── Endpoints ────────────────────────────────────────────────

@app.post("/user/register", response_model=RegisterResponse)
async def register(req: RegisterRequest):
    """Register a user. Email hashed immediately, never stored."""
    user_id, group = register_user(req.email)
    return RegisterResponse(user_id=user_id, study_group=group)


@app.post("/session", response_model=SessionResponse)
async def create_session(req: SessionRequest):
    """
    Record session. Text processed in memory, discarded after scoring.
    Only floats saved to SQLite.
    """
    try:
        # Step 1: hash email → user_id
        user_id, group = register_user(req.email)

        # Step 2: calculate scores (text is method-local here)
        try:
            ras_result = calculate_ras(req.pre_thinking, req.ai_output)
            ras = ras_result["ras"]
        except ValueError:
            ras = 0.0

        cii = calculate_cii(req.pre_thinking)

        scs_result = calculate_scs(
            req.prediction or "", req.ai_output
        )
        scs = scs_result.get("scs")

        # Step 3: save scores to SQLite (no text)
        session_num = save_session(user_id, req.task_type, ras, cii, scs)

        # Step 4: generate narrative for feedback group only
        narrative = None
        if is_feedback_group(user_id):
            narrative = generate_feedback(
                ras=ras, cii=cii, scs=scs,
                session_num=session_num,
                task_type=req.task_type,
            ) or None

        # Step 5: text parameters end here — garbage collected
        return SessionResponse(
            user_id=user_id,
            session_number=session_num,
            study_group=group,
            task_type=req.task_type,
            ras=round(ras, 4),
            cii=round(cii, 4),
            scs=round(scs, 4) if scs is not None else None,
            ras_interpretation=interpret_ras(ras),
            narrative=narrative,
            message="Session recorded. Text discarded. Only scores retained.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{user_id}", response_model=HistoryResponse)
async def get_history(user_id: str):
    """Return numerical session history. Zero text columns."""
    sessions = get_user_history(user_id)
    if not sessions:
        raise HTTPException(
            status_code=404,
            detail="No sessions found for this user_id."
        )
    return HistoryResponse(user_id=user_id, sessions=sessions)


@app.get("/research/stats", response_model=StatsResponse)
async def get_stats():
    """Group-level aggregate stats. No individual data exposed."""
    return StatsResponse(**get_research_stats())


@app.get("/health")
async def health():
    """Health check for ATLAS watchdog."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "privacy": "text never stored",
    }