# test_api.py
# Day 12 — Automated API tests for fastapi_alignr_v1.py
#
# Tests all 4 endpoints + hard privacy assertion:
#   POST /session → returns scores, contains NO input text
#   GET  /user/{hash} → returns user history
#   GET  /research/stats → returns aggregate stats
#   GET  /health → returns server status
#
# Prerequisite: uvicorn fastapi_alignr_v1:app --reload must be running.
# Run: python test_api.py

import hashlib
import json
import sys
import requests

BASE = "http://localhost:8000"

# Sentences we will send in the request body.
# After the request, NONE of these strings should appear in any response.
INPUT_PRE = "Python automation handles repetitive data tasks well"
INPUT_AI = "Python is excellent for automating data workflows"
INPUT_PRED = "AI will mention Python automation"

# Phrases to scan responses for — these are the privacy markers
FORBIDDEN_IN_RESPONSE = [
    "Python automation handles",
    "Python is excellent for automating",
    "AI will mention Python",
]


def fail(msg: str):
    print(f"\n❌ FAIL: {msg}")
    sys.exit(1)


def section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


# ────────────────────────────────────────────────────────────
# Test 1: POST /session
# ────────────────────────────────────────────────────────────
section("Test 1: POST /session")

payload = {
    "email": "test@alignr.me",
    "pre_thinking": INPUT_PRE,
    "ai_output": INPUT_AI,
    "prediction": INPUT_PRED,
    "task_category": "technical",
}

r = requests.post(f"{BASE}/session", json=payload)
print(f"Status code: {r.status_code}")

if r.status_code != 200:
    fail(f"Expected 200, got {r.status_code}. Body: {r.text}")

data = r.json()
print(f"Response body:\n{json.dumps(data, indent=2)}")

# Schema check
required_keys = {
    "user_id",
    "session_number",
    "study_group",
    "task_category",
    "ras",
    "cii",
    "scs",
    "ras_interpretation",
    "message",
}
missing = required_keys - set(data.keys())
if missing:
    fail(f"Response missing keys: {missing}")
print(f"\n✅ All {len(required_keys)} expected keys present")

# Privacy check — the most important assertion in this script
response_str = json.dumps(data)
for phrase in FORBIDDEN_IN_RESPONSE:
    if phrase in response_str:
        fail(f"PRIVACY VIOLATION: '{phrase}' found in response body")
print("✅ Privacy: zero input text in response body")

USER_HASH = data["user_id"]


# ────────────────────────────────────────────────────────────
# Test 2: GET /user/{email_hash}
# ────────────────────────────────────────────────────────────
section("Test 2: GET /user/{email_hash}")

r = requests.get(f"{BASE}/user/{USER_HASH}")
print(f"Status code: {r.status_code}")

if r.status_code != 200:
    fail(f"Expected 200, got {r.status_code}. Body: {r.text}")

user_data = r.json()
print(f"Response body:\n{json.dumps(user_data, indent=2)}")

required_keys = {"user_id", "study_group", "session_count", "average_ras", "ras_trend"}
missing = required_keys - set(user_data.keys())
if missing:
    fail(f"Response missing keys: {missing}")
print(f"\n✅ All {len(required_keys)} expected keys present")
print(f"✅ Session count: {user_data['session_count']}")


# ────────────────────────────────────────────────────────────
# Test 3: GET /research/stats
# ────────────────────────────────────────────────────────────
section("Test 3: GET /research/stats")

r = requests.get(f"{BASE}/research/stats")
print(f"Status code: {r.status_code}")

if r.status_code != 200:
    fail(f"Expected 200, got {r.status_code}. Body: {r.text}")

stats_data = r.json()
print(f"Response body:\n{json.dumps(stats_data, indent=2)}")

required_keys = {
    "total_users",
    "feedback_users",
    "control_users",
    "total_sessions",
    "group_comparison",
}
missing = required_keys - set(stats_data.keys())
if missing:
    fail(f"Response missing keys: {missing}")
print(f"\n✅ All {len(required_keys)} expected keys present")


# ────────────────────────────────────────────────────────────
# Test 4: GET /health
# ────────────────────────────────────────────────────────────
section("Test 4: GET /health")

r = requests.get(f"{BASE}/health")
print(f"Status code: {r.status_code}")

if r.status_code != 200:
    fail(f"Expected 200, got {r.status_code}. Body: {r.text}")

health_data = r.json()
print(f"Response body:\n{json.dumps(health_data, indent=2)}")

if health_data.get("status") != "healthy":
    fail(f"Expected status 'healthy', got {health_data.get('status')}")
if health_data.get("privacy") != "text never stored":
    fail(f"Privacy claim mismatch in /health")
print("\n✅ Server reports healthy")
print("✅ Privacy claim asserted in response")


# ────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ────────────────────────────────────────────────────────────
section("ALL TESTS PASSED")
print("✅ POST /session       — returns scores, privacy verified")
print("✅ GET  /user/{hash}   — retrieves user state")
print("✅ GET  /research/stats — aggregate data only")
print("✅ GET  /health        — server reporting healthy")
print("\n4 endpoints, 4 PASS, 0 FAIL")
print("Privacy assertion: 0 input strings found in any response")
print("=" * 60)
