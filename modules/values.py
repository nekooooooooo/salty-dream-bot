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

    try:
        print("Getting samplers...")
        resp = requests.get(f"{URL}/sdapi/v1/samplers", headers=headers)
        samplers = []
        for sampler in resp.json():
            samplers.append(sampler['name'])
        return samplers
    except requests.exceptions.RequestException as error:
        print ("An error has occured while getting samplers: ", error)
        return []
    
def get_models():
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        print("Getting models...")
        resp = requests.get(f"{URL}/sdapi/v1/sd-models", headers=headers)
        models = []
        for model in resp.json():
            models.append(model['title'])
        return models
    except requests.exceptions.RequestException as error:
        print ("An error has occured while getting models: ", error)
        return []
    
def get_hypernetworks():
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        print("Getting hypernetworks...")
        resp = requests.get(f"{URL}/sdapi/v1/hypernetworks", headers=headers)
        hypernetworks = []
        for hypernetwork in resp.json():
            hypernetworks.append(hypernetwork['name'])
        return hypernetworks
    except requests.exceptions.RequestException as error:
        print ("An error has occured while getting hypernetworks: ", error)
        return []