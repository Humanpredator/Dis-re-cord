import time
from discord.ext import commands

from bot.__main__ import DiscordClient
from bot.ext.misc.response import send_message, edit_message


class Ping(commands.Cog):
    """Get network latency between you and the server"""

    def __init__(self, bot: DiscordClient):
        """@param bot: The instance of DiscordClient"""
        self._bot = bot

    @commands.command(name="ping", help="Calculate the latency of the server.")
    async def ping_command(self, ctx: commands.Context):
        """
        Command to measure and report latency.
        @param ctx: Discord context
        """
        await self._bot.sudo_only(ctx)
        start_time = int(round(time.time() * 1000))
        msg = await send_message(ctx, "Starting Ping Test...")
        end_time = int(round(time.time() * 1000))
        await edit_message(msg, content=f"{end_time - start_time} ms")


def setup(bot: DiscordClient):
    """Load the Ping cog"""
    bot.add_cog(Ping(bot))
