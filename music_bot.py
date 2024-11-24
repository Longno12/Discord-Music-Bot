import discord
from discord.ext import commands
import yt_dlp
import asyncio
import requests

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global queue dictionary to store queues for different guilds
song_queues = {}
current_loop = {}  # Tracks loop states for songs
volume_levels = {}  # Tracks volume for each guild (default is 1.0)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

async def play_next(ctx):
    """Plays the next song in the queue."""
    guild_id = ctx.guild.id
    if guild_id in current_loop and current_loop[guild_id] == "single":
        # Replay the current song
        current_song = song_queues[guild_id][0]
        await play_song(ctx, current_song['query'])
    elif guild_id in song_queues and song_queues[guild_id]:
        next_song = song_queues[guild_id].pop(0)
        await play_song(ctx, next_song['query'])
    elif guild_id in current_loop and current_loop[guild_id] == "queue" and song_queues.get(guild_id):
        # Refill the queue for queue looping
        song_queues[guild_id] = song_queues[guild_id] * 1
        next_song = song_queues[guild_id].pop(0)
        await play_song(ctx, next_song['query'])
    else:
        await ctx.send("Queue is empty. Waiting for more songs to be added...")

async def play_song(ctx, query):
    """Helper to play a song."""
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        search_query = query if query.startswith("http") else f"ytsearch:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            audio_url = info['url']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': f'-vn -filter:a "volume={volume_levels.get(ctx.guild.id, 1.0)}"',
        }
        vc = ctx.voice_client
        vc.play(
            discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )
        await ctx.send(f"Now playing: {info.get('title', 'Unknown Title')}")
    except Exception as e:
        await ctx.send(f"Error playing the track: {str(e)}")

@bot.command(name="play", aliases=["p"])
async def play(ctx, *, query):
    # Ensure the bot is in the same voice channel as the user
    if not ctx.voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("You need to be in a voice channel for me to play music!")
            return

    guild_id = ctx.guild.id
    if guild_id not in song_queues:
        song_queues[guild_id] = []

    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            # Check if it's a playlist
            if 'entries' in info:
                for entry in info['entries']:
                    song_queues[guild_id].append({'query': entry['url'], 'requester': ctx.author.name})
                await ctx.send(f"Added playlist to queue: {info['title']} ({len(info['entries'])} songs)")
            else:
                song_queues[guild_id].append({'query': query, 'requester': ctx.author.name})
                await ctx.send(f"Added to queue: {info['title']}")

        if not ctx.voice_client.is_playing() and len(song_queues[guild_id]) == 1:
            await play_next(ctx)
    except Exception as e:
        await ctx.send(f"Error adding the track: {str(e)}")

@bot.command(name="lyrics")
async def lyrics(ctx):
    """Fetch and display lyrics for the currently playing song."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        guild_id = ctx.guild.id
        if guild_id in song_queues and song_queues[guild_id]:
            current_song = song_queues[guild_id][0]['query']
            search_query = f"{current_song} lyrics"

            try:
                response = requests.get(f"https://api.lyrics.ovh/v1/artist/{search_query}")
                response_data = response.json()
                if "lyrics" in response_data:
                    lyrics_text = response_data['lyrics']
                    if len(lyrics_text) > 2000:
                        lyrics_text = lyrics_text[:1997] + "..."
                    await ctx.send(f"Lyrics for **{current_song}**:\n```{lyrics_text}```")
                else:
                    await ctx.send(f"No lyrics found for **{current_song}**.")
            except Exception as e:
                await ctx.send(f"Error fetching lyrics: {str(e)}")
        else:
            await ctx.send("No song is currently playing!")
    else:
        await ctx.send("No song is currently playing!")

@bot.command(name="queue")
async def show_queue(ctx):
    guild_id = ctx.guild.id
    if guild_id in song_queues and song_queues[guild_id]:
        queue_list = "\n".join(
            [f"{i+1}. {song['query']} (requested by {song['requester']})" for i, song in enumerate(song_queues[guild_id])]
        )
        await ctx.send(f"Current queue:\n{queue_list}")
    else:
        await ctx.send("The queue is empty!")

@bot.command(name="volume")
async def volume(ctx, level: float):
    """Adjust playback volume."""
    if ctx.voice_client and 0.0 <= level <= 2.0:
        volume_levels[ctx.guild.id] = level
        await ctx.send(f"Volume set to {level * 100}%")
    else:
        await ctx.send("Please specify a volume level between 0.0 and 2.0.")

@bot.command(name="pause")
async def pause(ctx):
    """Pause the current track."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Playback paused.")
    else:
        await ctx.send("Nothing is currently playing.")

@bot.command(name="resume")
async def resume(ctx):
    """Resume the paused track."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Playback resumed.")
    else:
        await ctx.send("No track is paused.")

@bot.command(name="shuffle")
async def shuffle(ctx):
    """Shuffle the queue."""
    guild_id = ctx.guild.id
    if guild_id in song_queues and len(song_queues[guild_id]) > 1:
        from random import shuffle
        shuffle(song_queues[guild_id])
        await ctx.send("Queue shuffled!")
    else:
        await ctx.send("The queue is empty or has only one song.")

@bot.command(name="loop")
async def loop(ctx):
    """Loop the current song."""
    current_loop[ctx.guild.id] = "single"
    await ctx.send("Looping the current song.")

@bot.command(name="loopqueue")
async def loopqueue(ctx):
    """Loop the entire queue."""
    current_loop[ctx.guild.id] = "queue"
    await ctx.send("Looping the entire queue.")

@bot.command(name="remove")
async def remove(ctx, index: int):
    """Remove a song from the queue."""
    guild_id = ctx.guild.id
    if guild_id in song_queues and 1 <= index <= len(song_queues[guild_id]):
        removed_song = song_queues[guild_id].pop(index - 1)
        await ctx.send(f"Removed {removed_song['query']} from the queue.")
    else:
        await ctx.send("Invalid index or the queue is empty.")

@bot.command(name="clearqueue")
async def clearqueue(ctx):
    """Clear the current queue."""
    guild_id = ctx.guild.id
    song_queues.pop(guild_id, None)
    await ctx.send("The queue has been cleared.")

@bot.command(name="leave")
async def leave(ctx):
    """Disconnect the bot from the voice channel."""
    if ctx.voice_client:
        song_queues.pop(ctx.guild.id, None)
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel!")
    else:
        await ctx.send("I'm not connected to a voice channel!")

@bot.command(name="commands")
async def commands(ctx):
    """Show help message to the user who requested it."""
    help_message = (
        "**Music Bot Commands:**\n"
        "`!play <song>` or `!p <song>`: Play a song or add it to the queue.\n"
        "`!queue`: Show the current queue.\n"
        "`!volume <level>`: Adjust volume (0.0 to 2.0).\n"
        "`!pause`: Pause the current song.\n"
        "`!resume`: Resume the paused song.\n"
        "`!shuffle`: Shuffle the queue.\n"
        "`!loop`: Loop the current song.\n"
        "`!loopqueue`: Loop the entire queue.\n"
        "`!lyrics`: Fetch and display lyrics of the current song.\n"
        "`!remove <index>`: Remove a song from the queue.\n"
        "`!clearqueue`: Clear the queue.\n"
        "`!leave`: Disconnect the bot."
    )
    await ctx.author.send(help_message)
    await ctx.send("Check your DMs for the list of commands! 📩")


bot.run("DISCORD-TOKEN-HERE")
