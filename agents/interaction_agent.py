from schemas.patient_input import PatientInput
from schemas.structured_patient_data import StructuredPatientData

class InteractionAgent:
    """Agent responsible for parsing raw multi-modal inputs."""
    
    def process_raw_input(self, raw_input: PatientInput) -> StructuredPatientData:
        """
        Converts raw data into structured data.
        
        Args:
            raw_input (PatientInput): Raw multi-modal input.
            
        Returns:
            StructuredPatientData: Parsed and structured patient data.
        """
        pass
