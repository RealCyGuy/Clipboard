import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_used_prefix(self, ctx):
        print(ctx.prefix)
        if ctx.prefix == "<@!" + str(self.bot.user.id) + "> " or ctx.prefix == "<@" + str(self.bot.user.id) + "> ":
            return "@" + self.bot.user.name + " "
        else:
            return ctx.prefix

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        help_embed = discord.Embed(title='Command Categories', colour=0x56f795)
        help_embed.add_field(name='Clipboard', value=f'*Clipboard commands.*', inline=True)
        help_embed.add_field(name='Misc', value=f'*Miscellaneous commands.*', inline=True)
        help_embed.set_footer(text=f'Use {self.get_used_prefix(ctx)}help <category> to view the available commands.')
        await ctx.send(embed=help_embed)

    @help.command(name="clipboard")
    async def help_clipboard(self, ctx):
        embed = discord.Embed(title='Clipboard commands:', colour=0x56f795)
        embed.description = "Commands related to copying and pasting."
        embed.add_field(name=f'`{self.get_used_prefix(ctx)}copy <text>`', value="Copy some text.", inline=True)
        embed.add_field(name=f'`{self.get_used_prefix(ctx)}paste`', value="Paste some text.", inline=True)
        embed.set_footer(text=f'Use {self.get_used_prefix(ctx)}help to see the categories.')
        await ctx.send(embed=embed)

    @help.command(name="misc")
    async def help_misc(self, ctx):
        embed = discord.Embed(title='Miscellaneous commands:', colour=0x56f795)
        embed.description = "Commands that don't really belong anywhere else."
        embed.add_field(name=f'`{self.get_used_prefix(ctx)}help [category]`', value="Shows help.", inline=True)
        embed.add_field(name=f'`{self.get_used_prefix(ctx)}invite`', value="Get the invite link!.", inline=True)
        embed.set_footer(text=f'Use {self.get_used_prefix(ctx)}help to see the categories.')
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        invite = f"https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=67584&scope=bot"
        await ctx.send(embed=discord.Embed(
            color=discord.colour.Colour.teal(),
            description=f":mailbox_with_mail: [Invite]({invite}) me to your server!"))


def setup(bot):
    bot.add_cog(Misc(bot))
