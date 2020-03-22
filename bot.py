__version__ = "1.0.1"

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
import core.embeds as embeds

from dotenv import load_dotenv

load_dotenv()


async def get_prefix(bot, message):
    if message.guild is None:
        prefix = os.environ.get("DEFAULT_PREFIX", "c!")
    else:
        config = await bot.get_config()
        prefixes = config['prefixes']
        prefix = prefixes.get(str(message.guild.id), os.environ.get("DEFAULT_PREFIX", "c!"))

    return commands.when_mentioned_or(prefix)(bot, message)


class ClipboardBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        command_prefix = commands.when_mentioned_or("c!")
        super().__init__(command_prefix=get_prefix, *args, **kwargs)
        self.loading_cogs = ["cogs.clipboard", "cogs.misc"]
        self.remove_command("help")
        self.activity = discord.Game("\u200b")
        mongo_uri = os.environ.get("MONGO_URI", None)
        if mongo_uri is None or len(mongo_uri.strip()) == 0:
            print("\n" + Signals.FATAL + "A Mongo URI is necessary for the bot to function.\n")
            raise RuntimeError

        self.db = AsyncIOMotorClient(mongo_uri).clipboard_bot
        self.clipboard = self.db.clipboard
        self.config = self.db.config

        self.startup()

    async def on_ready(self):
        print('-' * 24)
        print('Logged in as:')
        print(Fore.LIGHTMAGENTA_EX + bot.user.name + "#" + bot.user.discriminator + Fore.RESET)
        print("Id: " + str(bot.user.id))
        print(f"Discord version: {Fore.CYAN}{discord.__version__}{Style.RESET_ALL}")
        print(f"Bot version: {Fore.CYAN}{__version__}{Style.RESET_ALL}")
        print('-' * 24)
        print(f"{Signals.SUCCESS}I am logged in and ready!")

    # async def on_guild_join(self, guild):
    #     config = await self.get_config()
    #     config["prefixes"][str(guild.id)] = "c!"
    #     await self.clipboard.find_one_and_update(
    #         {"_id": "config"},
    #         {"$set": {"prefixes": config}},
    #         upsert=True,
    #     )

    async def get_clipboard(self):
        new_clipboard = await self.clipboard.find_one({"_id": "clipboard"})
        if new_clipboard is None:
            await self.clipboard.find_one_and_update(
                {"_id": "clipboard"},
                {"$set": {"copied": dict()}},
                upsert=True,
            )
            new_clipboard = await self.clipboard.find_one({"_id": "clipboard"})
        return new_clipboard

    async def get_config(self):
        new_config = await self.config.find_one({"_id": "config"})
        if new_config is None:
            await self.config.find_one_and_update(
                {"_id": "config"},
                {"$set": {"prefixes": dict()}},
                upsert=True,
            )
            new_config = await self.config.find_one({"_id": "config"})
        return new_config

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

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.BadUnionArgument):
            msg = "Could not find the specified " + str([c.__name__ for c in exception.converters])

            await context.trigger_typing()
            await context.send(embed=embeds.error(msg))

        elif isinstance(exception, commands.BadArgument):
            await context.trigger_typing()
            await context.send(
                embed=embeds.error(str(exception))
            )
        elif isinstance(exception, commands.CommandNotFound):
            print("CommandNotFound: " + str(exception))
        elif isinstance(exception, commands.MissingRequiredArgument):
            await context.send(embed=embeds.error("Missing required arguments."))
        else:
            print("Unexpected exception: " + str(exception))


@tasks.loop(seconds=1.0)
async def status_update(the_bot):
    if the_bot.is_ready():
        clip_db = await the_bot.get_clipboard()

        copied = len(clip_db["copied"])
        default_prefix = os.environ.get("DEFAULT_PREFIX", "c!")
        text = f"{copied} copied to clipboard! Version {__version__} | {default_prefix}help"

        old_text = the_bot.guilds[0].me.activity.name
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

token = os.environ.get("TOKEN", None)
if token is None or len(token.strip()) == 0:
    print("\n" + Signals.FATAL + "A bot token is necessary for the bot to function.\n")
    raise RuntimeError
else:
    bot.run(token)
