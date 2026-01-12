import os
import telebot
from telebot import types

# टोकन को Render के Environment Variables में सेट करें
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

CHANNELS = ["@hackerscolonytech"] # आपका चैनल

def check_join(user_id):
    try:
        for channel in CHANNELS:
            status = bot.get_chat_member(channel, user_id).status
            # अगर यूजर एडमिन, ओनर या मेम्बर है तो True देगा
            if status in ['creator', 'administrator', 'member']:
                return True
        return False
    except Exception as e:
        print(f"Error checking status: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    if check_join(user_id):
        # अगर जॉइन किया हुआ है तो ये दिखेगा
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("✨ Generate New Year Link", url="https://happy-wishing-you.onrender.com")
        btn2 = types.InlineKeyboardButton("👨‍💻 Contact Admin", url="https://t.me/Roshanali000")
        markup.add(btn1, btn2)
        
        bot.send_message(message.chat.id, 
            "<b>Access Granted! ✅</b>\n\nYour personalized New Year 2026 magic link is ready below.", 
            parse_mode='HTML', reply_markup=markup)
    else:
        # अगर जॉइन नहीं किया है तो ये दिखेगा (Force Join)
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_join = types.InlineKeyboardButton("📢 Join Our Channel", url="https://t.me/hackerscolonytech")
        btn_verify = types.InlineKeyboardButton("🔄 Verify Membership", callback_data="verify")
        markup.add(btn_join, btn_verify)
        
        bot.send_message(message.chat.id, 
            "<b>Access Denied! ❌</b>\n\nYou must join our official channel to use this bot's premium features.", 
            parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "verify":
        if check_join(call.from_user.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message) # दोबारा स्टार्ट फंक्शन कॉल करेगा और लिंक दे देगा
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined the channel yet!", show_alert=True)

bot.polling()
