import os
from difflib import get_close_matches

import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands

import core.embeds as embeds


class ClipboardHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        bot = self.context.bot

        cogs = [bot.get_cog("Clipboard"), bot.get_cog("Settings"), bot.get_cog("Misc")]
        cog_commands = [cog.get_commands() for cog in cogs]

        help_embed = discord.Embed()
        help_embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
        help_embed.colour = 2228207
        help_embed.set_footer(text=f"Use {self.clean_prefix}help [command] to get help for a specific command.")

        for cog_command in cog_commands:
            value = '\n'.join(
                [f"**{self.clean_prefix}{command.qualified_name}** - *{command.short_doc.strip()}*" for command in
                 cog_command])
            value = value.replace(" - **", "")
            help_embed.add_field(
                name=cog_command[0].cog_name,
                value=value
            )
        await self.get_destination().send(embed=help_embed)

    async def send_command_help(self, command):
        bot = self.context.bot

        help_embed = discord.Embed()
        help_embed.set_author(name=bot.user, icon_url=bot.user.avatar_url)
        help_embed.colour = 2228207
        help_embed.set_footer(text=f"Use {self.clean_prefix}help [command] to get help for a specific command.")

        help_embed.title = f"{self.clean_prefix}{command.qualified_name} {command.signature}"
        description = command.help.split("~")
        help_embed.add_field(name="Description", value=description[0].replace("{prefix}", self.clean_prefix))
        help_embed.add_field(name="Usage",
                             value="```" + description[1].strip("\n ").replace("{prefix}", self.clean_prefix) + "```")
        try:
            help_embed.add_field(name="Note", value=description[2].replace("{prefix}", self.clean_prefix),
                                 inline=False)
        except IndexError:
            pass
        if command.aliases:
            aliases = "`" + "`, `".join(command.aliases) + "`"
        else:
            aliases = "No aliases."
        help_embed.add_field(name="Aliases", value=aliases, inline=False)
        help_embed.set_footer(
            text=f"Use {self.clean_prefix}help to see all the commands." +
                 "\n" + "\u2501" * 40 + "\n" +
                 "[]'s are optional arguments. <>'s are required arguments.")
        await self.get_destination().send(embed=help_embed)

    async def send_error_message(self, error):
        command = self.context.kwargs.get("command")
        command_names = set()
        for cmd in self.context.bot.walk_commands():
            if not cmd.hidden:
                command_names.add(cmd.qualified_name)
        closest = get_close_matches(command, command_names, 2)
        if not closest:
            closest = get_close_matches(command, command_names, 1, 0)
        closest = "` or `".join(closest)
        await self.get_destination().send(embed=embeds.error(
            f"Command `{command}` not found. Did you mean `{closest}`?"
        ))


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = ClipboardHelpCommand(
            verify_checks=False,
            command_attrs={
                "help":
                    """
                    Shows this help message.
                    ~
                    {prefix}help
                    {prefix}help invite
                    """
            },
        )
        self.bot.help_command.cog = self

    @commands.command(aliases=["givemebot"])
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
    @commands.cooldown(1, os.environ.get("FEEDBACK_COOLDOWN", 120), commands.BucketType.user)
    async def feedback(self, ctx, *, feedback):
        """
        Send feedback about the bot.
        ~
        {prefix}feedback this bot is very good.
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
