import json
import subprocess
from datetime import datetime
from typing import Dict, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.location import Location

class VideoMetaData:
    def __init__(self, video_path: str):
        """Initialize with path to video file."""
        self.video_path = video_path.replace('\\', '\\\\').replace('"', '\\"')
        self.geocoder = Nominatim(user_agent="my_video_metadata_app")

    def _run_node_script(self, script: str) -> Optional[Dict]:
        """Run Node.js script and return parsed JSON output."""
        try:
            cmd = ['node', '-e', script]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error running Node script: {result.stderr}")
                return None
                
            return json.loads(result.stdout) if result.stdout else None
            
        except Exception as e:
            print(f"Error executing Node script: {e}")
            return None

    def get_video_metadata(self) -> Dict:
        """
        Extract video metadata focusing on:
        - Creation date
        - GPS location (if available)
        """
        script = f"""
        const ffmpeg = require('fluent-ffmpeg');
        const exifr = require('exifr');

        (async () => {{
            try {{
                // Get GPS data using exifr
                const gps = await exifr.gps("{self.video_path}").catch(() => null);
                
                // Get video metadata using fluent-ffmpeg
                ffmpeg.ffprobe("{self.video_path}", (err, metadata) => {{
                    if (err) {{
                        console.error(err);
                        process.exit(1);
                    }}
                    
                    const result = {{
                        creation_time: metadata.format.tags?.creation_time,
                        gps: gps
                    }};
                    
                    console.log(JSON.stringify(result));
                }});
            }} catch (err) {{
                console.error(err);
                process.exit(1);
            }}
        }})();
        """
        
        metadata = self._run_node_script(script) or {}
        
        # Process and format the metadata
        result = {
            'creation_date': self._parse_date(metadata.get('creation_time')),
            'location': self._process_gps(metadata.get('gps'))
        }
        
        return result

    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse creation date string."""
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.isoformat()
        except ValueError:
            return date_str

    def _process_gps(self, gps_data: Optional[Dict]) -> Dict:
        """Process GPS data and get address if coordinates are available."""
        location = {
            'latitude': None,
            'longitude': None,
            'address': None
        }
        
        if gps_data and 'latitude' in gps_data and 'longitude' in gps_data:
            location['latitude'] = gps_data['latitude']
            location['longitude'] = gps_data['longitude']
            location['address'] = self.get_address_from_coordinates(
                gps_data['latitude'], 
                gps_data['longitude']
            )
        
        return location

    def get_address_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """Convert latitude and longitude to address."""
        try:
            location: Location = self.geocoder.reverse((latitude, longitude))
            return location.address if location else None
        except (GeocoderTimedOut, Exception) as e:
            print(f"Error getting address: {e}")
            return None

if __name__ == "__main__":
    # Create instance with video path
    video = VideoMetaData('SampleVideo.MOV')
    
    # Get metadata
    metadata = video.get_video_metadata()
    
    # Print formatted results
    print("\nVideo Metadata:")
    print("--------------")
    print(f"Creation Date: {metadata['creation_date']}")
    
    if metadata['location']['latitude'] and metadata['location']['longitude']:
        print("\nLocation:")
        print(f"GPS: {metadata['location']['latitude']}, {metadata['location']['longitude']}")
        if metadata['location']['address']:
            print(f"Address: {metadata['location']['address']}") 