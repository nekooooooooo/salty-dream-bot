import os
import dotenv
import requests

dotenv.load_dotenv()
URL = os.getenv('URL')

# TODO store strings better for localization
errorMsg = "No connection could be made to AUTOMATIC1111 Stable Diffusion WebUI backend. WebUI might be turned off."

# TODO store values somewhere better, json or yaml file maybe
orientation = {
    "square":{
        "ratio_width":1,
        "ratio_height":1
    },
    "portrait":{
        "ratio_width":1,
        "ratio_height":1.5
    },
    "landscape":{
        "ratio_width":1.5,
        "ratio_height":1
    }
}

sizes = {
    "small":{
        "dimensions":384
    },
    "normal":{
        "dimensions":512
    },
    "large":{
        "dimensions":768
    }
}

image_media_types = [
    "image/png",
    "image/jpeg"
]

def get_samplers():
    headers = {
        'Content-Type': 'application/json'
    }

    resp = requests.get(f"{URL}/sdapi/v1/samplers", headers=headers)
    samplers = []
    for sampler in resp.json():
        samplers.append(sampler['name'])
    return samplers