__version__ = "1.2.0"

import discord
from discord.ext import commands
from discord.ext import tasks

from motor.motor_asyncio import AsyncIOMotorClient

import os
import dns
from colorama import Fore, Style

from core.signals import Signals
import core.embeds as embeds

from dotenv import load_dotenv

load_dotenv()


async def get_prefix(bot, message):
    config = await bot.get_config()
    prefixes = config['prefixes']
    if message.guild is None:
        prefix = []
        for guild in bot.guilds:
            if str(guild.id) in prefixes and message.author in guild.members:
                prefix.append(prefixes[str(guild.id)])
        prefix.append(os.environ.get("DEFAULT_PREFIX", "c!"))
        prefix.append("")
        return commands.when_mentioned_or(*prefix)(bot, message)
    else:
        prefix = prefixes.get(str(message.guild.id), os.environ.get("DEFAULT_PREFIX", "c!"))
        return commands.when_mentioned_or(prefix)(bot, message)


class ClipboardBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=get_prefix, *args, **kwargs)
        self.loading_cogs = ["cogs.clipboard", "cogs.settings", "cogs.misc"]
        self.remove_command("help")
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
        await change_status(self)

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
            await context.send_help(context.command)
        elif isinstance(exception, commands.CommandOnCooldown):
            await context.send(
                embed=embeds.error(f"This command is on cooldown. Try again in {exception.retry_after:.2f}s."))
        else:
            print("Unexpected exception: " + str(exception))


@tasks.loop(minutes=2.0)
async def status_update(the_bot):
    if the_bot.is_ready():
        await change_status(the_bot)


async def change_status(the_bot):
    clip_db = await the_bot.get_clipboard()

    copied = len(clip_db["copied"])
    default_prefix = os.environ.get("DEFAULT_PREFIX", "c!")
    servers = "{:,}".format(len(the_bot.guilds))
    text = f"{default_prefix}help | {copied} copied | {servers} servers | v{__version__}"

    old_text = ""
    try:
        old_text = the_bot.guilds[0].me.activity.name
    except IndexError:
        print("I'm in no servers.")
    except AttributeError:
        print("Booting up.")

    if text != old_text:
        print(Fore.CYAN + "=" * 24 + Fore.RESET)
        print("Changing status to:")
        print(Fore.MAGENTA + "-" * 24 + Fore.RESET)
        print(text)
        print(Fore.CYAN + "=" * 24 + Fore.RESET)
        try:
            await the_bot.change_presence(activity=discord.Game(text))
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
