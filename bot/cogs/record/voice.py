import os
import time

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.sinks import WaveSink, Filters, AudioData

from bot import CONNECTIONS, RECORDING_PATH
from bot.ext.misc.response import send_message, delete_message, send_files


class FileSink(WaveSink):
    def __init__(self):
        super().__init__()
        self.output_dir = RECORDING_PATH
        os.makedirs(self.output_dir, exist_ok=True)

    @Filters.container
    def write(self, data, user):
        if user not in self.audio_data:
            user_file_path = os.path.join(self.output_dir, f"{user}.wav")
            file = open(user_file_path, 'wb')
            self.audio_data.update({user: AudioData(file)})
        else:
            file = self.audio_data[user].file

        file.write(data)
        file.flush()


class VoiceRecorder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.connections = {}  # To manage voice clients and recording status
        self.save_path = "./recordings"  # Directory to save recordings
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    @staticmethod
    async def _post_recording(sink: discord.sinks, ctx: Context, *args):
        recorded_users = [f"<@{user_id}>" for user_id in sink.audio_data.keys()]

        # Close and reopen files in read mode, preparing to send them
        files = []
        for user_id, audio in sink.audio_data.items():
            audio.file.close()  # Close the file after writing is done
            file_path = os.path.join(sink.output_dir, f"{user_id}.wav")
            files.append(file_path)
            # files.append(discord.File(file_path, f"{user_id}.wav"))
        await sink.vc.disconnect()  # Disconnect from the voice channel.
        await send_files(ctx, f"Finished recording audio for: {', '.join(recorded_users)}.")

    @commands.command(name="record", help="Start the voice recording")
    async def record(self, ctx):  # If you're using commands.Bot, this will also work.
        voice = ctx.author.voice

        if not voice:
            return await send_message(ctx, "You are not in a voice channel!")

        vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
        CONNECTIONS[ctx.guild.id] = {
            'vc': vc,
            'ctx': ctx,
            'st': time.time()

        }

        vc.start_recording(
            FileSink(),  # The sink type to use.
            self._post_recording,  # What to do once done.
            ctx,  # The channel to disconnect from.
            sync_start=True
        )
        return await send_message(ctx, "Recording Initiated!")

    @commands.command(name="stop", help="Stop the voice recording")
    async def stop_recording(self, ctx):
        conn = CONNECTIONS.get(ctx.guild.id)
        if not conn:
            return await send_message(ctx, "No recording session found in this channel.")

        vc = conn.get('vc')
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        await delete_message(conn.get('ctx').message)
        del conn  # Remove the guild from the cache.

    @commands.command(name="status", help="Show the status of the voice recording")
    async def status(self, ctx):
        """Command to display the current recording status."""
        conn = CONNECTIONS.get(ctx.guild.id)
        if not conn:
            return await send_message(ctx, "No recording session found in this channel.")

        recording_status = "Recording" if conn['vc'].recording else "Stopped"

        elapsed_time = int(time.time() - conn['st'])
        minutes, seconds = divmod(elapsed_time, 60)
        formatted_time = f"{minutes}m {seconds}s"
        format = "WAV"

        embed = discord.Embed(title=f"Recording Status in {ctx.author.voice.channel.name}", color=discord.Color.blue())
        embed.add_field(name="Recording Status", value=recording_status, inline=False)
        embed.add_field(name="Recording Time", value=formatted_time, inline=False)
        embed.add_field(name="Format", value=format, inline=False)
        return await send_message(ctx, embed=embed)


def setup(bot):
    bot.add_cog(VoiceRecorder(bot))
