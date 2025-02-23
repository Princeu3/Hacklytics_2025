from groq import Groq
import os
import base64
from typing import Dict, Optional

def encode_image(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_property_damage(image_path: str, api_key: str) -> Dict[str, any]:
    """
    Analyze an image for property damage using Groq's vision model.
    
    Args:
        image_path: Path to the image file
        api_key: Groq API key
    
    Returns:
        Dict containing analysis results with keys:
        - is_house: Boolean indicating if image contains a house
        - has_damage: Boolean indicating if damage is present
        - damage_details: String describing the type of damage if present
    """
    try:
        base64_image = encode_image(image_path)
        
        client = Groq(api_key="")
        
        # Enhanced prompt to include damage details
        prompt = """Analyze this image carefully and answer these specific questions:
        1. Is this image of a house/residential property? (Yes/No)
        2. If it is a house, is there any visible property damage? (Yes/No)
        3. If there is damage, describe the type of damage in detail (e.g., water damage, fire damage, structural damage, roof damage, etc.)
        
        Format your response exactly like this:
        HOUSE: Yes/No
        DAMAGE: Yes/No
        DAMAGE_TYPE: [brief description in 2 sentences of damage type and make sure to include the damage type, or N/A if no damage/not a house]
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )

        response = chat_completion.choices[0].message.content
        
        # Parse the response
        result = {
            "is_house": False,
            "has_damage": False,
            "damage_details": "N/A"
        }
        
        for line in response.split('\n'):
            if line.startswith('HOUSE:'):
                result['is_house'] = 'yes' in line.lower()
            elif line.startswith('DAMAGE:'):
                result['has_damage'] = 'yes' in line.lower()
            elif line.startswith('DAMAGE_TYPE:'):
                result['damage_details'] = line.split(':', 1)[1].strip()
        
        return result

    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {"is_house": False, "has_damage": False, "damage_details": "Error occurred"}

# Example usage
if __name__ == "__main__":
    api_key = ""
    image_path = "Mold.png"
    
    result = analyze_property_damage(image_path, api_key)
    print(f"Analysis Results:")
    print(f"Is this a house? {'Yes' if result['is_house'] else 'No'}")
    print(f"Property damage detected? {'Yes' if result['has_damage'] else 'No'}")
    if result['has_damage']:
        print(f"Type of damage: {result['damage_details']}")