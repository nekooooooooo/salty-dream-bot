import os
import dotenv
import re
import yaml
import time
import io, base64
import json
import discord
from discord.ui import Button, View
from discord.ext import commands
from modules import generate_image as webui
from modules import data as var
from modules import extras, interrupt

intents = discord.Intents.default()
intents.message_content = True

dotenv.load_dotenv()
# bot = commands.Bot(
#     command_prefix=config['prefix'],
#     owner_id=config['owner_id']
#     )
bot = commands.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    print(f"Stable Diffusion x AUTOMATIC1111")

@bot.slash_command(name = "test")
async def test(ctx: discord.Interaction, img: discord.commands.Option(discord.Attachment)):
    img = img
    await ctx.followup.send(file=img)

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
        )
    ):
    
    await ctx.response.defer()

    # get dimensions and ratio from variables.py dictionaries (need to find a better way to store these values)
    dimensions = var.sizes[size]['dimensions']
    ratio_width = var.orientation[orientation]['ratio_width']
    ratio_height = var.orientation[orientation]['ratio_height']

    image, embed = await generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed)

    upscale_2x_button = Button(label="Upscale 2x", style=discord.ButtonStyle.secondary)
    upscale_4x_button = Button(label="Upscale 4x", style=discord.ButtonStyle.secondary)
    regenerate_button = Button(                    style=discord.ButtonStyle.secondary, emoji="🔄")
    save_button       = Button(                    style=discord.ButtonStyle.secondary, emoji="💾")

    # TODO subclass views and buttons
    view = View(upscale_2x_button, upscale_4x_button, regenerate_button, save_button)

    async def upscale_2x_button_callback(interaction):
        # TODO finish upscale
        extras.upscale(image, 2)
        await interaction.response.send_message(embed=embed)

    async def upscale_4x_button_callback(interaction):
        # TODO finish upscale
        extras.upscale(image, 4)
        await interaction.response.send_message(embed=embed)

    async def regeneration_callback(interaction):
        await interaction.response.defer()
        image, embed = await generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed)
        await interaction.followup.send(embed=embed, file=image, view=view)

    upscale_2x_button.callback = upscale_2x_button_callback
    upscale_4x_button.callback = upscale_4x_button_callback
    regenerate_button.callback = regeneration_callback

    await ctx.followup.send(embed=embed, file=image, view=view)

# @dream.error
# async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
#     if isinstance(error, discord.errors.ApplicationCommandInvokeError):
#         await ctx.respond(error)
#     else:
#         raise error

async def generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed):

    # TODO move interrupt button view into subclass then override interraction check
    interrupt_button = Button(label="Interrupt", style=discord.ButtonStyle.secondary, emoji="❌")

    async def interrupt_button_callback(interaction):
        # check for author
        if interaction.user != ctx.author:
            await interaction.response.send_message(f"Only {ctx.author.name} can interrupt...", ephemeral=True)
            return
        await interrupt.interrupt()
        await interaction.response.send_message("Interrupted...")

    interrupt_button.callback = interrupt_button_callback
    await ctx.followup.send(f"Generating ``{prompt}``...", view=View(interrupt_button))

    image, imageWidth, imageHeight, imageSeed, elapsedTime = await get_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed)

    print("Image Generated!")
    print(f"Elapsed Time: {elapsedTime:.2f} second/s")

    embed = output_embed(prompt, imageWidth, imageHeight, imageSeed, elapsedTime)

    return image, embed

async def get_image_info(output):
    image64 = output["images"][0]
    image64 = image64.replace("data:image/png;base64,", "")

    imageInfo = json.loads(output["info"])

    imageWidth = imageInfo["width"]
    imageHeight = imageInfo["height"]

    # regex for getting image seed from old api
    # imageSeed = re.search(r"(\bSeed:\s+)(\S[^,]+)", imageInfo)
    
    imageSeed = imageInfo["seed"]

    return image64, imageWidth, imageHeight, imageSeed

async def get_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed):
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

    output = await webui.generate_image(prompt, neg_prompt, width, height, seed)

    # get generated image and related info from api request 
    image64, imageWidth, imageHeight, imageSeed = await get_image_info(output)

    # decode image from base64
    decoded_image = io.BytesIO(base64.b64decode(image64))

    # remove special characters for filename
    filename = re.sub(r'[\\/*?:"<>|]',"",prompt)
    filename = f"{filename[:200]}_{imageSeed}"
    image = discord.File(decoded_image, filename=f"{filename}.png")

    end = time.time()
    elapsedTime = end - start
    return image, imageWidth, imageHeight, imageSeed, elapsedTime

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

def error_embed(text):
    embed = discord.Embed(
        color=discord.Colour.red(),
        title="An Error has occured!",
        description=text
    )
    return embed

@bot.event
async def on_guild_join(guild):
    print(f'Joined {guild.name}!')

def main():
    print("Running bot...")
    bot.run(os.getenv('TOKEN'))

main()
