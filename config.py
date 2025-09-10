import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', '1400943479302914210'))
OUTPUT_CHANNEL_ID = int(os.getenv('OUTPUT_CHANNEL_ID', '1415310746174099457'))

# Bot Settings
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))

# Debug: Print all environment variables
print("🔍 Environment Variables Debug:")
print(f"   DISCORD_TOKEN: {'SET' if DISCORD_TOKEN else 'NOT SET'}")
print(f"   TARGET_CHANNEL_ID: {os.getenv('TARGET_CHANNEL_ID', 'NOT SET')}")
print(f"   OUTPUT_CHANNEL_ID: {os.getenv('OUTPUT_CHANNEL_ID', 'NOT SET')}")
print(f"   CHECK_INTERVAL: {os.getenv('CHECK_INTERVAL', 'NOT SET')}")

# Validate required variables
if not DISCORD_TOKEN:
    print("❌ ERROR: DISCORD_TOKEN environment variable is required!")
    print("Available environment variables:")
    for key, value in os.environ.items():
        if 'DISCORD' in key or 'CHANNEL' in key or 'INTERVAL' in key:
            print(f"   {key}: {value}")
    raise ValueError("DISCORD_TOKEN environment variable is required!")

print(f"✅ Bot configured:")
print(f"   Target Channel: {TARGET_CHANNEL_ID}")
print(f"   Output Channel: {OUTPUT_CHANNEL_ID}")
print(f"   Check Interval: {CHECK_INTERVAL} seconds")
