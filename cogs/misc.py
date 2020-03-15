import discord
from discord.ext import commands

import core.embeds as embeds

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_used_prefix(self, ctx):
        if ctx.prefix == "<@!" + str(self.bot.user.id) + "> " or ctx.prefix == "<@" + str(self.bot.user.id) + "> ":
            return "@" + self.bot.user.name + " "
        else:
            return ctx.prefix

    # @commands.group(invoke_without_command=True)
    # async def help(self, ctx):
    #     help_embed = discord.Embed(title='Command Categories', colour=0x56f795)
    #     help_embed.add_field(name='Clipboard', value=f'**{self.get_used_prefix(ctx)}copy <text>**', inline=True)
    #     help_embed.add_field(name='Misc', value=f'*Miscellaneous commands.*', inline=True)
    #     help_embed.set_footer(text=f'Use {self.get_used_prefix(ctx)}help <category> to view the available commands.')
    #     await ctx.send(embed=help_embed)
    #
    # @help.command(name="clipboard")
    # async def help_clipboard(self, ctx):
    #     embed = discord.Embed(title='Clipboard commands:', colour=0x56f795)
    #     embed.description = "Commands related to copying and pasting."
    #     embed.add_field(name=f'`{self.get_used_prefix(ctx)}copy <text>`', value="Copy some text.", inline=True)
    #     embed.add_field(name=f'`{self.get_used_prefix(ctx)}paste`', value="Paste some text.", inline=True)
    #     embed.set_footer(text=f'Use {self.get_used_prefix(ctx)}help to see the categories.')
    #     await ctx.send(embed=embed)
    #
    # @help.command(name="misc")
    # async def help_misc(self, ctx):
    #     embed = discord.Embed(title='Miscellaneous commands:', colour=0x56f795)
    #     embed.description = "Commands that don't really belong anywhere else."
    #     embed.add_field(name=f'`{self.get_used_prefix(ctx)}help [category]`', value="Shows help.", inline=True)
    #     embed.add_field(name=f'`{self.get_used_prefix(ctx)}invite`', value="Get the invite link!.", inline=True)
    #     embed.set_footer(text=f'Use {self.get_used_prefix(ctx)}help to see the categories.')
    #     await ctx.send(embed=embed)

    @commands.command(aliases=['commands'])
    async def help(self, ctx, *, command_name: str = None):
        """The new help command"""

        # Get all the cogs
        if not command_name:
            cogs = self.bot.cogs.values()
            cog_commands = [cog.get_commands() for cog in cogs]

        # Get the commands under a specific parent
        else:
            command_name = command_name.lower()
            command = self.bot
            for i in command_name.split():
                command = command.get_command(i)
                if not command:
                    return await ctx.send(embed=embeds.error(f"The command `{command_name}` could not be found."))
            base_command = command
            if isinstance(command, commands.Group):
                cog_commands = [list(set(command.walk_commands()))]
            else:
                cog_commands = []

        # Check which commands are runnable
        runnable_commands = []
        for cog in cog_commands:
            visible_cog_commands = []
            for command in cog:
                visible_cog_commands.append(command)
            visible_cog_commands.sort(key=lambda x: x.name.lower())  # Sort alphabetically
            if len(visible_cog_commands) > 0:
                runnable_commands.append(visible_cog_commands)

        # Sort cogs list based on name
        runnable_commands.sort(key=lambda x: x[0].cog_name.lower())

        # Make an embed
        help_embed = discord.Embed()
        help_embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        help_embed.colour = 2228207
        help_embed.set_footer(text=f"Use {self.get_used_prefix(ctx)}help <command> to get help for a specific command.")

        # Add commands to it
        if command_name:
            help_embed.add_field(name=f"{self.get_used_prefix(ctx)}{base_command.qualified_name} {base_command.signature}",
                                 value=base_command.help.replace("{prefix}", ctx.prefix))
        for cog_commands in runnable_commands:
            value = '\n'.join(
                [f"**{ctx.prefix}{command.qualified_name}** - *{command.short_doc}*" for command in cog_commands])
            value = value.replace(" - **", "")
            help_embed.add_field(
                name=cog_commands[0].cog_name,
                value=value
            )

        # Send it to the user
        if command_name:
            await ctx.send(embed=help_embed)
        else:
            try:
                await ctx.author.send(embed=help_embed)
                if ctx.guild:
                    await ctx.send(embed=embeds.success("Sent you a DM containing the help message!"))
            except discord.Forbidden:
                await ctx.send(embed=embeds.error("I don't have permissions to send you a DM."))
            except:
                await ctx.send(embed=embeds.error("I couldn't send you a DM."))

    @commands.command()
    async def invite(self, ctx):
        """Get the invite link of the bot."""
        invite = f"https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=67584&scope=bot"
        await ctx.send(embed=discord.Embed(
            color=discord.colour.Colour.teal(),
            description=f":mailbox_with_mail: [Invite]({invite}) me to your server!"))


def setup(bot):
    bot.add_cog(Misc(bot))
