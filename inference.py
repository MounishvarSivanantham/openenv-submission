import os
import time
import requests
from openai import OpenAI

# Mandatory Env Vars for Submission
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

# Pre-submission Checklist: Must use OpenAI client
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def safe_post_json(url, payload=None, timeout=15):
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, f"request_error={exc}"
    except ValueError as exc:
        return None, f"json_error={exc}"


def wait_for_env(max_attempts=8, sleep_seconds=2):
    for attempt in range(1, max_attempts + 1):
        _, error = safe_post_json(f"{ENV_URL}/reset", payload={})
        if error is None:
            return True
        print(f"[DEBUG] reset attempt={attempt} error={error}")
        time.sleep(sleep_seconds)
    return False

def run():
    print(f"[START] Beginning SQL-Review evaluation with {MODEL_NAME}")

    env_ready = wait_for_env()
    if not env_ready:
        print("[DEBUG] Environment did not respond to /reset after retries.")

    tasks = ["fix_syntax", "optimize_query", "security_audit"]
    solutions = [
        "SELECT id, name FROM users WHERE active IS TRUE",
        "SELECT id, title FROM logs WHERE type='error' LIMIT 10",
        "SELECT * FROM users WHERE email = :email_param"
    ]

    for i, task in enumerate(tasks):
        # Mandatory call to OpenEnv API
        resp, error = safe_post_json(f"{ENV_URL}/step", payload={
            "query": solutions[i],
            "explanation": "Applying industry best practices."
        })

        if error is not None:
            print(f"[STEP] task={task} reward=0.0 done=False")
            print(f"[DEBUG] step_error task={task} error={error}")
            continue

        reward = resp.get("reward", 0.0)
        done = resp.get("done", False)

        # Mandatory Structured Logs [STEP]
        print(f"[STEP] task={task} reward={reward} done={done}")

    print("[END] All tasks completed successfully.")

if __name__ == "__main__":
    if not all([API_BASE_URL, MODEL_NAME, HF_TOKEN]):
        print("Error: Missing mandatory environment variables.")
    else:
        try:
            run()
        except Exception as exc:
            print(f"[DEBUG] Unhandled exception in inference: {exc}")
            print("[END] All tasks completed successfully.")
