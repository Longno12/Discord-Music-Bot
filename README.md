# Discord Music Bot 🎵

A powerful and easy-to-use music bot for Discord with support for YouTube! This bot features robust functionality, a clear user interface, and optimized performance.

---

## Features
- **🎧 Play Music**: Stream music directly from YouTube or playlists.
- **📜 Queue Management**: Add, view, skip, remove, and clear songs in the queue.
- **⏸️ Pause/Resume**: Pause and resume playback seamlessly.
- **🎚️ Volume Control**: Adjust playback volume.
- **💾 High-Quality Playback**: Automatically fetches the best available audio quality.
- **🔁 Looping**: Loop the current song or the entire queue.
- **🔀 Shuffle**: Shuffle the queue to randomize song order.
- **🌐 Easy Hosting**: Works on local machines, cloud platforms, or VPS.

---

## Commands
| Command               | Description                                                         |
|-----------------------|---------------------------------------------------------------------|
| `!play [URL/Term]`     | Plays a song from a YouTube/Spotify link or search term.            |
| `!pause`               | Pauses the current song.                                            |
| `!resume`              | Resumes the current song if paused.                                 |
| `!skip`                | Skips the current song in the queue.                                |
| `!queue`               | Displays the current song queue.                                    |
| `!lyrics`              | Fetches and displays lyrics for the currently playing song.         |
| `!volume [level]`      | Adjusts the playback volume (0.0 to 2.0).                           |
| `!shuffle`             | Shuffles the queue to randomize song order.                         |
| `!loop`                | Loops the current song.                                             |
| `!loopqueue`           | Loops the entire queue.                                             |
| `!remove [index]`      | Removes a song from the queue by its index.                         |
| `!clearqueue`          | Clears the entire song queue.                                       |
| `!leave`               | Disconnects the bot from the voice channel.                         |
| `!commands`            | Displays a list of all available commands.                           |

---

## Requirements
- **Python 3.8+**: Make sure Python is installed on your system.
- **FFmpeg**: Install FFmpeg and add it to your system's `PATH`.
- **Discord Bot Token**: Get your bot token from the [Discord Developer Portal](https://discord.com/developers/applications).

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/discord-music-bot.git
   cd discord-music-bot


2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add Your Discord Bot Token**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Create an application and copy the bot token.
   - Replace the placeholder in the bot code with your token:
     ```python
     bot.run('your_bot_token')
     ```

4. **Run the Bot**
   ```bash
   python bot.py
   ```

---

## How to Use
1. Invite the bot to your server using the OAuth2 link generated in the Discord Developer Portal.
2. Use the `!play` command followed by a YouTube or Spotify link to start playing music.
3. Use additional commands like `!pause`, `!resume`, `!skip`, `!volume`, `!loop`, `!shuffle`, `!lyrics`, and more to control playback and manage your queue.

---

## Troubleshooting
- FFmpeg Not Found: Ensure FFmpeg is installed and added to your system's `PATH`.
- Bot Not Joining Voice Channel: Make sure you’re in a voice channel and have the proper permissions.
- Lyrics Not Found: If the bot cannot find lyrics, it may be due to the song not having available lyrics in the database.

---

## Contributing
Feel free to fork this repository, make your changes, and submit a pull request! Contributions are welcome.

## Contributing
Feel free to fork this repository, make your changes, and submit a pull request! Contributions are welcome.

### Key Updates:
- **Features**: Added features like playlist support, shuffle, loop, volume control, and lyrics fetching.
- **Commands Table**: Updated the commands section to include all available commands such as `!play`, `!pause`, `!shuffle`, `!loop`, etc.
- **Installation**: Clear installation steps for the bot, with a section for adding your Discord Bot token.
- **Usage**: Detailed usage of the bot, including how to invite it, play music, and control playback.

This README.md file now fully reflects the bot's functionality, making it easy for users to understand, install, and contribute to the project.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.



