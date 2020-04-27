import discord
from discord.ext import commands
from utils import YAMLConfigReader, Logger

class AdminCommands(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.reader = YAMLConfigReader('/config/administration.yml', defaults={
            'admins': [],
            'log_channels': []
        })

    def _allow_command(self, ctx):
        return not str(ctx.author) in self.reader.data.admins

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
        if str(new_admin) in self.reader.data.admins:
            await ctx.send(f'{new_admin.mention} is already and admin')
            return
        self.reader.update()
        self.reader.data.admins += [str(new_admin)]
        self.reader.save()
        await Logger.log(f'User {new_admin} has been made an admin')
        await ctx.send(
            f'Made {new_admin.mention} an admin for {self.bot.user.name}')

    @admin.command(name='log-to-channel')
    async def log_to_channel(self, ctx, channel: discord.TextChannel):
        if self._allow_command(ctx):
            return
        if channel.id in self.reader.data.log_channels:
            await ctx.send('Logging is already being sent to that channel')
            return
        self.reader.update()
        self.reader.data.log_channels += [channel.id]
        self.reader.save()
        Logger.update_logging()
        await channel.send(
            f'Logging for {self.bot.user.name} is now being sent here')

def setup(bot):
    bot.add_cog(AdminCommands(bot))
