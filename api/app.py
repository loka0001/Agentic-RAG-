from fastapi import FastAPI, HTTPException
from agents.interaction_agent import InteractionAgent
from schemas.patient_input import PatientInput
from schemas.structured_patient_data import StructuredPatientData
import logging

app = FastAPI(
    title="Agentic RAG Interaction Agent API",
    description="API for testing the InteractionAgent with raw patient input.",
    version="0.1.0",
)

interaction_agent = InteractionAgent()


@app.get("/health")
def health_check():
    return {"status": "ok", "component": "interaction-agent"}


@app.post(
    "/interaction/test",
    response_model=StructuredPatientData,
    summary="Test the InteractionAgent",
)
def test_interaction_agent(payload: PatientInput):
    try:
        structured_data = interaction_agent.process_raw_input(payload)
        return structured_data
    except Exception as exc:
        logging.exception("InteractionAgent failed")
        raise HTTPException(status_code=500, detail=str(exc) or "Interaction agent failure")
