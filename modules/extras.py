import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()

URL = os.getenv('URL')

async def upscale(image, upscale_size, model):
    data = json.dumps({
        "upscaling_resize": upscale_size,
        "upscaler_1": model,
        "image": f"data:image/png;base64,{image}"
    })

    headers = {
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/extra-single-image", headers=headers, data=data) as resp:
            return await resp.json()