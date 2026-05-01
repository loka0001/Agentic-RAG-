import os
from typing import Union, Optional, List, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openai import ChatOpenAI

from schemas.recovery_plan import RecoveryPlan
from schemas.patient_feedback import PatientFeedback
from schemas.mentor_state import MentorState

load_dotenv()


class PatientUpdateDecision(BaseModel):
    action: Literal[
        "completion",
        "question",
        "medical_review",
        "plan_modification",
    ] = Field(
        description="How the patient update should be handled."
    )
    extracted_question: Optional[str] = Field(
        default=None,
        description="The patient's extracted question if the update is a question.",
    )
    review_note: Optional[str] = Field(
        default=None,
        description="Short note describing the concern, symptom, or requested modification.",
    )


class PatientMentorAgent:
    """Agent responsible for mentoring the patient and tracking progress."""

    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.inference.ai.azure.com",
            temperature=0.2,
        )

        self.system_prompt = """
        You are a patient update triage assistant.

        Your task is to classify the patient's message into exactly one of these actions:

        1. completion
           - The patient clearly says they completed or followed the current recovery step.

        2. question
           - The patient is asking a question without reporting a concerning symptom.

        3. medical_review
           - The patient reports pain, swelling, bleeding, fever, worsening symptoms,
             inability to continue, or any issue that may need medical review.

        4. plan_modification
           - The patient wants to change, skip, stop, replace, or adjust the plan.

        Rules:
        - If the message is unclear, choose medical_review.
        - Do not give medical advice.
        - If action is question, fill extracted_question.
        - If action is medical_review or plan_modification, fill review_note with a short summary.
        - Return only structured output matching the schema.
        """

        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            response_format=ToolStrategy(PatientUpdateDecision),
        )

    def process_confirmed_plan(self, plan: RecoveryPlan) -> MentorState:
        """
        Initializes tracking state from a confirmed recovery plan.
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
        Receives a patient message and decides whether it means:
        - completed current step
        - asked a question
        - needs medical review
        - requests plan modification
        """
        text = patient_update.strip()

        if not text:
            return self._build_feedback("Empty update received.", [])

        current_step_text = self._get_current_step_text(current_state)

        result = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Current recovery step: {current_step_text}\n"
                            f"Patient message: {patient_update}"
                        ),
                    }
                ]
            }
        )

        decision = result["structured_response"]

        if decision.action == "completion":
            return self._advance_plan_step(current_state)

        if decision.action == "question":
            return self._build_feedback(
                None,
                [decision.extracted_question or patient_update],
            )

        if decision.action == "plan_modification":
            return self._build_feedback(
                decision.review_note or patient_update,
                [],
            )

        return self._build_feedback(
            decision.review_note or patient_update,
            [],
        )

    def _get_current_step_text(self, state: MentorState) -> str:
        steps = state.recovery_plan.steps

        if not steps:
            return "No current step."

        if state.current_step_index >= len(steps):
            return "Plan already completed."

        step = steps[state.current_step_index]
        return f"Step {step.step_number}: {step.instruction}"

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
