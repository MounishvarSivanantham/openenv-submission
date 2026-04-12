"""
Grader functions for the SQL-Review OpenEnv submission.

Each grader receives a dict with at least:
  - "query"       : the SQL string submitted by the agent
  - "explanation" : the agent's natural-language explanation

Each grader MUST return a float strictly in (0, 1) — i.e. never exactly 0.0 or 1.0.
"""

import re


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clamp(score: float, lo: float = 0.05, hi: float = 0.95) -> float:
    """Ensure the score is strictly inside (0, 1)."""
    return max(lo, min(hi, score))


def _normalize(query: str) -> str:
    return query.upper().strip()


# ---------------------------------------------------------------------------
# Task 1 – fix_syntax   (easy)
# ---------------------------------------------------------------------------

def grade_fix_syntax(submission: dict) -> float:
    """
    Rubric:
      - Has at least one comma between column names      → +0.30
      - Uses correct boolean keyword (TRUE/FALSE/1)      → +0.30
      - No syntax keywords missing (SELECT, FROM, WHERE) → +0.20
      - Explanation is non-empty                         → +0.10
    Max raw = 0.90  →  clamped to (0.05, 0.95)
    """
    query = _normalize(submission.get("query", ""))
    explanation = submission.get("explanation", "").strip()

    score = 0.0

    # Column list uses comma separation
    if "," in query:
        score += 0.30

    # Correct boolean keyword
    if re.search(r"\bTRUE\b|\bFALSE\b|\b1\b|\b0\b", query):
        score += 0.30

    # Core SQL keywords present
    for kw in ("SELECT", "FROM", "WHERE"):
        if kw in query:
            score += 0.067  # ~0.20 total for all three

    # Non-empty explanation
    if explanation:
        score += 0.10

    return _clamp(score)


# ---------------------------------------------------------------------------
# Task 2 – optimize_query   (medium)
# ---------------------------------------------------------------------------

def grade_optimize_query(submission: dict) -> float:
    """
    Rubric:
      - Avoids SELECT *                                  → +0.35
      - Uses LIMIT clause                                → +0.25
      - Has a WHERE / filtering condition                → +0.20
      - Explanation is non-empty                         → +0.10
    Max raw = 0.90  →  clamped to (0.05, 0.95)
    """
    query = _normalize(submission.get("query", ""))
    explanation = submission.get("explanation", "").strip()

    score = 0.0

    # No SELECT *
    if "SELECT *" not in query:
        score += 0.35

    # LIMIT clause
    if "LIMIT" in query:
        score += 0.25

    # WHERE clause (basic filtering)
    if "WHERE" in query:
        score += 0.20

    # Non-empty explanation
    if explanation:
        score += 0.10

    return _clamp(score)


# ---------------------------------------------------------------------------
# Task 3 – security_audit   (hard)
# ---------------------------------------------------------------------------

def grade_security_audit(submission: dict) -> float:
    """
    Rubric:
      - Uses a parameterized placeholder (?, %s, :name)  → +0.40
      - No raw string concatenation patterns detected    → +0.20
      - SELECT is scoped (not SELECT *)                  → +0.15
      - WHERE clause present                             → +0.10
      - Explanation mentions 'param' or 'inject'         → +0.10
    Max raw = 0.95  →  clamped to (0.05, 0.95)
    """
    query = _normalize(submission.get("query", ""))
    raw_query = submission.get("query", "")
    explanation = submission.get("explanation", "").lower()

    score = 0.0

    # Parameterized placeholder
    if re.search(r"\?|%s|:[a-zA-Z_]\w*", raw_query):
        score += 0.40

    # No obvious string concatenation like ' + or " +
    if not re.search(r"['\"]\\s*\+|\\+\\s*['\"]", raw_query):
        score += 0.20

    # Not SELECT *
    if "SELECT *" not in query:
        score += 0.15

    # WHERE clause
    if "WHERE" in query:
        score += 0.10

    # Explanation quality
    if "param" in explanation or "inject" in explanation:
        score += 0.10

    return _clamp(score)
