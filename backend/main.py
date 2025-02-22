from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import List, Dict, Any
import shutil
import os
from pathlib import Path
import uuid
import asyncio
import base64
from groq import Groq

def encode_image(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_property_damage(image_path: str, api_key: str) -> Dict[str, any]:
    """Analyze an image for property damage using Groq's vision model."""
    try:
        base64_image = encode_image(image_path)
        client = Groq(api_key="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")
        
        prompt = """Analyze this image carefully and answer these specific questions:
        1. Is this image of a house/residential property? (Yes/No)
        2. If it is a house, is there any visible property damage? (Yes/No)
        3. If there is damage, describe the type of damage in detail (e.g., water damage, fire damage, structural damage, roof damage, etc.)
        
        Format your response exactly like this:
        HOUSE: Yes/No
        DAMAGE: Yes/No
        DAMAGE_TYPE: [Detailed description of damage type, or N/A if no damage/not a house]
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )

        response = chat_completion.choices[0].message.content
        
        result = {"is_house": False, "has_damage": False, "damage_details": "N/A"}
        
        for line in response.split('\n'):
            if line.startswith('HOUSE:'):
                result['is_house'] = 'yes' in line.lower()
            elif line.startswith('DAMAGE:'):
                result['has_damage'] = 'yes' in line.lower()
            elif line.startswith('DAMAGE_TYPE:'):
                result['damage_details'] = line.split(':', 1)[1].strip()
        
        return result
    except Exception as e:
        return {"is_house": False, "has_damage": False, "damage_details": "Error occurred"}

app = FastAPI()

TEMP_DIR = "./temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

def save_temp_file(uploaded_file: UploadFile) -> str:
    file_ext = uploaded_file.filename.split(".")[-1]
    temp_filename = f"{uuid.uuid4()}.{file_ext}"
    temp_filepath = Path(TEMP_DIR) / temp_filename
    
    with temp_filepath.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    
    return str(temp_filepath)

def process_with_ai_models(file_paths: List[str]) -> Dict[str, Any]:
    results = {}
    for file_path in file_paths:
        results[file_path] = analyze_property_damage(file_path, "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")
    return results

@app.post("/process")
async def process_request(
    images: List[UploadFile] = File(None), 
    videos: List[UploadFile] = File(None), 
    pdfs: List[UploadFile] = File(None)
):
    if not (images or videos or pdfs):
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    file_paths = []
    
    for file_group in [images, videos, pdfs]:
        if file_group:
            for file in file_group:
                file_path = save_temp_file(file)
                file_paths.append(file_path)
    
    loop = asyncio.get_event_loop()
    ai_results = await loop.run_in_executor(None, process_with_ai_models, file_paths)
    
    return {"status": "success", "results": ai_results}
