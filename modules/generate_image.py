import os
import dotenv
import aiohttp
import logging
from modules.values import URL

dotenv.load_dotenv()
DEFAULTPROMPT = os.getenv('DEFAULTPROMPT')
NEGATIVEPROMPT = os.getenv('NEGATIVEPROMPT')

# TODO place these in a config file at some point
batch_size = 1
steps = 28
cfg_scale = 12

async def generate_image(
    prompt, neg_prompt, 
    width: int, height: int, 
    seed: int, sampler, 
    hypernetwork=None, hypernetwork_str=None, 
    image=None, denoising=0.6):

    if DEFAULTPROMPT:
        prompt = f"{DEFAULTPROMPT}, {prompt}"

    if NEGATIVEPROMPT:
        neg_prompt = f"{NEGATIVEPROMPT}, {neg_prompt}"

    logging.info(f"primary_prompt={prompt}, secondary_prompt={neg_prompt}, width={width}, height={height}, seed={seed}, sampler={sampler}, hypernetwork={hypernetwork}, hypernetwork_str={hypernetwork_str}, denoising={denoising}")

    # TODO config for parameters
    # edit default steps and CFG scale here

    data = {
            "prompt": prompt,
            "negative_prompt": neg_prompt,
            "seed": seed,
            "batch_size": batch_size,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "sampler_index": sampler
        }
    url = f"{URL}/sdapi/v1/txt2img"

    if image:
        logging.info("Using image")
        img2img_data = {
            "init_images": [
                f"data:image/png;base64,{image}"
            ],
            "denoising_strength": denoising
        }
        data.update(img2img_data)
        url = f"{URL}/sdapi/v1/img2img"

    headers = {
        'Content-Type': 'application/json'
    }

    override_settings = {}

    if hypernetwork:
        override_settings["sd_hypernetwork"] = hypernetwork
    
    if hypernetwork_str:
        override_settings["sd_hypernetwork_strength"] = hypernetwork_str

    override_data = {
        "override_settings": override_settings
    }

    data.update(override_data)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                return await resp.json()
    except Exception as e:
        # Handle any errors that occurred during the API call
        return logging.exception(e)
            
async def interrupt():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/interrupt") as result:
            logging.info("Interrupted!")