import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands

import core.embeds as embeds

import os


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_used_prefix(self, ctx):
        if ctx.prefix == "<@!" + str(self.bot.user.id) + "> " or ctx.prefix == "<@" + str(self.bot.user.id) + "> ":
            return "@" + self.bot.user.name + " "
        else:
            return ctx.prefix

    @commands.command(aliases=['commands'])
    async def help(self, ctx, *, command: str = None):
        """
        The new help command.
        ~
        {prefix}help\n{prefix}help copy
        ~
        Use `{prefix}help here` to send a list of commands into the channel (not DM).
        """

        # Get all the cogs
        if not command or command == "here":
            cogs = self.bot.cogs.values()
            cog_commands = [cog.get_commands() for cog in cogs]

        # Get the commands under a specific parent
        else:
            command = command.lower().replace("c!", "")
            got_command = self.bot.get_command(command)
            if not got_command:
                return await ctx.send(embed=embeds.error(f"The command `{command}` could not be found."))
            base_command = got_command

            if isinstance(got_command, commands.Group):
                cog_commands = [list(set(got_command.walk_commands()))]
            else:
                cog_commands = []

        # Check which commands are runnable
        runnable_commands = []
        for cog in cog_commands:
            visible_cog_commands = []
            for thecommand in cog:
                visible_cog_commands.append(thecommand)
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
        if command and command != "here":
            help_embed.title = f"{self.get_used_prefix(ctx)}{base_command.qualified_name} {base_command.signature}"
            description = base_command.help.split("~")
            help_embed.add_field(name="Description", value=description[0].replace("{prefix}", ctx.prefix))
            help_embed.add_field(name="Usage",
                                 value="```" + description[1].strip("\n ").replace("{prefix}", ctx.prefix) + "```")
            try:
                help_embed.add_field(name="Note", value=description[2].replace("{prefix}", ctx.prefix), inline=False)
            except IndexError:
                pass
            if base_command.aliases:
                aliases = "`" + "`, `".join(base_command.aliases) + "`"
            else:
                aliases = "No aliases."
            help_embed.add_field(name="Aliases", value=aliases, inline=False)
            help_embed.set_footer(
                text=f"Use {self.get_used_prefix(ctx)}help to see all the commands." + " " * 30 + "\u200b")
        for cog_commands in runnable_commands:
            value = '\n'.join(
                [f"**{ctx.prefix}{command.qualified_name}** - *{command.short_doc.strip()}*" for command in
                 cog_commands])
            value = value.replace(" - **", "")
            help_embed.add_field(
                name=cog_commands[0].cog_name,
                value=value
            )

        if command:
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

    @commands.command(aliases=["botplzplzplz", "letmehavebot", "iwant"])
    async def invite(self, ctx):
        """
        Get the invite link of the bot.
        ~
        {prefix}invite
        """
        invite = f"https://discordapp.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=67584&scope=bot"
        await ctx.send(embed=discord.Embed(
            color=discord.colour.Colour.teal(),
            description=f":mailbox_with_mail: [Invite]({invite}) me to your server!"))

    @commands.command()
    async def feedback(self, ctx, *, feedback):
        """
        Send feedback about the bot.
        ~
        {prefix}feedback this bot is very good. absolutely amazing!
        {prefix}feedback I have a command idea...
        """
        url = os.environ.get("FEEDBACK_WEBHOOK", None)
        if url:
            webhook = Webhook.from_url(url, adapter=RequestsWebhookAdapter())
            embed = discord.Embed(description=feedback, colour=discord.Colour.teal())
            embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f"User id: {ctx.author.id}")
            webhook.send(embed=embed)
            await ctx.send(embed=embeds.success("Sent the feedback!"))
        else:
            await ctx.send(embed=embeds.error("This command is disabled."))


def setup(bot):
    bot.add_cog(Misc(bot))
