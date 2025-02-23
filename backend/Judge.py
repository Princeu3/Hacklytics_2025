import sys
import os
from typing import Dict, List, Any
import re

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from methods.Image import analyze_property_damage
from methods.ImageMetaData import ImageMetaData
from methods.video_analysis import analyze_property_video
from methods.VideoMetaData import VideoMetaData
from methods.pdf_Parsing import extract_acroform_fields
from methods.SatelliteImagery import SatelliteDamage

def process_files(folder_path: str, api_key: str) -> List[Dict[str, Any]]:
    """Process all files in the given folder and return analysis results."""
    results = []
    
    # Supported file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.heic'}
    video_extensions = {'.mp4', '.mov', '.avi'}
    pdf_extensions = {'.pdf'}
    
    # First find and process PDF to get the address
    address = None
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            fields = extract_acroform_fields(pdf_path)
            address = fields.get("physical address of the insured propertyrow1") or fields.get("postal addressrow1")
            break

    # Configure satellite imagery
    satellite_config = {
        "groq_api_key": "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",
        "gmaps_api_key": "AIzaSyBImWOzs5sQJ9P2eipceflVVJhMoixLYxc",
        "img_path": os.path.join(folder_path, "satellite_image.jpg")
    }
    
    # Get satellite imagery analysis if address is available
    satellite_results = None
    if address:
        try:
            sd = SatelliteDamage(satellite_config, address)
            satellite_results = sd.run()
        except Exception as e:
            satellite_results = {"error": str(e)}
    
    # Process each file in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1].lower()
        
        file_result = {
            "filename": filename,
            "file_type": None,
            "analysis_results": None,
            "metadata": None
        }
        
        try:
            # Process images
            if ext in image_extensions:
                file_result["file_type"] = "image"
                # Get image analysis
                file_result["analysis_results"] = analyze_property_damage(file_path, api_key)
                # Get image metadata
                file_result["metadata"] = ImageMetaData(file_path).get_metadata()
            
            # Process videos
            elif ext in video_extensions:
                file_result["file_type"] = "video"
                # Get video analysis
                file_result["analysis_results"] = analyze_property_video(file_path, api_key)
                # Get video metadata
                file_result["metadata"] = VideoMetaData(file_path).get_video_metadata()
            
            # Process PDFs
            elif ext in pdf_extensions:
                file_result["file_type"] = "pdf"
                fields = extract_acroform_fields(file_path)
                
                # Format PDF results similar to other analyses
                file_result["analysis_results"] = {
                    "insured_name": fields.get("named insureds full namerow1") or fields.get("full namerow1"),
                    "physical_address": fields.get("physical address of the insured propertyrow1") or fields.get("postal addressrow1"),
                    "mobile_number": fields.get("text1") or fields.get("fill_24"),
                    "email": fields.get("email"),
                    "type_of_loss": fields.get("undefined_4"),
                    "loss_description": fields.get("description of loss and damagesrow1"),
                    "date_of_loss": _format_date_of_loss(
                        fields.get("undefined_5"),
                        fields.get("undefined_6"),
                        fields.get("undefined_7")
                    ),
                    "damages_list": _extract_damages_list(fields),
                    "satellite_analysis": satellite_results  # Add satellite analysis to PDF results
                }
            
            results.append(file_result)
            
        except Exception as e:
            file_result["error"] = str(e)
            results.append(file_result)
    
    return results

def _format_date_of_loss(month: str, day: str, year: str) -> str:
    """Helper function to format date of loss."""
    if month and day and year:
        return f"{month.strip()}/{day.strip()}/{year.strip()}"
    return None

def _extract_damages_list(fields: Dict) -> List[str]:
    """Helper function to extract and format damages list."""
    damages = []
    for key in fields:
        if key.isdigit():
            damage_text = fields[key]
            if damage_text and damage_text.strip():
                # Remove leading numbers and whitespace
                cleaned_text = re.sub(r"^\d+\s*", "", damage_text.strip())
                damages.append(cleaned_text)
    return sorted(damages)

if __name__ == "__main__":
    # Configuration
    api_key = "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"
    folder_path = "./Images and Videos"  # Create this folder and put your files in it
    
    # Make sure the sample_files directory exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created directory: {folder_path}")
        print("Please put your files in this directory and run the script again")
        sys.exit(0)
    
    # Process all files
    print("Processing files...")
    results = process_files(folder_path, api_key)
    
    # Print results
    for result in results:
        print("\n" + "="*50)
        print(f"File: {result['filename']}")
        print(f"Type: {result['file_type']}")
        
        if "error" in result:
            print(f"Error: {result['error']}")
            continue
            
        if result["analysis_results"]:
            print("\nAnalysis Results:")
            for key, value in result["analysis_results"].items():
                print(f"{key}: {value}")
        
        if result["metadata"]:
            print("\nMetadata:")
            for key, value in result["metadata"].items():
                print(f"{key}: {value}")