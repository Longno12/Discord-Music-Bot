import discord
from discord.ext import commands
import yt_dlp
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API Setup (replace these with your own credentials securely)
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'default_search': 'ytsearch'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def get_track_name_from_spotify(url):
    """Fetches the track name and artist from a Spotify link."""
    try:
        track_info = spotify.track(url)
        track_name = track_info['name']
        artist_name = track_info['artists'][0]['name']
        return f"{track_name} by {artist_name}"
    except Exception as e:
        print(f"Spotify API Error: {e}")
        return None


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")


@bot.command(name="play", help="Plays a song from a URL or search term.")
async def play(ctx, *, query):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You need to be in a voice channel to play music.")
            return

    async with ctx.typing():
        try:
            if "spotify.com/track" in query:
                song_name = get_track_name_from_spotify(query)
                if not song_name:
                    await ctx.send("Failed to fetch track information from Spotify.")
                    return
                query = song_name

            player = await YTDLSource.from_url(query, loop=bot.loop)
            ctx.voice_client.stop()
            def after_play(error):
                if error:
                    print(f"Error during playback: {error}")
                else:
                    print("Song playback finished.")
            ctx.voice_client.play(player, after=after_play)
            await ctx.send(f"Now playing: {player.title}")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")


@bot.command(name="stop", help="Stops and disconnects the bot.")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")
    else:
        await ctx.send("I'm not connected to a voice channel.")

bot.run('YOUR_DISCORD_BOT_TOKEN')
