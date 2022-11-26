import os
import dotenv
import re
import time
import io, base64
import json
import discord
import aiohttp
import asyncio
from urllib.parse import urlparse
from discord.ui import Button, View
from discord.ext import commands
from modules import generate_image as webui
from modules import values
from modules import extras, interrupt
from modules import interrogate as interr

intents = discord.Intents.default()
intents.message_content = True

dotenv.load_dotenv()
# bot = commands.Bot(
#     command_prefix=config['prefix'],
#     owner_id=config['owner_id']
#     )
bot = commands.Bot()

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")
            print(f"Loaded {file}")

samplers = values.get_samplers()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    print(f"Stable Diffusion x AUTOMATIC1111")

# TODO definitely need to move commands into cogs now
@bot.slash_command(name = "interrogate", description = "interrogate image")
async def interrogate(
        ctx: discord.Interaction,
        image_attachment: discord.commands.Option(
            discord.Attachment,
            "Upload image",
            required=False
        ),
        image_url: discord.commands.Option(
            str,
            "Image URL, this overrides attached image",
            required=False
        ),
        model: discord.commands.Option(
            str,
            "Model to use for interrogating (default CLIP)",
            required=False,
            default="CLIP",
            choices=["CLIP", "DeepDanbooru"]
        )
    ):

    await ctx.response.defer()

    # check if image url is valid
    if image_url:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        await resp.read()
                    else:
                        embed = error_embed("", "URL image not found...")
                        return await ctx.followup.send(embed=embed, ephemeral=True)
            except aiohttp.ClientConnectorError as e:
                print('Connection Error', str(e))
    
    # checks if url is used otherwise use attachment
    if image_url is None:
        # checks if both url and attachment params are missing, then checks if attachment is an image
        if image_attachment is None or image_attachment.content_type not in values.image_media_types:
            embed = error_embed("", "Please attach an image...")
            return await ctx.followup.send(embed=embed, ephemeral=True)

        image_url = image_attachment.url

    await ctx.followup.send(f"Interrogating...")
    
    # TODO find a better way to convert image to a discord file
    # get image from url then send it as a file
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            image = await resp.read()
            with io.BytesIO(image) as img:
                a = urlparse(image_url)
                filename = os.path.basename(a.path)
                file = discord.File(img, filename=filename)

    image_b64 = base64.b64encode(image).decode('utf-8')
    output = await interr.interrogate(image_b64, model.lower())

    tags = output['caption']

    embed = discord.Embed(
        color=discord.Colour.random(),
    )
    embed.add_field(name="📋 Interrogated Prompt",       value=f"```{tags}```")
    embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=bot.user.avatar.url)

    await ctx.interaction.edit_original_response(content="Interrogated!",embed=embed, file=file)

def error_embed(title, desc):
    embed = discord.Embed(
        color=discord.Colour.red(),
        title=title,
        description=desc
    )
    return embed

@bot.event
async def on_guild_join(guild):
    print(f'Joined {guild.name}!')

async def main():
    await load_cogs()
    await bot.start(os.getenv('TOKEN'))
    print("Running bot...")

asyncio.run(main())
