import subprocess
import threading
import discord
from discord.ext import commands
from bot_framework import JsonConfigReader, Logger

class AdminCommands(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.data = JsonConfigReader('framework_data.json')
        self._update_lock = threading.Lock()

    def _allow_command(self, ctx):
        return not str(ctx.author) in self.data.admins

    @commands.group(pass_context=True)
    async def admin(self, ctx):
        if self._allow_command(ctx):
            return
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid subcommand')

    @admin.command()
    async def help(self, ctx):
        if self._allow_command(ctx):
            return
        await ctx.send('Commands:\n - ' + '\n - '.join(
            [str(cmd) for cmd in self.get_commands()[0].commands]))

    @admin.command()
    @commands.is_owner()
    async def add(self, ctx, new_admin: discord.Member):
        if str(new_admin) in self.data.admins:
            await ctx.send(f'{new_admin.mention} is already and admin')
            return
        self.data.update()
        self.data.admins += [str(new_admin)]
        self.data.save()
        await Logger.log(f'User {new_admin} has been made an admin')
        await ctx.send(
            f'Made {new_admin.mention} an admin for {self.bot.user.name}')

    @admin.command(name='log-to-channel')
    async def log_to_channel(self, ctx, channel: discord.TextChannel):
        if self._allow_command(ctx):
            return
        if channel.id in self.data.log_channels:
            await ctx.send('Logging is already being sent to that channel')
            return
        self.data.update()
        self.data.log_channels += [channel.id]
        self.data.save()
        Logger.update_logging()
        await channel.send(
            f'Logging for {self.bot.user.name} is now being sent here')

    @admin.command()
    async def update(self, ctx):
        if self._allow_command(ctx):
            return
        self._update_lock.acquire()
        try:
            await self.safe_update(ctx)
        finally:
            self._update_lock.release()

    async def safe_update(self, ctx):
        result = subprocess.run(['git', 'remote', 'show', 'origin'],
                                stdout=subprocess.PIPE)
        if 'up to date' in str(result.stdout):
            await ctx.send('No new version found')
            return
        await ctx.send('Updating bot')
        result = subprocess.run(['git', 'pull', '--recurse-submodules'])
        if result.returncode != 0:
            await ctx.send('Failed to update bot')
            await Logger.log(result.stdout)
            return
        config = JsonConfigReader()
        from ..version import __version__
        try:
            from version import __version__ as bot_version
        except:
            bot_version = 'Unknown'
        result_msg = f'Bot updated!\nVersion: {bot_version}\n' \
                     f'Framework Version: {__version__}\n' \
                     'Extensions:'
        for extension in config.extensions:
            result = 'Success'
            try:
                self.bot.load_extension(extension)
            except commands.ExtensionAlreadyLoaded:
                self.bot.reload_extension(extension)
            except commands.ExtensionError as exception:
                result = str(exception)
            result_msg += f'\n - {extension}: {result}'
        await Logger.log(result_msg)
        await ctx.send('Bot successfully updated')

def setup(bot):
    bot.add_cog(AdminCommands(bot))
