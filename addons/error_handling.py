"""An error handling extension"""
from discord.ext import commands
from utils.logger import Logger

class ErrorHandling(commands.Cog):
    """Extension class for handling errors"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
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

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        msg = '**Error occured in:** {event}\nDetails:\n{sys.exc_info()}'
        await Logger.log(msg)

def setup(bot):
    """Add the extension as a cog"""
    bot.add_cog(ErrorHandling(bot))
