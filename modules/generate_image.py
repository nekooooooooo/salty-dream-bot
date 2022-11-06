import json
import os
import dotenv
import aiohttp
from modules import progress

dotenv.load_dotenv()

URL = os.getenv('URL')
DEFAULTPROMPT = os.getenv('DEFAULTPROMPT')
NEGATIVEPROMPT = os.getenv('NEGATIVEPROMPT')

async def generate_image(ctx, prompt, neg_prompt, width: int, height: int, seed: int):

    if not DEFAULTPROMPT:
        prompt = f"{DEFAULTPROMPT}, {prompt}"

    data = json.dumps({
        "prompt": prompt,
        "negative_prompt": f"{neg_prompt}, {NEGATIVEPROMPT}",
        "seed": seed,
        "batch_size": 1,
        "steps": 28,
        "cfg_scale": 11,
        "width": width,
        "height": height,
        "sampler_index": "Euler A"
    })

    headers = {
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as cs:
        async with cs.post(f"{URL}/sdapi/v1/txt2img", headers=headers, data=data) as r:
            # print(r.status)
            res = await r.json()
            return res

    # r = requests.request("POST", TXT2IMGURL, headers=headers, data=data)

    # with open("data/output.json", "w") as text_file:
    #     text_file.write(r.text) 

    # return r.json()
        

# generate_image("test", "", 512, 512, -1)
    
   
        