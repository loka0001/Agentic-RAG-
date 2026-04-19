from typing import Union
from schemas.recovery_plan import RecoveryPlan
from schemas.patient_feedback import PatientFeedback
from schemas.mentor_state import MentorState

class PatientMentorAgent:
    """Agent responsible for mentoring the patient and tracking progress."""
    
    def process_confirmed_plan(self, plan: RecoveryPlan) -> MentorState:
        """
        Makes sure the user follows the plan.
        Extracts instructions and initializes progress tracking.
        
        Args:
            plan (RecoveryPlan): The confirmed recovery plan.
            
        Returns:
            MentorState: The strict schema tracking plan, instructions, and progress.
        """
        pass

    def process_patient_update(self, patient_update: str) -> MentorState:
        """
        Evaluates daily input from the user regarding what they did or any questions.
        
        Args:
            patient_update (str): The raw text input from the patient.
            
        Returns:
            Union[MentorState, PatientFeedback]: 
                - Returns updated MentorState (e.g. updating current_step_index) if it's just a routine progress update.
                  signaling the orchestrator to route it back to the MediatorAgent.
        """
        pass
