import json
import aiohttp
import os
import io
import aiohttp
import discord
import logging
import math
from urllib.parse import urlparse
from modules import values

URL = values.URL

headers = {
    'Content-Type': 'application/json'
}

async def interrogate(image, model):
    data = {
        "image": f"data:image/png;base64,{image}",
        "model": model
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/interrogate", headers=headers, json=data) as resp:
            return await resp.json()

async def upscale(image, upscale_size, model):
    data = {
        "upscaling_resize": upscale_size,
        "upscaler_1": model,
        "image": f"data:image/png;base64,{image}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/extra-single-image", headers=headers, json=data) as resp:
            return await resp.json()
        
async def pnginfo(image):
    data = {
        "image": f"data:image/png;base64,{image}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/sdapi/v1/png-info", headers=headers, json=data) as resp:
            return await resp.json()
        
async def progress():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/sdapi/v1/progress") as resp:
            return await resp.json()

async def check_image(ctx, image_url, image_attachment):
    # check if image url is valid
    if image_url:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        await resp.read()
                    else:
                        embed = error_embed("", "URL image not found...")
                        await ctx.followup.send(embed=embed, ephemeral=True)
                        return None
            except aiohttp.ClientConnectorError as e:
                logging.error('Connection Error', str(e))
                return None
    
    # checks if url is used otherwise use attachment
    if image_url is None:
        # checks if both url and attachment params are missing, then checks if attachment is an image
        if image_attachment is None or image_attachment.content_type not in values.image_media_types:
            embed = error_embed("", "Please attach an image...")
            await ctx.followup.send(embed=embed, ephemeral=True)
            return None

        image_url = image_attachment.url

    return image_url

async def get_image_from_url(image_url):
    # TODO find a better way to convert image to a discord file
    # get image from url then send it as discord.file
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            image = await resp.read()
            with io.BytesIO(image) as img:
                # get filename from url
                a = urlparse(image_url)
                filename = os.path.basename(a.path)
                file = discord.File(img, filename=filename)

    return image, file

def error_embed(title, desc):
        embed = discord.Embed(
            color=discord.Colour.red(),
            title=title,
            description=desc
        )
        return embed

def aproxx_image_dim(width, height, target):
    # Calculate the aspect ratio of the image
    aspect_ratio = max(width, height) / min(width, height)

    # Calculate the new width and height of the image
    if width < height:
        new_width = target
        new_height = math.floor(new_width * aspect_ratio)
    else:
        new_height = target
        new_width = math.floor(new_height * aspect_ratio)

    # Make sure that the new width and height are divisible by 64
    new_width = math.ceil(new_width / 64) * 64
    new_height = math.ceil(new_height / 64) * 64

    return new_width, new_height

