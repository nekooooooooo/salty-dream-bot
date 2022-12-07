import discord
import base64
import logging
from discord import option
from discord.ext import commands
from discord.commands import SlashCommandGroup
from modules import values, extras

class Extras(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="interrogate", description="interrogate image")
    @option(
        "image_attachment",
        discord.Attachment,
        description="Upload image",
        required=False
    )
    @option(
        "image_url",
        str,
        description="Image URL, this overrides attached image",
        required=False
    )
    @option(
        "model",
        str,
        description="Model to use for interrogating (default CLIP)",
        required=False,
        default="CLIP",
        choices=["CLIP", "DeepDanbooru"]
    )
    async def interrogate(
            self,
            ctx: discord.ApplicationContext,
            image_attachment: discord.Attachment,
            image_url: str,
            model: str
        ):

        await ctx.response.defer()

        # check if url and image is valid
        #! this implementation is extremely ugly and dirty, need to find a better way
        new_image_url = await extras.check_image(ctx, image_url, image_attachment)

        if new_image_url is None:
            return
        
        await ctx.followup.send(f"Interrogating using {model}...")

        image, file = await extras.get_image_from_url(image_url)

        image_b64 = base64.b64encode(image).decode('utf-8')
        output = await extras.interrogate(image_b64, model.lower())

        tags = output['caption']

        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="📋 Interrogated Prompt", value=f"```{tags}```")
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=self.bot.user.avatar.url)

        await ctx.interaction.edit_original_response(content="Interrogated!",embed=embed, file=file)

    @discord.slash_command(name = "pnginfo", description = "View information about generation parameters")
    @option(
        "image_attachment",
        discord.Attachment,
        description="Upload image",
        required=False
    )
    @option(
        "image_url",
        str,
        description="Image URL, this overrides attached image",
        required=False
    )
    async def pnginfo(
            self,
            ctx: discord.ApplicationContext,
            image_attachment: discord.Attachment,
            image_url: str,
        ):

        await ctx.response.defer()

        # Check if the provided image URL or attachment is valid
        #! this implementation is extremely ugly and dirty, need to find a better way
        new_image_url = await extras.check_image(ctx, image_url, image_attachment)

        if new_image_url is None:
            return
        
        await ctx.followup.send(f"Getting info...")
        
        # Retrieve the image data from the URL
        image, file = await extras.get_image_from_url(new_image_url)

        # Encode the image data as a base64 string
        image_b64 = base64.b64encode(image).decode('utf-8')

        # Retrieve information about the PNG image
        output = await extras.pnginfo(image_b64)

        if png_info == '':
            png_info = "No info found"

        png_info = output['info']
        self.bot.logger.info(png_info)


        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="📋 PNG Info", value=f"```{png_info}```")
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=self.bot.user.avatar.url)

        await ctx.interaction.edit_original_response(content="",embed=embed, file=file)

    
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    hns = list(chunks(values.hypernetworks, 10))
    logging.info(f"{len(hns)} pages of hypernetworks loaded...")

    show = SlashCommandGroup("show", "Show stuff!")

    # TODO Pagination for large lists of hypernetworks
    @show.command(name="hypernetworks", description="Show list of hypernetworks")
    @option(
        "page",
        int,
        description="Select page",
        required=True,
        default=1,
        min_value=1,
        max_value=len(hns)
    )
    async def hypernetworks(self, 
            ctx: discord.ApplicationContext,
            page: int,
        ):

        value=""

        for hypernetwork in self.hns[page-1]:
            value = value + f"``{hypernetwork}``\n"

        embed = discord.Embed(
            color=discord.Colour.random(),
        )
        embed.add_field(name="Hypernetworks", value=f"{value}")
        await ctx.respond(embed=embed)

    
def setup(bot):
    bot.add_cog(Extras(bot))