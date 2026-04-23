# main.py
import base64
import json
import logging
from typing import List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from agents.interaction_agent import InteractionAgent
from schemas.patient_input import MediaItem, PatientInput

app = FastAPI(
    title="Agentic RAG Interaction Agent API",
    description="API for testing the InteractionAgent with raw patient input.",
    version="0.1.0",
)

interaction_agent = InteractionAgent()


@app.get("/health")
def health_check():
    return {"status": "ok", "component": "interaction-agent"}


@app.post("/test")
async def test_interaction_agent(
    # ── required text fields ──────────────────────────────────────────────────
    patient_info: str = Form(
        ...,
        description="JSON string of patient demographic/baseline data.",
    ),
    surgery_protocol: str = Form(
        ...,
        description="Text describing surgery or recovery protocol rules.",
    ),
    # ── optional text fields ──────────────────────────────────────────────────
    symptoms: Optional[str] = Form(
        default=None,
        description="Free-text daily symptom report.",
    ),
    medications: Optional[str] = Form(
        default=None,
        description='JSON array of medication strings, e.g. ["Ibuprofen 400mg"].',
    ),
    # ── optional file fields ──────────────────────────────────────────────────
    # Parallel lists: one description per file, matched by position.
    images: Optional[List[UploadFile]] = File(
        default=None,
        description="Medical or recovery-related image files.",
    ),
    image_descriptions: Optional[str] = Form(
        default=None,
        description='JSON array of descriptions for each uploaded image, e.g. ["knee swelling photo"].',
    ),
    documents: Optional[List[UploadFile]] = File(
        default=None,
        description="Medical documents such as reports or discharge summaries.",
    ),
    document_descriptions: Optional[str] = Form(
        default=None,
        description='JSON array of descriptions for each uploaded document, e.g. ["blood test report"].',
    ),
):
    try:
        # ── parse JSON form fields ────────────────────────────────────────────
        try:
            patient_info_dict = json.loads(patient_info)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"'patient_info' must be a valid JSON object: {exc}",
            )

        medications_list: Optional[List[str]] = None
        if medications is not None:
            try:
                medications_list = json.loads(medications)
                if not isinstance(medications_list, list):
                    raise ValueError("Expected a JSON array.")
            except (json.JSONDecodeError, ValueError) as exc:
                raise HTTPException(
                    status_code=422,
                    detail=f"'medications' must be a JSON array of strings: {exc}",
                )

        img_descs: List[str] = (
            json.loads(image_descriptions) if image_descriptions else []
        )
        doc_descs: List[str] = (
            json.loads(document_descriptions) if document_descriptions else []
        )

        # ── convert uploaded files → base64 MediaItems ────────────────────────
        async def files_to_media_items(
            uploads: Optional[List[UploadFile]],
            descriptions: List[str],
            field_name: str,
        ) -> Optional[List[MediaItem]]:
            if not uploads:
                return None

            # Pad missing descriptions with a generic fallback.
            descs = list(descriptions) + [""] * max(0, len(uploads) - len(descriptions))

            items: List[MediaItem] = []
            for idx, upload in enumerate(uploads):
                raw = await upload.read()
                b64 = base64.b64encode(raw).decode("utf-8")
                description = descs[idx] or upload.filename or f"{field_name}_{idx}"
                items.append(MediaItem(file_data=b64, description=description))

            return items

        image_items = await files_to_media_items(images, img_descs, "image")
        document_items = await files_to_media_items(documents, doc_descs, "document")

        # ── build the schema and call the agent ──────────────────────────────
        payload = PatientInput(
            patient_info=patient_info_dict,
            surgery_protocol=surgery_protocol,
            symptoms=symptoms,
            medications=medications_list,
            images=image_items,
            documents=document_items,
        )

        structured_data = interaction_agent.process_raw_input(payload)
        return structured_data

    except HTTPException:
        raise
    except Exception as exc:
        logging.exception("InteractionAgent failed")
        raise HTTPException(
            status_code=500,
            detail=str(exc) or "Interaction agent failure",
        )
