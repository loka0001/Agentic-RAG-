from agents.interaction_agent import InteractionAgent
from agents.mediator_agent import MediatorAgent
from agents.patient_mentor_agent import PatientMentorAgent

from schemas.patient_input import PatientInput
from schemas.doctor_feedback import DoctorFeedback
from schemas.patient_feedback import PatientFeedback


class SystemOrchestrator:
    """Manages the cyclic flow of the Post-Surgery Care System."""

    MODERATE_RISK_LEVELS = {"moderate", "high", "critical"}

    def __init__(self):
        self.interaction_agent = InteractionAgent()
        self.mediator_agent = MediatorAgent()
        self.mentor_agent = PatientMentorAgent()

        # Keep state between cycles
        self.pending_decision = None
        self.last_confirmed_plan = None

    def process_raw_input(self, raw_input: PatientInput):
        """
        Flow:
        1. Convert raw patient input into structured data.
        2. Analyze structured data using mediator.
        3. If risk is Moderate or higher, pause for doctor review.
        4. Otherwise, send confirmed recovery plan to mentor agent.
        """

        structured_data = self.interaction_agent.process_raw_input(raw_input)

        decision = self.mediator_agent.process_structured_data(structured_data)

        return self._handle_mediator_decision(decision)

    def process_doctor_feedback(self, feedback: DoctorFeedback = None):
        """
        Flow:
        1. If doctor gives feedback, mediator modifies the plan.
        2. If doctor gives no feedback, confirm the pending decision.
        3. Send confirmed recovery plan to mentor agent.
        """

        if feedback is not None and self._has_feedback_content(feedback):
            decision = self.mediator_agent.process_doctor_feedback(feedback)
        else:
            if self.pending_decision is None:
                return {
                    "status": "error",
                    "message": "No pending decision found for doctor confirmation.",
                }

            decision = self.pending_decision

        return self._confirm_and_send_plan(decision)

    def process_patient_feedback(self, feedback: PatientFeedback):
        """
        Flow:
        1. Patient feedback/question goes to mediator.
        2. Mediator generates updated decision.
        3. If risk is Moderate or higher, pause for doctor review.
        4. Otherwise, send updated plan to mentor agent.
        """

        decision = self.mediator_agent.process_patient_feedback(feedback)

        return self._handle_mediator_decision(decision)

    def _handle_mediator_decision(self, decision):
        """
        Shared logic after mediator produces a decision.
        """

        if decision is None:
            return {
                "status": "error",
                "message": "Mediator returned no decision.",
            }

        if self._requires_doctor_review(decision):
            self.pending_decision = decision

            return {
                "status": "doctor_review_required",
                "risk_level": self._get_risk_level(decision),
                "decision": decision,
                "message": "Doctor review is required before sending the plan to the patient.",
            }

        return self._confirm_and_send_plan(decision)

    def _confirm_and_send_plan(self, decision):
        """
        Confirms recovery plan and sends it to patient mentor.
        """

        recovery_plan = getattr(decision, "recovery_plan", None)

        if recovery_plan is None:
            return {
                "status": "error",
                "message": "Decision does not contain a recovery_plan.",
                "decision": decision,
            }

        mentor_response = self.mentor_agent.process_confirmed_plan(recovery_plan)

        self.last_confirmed_plan = recovery_plan
        self.pending_decision = None

        return {
            "status": "plan_delivered",
            "risk_level": self._get_risk_level(decision),
            "recovery_plan": recovery_plan,
            "mentor_response": mentor_response,
        }

    def _requires_doctor_review(self, decision) -> bool:
        """
        Returns True if risk level is Moderate or higher.
        Supports both string and numeric risk levels.
        """

        risk_level = self._get_risk_level(decision)

        if risk_level is None:
            return False

        # Numeric risk handling
        if isinstance(risk_level, (int, float)):
            return risk_level >= 2

        # String risk handling
        risk_level = str(risk_level).strip().lower()

        return risk_level in self.MODERATE_RISK_LEVELS

    def _get_risk_level(self, decision):
        """
        Safely extracts risk level from decision.
        """

        return getattr(decision, "risk_level", None)

    def _has_feedback_content(self, feedback) -> bool:
        """
        Checks if doctor feedback actually contains useful content.
        Works with normal classes and Pydantic models.
        """

        if feedback is None:
            return False

        # Pydantic v2
        if hasattr(feedback, "model_dump"):
            data = feedback.model_dump()
            return any(value not in [None, "", [], {}] for value in data.values())

        # Pydantic v1
        if hasattr(feedback, "dict"):
            data = feedback.dict()
            return any(value not in [None, "", [], {}] for value in data.values())

        # Normal Python object
        if hasattr(feedback, "__dict__"):
            return any(
                value not in [None, "", [], {}]
                for value in feedback.__dict__.values()
            )

        return bool(feedback)