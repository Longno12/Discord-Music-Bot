import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import lyricsgenius

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

song_queues = {}
volume_levels = {}
loop_status = {}
skip_votes = {}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

ydl_opts = {
    'format': 'bestaudio/best',
    'extract_flat': 'in_playlist',
}

VERSION = "1.6.0"
PREVIOUS_VERSION = "1.5.2"
SPOTIPY_CLIENT_ID = 'SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'SPOTIPY_CLIENT_SECRET'
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Initialize Genius API client
genius = lyricsgenius.Genius("YOUR_GENIUS_API_TOKEN")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!commands"))

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        
        if 'entries' in data:
            # It's a playlist
            playlist_urls = [entry['url'] for entry in data['entries'] if entry.get('url')]
            return playlist_urls
        else:
            # It's a single video
            return cls(discord.FFmpegPCMAudio(data['url'], **FFMPEG_OPTIONS), data=data)

async def update_presence(ctx, song_title):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=song_title))

async def play_next(ctx):
    if ctx.guild.id in loop_status:
        if loop_status[ctx.guild.id] == "song" and ctx.voice_client.source:
            await play_song(ctx, ctx.voice_client.source.url)
            return
        elif loop_status[ctx.guild.id] == "queue" and ctx.guild.id in song_queues and song_queues[ctx.guild.id]:
            song_queues[ctx.guild.id].append(song_queues[ctx.guild.id].pop(0))

    if ctx.guild.id in song_queues and song_queues[ctx.guild.id]:
        query = song_queues[ctx.guild.id].pop(0)
        await play_song(ctx, query)
    else:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!commands"))

async def play_song(ctx, query):
    try:
        async with ctx.typing():
            result = await YTDLSource.from_url(query, loop=bot.loop)
            if isinstance(result, list):
                song_queues[ctx.guild.id].extend(result)
                await ctx.send(f"Added {len(result)} songs from playlist to the queue.")
                if not ctx.voice_client.is_playing():
                    await play_next(ctx)
            else:
                player = result
                ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))       
                await update_presence(ctx, player.title)
                duration_str = f"{player.duration // 60}:{player.duration % 60:02d}" if player.duration else "Unknown"
                thumbnail = player.data.get('thumbnail')
                embed = discord.Embed(color=0x1DB954)
                embed.title = "🎵 Now Playing"
                embed.description = f"**[{player.title}]({player.url})**"
                if thumbnail:
                    embed.set_thumbnail(url=thumbnail)
                embed.add_field(name="Duration", value=f"`{duration_str}`", inline=True)
                embed.add_field(name="Queue", value=f"`{len(song_queues.get(ctx.guild.id, []))} songs`", inline=True)
                embed.add_field(name="Volume", value=f"`{int(volume_levels.get(ctx.guild.id, 1.0) * 100)}%`", inline=True)
                embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

                await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        if ctx.guild.id in song_queues and song_queues[ctx.guild.id]:
            song_queues[ctx.guild.id].pop(0)
        await play_next(ctx)

async def get_spotify_track(url):
    try:
        track_id = url.split('/')[-1].split('?')[0]
        track_info = sp.track(track_id)
        query = f"{track_info['name']} {' '.join([artist['name'] for artist in track_info['artists']])}"
        return query
    except Exception as e:
        print(f"Error processing Spotify URL: {e}")
        return None

async def get_spotify_playlist(url):
    try:
        playlist_id = url.split('/')[-1].split('?')[0]
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        
        queries = []
        for item in tracks:
            track = item['track']
            query = f"{track['name']} {' '.join([artist['name'] for artist in track['artists']])}"
            queries.append(query)
        return queries
    except Exception as e:
        print(f"Error processing Spotify playlist URL: {e}")
        return None

async def get_spotify_album(url):
    try:
        album_id = url.split('/')[-1].split('?')[0]
        results = sp.album_tracks(album_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        queries = []
        for track in tracks:
            query = f"{track['name']} {' '.join([artist['name'] for artist in track['artists']])}"
            queries.append(query)
        return queries
    except Exception as e:
        print(f"Error processing Spotify album URL: {e}")
        return None

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return
    
    channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='play', aliases=['p'], help='To play a song or add it to the queue (supports song names, YouTube links, and Spotify links)')
async def play(ctx, *, query):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command('join'))

    if ctx.guild.id not in song_queues:
        song_queues[ctx.guild.id] = []

    if 'open.spotify.com/track' in query:
        query = await get_spotify_track(query)
        if not query:
            await ctx.send("Failed to process Spotify track. Please try a different link or search query.")
            return
    elif 'open.spotify.com/playlist' in query:
        playlist_queries = await get_spotify_playlist(query)
        if not playlist_queries:
            await ctx.send("Failed to process Spotify playlist. Please try a different link or search query.")
            return
        song_queues[ctx.guild.id].extend(playlist_queries)
        await ctx.send(f"Added {len(playlist_queries)} songs from Spotify playlist to the queue.")
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
        return
    elif 'open.spotify.com/album' in query:
        album_queries = await get_spotify_album(query)
        if not album_queries:
            await ctx.send("Failed to process Spotify album. Please try a different link or search query.")
            return
        song_queues[ctx.guild.id].extend(album_queries)
        await ctx.send(f"Added {len(album_queries)} songs from Spotify album to the queue.")
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
        return

    if not query.startswith("http"):
        query = f"ytsearch:{query}"

    song_queues[ctx.guild.id].append(query)

    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send(f"Added to queue: {query}")

@bot.command(name='stop', help='Stops the music and clears the queue')
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
    if ctx.guild.id in song_queues:
        song_queues[ctx.guild.id].clear()
    await ctx.send("Stopped the music and cleared the queue.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!commands"))

@bot.command(name='queue', aliases=['q'], help='Shows the current queue')
async def queue(ctx):
    if ctx.guild.id not in song_queues or not song_queues[ctx.guild.id]:
        await ctx.send("The queue is empty.")
        return

    queue_list = "\n".join([f"{i+1}. {song}" for i, song in enumerate(song_queues[ctx.guild.id])])
    await ctx.send(f"Current queue:\n{queue_list}")

@bot.command(name='skip', help='Skips the current song')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name='commands', help='Shows all available commands')
async def show_commands(ctx):
    embed = discord.Embed(title="Music Bot Commands", color=0x1DB954)
    embed.set_footer(text=f"Bot version: {VERSION}")
    
    for command in bot.commands:
        embed.add_field(name=f"!{command.name}", value=command.help, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='update', help='Shows what got updated/added in the latest version')
async def update(ctx):
    embed = discord.Embed(title="Latest Update", color=0x1DB954)
    embed.add_field(name="Current Version", value=VERSION, inline=False)
    embed.add_field(name="Previous Version", value=PREVIOUS_VERSION, inline=False)
    embed.add_field(name="What's New", value="""    
    1. Added lyrics command to fetch song lyrics.
    2. Implemented a song recommendation system.
    3. Added save_playlist and load_playlist commands.
    4. Introduced volume control with !volume command.
    5. Added loop functionality for songs and queue.
    6. New nowplaying command to show current song info.
    7. Implemented a voting system for skipping songs.
    8. Added remove command to remove specific songs from the queue.
    9. General improvements and bug fixes.
    """, inline=False)

    await ctx.send(embed=embed)

@bot.command(name='shuffle', help='Shuffles the current queue')
async def shuffle(ctx):
    if ctx.guild.id not in song_queues or not song_queues[ctx.guild.id]:
        await ctx.send("The queue is empty. Nothing to shuffle.")
        return
    
    random.shuffle(song_queues[ctx.guild.id])
    await ctx.send("The queue has been shuffled!")

@bot.command(name='lyrics', help='Fetches lyrics for the currently playing song')
async def lyrics(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        current_song = ctx.voice_client.source.title
        song = genius.search_song(current_song)
        if song:
            await ctx.send(f"Lyrics for {current_song}:\n\n{song.lyrics[:2000]}...")
        else:
            await ctx.send(f"Couldn't find lyrics for {current_song}")
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name='recommend', help='Recommends a song based on the current playlist')
async def recommend(ctx):
    if ctx.guild.id in song_queues and song_queues[ctx.guild.id]:
        sample_song = random.choice(song_queues[ctx.guild.id])
        search_response = await YTDLSource.from_url(f"ytsearch:{sample_song}", loop=bot.loop)
        if isinstance(search_response, YTDLSource):
            await ctx.send(f"Based on your queue, you might like: {search_response.title}\n{search_response.url}")
        else:
            await ctx.send("Couldn't find a recommendation at this time.")
    else:
        await ctx.send("The queue is empty. Add some songs to get recommendations!")

@bot.command(name='save_playlist', help='Saves the current queue as a playlist')
async def save_playlist(ctx, name: str):
    if ctx.guild.id in song_queues and song_queues[ctx.guild.id]:
        playlists = {}
        try:
            with open('playlists.json', 'r') as f:
                playlists = json.load(f)
        except FileNotFoundError:
            pass
        
        playlists[name] = song_queues[ctx.guild.id]
        
        with open('playlists.json', 'w') as f:
            json.dump(playlists, f)
        
        await ctx.send(f"Playlist '{name}' has been saved!")
    else:
        await ctx.send("The queue is empty. Nothing to save.")

@bot.command(name='load_playlist', help='Loads a saved playlist')
async def load_playlist(ctx, name: str):
    try:
        with open('playlists.json', 'r') as f:
            playlists = json.load(f)
        
        if name in playlists:
            if ctx.guild.id not in song_queues:
                song_queues[ctx.guild.id] = []
            song_queues[ctx.guild.id].extend(playlists[name])
            await ctx.send(f"Playlist '{name}' has been loaded and added to the queue!")
        else:
            await ctx.send(f"Playlist '{name}' not found.")
    except FileNotFoundError:
        await ctx.send("No playlists have been saved yet.")

@bot.command(name='volume', aliases=['vol'], help='Adjusts the volume of the bot (0-100)')
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send("Not connected to a voice channel.")

    if 0 <= volume <= 100:
        ctx.voice_client.source.volume = volume / 100
        volume_levels[ctx.guild.id] = volume / 100
        await ctx.send(f"Changed volume to {volume}%")
    else:
        await ctx.send("Volume must be between 0 and 100.")

@bot.command(name='loop', help='Toggles loop mode (off/song/queue)')
async def loop(ctx, mode: str = None):
    if ctx.guild.id not in loop_status:
        loop_status[ctx.guild.id] = "off"

    if mode is None:
        current_mode = loop_status[ctx.guild.id]
        await ctx.send(f"Current loop mode: {current_mode}")
    elif mode.lower() in ["off", "song", "queue"]:
        loop_status[ctx.guild.id] = mode.lower()
        await ctx.send(f"Loop mode set to: {mode.lower()}")
    else:
        await ctx.send("Invalid loop mode. Use 'off', 'song', or 'queue'.")

@bot.command(name='nowplaying', aliases=['np'], help='Shows information about the currently playing song')
async def nowplaying(ctx):
    if ctx.voice_client and ctx.voice_client.source:
        player = ctx.voice_client.source
        duration_str = f"{player.duration // 60}:{player.duration % 60:02d}" if player.duration else "Unknown"
        
        embed = discord.Embed(color=0x1DB954)
        embed.title = "🎵 Now Playing"
        embed.description = f"**[{player.title}]({player.url})**"
        if player.data.get('thumbnail'):
            embed.set_thumbnail(url=player.data['thumbnail'])
        embed.add_field(name="Duration", value=f"`{duration_str}`", inline=True)
        embed.add_field(name="Requested by", value=ctx.voice_client.source.requester.mention if hasattr(ctx.voice_client.source, 'requester') else "Unknown", inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name='voteskip', help='Vote to skip the current song')
async def voteskip(ctx):
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("No song is currently playing.")

    if ctx.guild.id not in skip_votes:
        skip_votes[ctx.guild.id] = set()

    skip_votes[ctx.guild.id].add(ctx.author.id)
    required_votes = len(ctx.voice_client.channel.members) // 2
    current_votes = len(skip_votes[ctx.guild.id])

    if current_votes >= required_votes:
        await ctx.invoke(bot.get_command('skip'))
        skip_votes[ctx.guild.id].clear()
    else:
        await ctx.send(f"Vote to skip added. {current_votes}/{required_votes} votes required to skip.")

@bot.command(name='remove', help='Removes a song from the queue by its position')
async def remove(ctx, position: int):
    if ctx.guild.id not in song_queues or not song_queues[ctx.guild.id]:
        return await ctx.send("The queue is empty.")

    if 1 <= position <= len(song_queues[ctx.guild.id]):
        removed_song = song_queues[ctx.guild.id].pop(position - 1)
        await ctx.send(f"Removed song from position {position}: {removed_song}")
    else:
        await ctx.send("Invalid position. Please provide a valid queue position.")

bot.run("Discord Bot Token")

