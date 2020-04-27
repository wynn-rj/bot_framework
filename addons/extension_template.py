"""A template/example extension file"""
import discord
from discord.ext import commands

class ExtensionTemplate(commands.Cog):
    """Extension class"""
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    """Add the extension as a cog"""
    bot.add_cog(ExtensionTemplate(bot))
