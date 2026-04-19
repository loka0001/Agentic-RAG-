from typing import Optional, List
from pydantic import BaseModel

class PatientFeedback(BaseModel):
    """Input received from the patient regarding the recovery plan."""
    confirmed: bool
    notes_for_modification: Optional[str] = None
    questions: List[str] = []
