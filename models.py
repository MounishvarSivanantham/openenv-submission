from pydantic import BaseModel
from typing import List, Optional

class SQLAction(BaseModel):
    query: str
    explanation: str

class SQLObservation(BaseModel):
    feedback: str
    is_valid: bool
    current_task: str

class Reward(BaseModel):
    value: float
