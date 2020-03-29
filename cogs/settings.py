import discord
from discord.ext import commands

import core.embeds as embeds

import os
from core.text import code


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def prefix(self, ctx, new_prefix=None):
        """
        View and change the prefix
        ~
        {prefix}prefix
        {prefix}prefix ?
        {prefix}prefix thisisthenewprefix
        ~
        Use without param to view the prefix.
        """
        if new_prefix is not None:
            if ctx.guild is None:
                await ctx.send(embed=embeds.error("You can only change prefixes in a server."))
            else:
                if ctx.author.permissions_in(ctx.channel).manage_guild:
                    user_id = self.bot.user.id
                    if new_prefix not in [f'<@{user_id}>', f'<@!{user_id}>']:
                        if len(new_prefix) < 20:
                            config = await self.bot.get_config()
                            prefixes = config["prefixes"]
                            prefixes[str(ctx.guild.id)] = new_prefix
                            await self.bot.config.find_one_and_update(
                                {"_id": "config"},
                                {"$set": {"prefixes": prefixes}},
                                upsert=True,
                            )
                            embed = embeds.success(f"Changed prefix to `{new_prefix}`.")
                            embed.set_footer(text="You can always mention me!")
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send(embed=embeds.error("Prefix must be under 20 characters."))
                    else:
                        await ctx.send(embed=embeds.error("Mentions are already usable."))
                else:
                    await ctx.send(embed=embeds.error("You need the `manage_guild` permission to do this."))
        else:
            embed = discord.Embed(title=f"Command Prefixes", colour=discord.Colour.dark_magenta())

            default_prefix = os.environ.get("DEFAULT_PREFIX", "c!")
            embed.add_field(name="Default Prefix", value=code(default_prefix), inline=True)

            config = await self.bot.get_config()
            prefixes = config["prefixes"]
            if ctx.guild is not None:
                server_prefix = prefixes.get(str(ctx.guild.id), default_prefix)
                embed.add_field(name="Server Prefix", value=code(server_prefix), inline=True)

            dm_prefixes = [code(default_prefix)]
            for guild in self.bot.guilds:
                if str(guild.id) in prefixes and ctx.author in guild.members:
                    dm_prefixes.append(code(prefixes[str(guild.id)]))
            embed.add_field(name=ctx.author.name + "'s DM prefixes.", value=", ".join(dm_prefixes))

            embed.set_footer(text="You can always mention me!")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Settings(bot))
