import os
import subprocess
import discord
from discord.ext import commands
from utils import YAMLConfigReader, Logger

class UpdateCommands(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.reader = YAMLConfigReader('/config/administration.yml', defaults={
            'admins': [],
        })

    def _allow_command(self, ctx):
        self.reader.update()
        return not str(ctx.author) in self.reader.data.admins

    @commands.group(pass_context=True)
    async def update(self, ctx):
        pass

    @update.command()
    async def help(self, ctx):
        if self._allow_command(ctx):
            return
        await ctx.send('Commands:\n - ' + '\n - '.join(
            [str(cmd) for cmd in self.get_commands()[0].commands]))

    @update.command()
    async def extensions(self, ctx):
        if self._allow_command(ctx):
            return
        if os.path.exists('/app/extensions/.git'):
            res = subprocess.run(['git', 'pull'], cwd='/app/extensions')
            if res.returncode != 0:
                Logger.log('Failed to reload update extensions')
        config = YAMLConfigReader().data
        result_msg = 'Extensions have been reloaded:'
        for extension in config.extensions:
            result = "Success"
            try:
                self.bot.reload_extension(extension)
            except commands.ExtensionNotLoaded:
                try:
                    self.bot.load_extension(extension)
                except commands.ExtensionError as exception:
                    result = str(exception)
            except commands.ExtensionError as exception:
                result = str(exception)
            result_msg += f'\n - {extension}: {result}'
        await ctx.send(result_msg)
        await Logger.log(result_msg)

def setup(bot):
    bot.add_cog(UpdateCommands(bot))
