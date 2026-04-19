from schemas.structured_patient_data import StructuredPatientData
from schemas.mediator_decision import MediatorDecision
from schemas.doctor_feedback import DoctorFeedback
from schemas.patient_feedback import PatientFeedback

class MediatorAgent:
    """Agent responsible for evaluating risk and generating recovery plans using RAG."""
    
    def process_structured_data(self, data: StructuredPatientData) -> MediatorDecision:
        """
        Analyzes all structured data and generates the initial mediator_decision.
        """
        pass

    def process_doctor_feedback(self, current_decision: MediatorDecision, feedback: DoctorFeedback) -> MediatorDecision:
        """
        Modifies the recovery plan based on explicit doctor feedback.
        """
        pass
        
    def process_patient_feedback(self, current_decision: MediatorDecision, feedback: PatientFeedback) -> MediatorDecision:
        """
        Re-analyzes the plan based on patient questions or feedback, potentially triggering a new cycle.
        """
        pass
