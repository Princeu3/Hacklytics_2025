import requests
from inference_sdk import InferenceHTTPClient
from groq import Groq
from PIL import Image
import base64
import io


class SatelliteDamage:
    def __init__(self, config, address):
        self.config = config
        self.img_path = self.config.get("img_path")
        self.address = address

    def get_image(self):

        params = {
            "center": self.address,  # or "latitude,longitude",  # or "address"
            "zoom": 20,
            "size": "600x400",
            "maptype": "satellite",
            "markers": "color:red|label:C|latitude,longitude",
            "key": self.config.get("gmaps_api_key"),
        }

        res = requests.get("https://maps.googleapis.com/maps/api/staticmap", params=params, stream=True)
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        with open(self.config.get("img_path"), "wb") as file:
            for chunk in res.iter_content(1024):
                file.write(chunk)

        print("Map image saved successfully!")

    def classify_image(self):
        # Initialize Groq client
        client = Groq(api_key="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")

        # Load and encode the image
        with open(self.config.get("img_path"), "rb") as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Prepare the prompt for damage assessment
        prompt = """Analyze this satellite image and classify the property damage into one of these categories:
        - no-damage
        - minor-damage
        - major-damage
        - destroyed
        
        Only respond with one of these exact categories."""

        # Call Llama vision model
        completion = client.chat.completions.create(
            model= "llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        # Get the classification from the response
        classification = completion.choices[0].message.content.strip().lower()

        # Validate if the response matches our expected categories
        valid_categories = ["no-damage", "minor-damage", "major-damage", "destroyed"]
        if classification not in valid_categories:
            classification = False

        return classification

    def run(self):
        self.get_image()
        classification = self.classify_image()
        
        findings = {
            "no-damage": "Analysis of satellite imagery shows no damage to the property.",
            "minor-damage": "Analysis of satellite imagery shows minor damage to the property.",
            "major-damage": "Analysis of satellite imagery shows major damage to the property.",
            "destroyed": "Analysis of satellite imagery shows complete destruction of the property."
        }
        
        return findings.get(classification, "Analysis of satellite imagery is inconclusive.")

# Move these outside the class
if __name__ == "__main__":
    # Get address from PDF parsing
    from pdf_Parsing import extract_acroform_fields
    
    pdf_path = "FORM-Dwelling-Property-ENG-9.2022 copy 2.pdf"
    fields = extract_acroform_fields(pdf_path)
    address = fields.get("physical address of the insured propertyrow1", "")
    print(address)
    
    config = {
        "groq_api_key": "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",
        "gmaps_api_key": "AIzaSyBImWOzs5sQJ9P2eipceflVVJhMoixLYxc",
        "img_path": "Images and Videos/satellite_image.jpg"
    }

    sd = SatelliteDamage(config, address)
    var = sd.run()
    print(var)
    