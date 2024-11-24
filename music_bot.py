import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

song_queues = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel for me to join!")

async def play_next(ctx):
    """Plays the next song in the queue."""
    guild_id = ctx.guild.id
    if guild_id in song_queues and song_queues[guild_id]:
        next_song = song_queues[guild_id].pop(0)
        try:
            ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
            search_query = next_song['query']
            if not search_query.startswith("http"):
                search_query = f"ytsearch:{search_query}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                audio_url = info['url']

            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }
            vc = ctx.voice_client
            vc.play(
                discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
            )
            await ctx.send(f"Now playing: {info.get('title', 'Unknown Title')}")
        except Exception as e:
            await ctx.send(f"Error playing the track: {str(e)}")
            await play_next(ctx)
    else:
        await ctx.send("Queue is empty. Waiting for more songs to be added...")

@bot.command(name="play", aliases=["p"])
async def play(ctx, *, query):
    if not ctx.voice_client:
        await ctx.send("I'm not connected to a voice channel! Use `!join` first.")
        return

    guild_id = ctx.guild.id
    if guild_id not in song_queues:
        song_queues[guild_id] = []

    song_queues[guild_id].append({'query': query, 'requester': ctx.author.name})
    await ctx.send(f"Added to queue: {query}")

    if not ctx.voice_client.is_playing() and len(song_queues[guild_id]) == 1:
        await play_next(ctx)

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

@bot.command(name="skip")
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipping to the next song...")
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        song_queues.pop(ctx.guild.id, None)
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel!")
    else:
        await ctx.send("I'm not connected to a voice channel!")

bot.run("BOT-TOKEN")
