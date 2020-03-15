import discord


def error(message):
    return discord.Embed(description=message, colour=discord.Colour.red())


def success(message):
    return discord.Embed(description=message, colour=6356861)
