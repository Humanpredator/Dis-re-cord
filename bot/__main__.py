import os
import time
from typing import Any, Optional, List

import discord
from discord import Message
from discord.ext import commands

from bot import SESSION, ENGINE, LOGGER, BOT_TOKEN
from bot.ext.command.help import MyHelpCommand
from bot.ext.misc.response import send_message
from bot.model.auth import Auth


class DiscordClient(commands.Bot):
    """Discord Bot"""

    def __init__(
            self,
            command_prefix="!",
            *,
            intents=discord.Intents.all(),
            **options: Any,
    ):
        """
        @param command_prefix: Symbol used to invoke the commands
        @param intents: Scope to be used
        @param options: Optional key=value arguments
        """
        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        self.bot_start_time = time.time()
        self.logger = LOGGER.logger
        self.help_command = MyHelpCommand()
        self.db_tables: Optional[List[Any]] = [Auth]
        self.module_path = os.path.dirname(os.path.abspath(__file__))
        self._create_tables()

    @staticmethod
    def _get_all_users(guild_id) -> List[int]:
        """
        Get all users who have access to invoke commands
        @return: List of user IDs
        """
        with SESSION as session:
            user_data: Auth = session.query(Auth).filter(Auth.guild_id == str(guild_id)).first()
        return user_data.retrieve() if user_data else []

    @staticmethod
    async def owner_only(ctx: commands.Context) -> bool | Message:
        """
        Check if the command is invoked by the guild owner
        @param ctx: Discord context
        @return: True if the author is the guild owner, otherwise False
        """
        if ctx.author.id != ctx.guild.owner_id:
            return await send_message(ctx, "You are not allowed to use this command")
        return True

    async def sudo_only(self, ctx: commands.Context) -> bool | Message:
        """
        Check if the command is invoked by a sudo user in the DB
        @param ctx: Discord context or user ID
        @return: True if the author or user ID is in the allowed list, otherwise False
        """
        user_id = ctx.author.id if isinstance(ctx, commands.Context) else ctx
        if user_id not in user_id in self._get_all_users(ctx.guild.id):
            return await send_message(ctx, "You are not allowed to use this command")
        return True

    def _create_tables(self):
        for table in self.db_tables:
            table.__table__.create(ENGINE, checkfirst=True)
        return True

    async def _load_default(self) -> None:
        """Load default cogs"""
        self.logger.info("Loading Default Cogs, Please Wait...")
        cog_dir = os.path.join(self.module_path, "cogs")
        for root, _, files in os.walk(cog_dir):
            for filename in files:
                if filename.endswith(".py") and filename != "__init__.py":
                    rel_path = os.path.relpath(os.path.join(root, filename), self.module_path)
                    cog_module = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")
                    cog_module = f"bot.{cog_module}"
                    self.load_extension(cog_module)
        self.logger.info("All Cogs Were Loaded!")
        self.logger.info("Discord Bot Online!")

    def run_bot(self):
        """
        Run the Discord bot with some default cogs
        """
        self.add_listener(self._load_default, "on_ready")
        self.run(BOT_TOKEN)


if __name__ == "__main__":
    bot = DiscordClient()
    bot.run_bot()
