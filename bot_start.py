"""A bot starter framework"""
import os
import sys
import discord
from discord.ext import commands
from bot_framework import __version__, JsonConfigReader, Logger, bot_version

def setup_bot(bot, prefix, config):
    """Setup the events and commands the bot responds to"""
    result_msg = f'Bot started!\nVersion: {bot_version}\n' \
                 f'Framework Version: {__version__}\n' \
                  'Extensions:'
    for extension in config.extensions:
        result = "Success"
        try:
            bot.load_extension(extension)
        except commands.ExtensionError as exception:
            result = str(exception)
        result_msg += f'\n - {extension}: {result}'

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord')
        await bot.change_presence(
            activity=discord.Game(name=f'{config.playing} | {prefix}help'))
        await Logger.log(result_msg)

    @bot.event
    async def on_command_error(ctx, error):
        type_responses = {
            commands.CommandNotFound: None,
            commands.BadArgument: 'Bad Argument',
            commands.TooManyArguments: 'Too many arguments',
            commands.MissingRequiredArgument: 'Missing required arguments',
        }

        for error_type, msg in type_responses.items():
            if isinstance(error, error_type):
                if msg:
                    await ctx.send(msg)
                return
        await Logger.log(str(error))

    @bot.event
    async def on_error(event, *args, **kwargs):
        msg = '**Error occured in:** {event}\nDetails:\n{sys.exc_info()}'
        await Logger.log(msg)


def start_bot():
    """Start the discord bot"""
    config = JsonConfigReader()
    bot = commands.Bot(command_prefix=config.prefix)
    Logger.initialize(bot)
    setup_bot(bot, config.prefix, config)
    bot.run(os.getenv('DISCORD_TOKEN'))
