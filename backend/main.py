from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from backend.Judge import process_files

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
UPLOAD_DIR = Path("./temp_uploads")
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
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{upload_file.filename}"
        file_path = UPLOAD_DIR / filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return str(file_path)
    finally:
        await upload_file.close()

def cleanup_old_files(max_age_hours: int = 24):
    """Remove files older than specified hours"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        for file in UPLOAD_DIR.glob("*"):
            try:
                # Get file creation time
                creation_time = datetime.fromtimestamp(file.stat().st_ctime)
                if creation_time < cutoff_time:
                    file.unlink()
            except Exception as e:
                print(f"Error processing {file}: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

@app.post("/process")
async def process_files_endpoint(
    images: Optional[List[UploadFile]] = File(None),
    videos: Optional[List[UploadFile]] = File(None),
    pdfs: Optional[List[UploadFile]] = File(None)
):
    """
    Process uploaded files using the Judge function.
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

        # Process the files using the existing Judge function
        results = process_files(str(UPLOAD_DIR), API_KEY)

        return {
            "status": "success",
            "results": results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing files: {str(e)}"
        }

# Cleanup old files periodically (every 24 hours)
@app.on_event("startup")
async def startup_event():
    cleanup_old_files()

@app.on_event("shutdown")
async def shutdown_event():
    cleanup_old_files()
