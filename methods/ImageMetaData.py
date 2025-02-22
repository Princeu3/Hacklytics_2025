import json
import subprocess
from datetime import datetime
from typing import Dict, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.location import Location

class ImageMetaData:
    def __init__(self, image_path: str):
        """Initialize with path to image file."""
        # Escape backslashes and quotes in the path
        self.image_path = image_path.replace('\\', '\\\\').replace('"', '\\"')
        # Initialize geocoder with a custom user agent
        self.geocoder = Nominatim(user_agent="my_image_metadata_app")
        
    def _run_node_script(self, script: str) -> Optional[Dict]:
        """Run Node.js script and return parsed JSON output."""
        try:
            # Create Node.js command that runs exifr
            cmd = ['node', '-e', script]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error running Node script: {result.stderr}")
                return None
                
            return json.loads(result.stdout) if result.stdout else None
            
        except Exception as e:
            print(f"Error executing Node script: {e}")
            return None

    def get_gps_location(self) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from image.
        Returns tuple of (latitude, longitude) or None if not found.
        """
        script = f"""
        const exifr = require('exifr');
        (async () => {{
            try {{
                const gps = await exifr.gps("{self.image_path}");
                console.log(JSON.stringify(gps));
            }} catch (err) {{
                console.error(err);
                process.exit(1);
            }}
        }})();
        """
        
        gps_data = self._run_node_script(script)
        if gps_data and 'latitude' in gps_data and 'longitude' in gps_data:
            return (gps_data['latitude'], gps_data['longitude'])
        return None

    def get_capture_date(self) -> Optional[datetime]:
        """
        Extract capture date from image.
        Returns datetime object or None if not found.
        """
        script = f"""
        const exifr = require('exifr');
        (async () => {{
            try {{
                const data = await exifr.parse("{self.image_path}", ['DateTimeOriginal', 'CreateDate']);
                console.log(JSON.stringify(data));
            }} catch (err) {{
                console.error(err);
                process.exit(1);
            }}
        }})();
        """
        
        metadata = self._run_node_script(script)
        if metadata:
            # Try DateTimeOriginal first, then CreateDate as fallback
            date_str = metadata.get('DateTimeOriginal') or metadata.get('CreateDate')
            if date_str:
                try:
                    # Try ISO format first (YYYY-MM-DDTHH:MM:SS.sssZ)
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        # Try EXIF format (YYYY:MM:DD HH:MM:SS)
                        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    except ValueError:
                        print(f"Unrecognized date format: {date_str}")
                        return None
        return None

    def get_address_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert latitude and longitude to address.
        Returns formatted address string or None if conversion fails.
        """
        try:
            location: Location = self.geocoder.reverse((latitude, longitude))
            return location.address if location else None
        except (GeocoderTimedOut, Exception) as e:
            print(f"Error getting address: {e}")
            return None

    def get_coordinates_from_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to latitude and longitude.
        Returns tuple of (latitude, longitude) or None if conversion fails.
        """
        try:
            location: Location = self.geocoder.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            return None
        except (GeocoderTimedOut, Exception) as e:
            print(f"Error getting coordinates: {e}")
            return None

    def get_metadata(self) -> Dict:
        """
        Get both GPS location and capture date.
        Returns dictionary with location and date information.
        """
        location = self.get_gps_location()
        date = self.get_capture_date()
        
        metadata = {
            'location': {
                'latitude': location[0] if location else None,
                'longitude': location[1] if location else None,
                'address': None
            },
            'capture_date': date.isoformat() if date else None
        }
        
        # If we have coordinates, try to get the address
        if location:
            metadata['location']['address'] = self.get_address_from_coordinates(location[0], location[1])
            
        return metadata

if __name__ == "__main__":
    # Create instance with image path
    image = ImageMetaData('MetadataTest.HEIC')
    
    # Get metadata which now includes address automatically
    metadata = image.get_metadata()
    
    # Print formatted results
    print("\nImage Metadata:")
    print("--------------")
    
    if metadata['location']['latitude'] and metadata['location']['longitude']:
        print(f"GPS Coordinates: {metadata['location']['latitude']}, {metadata['location']['longitude']}")
        if metadata['location']['address']:
            print(f"Address: {metadata['location']['address']}")
    else:
        print("No GPS coordinates found in image")
        
    if metadata['capture_date']:
        print(f"Capture Date: {metadata['capture_date']}")
    else:
        print("No capture date found in image")


