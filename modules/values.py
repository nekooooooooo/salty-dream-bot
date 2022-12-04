import os
import dotenv
import requests
import logging

# TODO store values somewhere better, json or yaml file maybe
dotenv.load_dotenv()


DEFAULTURL = "https//127.0.0.1:7860"
CUSTOMURL = os.getenv('URL')
# use default url if env custom url is not set
URL = DEFAULTURL if not CUSTOMURL else CUSTOMURL

# TODO store strings better for localization
errorMsg = "No connection could be made to AUTOMATIC1111 Stable Diffusion WebUI backend. WebUI might be turned off."

# TODO store values somewhere better, json or yaml file maybe x2
orientation = {
    "square": {
        "ratio_width": 1,
        "ratio_height": 1
    },
    "portrait": {
        "ratio_width": 1,
        "ratio_height": 1.5
    },
    "landscape": {
        "ratio_width": 1.5,
        "ratio_height": 1
    }
}

sizes = {
    "small": {
        "dimensions": 384
    },
    "normal": {
        "dimensions": 512
    },
    "large": {
        "dimensions": 768
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
        logging.info("Getting samplers...")
        resp = requests.get(f"{URL}/sdapi/v1/samplers", headers=headers)
        samplers = []
        for sampler in resp.json():
            samplers.append(sampler['name'])
        return samplers
    except requests.exceptions.RequestException as error:
        logging.info("An error has occured while getting samplers: ", error)
        return []


def get_models():
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        logging.info("Getting models...")
        resp = requests.get(f"{URL}/sdapi/v1/sd-models", headers=headers)
        models = []
        for model in resp.json():
            models.append(model['title'])
        return models
    except requests.exceptions.RequestException as error:
        logging.info("An error has occured while getting models: ", error)
        return []


def get_hypernetworks():
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        logging.info("Getting hypernetworks...")
        resp = requests.get(f"{URL}/sdapi/v1/hypernetworks", headers=headers)
        hypernetworks = []
        for hypernetwork in resp.json():
            hypernetworks.append(hypernetwork['name'])
        return hypernetworks
    except requests.exceptions.RequestException as error:
        logging.error("An error has occured while getting hypernetworks: ", error)
        return []


samplers = get_samplers()
models = get_models()
hypernetworks = get_hypernetworks()
