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

# Validate required variables
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required!")

print(f"✅ Bot configured:")
print(f"   Target Channel: {TARGET_CHANNEL_ID}")
print(f"   Output Channel: {OUTPUT_CHANNEL_ID}")
print(f"   Check Interval: {CHECK_INTERVAL} seconds")
