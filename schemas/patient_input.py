from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PatientInput(BaseModel):
    """Raw inputs received from the patient or system."""
    patient_info: Dict[str, Any] = Field(description="Patient demographic and baseline info (e.g., age, gender)")
    surgery_protocol: str = Field(description="Protocol or rules of surgery/recovery")
    symptoms: Optional[str] = Field(description="Daily report of symptoms")
    medications: Optional[List[str]] = Field(description="Medications that patient takes")
    images: Optional[List[str]] = Field(description="Images in general (paths or base64)")
    documents: Optional[List[str]] = Field(description="Documents in general (PDFs, etc.)")
