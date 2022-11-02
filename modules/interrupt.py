import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()

URL = os.getenv('URL')

async def interrupt():
    async with aiohttp.ClientSession() as cs:
        async with cs.post(f"{URL}/sdapi/v1/interrupt") as result:
            print("Interrupted!")