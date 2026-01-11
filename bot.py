import os
import telebot
from telebot import types

# टोकन को सुरक्षित रखने के लिए variable का इस्तेमाल
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = "7162565886"
CHANNELS = ["@hackerscolonytech"] # आपका टेलीग्राम चैनल

def check_join(user_id):
    for channel in CHANNELS:
        status = bot.get_chat_member(channel, user_id).status
        if status == 'left':
            return False
    return True

@bot.message_status_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_join(user_id):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("✨ Generate New Year Link", callback_data="gen_link")
        btn2 = types.InlineKeyboardButton("👨‍💻 Contact Admin", url="https://t.me/Roshanali000")
        markup.add(btn1, btn2)
        
        bot.send_message(message.chat.id, 
            "<b>Welcome to Hacker's Colony Tech!</b>\n\n"
            "Our system is ready to create your personalized New Year 2026 Auditor link.", 
            parse_mode='HTML', reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/hackerscolonytech")
        markup.add(btn)
        bot.send_message(message.chat.id, "<b>Access Denied!</b>\n\nPlease join our official channel to continue.", 
            parse_mode='HTML', reply_markup=markup)

# Broadcast Feature (Sirf Admin ke liye)
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.from_user.id) == ADMIN_ID:
        msg = bot.reply_to(message, "Enter the message you want to broadcast:")
        bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    # Yahan hum users ki list database se lekar loop chalayenge
    bot.send_message(message.chat.id, "Broadcast system is being configured...")

bot.polling()
