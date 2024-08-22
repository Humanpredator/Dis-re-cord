"""Manager user to invoke the command"""
from datetime import datetime

from discord import Embed, Message
from discord.ext.commands import Cog, command, Context

from bot import SESSION
from bot.__main__ import DiscordClient
from bot.ext.misc.response import send_message
from bot.model.auth import Auth


class Authorize(Cog):
    """Allow Server User to invoke the command"""

    def __init__(self, bot):
        """@param bot:"""
        super().__init__()
        self._bot: DiscordClient = bot

    @command("promote", help="Reply To The Message Of User, To Promote.")
    async def promote_user(self, ctx):
        """

        @param ctx:
        @return:
        """
        await self._bot.owner_only(ctx)
        if ctx.message.reference:
            og_message: Message = await ctx.fetch_message(ctx.message.reference.message_id)
            original_author_id = str(og_message.author.id)
            with SESSION as session:
                user_data: Auth = (
                    session.query(Auth)
                    .filter(Auth.guild_id == str(og_message.guild.id))
                    .first()
                )
                if not user_data:
                    return await send_message(ctx, "Please add the bot to server to invoke the command!")
                auth_user = user_data.retrieve_raw(include_owner=False)
                if original_author_id in auth_user:
                    return await send_message(ctx, "User was already Authorized")
                auth_user.append(original_author_id)
                user_data.authorized_id = ','.join(auth_user)
                user_data.commit()
            return await send_message(ctx, "User Promoted To Sudo")
        else:
            return await send_message(ctx, "Usage !promote reply to this to user!")

    @command("demote", help="Reply To The Message Of User,To Demote.")
    async def demote_user(self, ctx):
        """

        @param ctx:
        @return:
        """
        await self._bot.owner_only(ctx)
        if ctx.message.reference:
            og_message: Message = await ctx.fetch_message(ctx.message.reference.message_id)
            original_author_id = str(og_message.author.id)
            with SESSION as session:
                user_data: Auth = (
                    session.query(Auth)
                    .filter(Auth.guild_id == str(og_message.guild.id))
                    .first()
                )
                if not user_data:
                    return await send_message(ctx, "Please add the bot to server to invoke the command!")
                auth_user = user_data.retrieve_raw(include_owner=False)

                if original_author_id not in auth_user:
                    return await send_message(ctx, "User was not Authorized")

                auth_user.remove(original_author_id)
                user_data.authorized_id = ','.join(auth_user)
                user_data.commit()
            return await send_message(ctx, "Users De-Promoted")
        else:
            return await send_message(ctx, "Usage !demote reply to this to user...!")

    @command("users", help="Get All Sudo Users ID's.")
    async def show_sudo(self, ctx: Context):
        """

        @param ctx:
        @return:
        """
        await self._bot.owner_only(ctx)
        with SESSION as session:
            user_data: Auth = (
                session.query(Auth)
                .filter(Auth.guild_id == str(ctx.guild.id))
                .first()
            )
            if not user_data:
                return await send_message(ctx, "Please add the bot to server to invoke the command!")
            auth_user = user_data.retrieve_raw(include_owner=False)
            users = '\n'.join(auth_user)
            value = f"""
GuildId: ***{user_data.guild_id}***
OwnerId: ***{user_data.owner_id}***
SudoUsers: \n***{users}***
"""
            emd = Embed(timestamp=datetime.now())
            emd.add_field(
                name="Authorized Users",
                value=value,
                inline=False,
            )
            return await send_message(ctx, embed=emd)


def setup(bot: DiscordClient):
    """@param bot:"""
    bot.add_cog(Authorize(bot))
