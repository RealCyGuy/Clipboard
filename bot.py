__version__ = "1.0.0 beta"

import discord
from discord.ext import commands
from discord.ext import tasks

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

import os
import json
import dns
from colorama import Fore, Style

from core.signals import Signals

with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)


class ClipboardBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        command_prefix = ["c!"]
        super().__init__(command_prefix=command_prefix, *args, **kwargs)
        self.loading_cogs = ["cogs.clipboard", "cogs.misc"]
        self.remove_command("help")
        self.activity = discord.Game("\u200b")
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

    async def on_message(self, message):
        if self.user.mentioned_in(message):
            await message.channel.send("My prefix is `c!`. Use `c!help` for help.")
        await self.process_commands(message)

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


@tasks.loop(minutes=1.0)
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
        text = f"{copied} copied to clipboard!\nVersion {__version__}"

        old_text = ""
        try:
            old_text = the_bot.guilds[0].me.activity.name
        except:
            pass
        if text != old_text:
            print(Fore.CYAN + "=" * 24 + Fore.RESET)
            print("Changing status to:")
            print(Fore.MAGENTA + "-" * 24 + Fore.RESET)
            print(f"Watching {text}")
            print(Fore.CYAN + "=" * 24 + Fore.RESET)
            try:
                await the_bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.watching))
                print(f"{Signals.SUCCESS}Changed status.")
            except Exception as e:
                print(f"{Signals.ERROR}Failed to update status: {type(e).__name__}")


bot = ClipboardBot()
status_update.start(bot)

token = config.get("token", None)
if token is None or len(token.strip()) == 0:
    print("\n" + Signals.FATAL + "A bot token is necessary for the bot to function.\n")
    raise RuntimeError
else:
    bot.run(token)
