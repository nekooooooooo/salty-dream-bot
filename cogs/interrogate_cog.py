import discord
import aiohttp
import io
import base64
import os
from urllib.parse import urlparse
from discord.ext import commands
from discord import option
from modules import interrogate as interr
from modules import values

class Interrogate(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name = "interrogate", description = "interrogate image")
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

        # check if image url is valid
        if image_url:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            await resp.read()
                        else:
                            embed = self.error_embed("", "URL image not found...")
                            return await ctx.followup.send(embed=embed, ephemeral=True)
                except aiohttp.ClientConnectorError as e:
                    print('Connection Error', str(e))
        
        # checks if url is used otherwise use attachment
        if image_url is None:
            # checks if both url and attachment params are missing, then checks if attachment is an image
            if image_attachment is None or image_attachment.content_type not in values.image_media_types:
                embed = self.error_embed("", "Please attach an image...")
                return await ctx.followup.send(embed=embed, ephemeral=True)

            image_url = image_attachment.url

        await ctx.followup.send(f"Interrogating...")
        
        # TODO: find a better way to convert image to a discord file
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
        embed.set_footer(text="Salty Dream Bot | AUTOMATIC1111 | Stable Diffusion", icon_url=self.bot.user.avatar.url)

        await ctx.interaction.edit_original_response(content="Interrogated!",embed=embed, file=file)

    def error_embed(self, title, desc):
        embed = discord.Embed(
            color=discord.Colour.red(),
            title=title,
            description=desc
        )
        return embed
    
def setup(bot):
    bot.add_cog(Interrogate(bot))