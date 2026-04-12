import os
import sys

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Make sure the server directory is importable
sys.path.insert(0, os.path.dirname(__file__))
from graders import grade_fix_syntax, grade_optimize_query, grade_security_audit


class SQLAction(BaseModel):
    query: str
    explanation: str = ""


app = FastAPI()

# Environment State
STATE = {"task_index": 0}
TASK_LIST = ["fix_syntax", "optimize_query", "security_audit"]

GRADERS = {
    "fix_syntax":     grade_fix_syntax,
    "optimize_query": grade_optimize_query,
    "security_audit": grade_security_audit,
}


@app.post("/reset")
def reset():
    STATE["task_index"] = 0
    return {"message": "Environment reset", "current_task": TASK_LIST[0]}


@app.get("/state")
def get_state():
    idx = STATE["task_index"]
    task = TASK_LIST[idx] if idx < len(TASK_LIST) else "done"
    return {"current_task": task, "task_index": idx}


@app.post("/step")
def step(action: SQLAction):
    idx = STATE["task_index"]
    if idx >= len(TASK_LIST):
        return {
            "observation": {"feedback": "All tasks completed", "current_task": "done"},
            "reward": 0.5,
            "done": True,
        }

    task_id = TASK_LIST[idx]
    grader = GRADERS[task_id]

    # Score via grader – always strictly in (0, 1)
    reward = grader({"query": action.query, "explanation": action.explanation})

    # Advance to next task
    STATE["task_index"] += 1
    done = STATE["task_index"] >= len(TASK_LIST)

    return {
        "observation": {
            "feedback": f"Task '{task_id}' evaluated.",
            "current_task": task_id,
            "next_task": TASK_LIST[STATE["task_index"]] if not done else "done",
        },
        "reward": reward,
        "done": done,
    }


@app.post("/grade")
def grade(action: SQLAction):
    """
    Explicit grading endpoint — called by the OpenEnv evaluator for each task.
    Query param ?task_id selects the grader; falls back to current task.
    """
    from fastapi import Request  # late import to keep signature simple
    idx = STATE["task_index"]
    task_id = TASK_LIST[idx] if idx < len(TASK_LIST) else TASK_LIST[-1]
    grader = GRADERS[task_id]
    score = grader({"query": action.query, "explanation": action.explanation})
    return {"task_id": task_id, "score": score}


def main():
    port_raw = os.getenv("PORT", "7860")
    try:
        port = int(port_raw)
    except (TypeError, ValueError):
        port = 7860
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
