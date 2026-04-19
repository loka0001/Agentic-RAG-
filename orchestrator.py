from agents.interaction_agent import InteractionAgent
from agents.mediator_agent import MediatorAgent
from agents.patient_mentor_agent import PatientMentorAgent
from schemas.patient_input import PatientInput
from schemas.doctor_feedback import DoctorFeedback
from schemas.patient_feedback import PatientFeedback

class SystemOrchestrator:
    """Manages the cyclic flow of the Post-Surgery Care System."""
    
    def __init__(self):
        # Initialize the three clear agents
        self.interaction_agent = InteractionAgent()
        self.mediator_agent = MediatorAgent()
        self.mentor_agent = PatientMentorAgent()

    def process_raw_input(self, raw_input: PatientInput):
        """
        Flow:
        1. interaction_agent.process_raw_input() converts raw data into structured data.
        2. mediator_agent.process_structured_data() analyzes data and generates mediator_decision.
        3. If decision.risk_level >= Moderate -> Pause for Doctor Review.
        4. Else -> Pass recovery plan to mentor_agent.process_confirmed_plan(decision.recovery_plan).
        """
        pass

    def process_doctor_feedback(self, feedback: DoctorFeedback):
        """
        Flow:
        1. If doctor gives feedback -> mediator_agent.process_doctor_feedback() modifies the plan.
        2. Else -> confirm it.
        3. Pass confirmed recovery plan to mentor_agent.process_confirmed_plan(decision.recovery_plan).
        """
        pass

    def process_patient_feedback(self, feedback: PatientFeedback):
        """
        Flow:
        1. If user has question/feedback -> Send back to mediator_agent.process_patient_feedback().
        2. mediator_agent applies same cycle (Doctor review if needed).
        3. Once confirmed, give updated plan back to mentor_agent.process_confirmed_plan(decision.recovery_plan).
        """
        pass
