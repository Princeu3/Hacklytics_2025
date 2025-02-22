import cv2
from Image import analyze_property_damage
import os
from typing import Dict, List
import time

def extract_frames(video_path: str, output_dir: str, frame_interval: int = 30) -> List[str]:
    """
    Extract frames from a video file at specified intervals.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames
        frame_interval: Extract one frame every N frames (default: 30)
    
    Returns:
        List of paths to extracted frame images
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    video = cv2.VideoCapture(video_path)
    frame_paths = []
    frame_count = 0
    
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            
        frame_count += 1
        
    video.release()
    return frame_paths

def analyze_property_video(
    video_path: str,
    api_key: str,
    frame_interval: int = 30,
    temp_dir: str = "temp_frames",
    confidence_threshold: float = 0.8,  # Add early stopping threshold
    max_consistent_frames: int = 3  # Number of consistent frames needed
) -> Dict[str, any]:
    """
    Analyze a video for property damage by processing individual frames.
    
    Args:
        video_path: Path to the video file
        api_key: Groq API key
        frame_interval: Extract one frame every N frames
        temp_dir: Directory to temporarily store extracted frames
        confidence_threshold: Threshold for early stopping
        max_consistent_frames: Number of consistent frames needed for early stopping
    """
    try:
        # Extract frames from video
        frame_paths = extract_frames(video_path, temp_dir, frame_interval)
        
        if not frame_paths:
            return {"success": False, "error": "No frames could be extracted", "frames_analyzed": 0}
        
        # Analysis variables
        frame_results = []
        total_frames = len(frame_paths)
        consistent_damage_frames = 0
        damage_confidence_sum = 0
        
        # Process frames with progress indicator
        print(f"\nProcessing {total_frames} frames...")
        for idx, frame_path in enumerate(frame_paths, 1):
            print(f"Analyzing frame {idx}/{total_frames}", end='\r')
            
            result = analyze_property_damage(
                frame_path, 
                api_key
            )
            
            frame_results.append(result)
            damage_confidence_sum += result.get("damage_confidence", 0)
            
            # Early stopping if we have consistent high-confidence damage detection
            if result.get("has_damage") and result.get("damage_confidence", 0) > confidence_threshold:
                consistent_damage_frames += 1
                if consistent_damage_frames >= max_consistent_frames:
                    print("\nHigh confidence damage detected - stopping early")
                    break
            else:
                consistent_damage_frames = 0
            
            time.sleep(0.5)  # API rate limit
        
        # Aggregate results with probabilities
        frames_analyzed = len(frame_results)
        damage_probability = damage_confidence_sum / frames_analyzed
        house_detected = any(result["is_house"] for result in frame_results)
        damage_detected = any(result["has_damage"] for result in frame_results)
        
        # Collect unique damage types with confidence scores
        damage_types = {}
        for result in frame_results:
            if result["has_damage"] and result["damage_details"] != "N/A":
                damage_type = result["damage_details"]
                confidence = result.get("damage_confidence", 0)
                if damage_type in damage_types:
                    damage_types[damage_type] = max(damage_types[damage_type], confidence)
                else:
                    damage_types[damage_type] = confidence
        
        return {
            "success": True,
            "frames_analyzed": frames_analyzed,
            "total_frames": total_frames,
            "is_house_video": house_detected,
            "has_damage": damage_detected,
            "damage_probability": round(damage_probability, 2),
            "damage_types": [{"type": k, "confidence": round(v, 2)} for k, v in damage_types.items()],
            "frame_by_frame_results": frame_results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "frames_analyzed": 0}
    finally:
        # Cleanup temporary frames
        if os.path.exists(temp_dir):
            for frame_path in frame_paths:
                try:
                    os.remove(frame_path)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass

# Example usage
if __name__ == "__main__":
    api_key = "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"
    video_path = "SampleVideo.MOV"
    
    print("Analyzing video for property damage...")
    results = analyze_property_video(video_path, api_key)
    
    if results["success"]:
        print(f"\nAnalysis completed! Processed {results['frames_analyzed']} out of {results['total_frames']} frames")
        print(f"Is this a video of a house? {'Yes' if results['is_house_video'] else 'No'}")
        print(f"Overall damage probability: {results['damage_probability']*100:.1f}%")
        
        if results["has_damage"]:
            print("\nTypes of damage detected:")
            for damage_info in results["damage_types"]:
                print(f"- {damage_info['type']} (Confidence: {damage_info['confidence']*100:.1f}%)")
    else:
        print(f"Error analyzing video: {results['error']}") 