# Discord Music Bot 🎵

A powerful and easy-to-use music bot for Discord with support for YouTube and Spotify links! This bot features robust functionality, a clear user interface, and optimized performance.

---

## Features
- **🎧 Play Music**: Stream music directly from YouTube or Spotify.
- **📜 Queue Management**: Add, view, skip, and clear songs in the queue.
- **⏸️ Pause/Resume**: Pause and resume playback seamlessly.
- **🎚️ Volume Control**: Adjust playback volume.
- **💾 High-Quality Playback**: Automatically fetches the best available audio quality.
- **🌐 Easy Hosting**: Works on local machines, cloud platforms, or VPS.

---

## Commands
| Command           | Description                                                       |
|-------------------|-------------------------------------------------------------------|
| `!play [URL/Term]` | Plays a song from a YouTube/Spotify link or search term.          |
| `!pause`          | Pauses the current song.                                          |
| `!resume`         | Resumes the paused song.                                          |
| `!skip`           | Skips the current song in the queue.                              |
| `!queue`          | Displays the current song queue.                                  |
| `!clear`          | Clears the entire song queue and stops the bot.                   |
| `!stop`           | Disconnects the bot from the voice channel.                       |
| `!volume [1-100]` | Adjusts the volume of the bot. Default is 50%.                    |

---

## Requirements
- **Python 3.8+**: Make sure Python is installed on your system.
- **FFmpeg**: Install FFmpeg and add it to your system's `PATH`.
- **Discord Bot Token**: Get your bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
- **Spotify API Credentials**: Get a `CLIENT_ID` and `CLIENT_SECRET` from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).

---

## Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/discord-music-bot.git
   cd discord-music-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Spotify API**
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and create an application.
   - Copy your `CLIENT_ID` and `CLIENT_SECRET`.
   - Replace the placeholders in the bot code with your credentials:
     ```python
     SPOTIFY_CLIENT_ID = "your_client_id"
     SPOTIFY_CLIENT_SECRET = "your_client_secret"
     ```

4. **Add Your Discord Bot Token**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Create an application and copy the bot token.
   - Replace the placeholder in the bot code with your token:
     ```python
     bot.run('your_bot_token')
     ```

5. **Run the Bot**
   ```bash
   python bot.py
   ```

---

## How to Use
1. Invite the bot to your server using the OAuth2 link generated in the Discord Developer Portal.
2. Use the `!play` command followed by a YouTube or Spotify link to start playing music.
3. Use additional commands like `!pause`, `!resume`, and `!stop` to control playback.

---

## Troubleshooting
- **FFmpeg Not Found**: Ensure FFmpeg is installed and added to your system's `PATH`.
- **Bot Not Joining Voice Channel**: Make sure you’re in a voice channel and have the proper permissions.
- **Spotify Errors**: Ensure your Spotify API credentials are correctly configured.

---

## Contributing
Feel free to fork this repository, make your changes, and submit a pull request! Contributions are welcome.
