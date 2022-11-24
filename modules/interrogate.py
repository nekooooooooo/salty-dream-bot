import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()

URL = os.getenv('URL')

async def interrogate(image, model):

    data = json.dumps({
        "image": f"data:image/png;base64,{image}",
        "model": model
    })

    headers = {
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/interrogate", headers=headers, data=data) as resp:
            return await resp.json()