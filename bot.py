__version__ = "1.0.0"

import discord
from discord.ext import commands
from discord.ext import tasks

import asyncio
import motor
import os
import json
from colorama import Fore, Back, Style

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)


class ClipboardBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        command_prefix = commands.when_mentioned_or("clip!")
        super().__init__(command_prefix=command_prefix, *args, **kwargs)
        self.loading_cogs = ["cogs.clipboard", "cogs.misc"]
        self.help_command = commands.DefaultHelpCommand()
        self.startup()

    async def on_ready(self):
        print('-' * 24)
        print('Logged in as:')
        print(Fore.LIGHTMAGENTA_EX + bot.user.name + "#" + bot.user.discriminator + Style.RESET_ALL)
        print("Id: " + str(bot.user.id))
        print(f"Discord version: {Fore.CYAN}{discord.__version__}{Style.RESET_ALL}")
        print(f"Bot version: {Fore.CYAN}{__version__}{Style.RESET_ALL}")
        print('-' * 24)

    def startup(self):
        print('=' * 24)
        print("Clipboard")
        print(f"By: {Fore.LIGHTBLUE_EX}Cyrus{Style.RESET_ALL}")
        print('=' * 24)
        for cog in self.loading_cogs:
            print(f"Loading {cog}...")
            try:
                self.load_extension(cog)
                print(f"{Fore.LIGHTGREEN_EX}Successfully loaded {cog}.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Failed to load {cog}.{Style.RESET_ALL}")
                print(e)


@tasks.loop(minutes=2.0)
async def status_update(the_bot):
    if the_bot.is_ready():
        text = "🚧Nothing🚧"

        old_text = ""
        try:
            old_text = the_bot.guilds[0].me.activity.name
        except (IndexError, AttributeError, TypeError):
            pass
        if text != old_text:
            try:
                await the_bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.watching))
                print(f"Changing status to: {text.replace(' ', ' ')}")
            except Exception as e:
                print(f"Failed to update status: {type(e).__name__}")


bot = ClipboardBot()
status_update.start(bot)
bot.run(config["token"])
