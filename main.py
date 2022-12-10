import os
import dotenv
import discord
import logging
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

dotenv.load_dotenv()
# bot = commands.Bot(
#     command_prefix=config['prefix'],
#     owner_id=config['owner_id']
#     )
bot = commands.Bot()

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

bot.logger = logging.getLogger(__name__)


def load_cogs():
    # Get a list of all files ending with ".py" in the "./cogs" directory
    files = [
        file for file in os.listdir("./cogs") 
        if file.endswith(".py") and file != "tempCodeRunnerFile.py"
    ]
    
    # Iterate over the list of files
    for file in files:
        bot.logger.info(f"Loading {file}")
        bot.load_extension(f"cogs.{file[:-3]}")
        bot.logger.info(f"Loaded {file}")


@bot.event
async def on_ready():
    bot.logger.info(f"{bot.user} is ready and online!")


@bot.event
async def on_guild_join(guild):
    bot.logger.info(f'Joined {guild.name}!')


def main():
    load_cogs()
    bot.logger.info("Running bot...")
    bot.run(os.getenv('TOKEN'))


main()
