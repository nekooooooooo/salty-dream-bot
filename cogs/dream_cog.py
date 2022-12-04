import discord
import time
import json
import io
import base64
import re
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks
from discord.ui import Button, View
from modules import generate_image
from modules import values, extras

class Dream(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.is_generating = False

    dream = SlashCommandGroup("dream", "Generate Image!")
    
    @dream.command(name="txt2img", description="Generate image using text")
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
        "hypernetwork_str",
        float,
        description="Input hypernetwork strenght (for advanced users, leave empty for default)",
        required=False,
        min_value=0.0,
        max_value=1.0
    )
    async def txt2img(
            self, 
            ctx: discord.ApplicationContext,
            prompt: str,
            neg_prompt: str = None,
            orientation: str = "square",
            size: str = "normal",
            seed: int = -1,
            sampler: str = "Euler a",
            hypernetwork: str = None,
            hypernetwork_str: float = None
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

        image, embed = await self.generate_image(
            ctx, prompt, 
            neg_prompt, orientation, 
            dimensions, ratio_width, 
            ratio_height, seed, 
            sampler, hypernetwork, 
            hypernetwork_str)
       

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
        await ctx.interaction.edit_original_response(
            content=f"Generated! {ctx.author.mention}",
            embed=embed, 
            file=image, 
            view=View())

    # TODO error handling
    # @dream.error
    # async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    #     if isinstance(error, discord.errors.ApplicationCommandInvokeError):
    #         await ctx.respond(error)
    #     else:
    #         raise error

    # TODO might just remove subclassing and combine txt2img and img2img into one
    @dream.command(name="img2img", description="Generate image using image")
    @option(
        "image_attachment",
        discord.Attachment,
        description="Upload image",
        required=True
    )
    @option(
        "prompt",
        str,
        description="Enter prompt here",
        max_lenght=500,
        required=True
    )
    @option(
        "image_url",
        str,
        description="Image URL, this overrides attached image",
        required=False
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
        "hypernetwork",
        str,
        description="Select hypernetwork (leave empty for default)",
        required=False
    )
    @option(
        "hypernetwork_str",
        float,
        description="Input hypernetwork strenght (for advanced users, leave empty for default)",
        required=False,
        min_value=0.0,
        max_value=1.0
    )
    async def img2img(
            self, 
            ctx: discord.ApplicationContext,
            image_attachment: discord.Attachment = None,
            prompt: str = None,
            image_url: str = None,
            denoising: float = 0.6,
            neg_prompt: str = None,
            orientation: str = "square",
            size: str = "normal",
            seed: int = -1,
            sampler: str = "Euler a",
            hypernetwork: str = None,
            hypernetwork_str: float = None,
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

        new_image_url = await extras.check_image(ctx, image_url, image_attachment)

        if new_image_url is None:
            self.is_generating = False
            return 

        input_image, file = await extras.get_image_from_url(new_image_url)
        input_image_b64 = base64.b64encode(input_image).decode('utf-8')

        output_image, embed = await self.generate_image(
            ctx, prompt, 
            neg_prompt, orientation, 
            dimensions, ratio_width, 
            ratio_height, seed, 
            sampler, hypernetwork, 
            hypernetwork_str, input_image_b64,
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
        if file:
            await ctx.followup.send(message, view=View(interrupt_button), file=file)
        else:
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

        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="📋 Prompt",
                        value=f"```{prompt}```",
                        inline=False)
        if image_neg_prompt:
            embed.add_field(name="❌ Negative Prompt",
                            value=f"```{image_neg_prompt}```",
                            inline=False)
        embed.add_field(name="📐 Size",
                        value=f"```{image_width} x {image_height}```",
                        inline=True)
        embed.add_field(name="🌱 Seed",
                        value=f"```{image_seed}```",
                        inline=True)
        embed.add_field(name="🧪 Sampler",
                        value=f"```{image_sampler}```",
                        inline=True)
        embed.add_field(name="⚖ CFG Scale",
                        value=f"```{image_scale}```",
                        inline=True)
        embed.add_field(name="👣 Steps",
                        value=f"```{image_steps}```",
                        inline=True)
        embed.add_field(name="⏱ Elapsed Time",
                        value=f"```{elapsed_time:.2f} second/s```",
                        inline=True)
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion",
                         icon_url=self.bot.user.avatar.url)

        return image_b64, embed
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
    bot.add_cog(Dream(bot))