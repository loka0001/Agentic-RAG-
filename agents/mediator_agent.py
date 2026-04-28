from schemas.structured_patient_data import StructuredPatientData
from schemas.mediator_decision import MediatorDecision
from schemas.doctor_feedback import DoctorFeedback
from schemas.patient_feedback import PatientFeedback

class MediatorAgent:
    def __init__(self, rag_service):
        self.rag_service = rag_service
        
    def process_structured_data(self, data: StructuredPatientData) -> MediatorDecision:
        analysis_result = self.rag_service.analyze_data(data)
        return MediatorDecision(**analysis_result)

    def process_doctor_feedback(self, current_decision: MediatorDecision, feedback: DoctorFeedback) -> MediatorDecision:
        updated_result = self.rag_service.apply_doctor_feedback(current_decision, feedback)
        return MediatorDecision(**updated_result)
        
    def process_patient_feedback(self, current_decision: MediatorDecision, feedback: PatientFeedback) -> MediatorDecision:
        adjusted_result = self.rag_service.apply_patient_feedback(current_decision, feedback)
        return MediatorDecision(**adjusted_result)
