from typing import List, Dict, Any
from pydantic import BaseModel

class StructuredPatientData(BaseModel):
    """Normalized and structured data ready for mediator analysis."""
    patient_info: Dict[str, Any]
    surgery_protocol: List[str]
    parsed_symptoms: List[str]
    medications_list: List[str]
    images_descriptions: List[str]
    documents_descriptions: List[str]
