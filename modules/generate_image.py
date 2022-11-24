import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()
URL = os.getenv('URL')
DEFAULTPROMPT = os.getenv('DEFAULTPROMPT')
NEGATIVEPROMPT = os.getenv('NEGATIVEPROMPT')

async def generate_image(prompt, neg_prompt, width: int, height: int, seed: int, sampler):

    if DEFAULTPROMPT:
        prompt = f"{DEFAULTPROMPT}, {prompt}"

    if NEGATIVEPROMPT:
        neg_prompt = f"{neg_prompt}, {NEGATIVEPROMPT}"

    data = json.dumps({
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "seed": seed,
        "batch_size": 1,
        "steps": 28,
        "cfg_scale": 11,
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
   
        