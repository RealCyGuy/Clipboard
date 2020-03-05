import discord
from discord.ext import commands


class Misc(commands.Cog):
    """Misc commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        """The invite link!"""
        invite = f"https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=67584&scope=bot"
        await ctx.send(embed=discord.Embed(
            color=discord.colour.Colour.teal(),
            description=f"[Invite]({invite}) me to your server!"))


def setup(bot):
    bot.add_cog(Misc(bot))
