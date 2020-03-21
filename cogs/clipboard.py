import discord
from discord.ext import commands

import core.embeds as embeds


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

    async def copy_to_clipboard(self, ctx, text):
        clipboard = await self.bot.get_clipboard()
        copied = clipboard["copied"]
        copied[str(ctx.author.id)] = text
        await self.bot.clipboard.find_one_and_update(
            {"_id": "clipboard"},
            {"$set": {"copied": copied}},
            upsert=True,
        )

    @commands.command()
    async def copy(self, ctx, *, text):
        """
        Copies the text.
        ~
        {prefix}copy 12451245
        {prefix}copy I like cheese.
        """
        await self.copy_to_clipboard(ctx, text)
        await ctx.send(embed=embeds.success("Copied!"))

    @commands.command()
    async def paste(self, ctx):
        """
        Pastes the copied text.
        ~
        {prefix}paste
        """
        clipboard = await self.bot.get_clipboard()
        copied = clipboard["copied"]
        if str(ctx.author.id) in copied:
            embed = discord.Embed(description=copied[str(ctx.author.id)], colour=discord.Colour.gold())
            embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        else:
            embed = embeds.error("You don't have anything copied to clipboard.")
            embed.set_footer("Use c!help for more info.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Clipboard(bot))
