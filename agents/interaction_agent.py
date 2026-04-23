from schemas.patient_input import PatientInput
from schemas.structured_patient_data import StructuredPatientData
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy
from dotenv import load_dotenv
import os

load_dotenv()


class InteractionAgent:
    """Agent responsible for parsing raw multi-modal inputs."""

    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.inference.ai.azure.com",
            temperature=0.6,
        )
        self.system_prompt = """
                            You are a medical data structuring assistant.

                            Your task is to convert raw patient input into clean, structured data
                            that matches the StructuredPatientData schema.

                            Rules:

                            1. patient_info
                            - Keep all provided demographic information.
                            - Do not remove useful fields.

                            2. surgery_protocol
                            - Split the protocol text into clear individual steps.
                            - Return them as a list of short instructions.

                            3. parsed_symptoms
                            - Extract symptoms mentioned in the symptoms text.
                            - Return them as a list of short symptom phrases.
                            - If none, return an empty list.

                            4. medications_list
                            - Return medications as a clean list.
                            - Remove duplicates.
                            - If none, return an empty list.

                            5. images_descriptions
                            - Extract only the descriptions of what images represent.
                            - Ignore file paths or base64 data.
                            - Return list of short descriptions.

                            6. documents_descriptions
                            - Briefly describe what each document represents.
                            - Return short summaries.

                            General Rules:

                            - Do not invent missing data.
                            - Remove duplicates.
                            - Keep wording short and clear.
                            - Always return lists (never null).
                            - Do not provide diagnosis or medical advice.

                            Return only structured data matching StructuredPatientData.
                            Do not include explanations.
                            """

        self.agent = self._get_agent()

    def process_raw_input(
        self, raw_input: PatientInput, thread_id="1"
    ) -> StructuredPatientData:
        messages = self._prepare_messages(raw_input)
        result = self.agent.invoke(
            {"messages": messages},
            {"configurable": {"thread_id": thread_id}},
        )
        return result["structured_response"]

    def _get_agent(self):
        return create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            checkpointer=InMemorySaver(),
            response_format=ToolStrategy(StructuredPatientData),
        )

    def _prepare_messages(self, raw_input: PatientInput):
        patient_info = " ".join(
            [f"{key}:{value}" for key, value in raw_input.patient_info.items()]
        )
        patient_info += (
            " surgery_protocol "
            + (raw_input.surgery_protocol or "")
            + " symptoms "
            + (raw_input.symptoms or "")
            + " medications "
            + " ".join(raw_input.medications or [])
        )

        messages = [{"role": "user", "content": f"patient_info {patient_info} "}]

        if raw_input.images:
            for image in raw_input.images:
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"this image is about {image.description}.",
                            },
                            {
                                "type": "image",
                                "base64": image.file_data,
                                "mime_type": "image/jpeg",
                            },
                        ],
                    }
                )

        if raw_input.documents:
            for doc in raw_input.documents:
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"this document is about {doc.description}.",
                            },
                            {
                                "type": "image",
                                "base64": doc.file_data,
                                "mime_type": "image/jpeg",
                            },
                        ],
                    }
                )

        return messages
