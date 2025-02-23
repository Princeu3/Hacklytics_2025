from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
from pathlib import Path
from backend.fraud_detector import analyze_insurance_claim

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=False,  # Set to False since we're not using credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define constant for upload directory
UPLOAD_DIR = Path("./frontend/public/uploads")
API_KEY = "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"

# Create upload directory if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def clear_upload_directory():
    """Remove all files from the upload directory"""
    try:
        for file in UPLOAD_DIR.glob("*"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Error deleting {file}: {e}")
    except Exception as e:
        print(f"Error clearing directory: {e}")

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file to the temp directory and return its path"""
    try:
        file_path = UPLOAD_DIR / upload_file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return str(file_path)
    finally:
        await upload_file.close()

@app.post("/process")
async def process_files_endpoint(
    images: Optional[List[UploadFile]] = File(None),
    videos: Optional[List[UploadFile]] = File(None),
    pdfs: Optional[List[UploadFile]] = File(None)
):
    """
    Process uploaded files using the fraud detector.
    Each type of file is optional, but at least one file should be provided.
    """
    try:
        # Clear the upload directory before processing new files
        clear_upload_directory()
        
        # Initialize empty lists for missing file types
        images = images or []
        videos = videos or []
        pdfs = pdfs or []

        # Validate that at least one file was uploaded
        if not (images or videos or pdfs):
            return {
                "status": "error",
                "message": "No files provided. Please upload at least one file."
            }

        # Save all uploaded files
        for file in [*images, *videos, *pdfs]:
            await save_upload_file(file)

        # Process the files using the fraud detector
        results = analyze_insurance_claim(str(UPLOAD_DIR), API_KEY)

        satellite_image = UPLOAD_DIR / "satellite_image.jpg"
        
        # Extract fraud assessment details
        fraud_assessment = results.get("fraud_assessment", {})
        
        return {
            "status": "success",
            "fraud_analysis": {
                "probability": fraud_assessment.get("fraud_probability"),
                "risk_level": fraud_assessment.get("risk_level"),
                "summary": fraud_assessment.get("analysis_summary"),
                "raw_analysis": fraud_assessment.get("raw_analysis"),  # Include the complete AI reasoning
                "key_findings": [],  # These will be populated by the frontend based on raw_analysis
                "red_flags": [],
                "recommendations": []
            },

            "claim_details": results.get("claim_processing_results", [])
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing files: {str(e)}"
        }
