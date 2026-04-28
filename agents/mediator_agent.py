from schemas import MediatorDecision
class MediatorAgent:
    """
    The MediatorAgent is responsible for:
    1. Receiving structured patient data.
    2. Analyzing it using internal RAG logic.
    3. Producing a structured medical decision.
    4. Updating the decision based on doctor or patient feedback.
    """

    def __init__(self):
        pass

    def process_structured_data(self, data):
        """
        Receives structured patient data and produces a mediator decision.
        """

        analysis_result = self.analyze_with_rag(data)

        return MediatorDecision(**analysis_result)

    def analyze_with_rag(self, data):
        """
        Internal RAG function.

        This function:
        1. Takes structured patient data.
        2. Retrieves relevant medical context.
        3. Uses the retrieved context to generate a decision.
        """

        relevant_context = self.retrieve_relevant_context(data)

        analysis_result = self.generate_decision_from_context(
            patient_data=data,
            context=relevant_context
        )

        return analysis_result

    def retrieve_relevant_context(self, data):
        """
        Retrieves relevant medical knowledge, guidelines, or protocols
        based on the patient's structured data.

        In the real system, this may search:
        - Medical guidelines
        - Post-operative care protocols
        - Hospital instructions
        - Previous similar cases
        """

        # Placeholder example
        context = {
            "source": "post-operative recovery guideline",
            "content": "Patients with moderate or severe symptoms require doctor review."
        }

        return context

    def generate_decision_from_context(self, patient_data, context):
        """
        Generates the clinical decision using patient data
        and the retrieved medical context.
        """

        # Example simplified logic
        risk_level = self.estimate_risk_level(patient_data)

        recovery_plan = self.create_recovery_plan(
            patient_data=patient_data,
            risk_level=risk_level,
            context=context
        )

        analysis_result = {
            "risk_level": risk_level,
            "recovery_plan": recovery_plan,
            "reasoning": "Decision generated based on structured patient data and retrieved medical context."
        }

        return analysis_result

    def estimate_risk_level(self, patient_data):
        """
        Estimates patient risk level.

        This is a simplified example.
        In the real system, this should depend on symptoms,
        vital signs, wound status, pain severity, fever, etc.
        """

        fever = getattr(patient_data, "fever", False)
        severe_pain = getattr(patient_data, "severe_pain", False)
        wound_discharge = getattr(patient_data, "wound_discharge", False)

        if fever or severe_pain or wound_discharge:
            return "moderate"

        return "low"

    def create_recovery_plan(self, patient_data, risk_level, context):
        """
        Creates a recovery plan according to the patient's condition.
        """

        if risk_level == "low":
            return {
                "instructions": [
                    "Continue routine post-operative care.",
                    "Take medications as prescribed.",
                    "Keep the wound clean and dry.",
                    "Contact the doctor if symptoms worsen."
                ],
                "follow_up": "Routine follow-up."
            }

        return {
            "instructions": [
                "Doctor review is recommended before sending final instructions.",
                "Monitor symptoms closely.",
                "Avoid self-medication unless prescribed."
            ],
            "follow_up": "Doctor review required."
        }

    def process_doctor_feedback(self, current_decision, feedback):
        """
        Updates the current mediator decision based on doctor feedback.
        """

        if current_decision is None:
            raise ValueError("No current decision available to update.")

        if not self._has_feedback_content(feedback):
            return current_decision

        updated_decision_data = current_decision.model_dump()

        doctor_notes = getattr(feedback, "notes", None)
        updated_plan = getattr(feedback, "updated_plan", None)
        updated_risk_level = getattr(feedback, "risk_level", None)

        if doctor_notes:
            updated_decision_data["doctor_notes"] = doctor_notes

        if updated_plan:
            updated_decision_data["recovery_plan"] = updated_plan

        if updated_risk_level:
            updated_decision_data["risk_level"] = updated_risk_level

        return MediatorDecision(**updated_decision_data)

    def process_patient_feedback(self, current_decision, feedback):
        """
        Handles patient feedback after receiving a recovery plan.

        Example:
        - New symptom appeared
        - Pain increased
        - Patient could not follow instructions
        """

        if current_decision is None:
            raise ValueError("No current decision available to update.")

        if not self._has_feedback_content(feedback):
            return current_decision

        updated_decision_data = current_decision.model_dump()

        patient_notes = getattr(feedback, "notes", None)
        new_symptoms = getattr(feedback, "new_symptoms", None)

        if patient_notes:
            updated_decision_data["patient_feedback"] = patient_notes

        if new_symptoms:
            updated_decision_data["risk_level"] = "moderate"
            updated_decision_data["reasoning"] = (
                "Risk level increased because the patient reported new symptoms."
            )

        return MediatorDecision(**updated_decision_data)

    def _has_feedback_content(self, feedback):
        """
        Checks whether feedback contains meaningful content.
        """

        if feedback is None:
            return False

        if hasattr(feedback, "model_dump"):
            feedback_dict = feedback.model_dump()
        elif hasattr(feedback, "dict"):
            feedback_dict = feedback.dict()
        elif hasattr(feedback, "__dict__"):
            feedback_dict = feedback.__dict__
        else:
            return bool(feedback)

        return any(value not in [None, "", [], {}] for value in feedback_dict.values())
