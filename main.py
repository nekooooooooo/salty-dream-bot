import os
import dotenv
import re
import time
import io, base64
import json
import discord
import aiohttp
from urllib.parse import urlparse
from discord.ui import Button, View
from discord.ext import commands
from modules import generate_image as webui
from modules import data as var
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

samplers = var.get_samplers()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    print(f"Stable Diffusion x AUTOMATIC1111")

# TODO put commands into cogs
@bot.slash_command(name = "dream", description = "Generate Image")
async def dream(
        ctx: discord.Interaction,
        prompt: discord.commands.Option(
            str,
            "Enter prompt here",
            max_length=350,
            required=True
        ),
        neg_prompt: discord.commands.Option(
            str,
            "Enter negative prompt here",
            max_length=300,
            required=False,
            default=""
        ),
        orientation: discord.commands.Option(
            str,
            "Composition of the image",
            choices=var.orientation,
            required=False,
            default="square"
        ),
        size: discord.commands.Option(
            str,
            "Size of the image (Large is slow, expect double generation time)",
            choices=var.sizes,
            required=False,
            default="normal"
        ),
        seed: discord.commands.Option(
            int,
            "Seed for your image, -1 for random",
            required=False,
            default=-1
        ),
        sampler: discord.commands.Option(
            str,
            "Select sampler (for advanced users, leave empty for default)",
            required=False,
            default="Euler a",
            choices=var.get_samplers()
        )
    ):
    
    await ctx.response.defer()

    # get dimensions and ratio from variables.py dictionaries
    # TODO need to find a better way to store these values
    dimensions = var.sizes[size]['dimensions']
    ratio_width = var.orientation[orientation]['ratio_width']
    ratio_height = var.orientation[orientation]['ratio_height']

    image, embed, image_b64, filename = await generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed, sampler)

    # upscale_2x_button = Button(label="Upscale 2x", style=discord.ButtonStyle.secondary)
    # upscale_4x_button = Button(label="Upscale 4x", style=discord.ButtonStyle.secondary)
    # regenerate_button = Button(                    style=discord.ButtonStyle.secondary, emoji="🔄")
    # save_button       = Button(                    style=discord.ButtonStyle.secondary, emoji="💾")

    # # TODO subclass views and buttons
    # view = View(upscale_2x_button, upscale_4x_button, regenerate_button, save_button)

    # # TODO refactor this ugly code, disable buttons when pressed
    # async def upscale_2x_button_callback(interaction):
    #     upscale_size = 2
    #     await upscale_button(interaction, upscale_size, image_b64, filename)

    # async def upscale_4x_button_callback(interaction):
    #     upscale_size = 4
    #     await upscale_button(interaction, upscale_size, image_b64, filename)
        
    # async def regeneration_callback(interaction):
    #     await interaction.response.defer()
    #     interaction.response.edit_message_response()
    #     image, embed, _, _ = await generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed, sampler)
    #     await interaction.followup.send(embed=embed, file=image, view=view)

    # upscale_2x_button.callback = upscale_2x_button_callback
    # upscale_4x_button.callback = upscale_4x_button_callback
    # regenerate_button.callback = regeneration_callback

    # await ctx.followup.send(embed=embed, file=image, view=view)

    await ctx.interaction.edit_original_response(content="Generated...",embed=embed, file=image, view=View())

# TODO error handling
# @dream.error
# async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
#     if isinstance(error, discord.errors.ApplicationCommandInvokeError):
#         await ctx.respond(error)
#     else:
#         raise error
    
async def generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed, sampler):

    # TODO move interrupt button view into subclass then override interraction check
    interrupt_button = Button(label="Interrupt", style=discord.ButtonStyle.secondary, emoji="❌")

    await ctx.followup.send(f"Generating ``{prompt}``...", view=View(interrupt_button))

    async def interrupt_button_callback(interaction):
        # check for author
        if interaction.user != ctx.author:
            await interaction.response.send_message(f"Only {ctx.author.name} can interrupt...", ephemeral=True)
            return
        await interrupt.interrupt()
        await ctx.interaction.edit_original_response(content="Interrupted...")

    interrupt_button.callback = interrupt_button_callback
    
    start = time.time()

    # calculate image width and height based on selected dimensions and orientation
    width = dimensions * ratio_width
    height = dimensions * ratio_height

    log_message = f"""
        Generating Image
        Prompt: {prompt}
        Negative Prompt: {neg_prompt}
        Composition: {orientation} ({width} x  {height})
        Seed: {seed}
    """
    print(log_message)

    output = await webui.generate_image(prompt, neg_prompt, width, height, seed, sampler)

    # get generated image and related info from api request
    image_b64 = output["images"][0]
    image_b64 = image_b64.replace("data:image/png;base64,", "")

    imageInfo = json.loads(output["info"])

    imageWidth = imageInfo["width"]
    imageHeight = imageInfo["height"]

    # regex for getting image seed from old api
    # imageSeed = re.search(r"(\bSeed:\s+)(\S[^,]+)", imageInfo)
    
    imageSeed = imageInfo["seed"]

    # decode image from base64
    decoded_image = io.BytesIO(base64.b64decode(image_b64))

    # remove special characters for filename
    filename = re.sub(r'[\\/*?:"<>|]',"",prompt)
    filename = f"{filename[:200]}_{imageSeed}"
    image = discord.File(decoded_image, filename=f"{filename}.png")

    end = time.time()
    elapsedTime = end - start

    print("Image Generated!")
    print(f"Elapsed Time: {elapsedTime:.2f} second/s")

    embed = output_embed(prompt, imageWidth, imageHeight, imageSeed, elapsedTime)

    return image, embed, image_b64, filename

async def upscale_button(interaction, upscale_size, image_b64, filename):
    await interaction.response.defer()
    await interaction.followup.send(f"Upscaling...")
    upscaled_image = await get_upscaled(image_b64, upscale_size, "4x-UltraSharp")
    file = discord.File(upscaled_image, filename=f"{filename}_upscaled_{upscale_size}x.png")
    return await interaction.followup.send(file=file)

async def get_upscaled(image_b64, size, model):
    output = await extras.upscale(image_b64, size, model)

    upscaled_image_b64 = output["image"]
    upscaled_image_b64 = upscaled_image_b64.replace("data:image/png;base64,", "")

    # decode image from base64
    upscaled_image = io.BytesIO(base64.b64decode(upscaled_image_b64))

    return upscaled_image

def output_embed(prompt, imageWidth, imageHeight, imageSeed, elapsedTime):
    embed = discord.Embed(
        color=discord.Colour.random(),
    )
    embed.add_field(name="📋 Prompt",       value=f"```{prompt}```",                     inline=False)
    embed.add_field(name="📐 Size",         value=f"```{imageWidth} x {imageHeight}```", inline=True)
    embed.add_field(name="🌱 Seed",         value=f"```{imageSeed}```",                  inline=True)
    embed.add_field(name="⏱ Elapsed Time", value=f"```{elapsedTime:.2f} second/s```",   inline=True)
    embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=bot.user.avatar.url)

    return embed

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
            "Model to use for interrogating (default clip)",
            required=False,
            default="clip",
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
        if image_attachment is None or image_attachment.content_type not in var.image_media_types:
            embed = error_embed("", "Please attach an image...")
            return await ctx.followup.send(embed=embed, ephemeral=True)

        image_url = image_attachment.url
    
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

    await ctx.followup.send(embed=embed, file=file)

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

def main():
    print("Running bot...")
    bot.run(os.getenv('TOKEN'))

main()
