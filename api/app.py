from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import sys
import os
import json
import base64
from typing import List, Optional
from agents.patient_mentor_agent import PatientMentorAgent
from schemas.mentor_state import MentorState
from schemas.recovery_plan import RecoveryPlan
# في أول ملف app.py
from dotenv import load_dotenv
import os

# ده هيخلي البرنامج يدور على الملف في المجلد اللي فوق مجلد api
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add root directory to path to allow importing from root-level modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.interaction_agent import InteractionAgent
from schemas.patient_input import PatientInput, MediaItem

app = FastAPI(
    title="Interaction Agent Test API",
    description="Simple API to test the Interaction Agent with file uploads",
    version="1.0.0"
)

# Initialize only the Interaction Agent for testing
interaction_agent = InteractionAgent()

@app.post("/api/test-interaction-agent", summary="Test Interaction Agent")
async def test_interaction_agent(
    patient_data_json: str = Form(..., description="JSON string containing patient_info (dict), surgery_protocol (str), symptoms (str), and medications (str)"),
    images: Optional[List[UploadFile]] = File(None, description="Image files to upload"),
    image_descriptions: Optional[List[str]] = Form(None, description="Descriptions corresponding to each image"),
    documents: Optional[List[UploadFile]] = File(None, description="Document files (e.g. PDFs) to upload"),
    document_descriptions: Optional[List[str]] = Form(None, description="Descriptions corresponding to each document"),
    thread_id: str = Form("test-thread")
):
    """
    Takes patient data (as JSON string) along with file uploads (images/documents),
    converts the files to base64, constructs the PatientInput schema, 
    runs it through the Interaction Agent, and returns the structured patient data.
    """
    try:
        # Parse the core patient data from JSON
        try:
            data = json.loads(patient_data_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format in patient_data_json")

        # Process and convert images to base64
        media_images = []
        if images:
            img_descs = image_descriptions or []
            for i, img_file in enumerate(images):
                content = await img_file.read()
                b64_data = base64.b64encode(content).decode('utf-8')
                desc = img_descs[i] if i < len(img_descs) else img_file.filename
                media_images.append(MediaItem(file_data=b64_data, description=desc))

        # Process and convert documents to base64
        media_docs = []
        if documents:
            doc_descs = document_descriptions or []
            for i, doc_file in enumerate(documents):
                content = await doc_file.read()
                b64_data = base64.b64encode(content).decode('utf-8')
                desc = doc_descs[i] if i < len(doc_descs) else doc_file.filename
                media_docs.append(MediaItem(file_data=b64_data, description=desc))

        # Construct the PatientInput object expected by the agent
        patient_input = PatientInput(
            patient_info=data.get("patient_info", {}),
            surgery_protocol=data.get("surgery_protocol", ""),
            symptoms=data.get("symptoms"),
            medications=data.get("medications"),
            images=media_images if media_images else None,
            documents=media_docs if media_docs else None
        )
        
        # Run the agent
        structured_data = interaction_agent.process_raw_input(patient_input, thread_id=thread_id)
        
        return {"status": "success", "structured_data": structured_data}
        
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/", summary="Health check")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}

# تحت سطر interaction_agent = InteractionAgent()
mentor_agent = PatientMentorAgent()
# --- نقاط اتصال الـ Patient Mentor Agent ---

@app.post("/api/mentor/initialize", summary="Initialize Patient Recovery Plan")
async def initialize_mentor_plan(plan: RecoveryPlan):
    """
    تأخذ خطة التعافي وترتبها وتبدأ الحالة من الخطوة الأولى.
    """
    try:
        # استدعاء الدالة التي ترتب الخطوات وتصفر الذاكرة
        initial_state = mentor_agent.process_confirmed_plan(plan)
        return {"status": "success", "data": initial_state}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/mentor/update", summary="Process Patient Update")
async def process_patient_step_update(
    current_state: MentorState, 
    patient_message: str = Form(..., description="Message from the patient about their progress")
):
    """
    تأخذ الحالة الحالية للمريض ورسالته، وتقرر:
    1. الانتقال للخطوة التالية (MentorState)
    2. أو طلب توضيح/مراجعة طبية (PatientFeedback)
    """
    try:
        # تشغيل العميل لتحليل الرسالة
        result = mentor_agent.process_patient_update(current_state, patient_message)
        
        # تحديد نوع المخرج لإعلام الواجهة الأمامية (Frontend) بكيفية التصرف
        if isinstance(result, MentorState):
            return {
                "status": "success",
                "type": "state_updated",
                "message": "Patient moved to the next step.",
                "new_state": result
            }
        else:
            return {
                "status": "success",
                "type": "feedback_required",
                "message": "Action required: Question or Medical Review.",
                "feedback": result
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}