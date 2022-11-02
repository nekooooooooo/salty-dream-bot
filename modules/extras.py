import requests
import json
import os
import dotenv

dotenv.load_dotenv()

STABLEDIFFUSIONURL = os.getenv('STABLEDIFFUSIONURL')

def upscale(image64, upscale_size):
    print(f"deez {upscale_size}")