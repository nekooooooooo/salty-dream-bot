import os
import dotenv
import discord
import asyncio
from discord.ext import commands

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

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    print(f"Stable Diffusion x AUTOMATIC1111")

@bot.event
async def on_guild_join(guild):
    print(f'Joined {guild.name}!')

async def main():
    await load_cogs()
    await bot.start(os.getenv('TOKEN'))
    print("Running bot...")

asyncio.run(main())
