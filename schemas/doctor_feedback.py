from typing import Optional
from pydantic import BaseModel
from schemas.recovery_plan import RecoveryPlan

class DoctorFeedback(BaseModel):
    """Input received from the doctor."""
    instructions: str
    adjusted_recovery_plan: Optional[RecoveryPlan]
    follow_up_required: bool
