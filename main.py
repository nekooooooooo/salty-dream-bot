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

def load_cogs():
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

def main():
    load_cogs()
    print("Running bot...")
    bot.run(os.getenv('TOKEN'))

main()
