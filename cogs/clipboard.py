import discord
from discord.ext import commands


class Clipboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, message):
        """
        Echos your words.
        ~
        {prefix}hi
        """
        await ctx.send(message.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere"))


def setup(bot):
    bot.add_cog(Clipboard(bot))
