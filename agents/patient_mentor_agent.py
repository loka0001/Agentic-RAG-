from typing import Union, Optional, List
from schemas.recovery_plan import RecoveryPlan
from schemas.patient_feedback import PatientFeedback
from schemas.mentor_state import MentorState


class PatientMentorAgent:
    """Agent responsible for mentoring the patient and tracking progress."""

    COMPLETION_MARKERS = ["done", "completed", "finished", "did it"]
    QUESTION_MARKERS = ["?", "can i", "should i", "may i"]
    def process_confirmed_plan(self, plan: RecoveryPlan) -> MentorState:
        """
        Makes sure the user follows the plan.
        Extracts instructions and initializes progress tracking.
        """
        if not plan.steps:
            raise ValueError("Cannot process a recovery plan with no steps.")

        ordered_steps = sorted(plan.steps, key=lambda step: step.step_number)
        ordered_plan = RecoveryPlan(steps=ordered_steps)

        return MentorState(
            recovery_plan=ordered_plan,
            current_step_index=0,
        )

    def process_patient_update(
        self,
        current_state: MentorState,
        patient_update: str,
    ) -> Union[MentorState, PatientFeedback]:
        """
        Evaluates daily input from the user regarding what they did or any questions.

        Returns:
            Union[MentorState, PatientFeedback]:
                - Returns updated MentorState if the message is a routine progress update.
                - Returns PatientFeedback if the message contains a question or needs review.
        """
        text = patient_update.strip().lower()

        if not text:
            return self._build_feedback("Empty update received.", [])

        if self._looks_like_question(text):
            return self._build_feedback(None, [patient_update])

        if self._looks_like_clear_completion(text):
            return self._advance_plan_step(current_state)

        return self._build_feedback(patient_update, [])

    def _looks_like_question(self, text: str) -> bool:
        return any(marker in text for marker in self.QUESTION_MARKERS)

    def _looks_like_clear_completion(self, text: str) -> bool:
        return any(marker in text for marker in self.COMPLETION_MARKERS)

    def _advance_plan_step(self, state: MentorState) -> MentorState:
        total_steps = len(state.recovery_plan.steps)
        next_index = state.current_step_index + 1

        if next_index >= total_steps:
            next_index = total_steps - 1

        return state.model_copy(update={"current_step_index": next_index})

    def _build_feedback(
        self,
        note: Optional[str],
        questions: List[str],
    ) -> PatientFeedback:
        return PatientFeedback(
            confirmed=False,
            notes_for_modification=note,
            questions=questions,
        )
