from typing import List
from pydantic import BaseModel

class RecoveryPlanStep(BaseModel):
    step_number: int
    instruction: str

class RecoveryPlan(BaseModel):
    steps: List[RecoveryPlanStep]