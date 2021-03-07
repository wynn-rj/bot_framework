#! /usr/bin/env python3

"""Pamus, A discord bot framework"""
import os
import subprocess
import discord
from discord.ext import commands
from utils.config_reader import YAMLConfigReader
from utils.logger import Logger
from version import __version__

def setup_bot(bot, prefix, config):
    """Sets up the events and commands the bot responds to via extensions"""
    result_msg = 'Bot started!\nUsing Pamus framework Version: ' \
                 f'{__version__}\nExtensions:'
    error_occurred = False
    for extension in config.data.extensions:
        result = "Success"
        try:
            bot.load_extension(extension)
        except commands.ExtensionError as exception:
            result = str(exception)
            error_occurred = True
        result_msg += f'\n - {extension}: {result}'

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord')
        if config.data.playing:
            await bot.change_presence(activity=discord.Game(
                config.data.playing.replace('{prefix}', prefix)))
        if error_occurred or config.data.log_on_successful_startup:
            await Logger.log(result_msg)

def main():
    """Start the discord bot"""
    config = YAMLConfigReader(defaults={
        'prefix': '!',
        'playing': None,
        'extensions': [],
        'log_on_successful_startup': True,
    })
    bot = commands.Bot(command_prefix=config.data.prefix)
    Logger.initialize(bot)
    if os.path.exists('/app/extensions/requirements.txt'):
        subprocess.run(['pip3', 'install', '-r',
                        '/app/extensions/requirements.txt'], check=True)
    setup_bot(bot, config.data.prefix, config)
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    main()
