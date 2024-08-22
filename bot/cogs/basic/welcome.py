from discord.ext import commands
import discord

from bot import SESSION
from bot.ext.misc.response import send_message
from bot.model.auth import Auth


class GuildWelcome(commands.Cog):
    """Cog to handle actions when the bot joins a new guild"""

    def __init__(self, bot: commands.Bot):
        """
        @param bot: The instance of the Discord bot
        """
        self._bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Event triggered when the bot joins a new guild.
        @param guild: The guild (server) that the bot joined
        """
        # Example action: Send a welcome message to the default channel
        if guild.system_channel:
            auth = SESSION.query(Auth).filter(Auth.guild_id == str(guild.id)).first()
            if not auth:
                auth = Auth(
                    guild_id=str(guild.id),
                    owner_id=str(guild.owner_id)
                )
                auth.commit()
            await send_message(guild.system_channel,
                               content=f"Thank you for inviting me to {guild.name}! I'm here to help you. Use `!help` to get started.")


def setup(bot: commands.Bot):
    """Load the GuildWelcome cog"""
    bot.add_cog(GuildWelcome(bot))
