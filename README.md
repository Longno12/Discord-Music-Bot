# Discord Music Bot 🎵

A powerful and feature-rich Discord music bot that supports YouTube and Spotify! This bot offers high-quality audio playback, queue management, playlist support, and more.

---

## Features
- **🎧 Play Music**: Stream songs from YouTube and Spotify.
- **📜 Queue Management**: Add, view, skip, remove, and clear songs in the queue.
- **⏸️ Pause/Resume**: Control playback with simple commands.
- **🎚️ Volume Control**: Adjust playback volume dynamically.
- **🔁 Looping**: Loop individual songs or the entire queue.
- **🔀 Shuffle**: Randomize the queue order.
- **🎤 Lyrics Fetching**: Retrieve lyrics for the currently playing song.
- **💾 Playlist Support**: Save and load custom playlists.
- **🤖 Auto-Reconnect**: The bot reconnects if disconnected from the voice channel.
- **⚡ Optimized Performance**: Uses `yt-dlp`, `FFmpeg`, and `Spotify API` for the best music experience.

---

## Commands
| Command                 | Description                                                    |
|-------------------------|----------------------------------------------------------------|
| `!play [URL/Term]`      | Plays a song from YouTube/Spotify or searches for a term.     |
| `!pause`                | Pauses the current song.                                      |
| `!resume`               | Resumes the paused song.                                     |
| `!skip`                 | Skips the current song.                                      |
| `!queue` / `!q`         | Displays the current queue.                                 |
| `!volume [level]`       | Adjusts playback volume (0-100).                            |
| `!shuffle`              | Shuffles the song queue.                                    |
| `!loop [off/song/queue]`| Loops the current song or the entire queue.                 |
| `!lyrics`               | Fetches lyrics for the current song.                        |
| `!nowplaying` / `!np`   | Shows information about the currently playing song.         |
| `!save_playlist [name]` | Saves the current queue as a named playlist.               |
| `!load_playlist [name]` | Loads a saved playlist.                                     |
| `!remove [index]`       | Removes a song from the queue by index.                     |
| `!stop`                 | Stops playback and clears the queue.                        |
| `!leave`                | Disconnects the bot from the voice channel.                 |
| `!commands`             | Displays all available commands.                            |
| `!recommend`            | Suggests a song based on the current queue.                 |
| `!voteskip`             | Initiates a vote to skip the current song.                  |

---

## Requirements
- **Python 3.8+**: Ensure you have Python installed.
- **FFmpeg**: Install and add FFmpeg to your system's `PATH`.
- **Discord Bot Token**: Obtain a token from the [Discord Developer Portal](https://discord.com/developers/applications).
- **Spotify API Credentials**: Get `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` from the [Spotify Developer Dashboard](https://developer.spotify.com/).
- **Genius API Token**: Required for the lyrics feature.

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Longno12/discord-music-bot.git
   cd discord-music-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Credentials**
   - Open `bot.py` and replace the placeholders with your credentials:
     ```python
     bot.run('YOUR_DISCORD_BOT_TOKEN')
     SPOTIPY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
     SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET'
     genius = lyricsgenius.Genius("YOUR_GENIUS_API_TOKEN")
     ```

4. **Run the Bot**
   ```bash
   python bot.py
   ```

---

## How to Use
1. **Invite the bot** to your Discord server using the OAuth2 link from the [Discord Developer Portal](https://discord.com/developers/applications).
2. **Join a voice channel** and use the `!play` command to start playing music.
3. **Manage playback** using commands like `!pause`, `!resume`, `!skip`, `!shuffle`, `!loop`, etc.
4. **Enjoy your music experience!** 🎵

---

## Troubleshooting
- **Bot not responding?** Make sure the bot has the correct permissions.
- **No sound?** Ensure FFmpeg is installed and correctly set up.
- **Spotify links not working?** Check your Spotify API credentials.
- **Lyrics not found?** The song may not be available in the Genius database.

---

## Changelog (Latest Update)
### Version 1.6.0
- **Added lyrics support** using Genius API.
- **Implemented song recommendations** based on the current queue.
- **Added support for saving and loading playlists**.
- **Improved queue management and performance enhancements**.
- **New vote-based skip system**.

---

## Contributing
Feel free to fork this repository, make improvements, and submit a pull request! Contributions are always welcome. 🚀

---

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE.md) file for details.

