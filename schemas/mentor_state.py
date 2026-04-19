from pydantic import BaseModel
from schemas.recovery_plan import RecoveryPlan

class MentorState(BaseModel):
    """Schema representing the state managed by the Patient Mentor."""
    recovery_plan: RecoveryPlan
    current_step_index: int = 0

