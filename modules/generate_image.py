import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()
URL = os.getenv('URL')
DEFAULTPROMPT = os.getenv('DEFAULTPROMPT')
NEGATIVEPROMPT = os.getenv('NEGATIVEPROMPT')

# TODO place these in a config file at some point
batch_size = 1
steps = 28
cfg_scale = 12

async def generate_image(prompt, neg_prompt, width: int, height: int, seed: int, sampler):

    if DEFAULTPROMPT:
        prompt = f"{DEFAULTPROMPT}, {prompt}"

    if NEGATIVEPROMPT:
        neg_prompt = f"{NEGATIVEPROMPT}, {neg_prompt}"

    # TODO config for parameters
    # edit default steps and CFG scale here
    data = json.dumps({
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "seed": seed,
        "batch_size": batch_size,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height,
        "sampler_index": sampler
    })

    headers = {
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/txt2img", headers=headers, data=data) as resp:
            return await resp.json()
        
async def interrupt():
    async with aiohttp.ClientSession() as cs:
        async with cs.post(f"{URL}/sdapi/v1/interrupt") as result:
            print("Interrupted!")