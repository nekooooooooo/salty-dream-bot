import json
import aiohttp
from modules.values import URL

URL = URL

headers = {
    'Content-Type': 'application/json'
}

async def interrogate(image, model):
    data = json.dumps({
        "image": f"data:image/png;base64,{image}",
        "model": model
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/interrogate", headers=headers, data=data) as resp:
            return await resp.json()

async def upscale(image, upscale_size, model):
    data = json.dumps({
        "upscaling_resize": upscale_size,
        "upscaler_1": model,
        "image": f"data:image/png;base64,{image}"
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/extra-single-image", headers=headers, data=data) as resp:
            return await resp.json()
        
async def pnginfo(image):
    data = json.dumps({
        "image": f"data:image/png;base64,{image}"
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/png-info", headers=headers, data=data) as resp:
            return await resp.json()
        
async def progress():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/sdapi/v1/progress") as resp:
            return await resp.json()

