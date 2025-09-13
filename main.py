#!/usr/bin/env python3
"""
Main entry point for the Discord Decoy Status Bot with API Server
This file is used by Railway as a fallback if Procfile is not detected
"""

import threading
import time
from api_server import run_api_server
from discord_bot import client, DISCORD_TOKEN
from shared_state import decoy_status_manager

def run_discord_bot():
    """Run the Discord bot in a separate thread"""
    try:
        print("🤖 Starting Discord bot...")
        client.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Discord bot error: {e}")
        decoy_status_manager.set_bot_online(False)

def run_api():
    """Run the API server in a separate thread"""
    try:
        print("🌐 Starting API server...")
        run_api_server()
    except Exception as e:
        print(f"❌ API server error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Discord Decoy Status Bot with Public API")
    print("=" * 50)
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Give API server time to start
    time.sleep(2)
    
    # Start Discord bot (this will block)
    try:
        run_discord_bot()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        decoy_status_manager.set_bot_online(False)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        decoy_status_manager.set_bot_online(False)
