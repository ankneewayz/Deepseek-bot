import os
import random
import asyncio
import sqlite3
from datetime import datetime
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

# High-Quality Cyberpunk / Anime / Superhero / Aesthetic Banner URLs
BANNER_URLS = [
    "https://images.hdqwalls.com/wallpapers/batman-dark-aesthetic-4k-qw.jpg",
    "https://images.hdqwalls.com/wallpapers/cyberpunk-2077-anime-girl-4k-i0.jpg",
    "https://images.hdqwalls.com/wallpapers/anime-boy-cyberpunk-city-neon-4k-zz.jpg",
    "https://images.hdqwalls.com/wallpapers/superhero-dark-knight-minimal-4k-ho.jpg",
    "https://images.hdqwalls.com/wallpapers/neon-girl-aesthetic-art-4k-xl.jpg"
]

# Database Setup
DB_FILE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    videos_consumed INTEGER DEFAULT 0,
                    last_active TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sent_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_id INTEGER
                )''')
    conn.commit()
    conn.close()

init_db()

# Database Helper Functions
def db_add_or_update_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO users (user_id, username, first_name, videos_consumed, last_active)
                 VALUES (?, ?, ?, 0, ?)
                 ON CONFLICT(user_id) DO UPDATE SET
                 username=excluded.username,
                 first_name=excluded.first_name,
                 last_active=excluded.last_active''', (user_id, username or "NoUsername", first_name or "User", now))
    conn.commit()
    conn.close()

def db_increment_video(user_id, count=1):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET videos_consumed = videos_consumed + ? WHERE user_id = ?", (count, user_id))
    conn.commit()
    conn.close()

def db_save_video_msg(user_id, message_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO sent_videos (user_id, message_id) VALUES (?, ?)", (user_id, message_id))
    conn.commit()
    conn.close()

def db_pop_last_video_msg(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, message_id FROM sent_videos WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    row = c.fetchone()
    if row:
        record_id, msg_id = row
        c.execute("DELETE FROM sent_videos WHERE id = ?", (record_id,))
        c.execute("UPDATE users SET videos_consumed = MAX(0, videos_consumed - 1) WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return msg_id
    conn.close()
    return None

def db_get_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT SUM(videos_consumed) FROM users")
    total_vids = c.fetchone()[0] or 0
    
    c.execute("SELECT user_id, username, first_name, videos_consumed, last_active FROM users ORDER BY videos_consumed DESC LIMIT 10")
    top_users = c.fetchall()
    
    conn.close()
    return total_users, total_vids, top_users


# --- INITIALIZE TELETHON CLIENTS ---
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


# --- VIDEO FETCHING LOGIC ---
async def fetch_random_video():
    """Fetches a video from one of the target source channels/bots."""
    target_chat = random.choice(SOURCE_CHATS)
    try:
        messages = await user_client.get_messages(target_chat, limit=50)
        video_msgs = [m for m in messages if m.video or (m.media and hasattr(m.media, 'document'))]
        if video_msgs:
            return random.choice(video_msgs)
    except Exception as e:
        print(f"Error fetching from {target_chat}: {e}")
    return None

async def process_and_send_videos(user_id, event, count=1):
    # Send animated waiting indicator
    waiting_msg = await event.respond("⚡ **[ System Processing ]**\n` Fetching hyper-stream content from matrix...`\n⏳ *Please wait...*")
    
    sent_count = 0
    for _ in range(count):
        video_msg = await fetch_random_video()
        if not video_msg:
            continue

        temp_video_path = None
        temp_thumb_path = None
        try:
            # First try direct forwarding
            sent = await bot.forward_messages(user_id, video_msg)
            db_save_video_msg(user_id, sent.id)
            sent_count += 1
        except ChatForwardsRestrictedError:
            # Fallback: Download and re-upload bypass
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
                db_save_video_msg(user_id, sent.id)
                sent_count += 1
            except Exception as ex:
                print(f"Failed re-upload: {ex}")
            finally:
                for path in (temp_video_path, temp_thumb_path):
                    if path and os.path.exists(path):
                        os.remove(path)

    # Delete loading state message
    await waiting_msg.delete()

    if sent_count > 0:
        db_increment_video(user_id, sent_count)
        return True
    else:
        await event.respond("❌ **Error:** Unable to fetch videos right now. Try again shortly!")
        return False


# --- BOT HANDLERS ---

WELCOME_TEXT = """
🔥 **WELCOME TO THE ULTRA VIP STREAM HUB** 🔥

⚡ *High-speed media bypass system activated.*
Select an action using the control panel below:
"""

MAIN_BUTTONS = [
    [Button.inline("➕ +1 Video", data=b"btn_plus1"), Button.inline("🗑️ -1 Video", data=b"btn_minus1")],
    [Button.inline("🎬 Custom Amount (/vid)", data=b"btn_custom_info")],
    [Button.inline("👑 Request Admin for More", data=b"btn_req_admin")]
]

@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    user = await event.get_sender()
    db_add_or_update_user(user.id, user.username, user.first_name)
    
    # Mind blowing entry with random aesthetic banner
    random_banner = random.choice(BANNER_URLS)
    
    await bot.send_file(
        event.chat_id,
        file=random_banner,
        caption=WELCOME_TEXT,
        buttons=MAIN_BUTTONS
    )

@bot.on(events.NewMessage(pattern=r"^/vid(?:\s+(\d+))?"))
async def vid_command_handler(event):
    user = await event.get_sender()
    db_add_or_update_user(user.id, user.username, user.first_name)
    
    match = event.pattern_match.group(1)
    if not match:
        await event.respond("⚠️ **Usage:** `/vid <1-10>`\n*Example:* `/vid 5` to fetch 5 videos.")
        return
    
    amount = int(match)
    if amount < 1 or amount > 10:
        await event.respond("🛑 **Limit Exceeded:** You can request between **1** and **10** videos at once.")
        return
        
    await process_and_send_videos(event.chat_id, event, count=amount)


@bot.on(events.CallbackQuery)
async def callback_handler(event):
    user = await event.get_sender()
    db_add_or_update_user(user.id, user.username, user.first_name)
    data = event.data

    if data == b"btn_plus1":
        await event.answer("⚡ Fetching 1 Video...")
        await process_and_send_videos(event.chat_id, event, count=1)

    elif data == b"btn_minus1":
        msg_id_to_del = db_pop_last_video_msg(user.id)
        if msg_id_to_del:
            try:
                await bot.delete_messages(event.chat_id, msg_id_to_del)
                await event.answer("🗑️ Deleted last sent video!", alert=True)
            except Exception:
                await event.answer("⚠️ Could not delete message (might be older than 48h).", alert=True)
        else:
            await event.answer("❌ No recent video found to delete.", alert=True)

    elif data == b"btn_custom_info":
        await event.answer()
        await event.respond("ℹ️ **To get multiple videos:**\nType `/vid <amount>` in chat.\n*Maximum limit is 10 videos per request.*")

    elif data == b"btn_req_admin":
        await event.answer("📩 Request sent to Admins!")
        msg = f"🔔 **ADMIN REQUEST**\nUser: [{user.first_name}](tg://user?id={user.id}) (`@{user.username}`)\nID: `{user.id}` requested more videos!"
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, msg)
            except Exception as e:
                print(f"Failed notifying admin {admin_id}: {e}")
        await event.respond("✅ **Admins have been notified!** They will review your request shortly.")


# --- ADMIN PANEL COMMANDS ---

@bot.on(events.NewMessage(pattern="/admin"))
async def admin_panel(event):
    if event.sender_id not in ADMIN_IDS:
        return
    
    total_users, total_vids, top_users = db_get_stats()
    
    admin_text = f"👑 **VIP SYSTEM ADMIN PANEL** 👑\n\n"
    admin_text += f"👥 **Total Registered Users:** `{total_users}`\n"
    admin_text += f"🎥 **Total Videos Delivered:** `{total_vids}`\n\n"
    admin_text += "📊 **TOP USER CONSUMPTION:**\n"
    admin_text += "───────────────────────────\n"
    
    for idx, u in enumerate(top_users, 1):
        uid, uname, fname, vids, last_act = u
        admin_text += f"**{idx}.** `{fname}` (@{uname}) | ID: `{uid}`\n   └ 🎬 **Vids:** `{vids}` | 🕒 **Last Active:** `{last_act}`\n"
        
    await event.respond(admin_text)


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
