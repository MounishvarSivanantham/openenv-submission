import os

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

class SQLAction(BaseModel):
    query: str
    explanation: str

app = FastAPI()

# Environment State
STATE = {"task_index": 0}
TASK_LIST = ["fix_syntax", "optimize_query", "security_audit"]

@app.post("/reset")
def reset():
    STATE["task_index"] = 0
    return {"message": "Environment reset", "current_task": TASK_LIST[0]}

@app.get("/state")
def get_state():
    return {"current_task": TASK_LIST[STATE["task_index"]]}

@app.post("/step")
def step(action: SQLAction):
    task_id = TASK_LIST[STATE["task_index"]]
    reward = 0.0
    done = False

    # Grading Logic (As per architecture: Syntax + Perf + Security)
    if task_id == "fix_syntax":
        if "," in action.query and "TRUE" in action.query.upper():
            reward = 1.0
            done = True
    elif task_id == "optimize_query":
        if "SELECT *" not in action.query.upper() and "LIMIT" in action.query.upper():
            reward = 1.0
            done = True
        elif "SELECT *" not in action.query.upper():
            reward = 0.5 # Partial reward
    elif task_id == "security_audit":
        if any(c in action.query for c in ["?", "%s", ":"]):
            reward = 1.0
            done = True

    if done and STATE["task_index"] < 2:
        STATE["task_index"] += 1
        done = False # Move to next task in sequence

    return {"observation": {"feedback": "Processed", "current_task": task_id}, "reward": reward, "done": done}


def main():
    # HF Spaces sets PORT, but guard against empty/non-integer values.
    port_raw = os.getenv("PORT", "7860")
    try:
        port = int(port_raw)
    except (TypeError, ValueError):
        port = 7860
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
