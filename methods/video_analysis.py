import cv2
from methods.Image import analyze_property_damage
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
    max_consistent_frames: int = 3,
    damage_threshold: float = 0.5
) -> Dict[str, any]:
    """
    Analyze a video for property damage by processing individual frames.
    """
    try:
        # Extract frames from video
        frame_paths = extract_frames(video_path, temp_dir, frame_interval)
        
        if not frame_paths:
            return {"success": False, "error": "No frames could be extracted"}
        
        # Analysis variables
        frame_results = []
        total_frames = len(frame_paths)
        consistent_frames = 0
        damage_count = 0
        
        # Process frames with progress indicator
        print(f"\nProcessing {total_frames} frames...")
        for idx, frame_path in enumerate(frame_paths, 1):
            print(f"Analyzing frame {idx}/{total_frames}", end='\r')
            
            result = analyze_property_damage(frame_path, api_key)
            frame_results.append(result)
            
            # Count frames with damage
            if result.get("has_damage"):
                damage_count += 1
            
            # Early stopping if we have consistent results
            if result.get("has_damage") and result.get("is_house"):
                consistent_frames += 1
                if consistent_frames >= max_consistent_frames:
                    print("\nConfident results obtained - stopping early")
                    break
            else:
                consistent_frames = 0
            
            time.sleep(0.5)  # API rate limit
        
        # Aggregate results
        frames_analyzed = len(frame_results)
        is_house = any(result["is_house"] for result in frame_results)
        
        # Determine if the video has damage based on the threshold
        has_damage = (damage_count / frames_analyzed) >= damage_threshold
        
        # Collect unique damage types directly from the model
        damage_types = set()
        for result in frame_results:
            if result["has_damage"] and result["damage_details"] != "N/A":
                damage_types.add(result["damage_details"])
        
        return {
            "success": True,
            "frames_analyzed": frames_analyzed,
            "total_frames": total_frames,
            "is_house_video": is_house,
            "has_damage": has_damage,
            "damage_types": sorted(list(damage_types))
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
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
    video_path = "6694066-uhd_3840_2160_30fps.mp4"
    
    print("Analyzing video for property damage...")
    results = analyze_property_video(video_path, api_key)
    
    if results["success"]:
        print(f"\nAnalysis completed!")
        print(f"House: {'Yes' if results['is_house_video'] else 'No'}")
        print(f"Damage: {'Yes' if results['has_damage'] else 'No'}")
        
        if results["has_damage"]:
            print("Damage types:", ", ".join(results["damage_types"]))
    else:
        print(f"Error analyzing video: {results['error']}") 