import sys
import os
from typing import Dict, List, Any

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from methods.Image import analyze_property_damage
from methods.ImageMetaData import ImageMetaData
from methods.video_analysis import analyze_property_video
from methods.VideoMetaData import VideoMetaData

def process_files(folder_path: str, api_key: str) -> List[Dict[str, Any]]:
    """Process all files in the given folder and return analysis results."""
    results = []
    
    # Supported file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.heic'}
    video_extensions = {'.mp4', '.mov', '.avi'}
    
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
            
            results.append(file_result)
            
        except Exception as e:
            file_result["error"] = str(e)
            results.append(file_result)
    
    return results

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