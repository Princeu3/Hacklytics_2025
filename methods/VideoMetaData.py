from datetime import datetime
from typing import Dict, Optional
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.location import Location

class VideoMetaData:
    def __init__(self, video_path: str):
        """Initialize with path to video file."""
        self.video_path = video_path
        self.geocoder = Nominatim(user_agent="my_video_metadata_app")

    def get_video_metadata(self) -> Dict:
        """
        Extract video metadata focusing on:
        - Creation date
        - Location (if available)
        """
        try:
            result = {
                'creation_date': self._get_creation_time(),
                'location': self._extract_gps_data()
            }
            return result
            
        except Exception as e:
            print(f"Error reading video: {e}")
            return {}

    def _extract_gps_data(self) -> Dict:
        """Extract GPS data from video metadata."""
        location = {
            'latitude': None,
            'longitude': None,
            'address': None
        }
        
        try:
            parser = createParser(self.video_path)
            if not parser:
                return location
            
            metadata = extractMetadata(parser)
            if not metadata:
                return location

            # Try to get GPS coordinates
            for key, value in metadata.items():
                if 'gps' in key.lower():
                    if 'latitude' in key.lower():
                        location['latitude'] = float(value)
                    elif 'longitude' in key.lower():
                        location['longitude'] = float(value)

            # If we found coordinates, get the address
            if location['latitude'] and location['longitude']:
                location['address'] = self.get_address_from_coordinates(
                    location['latitude'],
                    location['longitude']
                )
                
        except Exception as e:
            print(f"Error extracting GPS data: {e}")
        
        return location

    def get_address_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """Convert latitude and longitude to address."""
        try:
            location: Location = self.geocoder.reverse((latitude, longitude))
            return location.address if location else None
        except (GeocoderTimedOut, Exception) as e:
            print(f"Error getting address: {e}")
            return None

    def _get_creation_time(self) -> Optional[str]:
        """Get file creation time."""
        try:
            import os
            import platform
            
            # Get file creation time based on OS
            if platform.system() == 'Windows':
                timestamp = os.path.getctime(self.video_path)
            else:  # Unix-based systems
                stat = os.stat(self.video_path)
                try:
                    timestamp = stat.st_birthtime  # macOS
                except AttributeError:
                    timestamp = stat.st_mtime  # Linux
            
            # Convert timestamp to ISO format
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat()
        except Exception as e:
            print(f"Error getting creation time: {e}")
            return None

if __name__ == "__main__":
    # Create instance with video path
    video = VideoMetaData('SampleVideo.MOV')
    
    # Get metadata
    metadata = video.get_video_metadata()
    
    # Print formatted results
    print("\nVideo Metadata:")
    print("--------------")
    print(f"Creation Date: {metadata.get('creation_date')}")
    
    # Print location information if available
    location = metadata.get('location', {})
    if location.get('latitude') and location.get('longitude'):
        print("\nLocation Information:")
        print(f"Latitude: {location['latitude']}")
        print(f"Longitude: {location['longitude']}")
        if location.get('address'):
            print(f"Address: {location['address']}") 