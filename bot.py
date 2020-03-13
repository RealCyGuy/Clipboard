__version__ = "1.0.0"

import discord
from discord.ext import commands
from discord.ext import tasks

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

import os
import json
import dns
from colorama import Fore, Back, Style

from core.signals import Signals

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)


class ClipboardBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        command_prefix = commands.when_mentioned_or("clip!")
        super().__init__(command_prefix=command_prefix, *args, **kwargs)
        self.loading_cogs = ["cogs.clipboard", "cogs.misc"]
        self.help_command = commands.DefaultHelpCommand()
        mongo_uri = config.get("mongo_uri", None)
        if mongo_uri is None or len(mongo_uri.strip()) == 0:
            print("\n" + Signals.FATAL + "A Mongo URI is necessary for the bot to function.\n")
            raise RuntimeError

        self.db = AsyncIOMotorClient(mongo_uri).clipboard_bot
        self.clipboard = self.db.clipboard

        self.startup()

    async def on_ready(self):
        print('-' * 24)
        print('Logged in as:')
        print(Fore.LIGHTMAGENTA_EX + bot.user.name + "#" + bot.user.discriminator + Fore.RESET)
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
                print(f"{Fore.RED}Failed to load {cog}.{Style.RESET_ALL} Error type: {type(e).__name__}")


@tasks.loop(seconds=10.0)
async def status_update(the_bot):
    if the_bot.is_ready():
        new_clipboard = await the_bot.clipboard.find_one({"_id": "clipboard"})
        if new_clipboard is None:
            await the_bot.clipboard.find_one_and_update(
            {"_id": "clipboard"},
            {"$set": {"copied": dict()}},
            upsert=True,
            )
            new_clipboard = await the_bot.clipboard.find_one({"_id": "clipboard"})

        copied = len(new_clipboard["copied"])
        text = f"{copied} copied to clipboard!"

        old_text = ""
        try:
            old_text = the_bot.guilds[0].me.activity.name
        except (IndexError, AttributeError, TypeError):
            pass
        if text != old_text:
            print(f"Changing status to: Watching {text}")
            try:
                await the_bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.watching))
                print(Signals.SUCCESS + "Changed status.")
            except Exception as e:
                print(f"{Signals.ERROR}Failed to update status: {type(e).__name__} {e}")


bot = ClipboardBot()
status_update.start(bot)

token = config.get("token", None)
if token is None or len(token.strip()) == 0:
    print("\n" + Signals.FATAL + "A bot token is necessary for the bot to function.\n")
    raise RuntimeError
else:
    bot.run(token)
