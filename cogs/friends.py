import discord
import time
import json
import io
import base64
import re
import logging
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks
from discord.ui import Button, View
from modules import generate_image
from modules import values, extras
from PIL import Image


class Friends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_generating = False

    # friend requested for this command, uses mostly anythingv3 model
    @discord.slash_command(name="lazyanimeify", description="animeify image")
    @option(
        "image_attachment",
        discord.Attachment,
        description="Upload image",
        required=True
    )
    @option(
        "image_url",
        str,
        description="Image URL, this overrides attached image",
        required=False
    )
    @option(
        "prompt",
        str,
        description="Enter prompt here",
        max_lenght=500,
        required=False,
    )
    @option(
        "denoising",
        float,
        description="Input denoising strenght",
        required=False,
        min_value=0.0,
        max_value=1.0
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
        "model",
        str,
        description="model lol",
        required=False,
        choices=['clip', 'deepdanbooru'],
    )
    async def lazyanimeify(
            self, 
            ctx: discord.ApplicationContext,
            image_attachment: discord.Attachment = None,
            image_url: str = None,
            prompt: str = "",
            denoising: float = 0.65,
            neg_prompt: str = None,
            orientation: str = None,
            size: str = "normal",
            seed: int = -1,
            sampler: str = "Euler a",
            model: str = "deepdanbooru"
        ):
        await ctx.response.defer()


        # TODO implement queue and remove this ugly fix
        if self.is_generating:
            return await ctx.followup.send(f"Generation in progress... Try again later")
        
        self.is_generating = True

        new_image_url = await extras.check_image(ctx, image_url, image_attachment)

        if new_image_url is None:
            self.is_generating = False
            return 

        input_image, file = await extras.get_image_from_url(new_image_url)
        input_image_b64 = base64.b64encode(input_image).decode('utf-8')

        # image_height = image_attachment.height
        # image_width = image_attachment.width

        with Image.open(io.BytesIO(input_image)) as image:
            image_width, image_height = image.size

        # Determine the orientation of the image
        if not orientation:
            # Compare the image height and width
            if image_height > image_width:
                orientation = "portrait"
            elif image_height < image_width:
                orientation = "landscape"
            else:
                orientation = "square"

            # Calculate the aspect ratio
            aspect_ratio = abs(max(image_width, image_height) / min(image_width, image_height))
            # Check if the aspect ratio is close to 1 (indicating a square image)
            if (aspect_ratio - 1) < 0.2:
                orientation = "square"

        # get dimensions and ratio from values.py dictionaries
        # TODO need to find a better way to store these values
        dimensions = values.sizes[size]['dimensions']
        ratio_width = values.orientation[orientation]['ratio_width']
        ratio_height = values.orientation[orientation]['ratio_height']

        logging.info("Interrogating")
        await ctx.followup.send("Interrogating...")
        output = await extras.interrogate(input_image_b64, model)

        interrogated_prompt = f"{output['caption']}"
        # print the original interrogated prompt
        logging.info(f"Interrogated: {interrogated_prompt}")
        # split the prompt into a list of words, using ", " as the delimiter
        words = interrogated_prompt.split(", ")
        # create a list of words that will be removed from the prompt
        words_to_remove = [
            "lips", "photorealistic", "realistic", 
            "nose", "blurry", 
            "3d", "long fingernails", "fingernails"]
        # print the list of words that will be removed
        logging.info(f"Removing: {words_to_remove}")
        # create a new list of words by only keeping those words that are not in words_to_remove
        resultwords = [word for word in words if word.lower() not in words_to_remove]
        # combine the resulting words into a string, using ", " as the delimiter
        result =  ', '.join(resultwords)
        # print the final prompt
        logging.info(f"New Prompt: {result}")
        
        prompt = f"{result}, {prompt}" if prompt else f"{result}"

        neg_prompt = neg_prompt or "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name"

        output_image, embed = await self.generate_image(
            ctx, prompt, 
            neg_prompt, orientation, 
            dimensions, ratio_width, 
            ratio_height, seed, 
            sampler, None, 
            None, input_image_b64,
            denoising, file)

        self.is_generating = False
        await ctx.interaction.edit_original_response(
            content=f"Generated! {ctx.author.mention}",
            embed=embed, 
            file=output_image, 
            view=View())
            
    async def generate_image(self, 
            ctx, prompt, 
            neg_prompt, orientation, 
            dimensions, ratio_width, 
            ratio_height, seed, 
            sampler, hypernetwork, 
            hypernetwork_str, image_b64=None,
            denoising=None, file=None):

        # TODO move interrupt button view into subclass then override interraction check
        interrupt_button = Button(label="Interrupt", style=discord.ButtonStyle.secondary, emoji="❌")

        message = f"Generating ``{prompt}``..."

        view = View(interrupt_button)
        await ctx.interaction.edit_original_response(content=message, view=view, file=file if file else None)

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
Seed: {seed}"""
        self.bot.logger.info(log_message)
        
        self.progress.start(ctx, message)

        output = await generate_image.generate_image(
            prompt, neg_prompt, 
            width, height, 
            seed, sampler, 
            hypernetwork, hypernetwork_str,
            image_b64, denoising)

        self.progress.cancel()

        # get generated image and related info from api request
        image_b64 = output["images"][0]
        image_b64 = image_b64.replace("data:image/png;base64,", "")

        image_info = json.loads(output["info"])
        image_width = image_info["width"]
        image_height = image_info["height"]
        # regex for getting image seed from old api
        # imageSeed = re.search(r"(\bSeed:\s+)(\S[^,]+)", imageInfo)
        image_seed = image_info["seed"]
        image_sampler = image_info["sampler_name"]
        image_scale = image_info["cfg_scale"]
        image_steps = image_info["steps"]
        image_neg_prompt = image_info["negative_prompt"]

        # decode image from base64
        decoded_image = io.BytesIO(base64.b64decode(image_b64))

        # remove special characters for filename
        filename = re.sub(r'[\\/*?:"<>|]',"",prompt)
        filename = f"{filename[:200]}_{image_seed}"
        image_b64 = discord.File(decoded_image, filename=f"{filename}.png")

        end = time.time()
        elapsed_time = end - start

        self.bot.logger.info("Image Generated!")
        self.bot.logger.info(f"Elapsed Time: {elapsed_time:.2f} second/s")

        embed = discord.Embed(color=discord.Colour.random())

        # define the fields to be added to the embed object
        fields = [
            ("📋 Prompt", f"```{prompt}```", False),
            ("❌ Negative Prompt", f"```{image_neg_prompt}```", False),
            ("📐 Size", f"```{image_width} x {image_height}```", True),
            ("🌱 Seed", f"```{image_seed}```", True),
            ("🧪 Sampler", f"```{image_sampler}```", True),
            ("⚖ CFG Scale", f"```{image_scale}```", True),
            ("👣 Steps", f"```{image_steps}```", True),
            ("⏱ Elapsed Time", f"```{elapsed_time:.2f} second/s```", True),
        ]

        # add the fields to the embed object using a loop
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        # set the footer for the embed object
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion",
                        icon_url=self.bot.user.avatar.url)

        return image_b64, embed

    @tasks.loop(seconds = 3)
    async def progress(self, ctx, original_message):
        result = await extras.progress()
        progress = result['progress']
        if progress > 0:
            eta = result['eta_relative']
            eta = f"{int(eta)}s" if int(eta) != 0 else "Unknown"
            self.bot.logger.info(f"{int(progress * 100)}% ETA: {eta}")
            await ctx.interaction.edit_original_response(content=f"{original_message} {int(progress * 100)}% ETA: {eta}")

def setup(bot):
    bot.add_cog(Friends(bot))