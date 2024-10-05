import asyncio
import discord
from discord.ext import commands
import yt_dlp


class Music(commands.Cog):
    """For streaming music from YouTube."""

    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.music_queue = []

    @commands.command(name='join', help='Bot joins voice channel')
    async def join(self, ctx):
        """Join voice channel same as author."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send('After you, please join a voice channel')

    @commands.command(name='play', help='Play a song from YouTube')
    async def play(self, ctx, *args):
        """Play the requested song from YouTube."""
        query = ' '.join(args)

        channel = ctx.author.voice.channel
        if not channel:
            await ctx.send('You need to be in a voice channel')
            return

        if ctx.voice_client is None:
            await channel.connect()

        song = self._search_yt(query)
        if not song:
            await ctx.send('Sorry, I cannot find the song right now')
        else:
            self.music_queue.append(song)

            if not self.is_playing:
                await self._play_next(ctx)
            else:
                await ctx.send(f'Song added to queue: {song['title']}')

    def _search_yt(self, query):
        """Search YouTube using youtube-dl."""
        YTDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
            try:
                info = ytdl.extract_info(
                    f'ytsearch:{query}', download=False
                )['entries'][0]
            except Exception:
                return False

        return {'source': info['url'], 'title': info['title']}

    async def _play_next(self, ctx):
        """Play songs from music queue."""
        if len(self.music_queue) > 0:
            self.is_playing = True

            song = self.music_queue.pop(0)

            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 '
                '-reconnect_streamed 1 '
                '-reconnect_delay_max 5',
                'options': '-vn'
            }

            ctx.voice_client.play(
                discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._play_next(ctx),
                    self.bot.loop
                ) if e is None else None,
            )
            await ctx.send(f'Now playing: {song['title']}')
        else:
            self.is_playing = False

    @commands.command(name='skip', help='Bot will play next song in queue')
    async def skip(self, ctx):
        """Skip and play next song in queue."""
        if self.is_playing:
            if len(self.music_queue) == 0:
                self.is_playing = False
            ctx.voice_client.stop()
            await ctx.send('Skipped the current song!')

    @commands.command(name='leave', help='Bot leaves the voice channel')
    async def leave(self, ctx):
        """Leave the voice channel."""
        self.music_queue = []
        self.is_playing = False
        await ctx.voice_client.disconnect()


async def setup(bot):
    await bot.add_cog(Music(bot))
