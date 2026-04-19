from pydantic import BaseModel, Field
from schemas.risk_level import RiskLevel
from schemas.recovery_plan import RecoveryPlan

class MediatorDecision(BaseModel):
    """Output from the Central Mediator Agent."""
    risk_level: RiskLevel
    reasoning: str = Field(description="Explainable AI reasoning for the decision")
    recovery_plan: RecoveryPlan = Field(description="List of steps for recovery")
    requires_doctor_communication: bool = Field(description="True if plan needs doctor adjustment, False to send to patient")
