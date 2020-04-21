"""A bot starter framework"""
import os
import discord
from discord.ext import commands
from bot_framework import __version__, JsonConfigReader, Logger, bot_version

def setup_bot(bot, prefix, config):
    """Setup the events and commands the bot responds to"""
    result_msg = f'Bot started!\nVersion: {bot_version}\n' \
                 f'Framework Version: {__version__}\n' \
                  'Extensions:\n'
    for extension in config.extensions:
        result = "Success"
        try:
            bot.load_extension(extension)
        except commands.ExtensionError as exception:
            result = str(exception)
        result_msg += f' - {extension}: {result}'

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord')
        await bot.change_presence(
            activity=discord.Game(name=f'{config.playing} | {prefix}help'))
        await Logger.log(result_msg)

def start_bot():
    """Start the discord bot"""
    config = JsonConfigReader()
    bot = commands.Bot(command_prefix=config.prefix)
    Logger.initialize(bot)
    setup_bot(bot, config.prefix, config)
    bot.run(os.getenv('DISCORD_TOKEN'))
