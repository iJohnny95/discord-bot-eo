# Discord Decoy Status Bot

A Discord self-bot that monitors for decoy status messages and updates a single status message in real-time.

## Features

- Monitors Discord channel for decoy status messages
- Updates single status message (no spam)
- Real-time periodic checking (every 5 seconds by default)
- Tags @everyone when decoy is ON
- Clean status display when decoy is OFF

## Commands

- `!decoy_status` - Update status message
- `!search_decoy` - Force search for decoy messages
- `!interval <seconds>` - Change check interval (30-600 seconds)
- `!cleanup` - Remove old status messages
- `!bot_info` - Show bot status

## Setup

### Local Development
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file:**
   ```bash
   cp env_template.txt .env
   ```
   Edit `.env` with your values:
   ```
   DISCORD_TOKEN=your_discord_token_here
   TARGET_CHANNEL_ID=1400943479302914210
   OUTPUT_CHANNEL_ID=1415310746174099457
   CHECK_INTERVAL=5
   ```

3. **Run the bot:**
   ```bash
   python discord_bot.py
   ```

### Railway Deployment (Recommended)
1. **Push code to GitHub**
2. **Go to [railway.app](https://railway.app)**
3. **New Project** → **Deploy from GitHub repo**
4. **Set Environment Variables:**
   - `DISCORD_TOKEN`: Your Discord token
   - `TARGET_CHANNEL_ID`: Channel to monitor
   - `OUTPUT_CHANNEL_ID`: Channel for status updates
   - `CHECK_INTERVAL`: Check interval in seconds (optional, default: 5)
5. **Deploy!** 🚀

### Heroku Deployment
1. **Create Heroku app**
2. **Set environment variables** in Heroku dashboard
3. **Deploy via Git:**
   ```bash
   git push heroku main
   ```

## Environment Variables

- `DISCORD_TOKEN`: Discord bot token (required)
- `TARGET_CHANNEL_ID`: Channel ID to monitor for decoy messages
- `OUTPUT_CHANNEL_ID`: Channel ID for status updates
- `CHECK_INTERVAL`: Check interval in seconds (optional, default: 5)

## Requirements

- Python 3.11+
- discord.py-self
- aiohttp
- python-dotenv

## Files

- `discord_bot.py` - Main bot code
- `config.py` - Configuration loader
- `requirements.txt` - Python dependencies
- `Procfile` - Railway/Heroku process file
- `runtime.txt` - Python version
- `env_template.txt` - Environment variables template
- `.gitignore` - Git ignore file
