import requests
from inference_sdk import InferenceHTTPClient


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
        # instantiate roboflow api client object
        CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=self.config.get("roboflow_api_key"),
        )

        # classify your image with the roboflow model for xBD
        result = CLIENT.infer(self.config.get("img_path"), model_id="xview2-xbd/10")
        predictions = result["predictions"]
        if len(predictions) >= 1:
            classification = predictions[0]["class"]
        else:
            classification = False

        return classification

    def run(self):

        # download the image from gmaps and save as .jpg file
        self.get_image()

        # use the satellite classification model to determine if the property is damaged.
        classification = self.classify_image()

        # translate output of model to natural language for interpretation by LLM
        if classification == "no-damage":
            finding = "Analysis of satellite imagery shows no damage to the property."
        elif classification == "minor-damage":
            finding = "Analysis of satellite imagery shows minor damage to the property."
        elif classification == "major-damage":
            finding = "Analysis of satellite imagery shows major damage to the property."
        elif classification == "destroyed":
            finding = "Analysis of satellite imagery shows complete destruction of the property."
        else:
            finding = "Analysis of satellite imagery is inconclusive."

        return finding