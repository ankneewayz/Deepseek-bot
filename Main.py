import os
import random
import asyncio
from collections import defaultdict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import ChatForwardsRestrictedError

# --- ENV CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

# Source channels / bots to pull videos from
SOURCE_CHATS = ["@Thenewpromobot", "@MrpromoterOgbot", "@WorldHilasanaBot"]

# Parse Admin IDs
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "7017637051,8598993143,7355946581").split(",") if x.strip()]

# High-Quality Aesthetic Banner URLs
BANNER_URLS = [
    "https://images.hdqwalls.com/wallpapers/batman-dark-aesthetic-4k-qw.jpg",
    "https://images.hdqwalls.com/wallpapers/cyberpunk-2077-anime-girl-4k-i0.jpg",
    "https://images.hdqwalls.com/wallpapers/anime-boy-cyberpunk-city-neon-4k-zz.jpg",
    "https://images.hdqwalls.com/wallpapers/superhero-dark-knight-minimal-4k-ho.jpg",
    "https://images.hdqwalls.com/wallpapers/neon-girl-aesthetic-art-4k-xl.jpg"
]

# --- IN-MEMORY NO-REPEAT TRACKER ---
# Structure: user_id -> set of (target_chat, message_id)
SEEN_VIDEOS = defaultdict(set)


# --- INITIALIZE TELETHON CLIENTS ---
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


# --- LIVE VIDEO FETCHING LOGIC (NO REPEATS) ---
async def fetch_random_unseen_video(user_id):
    """Fetches a live video from target chats that the user HAS NOT seen yet."""
    target_chat = random.choice(SOURCE_CHATS)
    try:
        messages = await user_client.get_messages(target_chat, limit=100)
        
        # Filter for videos not yet delivered to this user
        unseen_msgs = [
            m for m in messages 
            if (m.video or (m.media and hasattr(m.media, 'document'))) 
            and (target_chat, m.id) not in SEEN_VIDEOS[user_id]
        ]
        
        # If user has seen all 100 recent videos, clear memory for this chat to allow fresh cycle
        if not unseen_msgs:
            SEEN_VIDEOS[user_id] = {item for item in SEEN_VIDEOS[user_id] if item[0] != target_chat}
            unseen_msgs = [m for m in messages if m.video or (m.media and hasattr(m.media, 'document'))]

        if unseen_msgs:
            chosen_msg = random.choice(unseen_msgs)
            # Remember this video for the user so it is never repeated
            SEEN_VIDEOS[user_id].add((target_chat, chosen_msg.id))
            return chosen_msg

    except Exception as e:
        print(f"Error fetching from {target_chat}: {e}")
    return None

async def process_and_send_videos(user_id, event, count=1):
    waiting_msg = await event.respond("⚡ **[ Live Stream Fetch ]**\n` Pulling unseen media from matrix...`\n⏳ *Please wait...*")
    
    sent_count = 0
    for _ in range(count):
        video_msg = await fetch_random_unseen_video(user_id)
        if not video_msg:
            continue

        temp_video_path = None
        temp_thumb_path = None
        try:
            # Direct forward attempt
            await bot.forward_messages(user_id, video_msg)
            sent_count += 1
        except ChatForwardsRestrictedError:
            # Fallback: On-the-fly download & re-upload (No permanent storage)
            try:
                temp_thumb_path = await user_client.download_media(video_msg, thumb=-1) if hasattr(video_msg.media, 'document') else None
                temp_video_path = await user_client.download_media(video_msg)
                
                attributes = video_msg.media.document.attributes if hasattr(video_msg.media, 'document') else None
                
                await bot.send_file(
                    user_id,
                    temp_video_path,
                    caption=video_msg.text or "🎬 **Exclusive Stream**",
                    attributes=attributes,
                    thumb=temp_thumb_path,
                    supports_streaming=True
                )
                sent_count += 1
            except Exception as ex:
                print(f"Failed re-upload: {ex}")
            finally:
                # Immediate cleanup of local temp files
                for path in (temp_video_path, temp_thumb_path):
                    if path and os.path.exists(path):
                        os.remove(path)

    await waiting_msg.delete()

    if sent_count == 0:
        await event.respond("❌ **Error:** Unable to fetch unseen videos right now. Try again shortly!")


# --- BOT HANDLERS ---

WELCOME_TEXT = """
🔥 **WELCOME TO THE ULTRA VIP STREAM HUB** 🔥

⚡ *Live media stream active (Zero-Save No-Repeat Engine).*
Select an action using the control panel below:
"""

MAIN_BUTTONS = [
    [Button.inline("➕ Get 1 Video", data=b"btn_plus1")],
    [Button.inline("🎬 Custom Amount (/vid)", data=b"btn_custom_info")],
    [Button.inline("👑 Request Admin for More", data=b"btn_req_admin")]
]

@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    random_banner = random.choice(BANNER_URLS)
    await bot.send_file(
        event.chat_id,
        file=random_banner,
        caption=WELCOME_TEXT,
        buttons=MAIN_BUTTONS
    )

@bot.on(events.NewMessage(pattern=r"^/vid(?:\s+(\d+))?"))
async def vid_command_handler(event):
    match = event.pattern_match.group(1)
    if not match:
        await event.respond("⚠️ **Usage:** `/vid <1-10>`\n*Example:* `/vid 5` to fetch 5 unseen videos.")
        return
    
    amount = int(match)
    if amount < 1 or amount > 10:
        await event.respond("🛑 **Limit Exceeded:** You can request between **1** and **10** videos at once.")
        return
        
    await process_and_send_videos(event.chat_id, event, count=amount)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user = await event.get_sender()
    data = event.data

    if data == b"btn_plus1":
        await event.answer("⚡ Fetching 1 Unseen Video...")
        await process_and_send_videos(event.chat_id, event, count=1)

    elif data == b"btn_custom_info":
        await event.answer()
        await event.respond("ℹ️ **To get multiple unique videos:**\nType `/vid <amount>` in chat.\n*Maximum limit is 10 videos per request.*")

    elif data == b"btn_req_admin":
        await event.answer("📩 Request sent to Admins!")
        msg = f"🔔 **ADMIN REQUEST**\nUser: [{user.first_name}](tg://user?id={user.id}) (`@{user.username}`)\nID: `{user.id}` requested more videos!"
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, msg)
            except Exception as e:
                print(f"Failed notifying admin {admin_id}: {e}")
        await event.respond("✅ **Admins have been notified!**")


# --- MAIN RUNNER ---
async def main():
    print("Connecting User Client...")
    await user_client.start()
    print("User Client Connected.")
    
    print("Connecting Bot Client...")
    await bot.start()
    print("Bot Client Connected & Ready!")
    
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())
