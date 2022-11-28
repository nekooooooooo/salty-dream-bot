import discord
import time
import json
import io
import base64
import re
from discord import option
from discord.ext import commands, tasks
from discord.ui import Button, View
from modules import generate_image
from modules import values, extras

class Dream(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.is_generating = False
    
    @discord.slash_command(name = "dream", description = "Generate Image")
    @option(
        "prompt",
        str,
        description="Enter prompt here",
        max_lenght=500,
        required=True
    )
    @option(
        "neg_prompt",
        str,
        description="Enter negative prompt here",
        max_lenght=500,
        required=False,
    )
    @option(
        "orientation",
        str,
        description="Orientation of the image",
        choices=values.orientation,
        required=False,
    )
    @option(
        "size",
        str,
        description="Size of the image (Large is slow, expect double generation time)",
        choices=values.sizes,
        required=False,
    )
    @option(
        "seed",
        int,
        description="Seed for your image, -1 for random",
        required=False,
    )
    @option(
        "sampler",
        str,
        description="Select sampler (for advanced users, leave empty for default)",
        required=False,
        choices=values.samplers,
    )
    @option(
        "hypernetwork",
        str,
        description="Select hypernetwork (leave empty for default)",
        required=False
    )
    @option(
        "hypernetwork_strenght",
        float,
        description="Select hypernetwork strenght (for advanced users, leave empty for default)",
        required=False,
        min_value=0.0,
        max_value=1.0
    )
    async def dream(
            self, 
            ctx: discord.ApplicationContext,
            prompt: str,
            neg_prompt: str = None,
            orientation: str = "square",
            size: str = "normal",
            seed: int = -1,
            sampler: str = "Euler a",
            hypernetwork: str = None,
            hypernetwork_strenght: float = None
        ):
        await ctx.response.defer()

        # get dimensions and ratio from values.py dictionaries
        # TODO need to find a better way to store these values
        dimensions = values.sizes[size]['dimensions']
        ratio_width = values.orientation[orientation]['ratio_width']
        ratio_height = values.orientation[orientation]['ratio_height']

        # TODO implement queue and remove this ugly fix
        if self.is_generating:
            return await ctx.followup.send(f"Generation in progress... Try again later")
        
        self.is_generating = True

        image, embed = await self.generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed, sampler, hypernetwork, hypernetwork_strenght)
       

        #! fix this sht
        # image, embed, image_b64, filename = await self.generate_image(ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed, sampler)

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

        self.is_generating = False
        await ctx.interaction.edit_original_response(content=f"Generated! {ctx.author.mention}",embed=embed, file=image, view=View())

    # TODO error handling
    # @dream.error
    # async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    #     if isinstance(error, discord.errors.ApplicationCommandInvokeError):
    #         await ctx.respond(error)
    #     else:
    #         raise error
    
    async def generate_image(self, ctx, prompt, neg_prompt, orientation, dimensions, ratio_width, ratio_height, seed, sampler, hypernetwork, hypernetwork_strenght):

        # TODO move interrupt button view into subclass then override interraction check
        interrupt_button = Button(label="Interrupt", style=discord.ButtonStyle.secondary, emoji="❌")

        message = f"Generating ``{prompt}``..."
        await ctx.followup.send(message, view=View(interrupt_button))

        async def interrupt_button_callback(interaction):
            # check for author
            if interaction.user != ctx.author:
                await interaction.response.send_message(f"Only {ctx.author.name} can interrupt...", ephemeral=True)
                return
            await generate_image.interrupt()
            self.progress.cancel()
            await ctx.interaction.edit_original_response(content="Interrupted...")

        interrupt_button.callback = interrupt_button_callback
        
        start = time.time()

        # calculate image width and height based on selected dimensions and orientation
        width = dimensions * ratio_width
        height = dimensions * ratio_height

        log_message = f"""Generating Image

Prompt: {prompt}
Negative Prompt: {neg_prompt}
Composition: {orientation} ({width} x  {height})
Seed: {seed}

        """
        print(log_message)

        self.progress.start(ctx, message)
        output = await generate_image.generate_image(prompt, neg_prompt, width, height, seed, sampler, hypernetwork, hypernetwork_strenght)
        self.progress.cancel()

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

        embed = self.output_embed(prompt, imageWidth, imageHeight, imageSeed, elapsedTime)

        return image, embed
        # return image, embed, image_b64, filename

    async def upscale_button(self, interaction, upscale_size, image_b64, filename):
        await interaction.response.defer()
        await interaction.followup.send(f"Upscaling...")
        upscaled_image = await self.get_upscaled(image_b64, upscale_size, "4x-UltraSharp")
        file = discord.File(upscaled_image, filename=f"{filename}_upscaled_{upscale_size}x.png")
        return await interaction.followup.send(file=file)

    async def get_upscaled(self, image_b64, size, model):
        output = await extras.upscale(image_b64, size, model)

        upscaled_image_b64 = output["image"]
        upscaled_image_b64 = upscaled_image_b64.replace("data:image/png;base64,", "")

        # decode image from base64
        upscaled_image = io.BytesIO(base64.b64decode(upscaled_image_b64))

        return upscaled_image

    def output_embed(self, prompt, imageWidth, imageHeight, imageSeed, elapsedTime):
        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="📋 Prompt",       value=f"```{prompt}```",                     inline=False)
        embed.add_field(name="📐 Size",         value=f"```{imageWidth} x {imageHeight}```", inline=True)
        embed.add_field(name="🌱 Seed",         value=f"```{imageSeed}```",                  inline=True)
        embed.add_field(name="⏱ Elapsed Time", value=f"```{elapsedTime:.2f} second/s```",   inline=True)
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=self.bot.user.avatar.url)

        return embed
    
    @tasks.loop(seconds = 3)
    async def progress(self, ctx, original_message):
        result = await extras.progress()
        progress = result['progress']
        if progress != 0:
            eta = result['eta_relative']
            eta = f"{int(eta)}s" if int(eta) != 0 else "Unknown"
            print(f"{int(progress * 100)}% ETA: {eta}")
            await ctx.interaction.edit_original_response(content=f"{original_message} {int(progress * 100)}% ETA: {eta}")

def setup(bot):
    bot.add_cog(Dream(bot))