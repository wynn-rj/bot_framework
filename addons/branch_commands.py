import os
import subprocess
import discord
from discord.ext import commands
from utils import YAMLConfigReader, Logger

# NOTE: It is advised to only use this addon for a development bot

def stdout_cmd(cmd):
    try:
        return subprocess.run(
            cmd.split(' '), capture_output=True, check=True,
            cwd='/app/extensions').stdout.decode('utf-8', 'replace')
    except subprocess.SubprocessError:
        return None

class UpdateCommands(commands.Cog, ):
    def __init__(self, bot):
        self.bot = bot
        self.branch = stdout_cmd('git rev-parse --abbrev-ref HEAD')
        self.reader = YAMLConfigReader('/config/administration.yml', defaults={
            'admins': [],
        })

    @commands.Cog.listener()
    async def on_ready(self):
        await self._update_displayed_branch()

    async def _update_displayed_branch(self):
        await self.bot.change_presence(
            activity=discord.Game(f'on {self.branch}'))

    def _allow_command(self, ctx):
        self.reader.update()
        return not str(ctx.author) in self.reader.data.admins

    @commands.command(name='checkout-branch')
    async def checkout_branch(self, ctx, branch):
        if self._allow_command(ctx):
            return
        if not os.path.exists('/app/extensions/.git'):
            result_msg = 'Bot extensions not a git repo'
        elif branch == self.branch:
            result_msg = 'Already on branch'
        else:
            stdout_cmd('git fetch')
            branches = [s.strip() for s in
                        stdout_cmd('git branch --list').split('\n')]
            if branch in branches:
                # It is safe to use raw user input here because we know
                # it has to be an already existing branch
                stdout_cmd(f'git branch -D {branch}')
                if stdout_cmd(f'git checkout {branch}') is not None:
                    self.branch = branch
                    result_msg = f'Switched to branch {branch}. '\
                        'Please reload the extensions'
                    await Logger.log(result_msg)
                    await self._update_displayed_branch()
                else:
                    result_msg = f'Error switching to branch {branch}'
            else:
                result_msg = f'Unknown branch {branch}'
        await ctx.send(result_msg)

    @commands.command(name='show-branch')
    async def show_branch(self, ctx):
        await self._update_displayed_branch()
        await ctx.send(self.branch)

def setup(bot):
    bot.add_cog(UpdateCommands(bot))
