import os
import random
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import ChatForwardsRestrictedError

# --- DUMMY HTTP HEALTH CHECK FOR RENDER FREE TIER ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live and healthy!")

    def log_message(self, format, *args):
        return  # Suppress HTTP request logs in stdout

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# Start HTTP server in a background thread
threading.Thread(target=start_health_server, daemon=True).start()


# --- ENVIRONMENT CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

# Target channels to fetch media from
SOURCE_CHATS = ["@Thenewpromobot", "@MrpromoterOgbot", "@WorldHilasanaBot"]

# Parse Admin IDs from environment
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "7017637051,8598993143,7355946581").split(",") if x.strip()]

# High-Quality Cyberpunk / Aesthetic Banner URLs

# --- DIRECT CDN / GOOGLE HOSTED IMAGE LINKS ---
BANNER_URLS = [
    "https://i.imgur.com/2nLdaA4.jpg",
    "https://i.imgur.com/39A8pXp.jpeg",
    "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200",
    "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1200"
]


# --- IN-MEMORY STORAGE ---
SEEN_VIDEOS = defaultdict(set)
USER_SENT_MSGS = defaultdict(list)
USER_STATS = defaultdict(int)
USER_INFO = {}

# Global client placeholders
bot = None
user_client = None


# --- VIDEO FETCHING LOGIC ---
async def fetch_random_unseen_video(user_id):
    target_chat = random.choice(SOURCE_CHATS)
    try:
        messages = await user_client.get_messages(target_chat, limit=100)
        
        unseen_msgs = [
            m for m in messages 
            if (m.video or (m.media and hasattr(m.media, 'document'))) 
            and (target_chat, m.id) not in SEEN_VIDEOS[user_id]
        ]
        
        if not unseen_msgs:
            SEEN_VIDEOS[user_id] = {item for item in SEEN_VIDEOS[user_id] if item[0] != target_chat}
            unseen_msgs = [m for m in messages if m.video or (m.media and hasattr(m.media, 'document'))]

        if unseen_msgs:
            chosen_msg = random.choice(unseen_msgs)
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
            sent = await bot.forward_messages(user_id, video_msg)
            USER_SENT_MSGS[user_id].append(sent.id)
            sent_count += 1
        except ChatForwardsRestrictedError:
            try:
                temp_thumb_path = await user_client.download_media(video_msg, thumb=-1) if hasattr(video_msg.media, 'document') else None
                temp_video_path = await user_client.download_media(video_msg)
                
                attributes = video_msg.media.document.attributes if hasattr(video_msg.media, 'document') else None
                
                sent = await bot.send_file(
                    user_id,
                    temp_video_path,
                    caption=video_msg.text or "🎬 **Exclusive Stream**",
                    attributes=attributes,
                    thumb=temp_thumb_path,
                    supports_streaming=True
                )
                USER_SENT_MSGS[user_id].append(sent.id)
                sent_count += 1
            except Exception as ex:
                print(f"Failed re-upload: {ex}")
            finally:
                for path in (temp_video_path, temp_thumb_path):
                    if path and os.path.exists(path):
                        os.remove(path)

    await waiting_msg.delete()

    if sent_count > 0:
        USER_STATS[user_id] += sent_count
        return True
    else:
        await event.respond("❌ **Error:** Unable to fetch unseen videos right now. Try again shortly!")
        return False


# --- UI & COMMANDS ---
WELCOME_TEXT = """
🔥 **WELCOME TO THE ULTRA VIP STREAM HUB** 🔥

⚡ *Live media stream active (Zero-Save No-Repeat Engine).*
Select an action using the control panel below:
"""

MAIN_BUTTONS = [
    [Button.inline("➕ +1 Video", data=b"btn_plus1"), Button.inline("🗑️ -1 Video", data=b"btn_minus1")],
    [Button.inline("🎬 Custom Amount (/vid)", data=b"btn_custom_info")],
    [Button.inline("👑 Request Admin for More", data=b"btn_req_admin")]
]

def update_user_info(user):
    USER_INFO[user.id] = {
        "username": user.username or "NoUsername",
        "first_name": user.first_name or "User"
    }

async def start_handler(event):
    user = await event.get_sender()
    update_user_info(user)
    random_banner = random.choice(BANNER_URLS)
    await bot.send_file(
        event.chat_id,
        file=random_banner,
        caption=WELCOME_TEXT,
        buttons=MAIN_BUTTONS
    )

async def vid_command_handler(event):
    user = await event.get_sender()
    update_user_info(user)
    match = event.pattern_match.group(1)
    if not match:
        await event.respond("⚠️ **Usage:** `/vid <1-10>`\n*Example:* `/vid 5` to fetch 5 unseen videos.")
        return
    
    amount = int(match)
    if amount < 1 or amount > 10:
        await event.respond("🛑 **Limit Exceeded:** You can request between **1** and **10** videos at once.")
        return
        
    await process_and_send_videos(event.chat_id, event, count=amount)

async def callback_handler(event):
    user = await event.get_sender()
    update_user_info(user)
    data = event.data

    if data == b"btn_plus1":
        await event.answer("⚡ Fetching 1 Unseen Video...")
        await process_and_send_videos(event.chat_id, event, count=1)

    elif data == b"btn_minus1":
        if USER_SENT_MSGS[user.id]:
            last_msg_id = USER_SENT_MSGS[user.id].pop()
            try:
                await bot.delete_messages(event.chat_id, last_msg_id)
                USER_STATS[user.id] = max(0, USER_STATS[user.id] - 1)
                await event.answer("🗑️ Deleted last sent video!", alert=True)
            except Exception:
                await event.answer("⚠️ Could not delete message.", alert=True)
        else:
            await event.answer("❌ No recent video found in this session to delete.", alert=True)

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

async def admin_panel(event):
    if event.sender_id not in ADMIN_IDS:
        return
    
    total_users = len(USER_INFO)
    total_vids = sum(USER_STATS.values())
    
    admin_text = f"👑 **VIP SYSTEM ADMIN PANEL** 👑\n\n"
    admin_text += f"👥 **Total Tracked Users:** `{total_users}`\n"
    admin_text += f"🎥 **Total Videos Delivered:** `{total_vids}`\n\n"
    admin_text += "📊 **SESSION CONSUMPTION LEADERBOARD:**\n"
    admin_text += "───────────────────────────\n"
    
    sorted_users = sorted(USER_STATS.items(), key=lambda x: x[1], reverse=True)[:10]
    if not sorted_users:
        admin_text += "_No video consumption recorded yet in this session._\n"
    else:
        for idx, (uid, count) in enumerate(sorted_users, 1):
            info = USER_INFO.get(uid, {"first_name": "User", "username": "NoUsername"})
            admin_text += f"**{idx}.** `{info['first_name']}` (@{info['username']}) | ID: `{uid}`\n   └ 🎬 **Vids:** `{count}`\n"
        
    await event.respond(admin_text)


# --- MAIN ASYNC RUNNER ---
async def main():
    global bot, user_client

    # Instantiate clients inside the running event loop
    user_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    bot = TelegramClient('bot_session', API_ID, API_HASH)

    # Attach Event Handlers
    bot.add_event_handler(start_handler, events.NewMessage(pattern="/start"))
    bot.add_event_handler(vid_command_handler, events.NewMessage(pattern=r"^/vid(?:\s+(\d+))?"))
    bot.add_event_handler(callback_handler, events.CallbackQuery())
    bot.add_event_handler(admin_panel, events.NewMessage(pattern="/admin"))

    print("Connecting User Client...")
    await user_client.start()
    print("User Client Connected.")

    print("Connecting Bot Client...")
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot Client Connected & Ready!")

    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())
