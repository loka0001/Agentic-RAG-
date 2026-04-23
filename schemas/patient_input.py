from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MediaItem(BaseModel):
    file_data: str = Field(
        description=("Raw file reference such as file path, URL, or base64 string.")
    )

    description: str = Field(
        description=(
            "Short human-readable explanation of what this file represents. "
            "Examples: 'knee swelling photo', 'x-ray of left leg', "
            "'blood test report', 'discharge summary'."
        )
    )


class PatientInput(BaseModel):
    """Raw inputs received from the patient or system."""

    patient_info: Dict[str, Any] = Field(
        description="Patient demographic and baseline information such as age, gender, height, weight, and medical history."
    )

    surgery_protocol: str = Field(
        description="Text describing surgery or recovery instructions or protocol rules."
    )

    symptoms: Optional[str] = Field(
        description="Free-text daily report describing symptoms or physical observations."
    )

    medications: Optional[List[str]] = Field(
        description="List of medications the patient is taking, optionally including dosage."
    )

    images: Optional[List[MediaItem]] = Field(
        description="List of medical or recovery-related images."
    )

    documents: Optional[List[MediaItem]] = Field(
        description="List of medical documents such as reports or summaries."
    )
