from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from utils import save_pdf_file, analyze_pdf_content
from pydantic import BaseModel
import json
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware


router = APIRouter()




class AnalyzeRequest(BaseModel):
    file_path: str
    job_description: str


@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    file_path = save_pdf_file(file)
    return {"message": "PDF uploaded successfully.", "file_path": file_path}


# @router.post("/analyze")
# async def analyze(request: AnalyzeRequest):
#     try:
#         print("Analyze API hit ")
#         analysis_result = analyze_pdf_content(request.file_path, request.job_description)
#         data = json.loads(analysis_result)
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/analyze")
async def analyze(resume: UploadFile = File(...), job_description: str = Form(...)):
    try:
        print("Analyze API hit")
        # Ensure the 'storage' folder exists
        storage_dir = os.path.join(os.getcwd(), "storage")
        os.makedirs(storage_dir, exist_ok=True)

        # Prepare the path for saving the uploaded PDF
        file_save_path = os.path.join(storage_dir, resume.filename)

        # Save/replace the uploaded file
        with open(file_save_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        print(f'File saved to: {file_save_path}')

        # Call your analysis function (pass file path in 'storage' directory)
        analysis_result = analyze_pdf_content(file_save_path, job_description)
        data = json.loads(analysis_result)

        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Always clean up the file, even if analysis fails
        if os.path.isfile(file_save_path):
            os.remove(file_save_path)
