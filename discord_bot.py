import re
import discord
import asyncio
from datetime import datetime, timedelta
from config import DISCORD_TOKEN, TARGET_CHANNEL_ID, OUTPUT_CHANNEL_ID, CHECK_INTERVAL
from shared_state import decoy_status_manager

# Patterns for decoy status detection - EXACT matches only
DECOY_ON_PATTERNS = [
    re.compile(r"Server: Decoy check in progress\. Do not hit decoy npcs \(\d+ min\. remaining\)", re.IGNORECASE)
]

DECOY_OFF_PATTERNS = [
    re.compile(r"Server: Decoy check complete\. thank you \^\^", re.IGNORECASE)
]

# Initialize shared state
decoy_status_manager.set_check_interval(CHECK_INTERVAL)

# Use discord.py-self which is designed for self-bots
# Disable member list scraping to prevent spam warnings
try:
    # For discord.py-self, disable member list scraping
    intents = discord.Intents.default()
    intents.members = False
    intents.presences = False
    client = discord.Client(intents=intents, chunk_guilds_at_startup=False)
except Exception:
    # Fallback for older discord.py-self versions
    client = discord.Client(chunk_guilds_at_startup=False)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("Bot is monitoring for decoy status messages...")
    
    # Set bot as online in shared state
    decoy_status_manager.set_bot_online(True)
    
    # Check recent messages to determine current status
    await check_recent_messages()
    
    # Start the periodic check task
    asyncio.create_task(periodic_decoy_check())

async def periodic_decoy_check():
    """Check for decoy status changes periodically"""
    while True:
        try:
            check_interval = decoy_status_manager.get_check_interval()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Running periodic decoy check (every {check_interval}s)...")
            await check_recent_messages()
            await asyncio.sleep(check_interval)
        except Exception as e:
            print(f"Error in periodic check: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

async def cleanup_old_status_messages():
    """Remove old status messages to keep only one"""
    try:
        output_channel = client.get_channel(OUTPUT_CHANNEL_ID)
        if not output_channel:
            return
            
        # Get recent messages from the bot
        bot_messages = []
        async for message in output_channel.history(limit=50):
            if message.author.id == client.user.id and "DECOY STATUS" in message.content:
                bot_messages.append(message)
        
        # Keep only the most recent one, delete the rest
        if len(bot_messages) > 1:
            for message in bot_messages[1:]:  # Skip the first (most recent)
                try:
                    await message.delete()
                    print(f"🗑️ Deleted old status message")
                except:
                    pass
                    
    except Exception as e:
        print(f"Error cleaning up messages: {e}")

async def update_status_message():
    """Update the single status message in the output channel"""
    try:
        output_channel = client.get_channel(OUTPUT_CHANNEL_ID)
        if not output_channel:
            print("Could not find output channel")
            return
        
        # Get current status from shared state
        status_data = decoy_status_manager.get_status()
        latest_decoy_status = status_data['status']
        latest_message_time_str = status_data['last_update']
        
        # Format message based on decoy status
        if latest_decoy_status == "ON":
            status_text = f"@everyone\n🔴 **DECOY STATUS: {latest_decoy_status}**"
        else:
            status_text = f"🔴 **DECOY STATUS: {latest_decoy_status}**"
        
        if latest_message_time_str:
            latest_message_time = datetime.fromisoformat(latest_message_time_str)
            status_text += f"\n*Last updated: {latest_message_time.strftime('%Y-%m-%d %H:%M:%S')}*"
        else:
            status_text += "\n*No recent decoy activity detected*"
            
        # Get current status message ID
        status_message_id = decoy_status_manager.get_status_message_id()
        
        # If we have a message ID, try to edit it
        if status_message_id:
            try:
                message = await output_channel.fetch_message(status_message_id)
                await message.edit(content=status_text)
                print(f"✅ Updated existing status message: {status_text[:50]}...")
                return
            except discord.NotFound:
                # Message was deleted, create a new one
                print("⚠️ Status message was deleted, creating new one...")
                decoy_status_manager.set_status_message_id(None)
            except discord.Forbidden:
                # No permission to edit, create a new one
                print("⚠️ No permission to edit message, creating new one...")
                decoy_status_manager.set_status_message_id(None)
            except Exception as e:
                print(f"⚠️ Error editing message: {e}, creating new one...")
                decoy_status_manager.set_status_message_id(None)
        
        # Create new message if we don't have an ID or editing failed
        try:
            message = await output_channel.send(status_text)
            decoy_status_manager.set_status_message_id(message.id)
            print(f"✅ Created new status message: {status_text[:50]}...")
            
            # Clean up any old status messages
            await cleanup_old_status_messages()
        except Exception as e:
            print(f"❌ Error creating message: {e}")
        
    except Exception as e:
        print(f"Error updating status message: {e}")
        import traceback
        traceback.print_exc()

async def check_recent_messages(force_update=False):
    """Check recent messages to determine current decoy status"""
    try:
        channel = client.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            print("Could not find target channel")
            return
            
        print(f"Checking recent messages in channel: {channel.name}")
        message_count = 0
        decoy_messages_found = 0
        
        # Get current status from shared state
        current_status_data = decoy_status_manager.get_status()
        current_status = current_status_data['status']
        current_time_str = current_status_data['last_update']
        current_time = datetime.fromisoformat(current_time_str) if current_time_str else None
        
        # Get last 200 messages to find decoy messages
        decoy_messages = []  # Store all decoy messages found
        
        async for message in channel.history(limit=200):
            message_count += 1
            if message.author.id == client.user.id:
                continue
                
            content = message.content
            message_time = message.created_at
            
            # Check if this is a decoy message
            is_decoy_on = any(pattern.search(content) for pattern in DECOY_ON_PATTERNS)
            is_decoy_off = any(pattern.search(content) for pattern in DECOY_OFF_PATTERNS)
            
            if is_decoy_on or is_decoy_off:
                decoy_messages_found += 1
                decoy_status = "ON" if is_decoy_on else "OFF"
                decoy_messages.append({
                    'content': content,
                    'time': message_time,
                    'status': decoy_status
                })
                print(f"Found decoy message: [{message_time.strftime('%H:%M:%S')}] {decoy_status} - {content[:100]}...")
        
        # Find the most recent decoy message
        if decoy_messages:
            # Sort by time (most recent first)
            decoy_messages.sort(key=lambda x: x['time'], reverse=True)
            most_recent = decoy_messages[0]
            
            new_status = most_recent['status']
            new_time = most_recent['time']
            
            # Only update if status changed or this is a forced update
            status_changed = (current_status != new_status or 
                            current_time != new_time or 
                            force_update)
            
            if status_changed:
                # Update shared state
                decoy_status_manager.update_status(new_status, new_time)
                
                print(f"\n=== DECOY STATUS {'CHANGED' if current_status != new_status else 'UPDATED'} ===")
                for i, msg in enumerate(decoy_messages[:3]):  # Show first 3
                    print(f"{i+1}. [{msg['time'].strftime('%H:%M:%S')}] {msg['status']} - {msg['content']}")
                print(f"Current status: {new_status} at {new_time.strftime('%H:%M:%S')}")
                
                # Update the status message
                await update_status_message()
            else:
                print(f"Status unchanged: {current_status} (last check: {current_time.strftime('%H:%M:%S') if current_time else 'Never'})")
        else:
            print("No decoy messages found in the last 200 messages")
        
        print(f"Checked {message_count} messages, found {decoy_messages_found} decoy messages")
                    
    except Exception as e:
        print(f"Error checking recent messages: {e}")
        import traceback
        traceback.print_exc()

async def show_server_messages():
    """Show recent server messages to help identify decoy patterns"""
    try:
        channel = client.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            print("Could not find target channel")
            return
            
        print("Searching for server messages...")
        server_messages = []
        
        # Get last 100 messages
        async for message in channel.history(limit=100):
            if message.author.id == client.user.id:
                continue
                
            # Look for messages from "Server" or messages that might be system messages
            if (message.author.name.lower() == "server" or 
                "server:" in message.content.lower() or
                "decoy" in message.content.lower() or
                "check" in message.content.lower() or
                "complete" in message.content.lower() or
                "progress" in message.content.lower()):
                
                server_messages.append({
                    'content': message.content,
                    'author': message.author.name,
                    'time': message.created_at
                })
        
        print(f"Found {len(server_messages)} potential server messages:")
        for msg in server_messages[:10]:  # Show first 10
            print(f"[{msg['time'].strftime('%H:%M:%S')}] {msg['author']}: {msg['content']}")
            
    except Exception as e:
        print(f"Error showing server messages: {e}")
        import traceback
        traceback.print_exc()

async def show_all_decoy_messages():
    """Show all decoy messages found in recent history"""
    try:
        channel = client.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            print("Could not find target channel")
            return
            
        print("Searching for all decoy messages...")
        decoy_messages = []
        
        # Get last 500 messages to find more decoy messages
        async for message in channel.history(limit=500):
            if message.author.id == client.user.id:
                continue
                
            content = message.content
            message_time = message.created_at
            
            # Check if this is a decoy message
            is_decoy_on = any(pattern.search(content) for pattern in DECOY_ON_PATTERNS)
            is_decoy_off = any(pattern.search(content) for pattern in DECOY_OFF_PATTERNS)
            
            if is_decoy_on or is_decoy_off:
                decoy_status = "ON" if is_decoy_on else "OFF"
                decoy_messages.append({
                    'content': content,
                    'time': message_time,
                    'status': decoy_status
                })
        
        # Sort by time (most recent first)
        decoy_messages.sort(key=lambda x: x['time'], reverse=True)
        
        print(f"Found {len(decoy_messages)} decoy messages:")
        for i, msg in enumerate(decoy_messages):
            print(f"{i+1}. [{msg['time'].strftime('%Y-%m-%d %H:%M:%S')}] {msg['status']} - {msg['content']}")
            
        if decoy_messages:
            most_recent = decoy_messages[0]
            print(f"\nMost recent decoy status: {most_recent['status']} at {most_recent['time'].strftime('%Y-%m-%d %H:%M:%S')}")
            
    except Exception as e:
        print(f"Error showing decoy messages: {e}")
        import traceback
        traceback.print_exc()

@client.event
async def on_message(message):
    if message.channel.id != TARGET_CHANNEL_ID or message.author.id == client.user.id:
        return

    content = message.content
    message_time = message.created_at
    
    # Check if this is a decoy ON message
    is_decoy_on = any(pattern.search(content) for pattern in DECOY_ON_PATTERNS)
    
    # Check if this is a decoy OFF message
    is_decoy_off = any(pattern.search(content) for pattern in DECOY_OFF_PATTERNS)
    
    # Update status if we found a decoy message
    if is_decoy_on or is_decoy_off:
        # Get current status from shared state
        current_status_data = decoy_status_manager.get_status()
        current_time_str = current_status_data['last_update']
        current_time = datetime.fromisoformat(current_time_str) if current_time_str else None
        
        # Only update if this message is newer than our current latest
        if current_time is None or message_time > current_time:
            new_status = "ON" if is_decoy_on else "OFF"
            decoy_status_manager.update_status(new_status, message_time)
            
            # Update the single status message
            print(f"[{message_time.strftime('%H:%M:%S')}] Decoy status changed to {new_status} - Message: {content[:50]}...")
            await update_status_message()
    
    # Handle manual status check command
    if content.lower() == "!decoy_status":
        print("Status check requested")
        await update_status_message()
    
    # Handle manual search command
    elif content.lower() == "!search_decoy":
        print("Manual decoy search requested")
        await check_recent_messages(force_update=True)
    
    # Handle server messages only command
    elif content.lower() == "!server_messages":
        print("Server messages search requested")
        await show_server_messages()
    
    # Handle show all decoy messages command
    elif content.lower() == "!show_decoy_messages":
        print("Show all decoy messages requested")
        await show_all_decoy_messages()
    
    # Handle force update command
    elif content.lower() == "!update_status":
        print("Force status update requested")
        await update_status_message()
    
    # Handle interval change command
    elif content.lower().startswith("!interval"):
        try:
            parts = content.split()
            if len(parts) == 2:
                new_interval = int(parts[1])
                if 30 <= new_interval <= 600:  # Between 30 seconds and 10 minutes
                    decoy_status_manager.set_check_interval(new_interval)
                    print(f"Check interval changed to {new_interval} seconds")
                    output_channel = client.get_channel(OUTPUT_CHANNEL_ID)
                    if output_channel:
                        await output_channel.send(f"✅ Check interval changed to {new_interval} seconds")
                else:
                    print("Interval must be between 30 and 600 seconds")
            else:
                current_interval = decoy_status_manager.get_check_interval()
                print(f"Current interval: {current_interval} seconds. Use: !interval <seconds>")
        except ValueError:
            print("Invalid interval value. Use: !interval <seconds>")
    
    # Handle cleanup command
    elif content.lower() == "!cleanup":
        print("Cleanup requested")
        await cleanup_old_status_messages()
        output_channel = client.get_channel(OUTPUT_CHANNEL_ID)
        if output_channel:
            await output_channel.send("🧹 Cleaned up old status messages")
    
    # Handle status info command
    elif content.lower() == "!bot_info":
        print("Bot info requested")
        output_channel = client.get_channel(OUTPUT_CHANNEL_ID)
        if output_channel:
            status_data = decoy_status_manager.get_status()
            info_text = f"🤖 **Bot Status**\n"
            info_text += f"• Check interval: {status_data['check_interval']} seconds\n"
            info_text += f"• Current decoy status: {status_data['status'] or 'Unknown'}\n"
            if status_data['last_update']:
                last_update = datetime.fromisoformat(status_data['last_update'])
                info_text += f"• Last update: {last_update.strftime('%Y-%m-%d %H:%M:%S')}\n"
            info_text += f"• API available: Yes\n"
            info_text += f"• Commands: !decoy_status, !search_decoy, !interval <sec>, !cleanup, !bot_info"
            await output_channel.send(info_text)

if __name__ == "__main__":
    try:
        client.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Error running bot: {e}")
