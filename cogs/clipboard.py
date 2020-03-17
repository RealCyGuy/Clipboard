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

    @commands.command()
    async def copy(self, ctx, *, text):
        """
        Copies the text.
        ~
        {prefix}copy 12451245
        {prefix}copy I like cheese.
        """
        pass

    @commands.command()
    async def paste(self, ctx):
        """
        Pastes the copied text.
        ~
        {prefix}paste
        """
        pass



def setup(bot):
    bot.add_cog(Clipboard(bot))
