import telebot
import requests
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# ১. আপনার আসল বটের টোকেনটি এখানে বসান (অবশ্যই "" এর ভেতরে)
BOT_TOKEN = "এখানে_আপনার_বট_টোকেন_বসান"

ADMIN_ID = 8262679678  # আপনার নিজের টেলিগ্রাম ইউজার আইডি
CHANNEL_ID = "-1003956226642" 
GROUP_ID = "-1004309875319"

bot = telebot.TeleBot(BOT_TOKEN)
FREE_API_URL = "https://sms24.me/api/v1"
USERS_FILE = "users.txt"

# 🖥️ Render-কে ২৪ ঘণ্টা লাইভ রাখার জন্য Flask ওয়েব সার্ভার সেটআপ
app = Flask('')

@app.route('/')
def home():
    return "বট সচল আছে!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ইউজার আইডি ডাটাবেজে সেভ করা
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write(f"{user_id}\n")
    else:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
        if str(user_id) not in users:
            with open(USERS_FILE, "a") as f:
                f.write(f"{user_id}\n")

# মেম্বারশিপ চেক করার ফাংশন
def is_subscribed(user_id):
    try:
        channel_status = bot.get_chat_member(int(CHANNEL_ID), user_id).status
        group_status = bot.get_chat_member(int(GROUP_ID), user_id).status
        return channel_status not in ['left', 'kicked'] and group_status not in ['left', 'kicked']
    except Exception as e:
        print(f"মেম্বারশিপ চেকে সমস্যা: {e}")
        return True

# জয়েনিং মেনু
def send_join_request(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📢 Join OTP Channel", url="https://t.me/SHS_Otp_Channel"))
    markup.row(InlineKeyboardButton("💬 Join OTP Group", url="https://t.me/+DXdDIm7-rRU4YTQ1"))
    markup.row(InlineKeyboardButton("✅ Joined", callback_data="check_membership"))
    bot.send_message(chat_id, "⚠️ সার্ভিসটি ব্যবহার করতে প্রথমে আমাদের ওটিপি চ্যানেল এবং গ্রুপে জয়েন করুন। তারপর '✅ Joined' বাটনে ক্লিক করুন।", reply_markup=markup)

# মেইন মেনু
def send_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🇺🇸 USA", callback_data="free_US"), InlineKeyboardButton("🇬🇧 UK", callback_data="free_GB"))
    markup.row(InlineKeyboardButton("🇨🇦 Canada", callback_data="free_CA"))
    text = "👋 ফ্রি ভার্চুয়াল নাম্বার বটে স্বাগতম! দেশ সিলেক্ট করুন:"
    if message_id: 
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
    else: 
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_bot(message):
    save_user(message.chat.id)
    if is_subscribed(message.chat.id): 
        send_main_menu(message.chat.id)
    else: 
        send_join_request(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_membership(call):
    if is_subscribed(call.from_user.id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        send_main_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, text="❌ আপনি এখনো জয়েন করেননি!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("free_"))
def get_numbers(call):
    if not is_subscribed(call.from_user.id):
        send_join_request(call.message.chat.id)
        return
    country_code = call.data.split("_")[1]
    url = f"{FREE_API_URL}/countries/{country_code}"
    try:
        response = requests.get(url).json()
        if response.get('status') == 'success':
            numbers = response['numbers'][:5]
            markup = InlineKeyboardMarkup()
            for num in numbers:
                markup.add(InlineKeyboardButton(f"📱 {num}", callback_data=f"showotp_{num.replace('+', '')}"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="নম্বর সিলেক্ট করুন:", reply_markup=markup)
    except: 
        bot.send_message(call.message.chat.id, "❌ নম্বর লোড করতে সমস্যা হয়েছে।")

@bot.callback_query_handler(func=lambda call: call.data.startswith("showotp_"))
def get_otp(call):
    phone = call.data.split("_")[1]
    url = f"{FREE_API_URL}/numbers/{phone}"
    try:
        response = requests.get(url).json()
        if response.get('status') == 'success' and response.get('sms'):
            sms = response['sms'][0]
            msg_text = f"💬 **+{phone}** ওটিপি: {sms.get('text')}"
            
            # চ্যানেল ও গ্রুপে ওটিপি ফরওয়ার্ড
            bot.send_message(int(CHANNEL_ID), msg_text)
            bot.send_message(int(GROUP_ID), msg_text)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔄 Refresh", callback_data=f"showotp_{phone}"), InlineKeyboardButton("🔙 Back", callback_data="back_main")))
        else:
            bot.answer_callback_query(call.id, text="নতুন ওটিপি আসেনি।")
    except Exception as e: 
        print(f"ওটিপি পাঠাতে সমস্যা: {e}")
        bot.send_message(call.message.chat.id, "সমস্যা হয়েছে।")

@bot.message_handler(commands=['notice'])
def send_notice(message):
    if message.chat.id == ADMIN_ID:
        notice_text = message.text.replace("/notice", "").strip()
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                for user in f.read().splitlines():
                    try: 
                        bot.send_message(int(user), f"📢 **নোটিশ:**\n\n{notice_text}")
                    except: 
                        pass
            bot.reply_to(message, "✅ সফলভাবে নোটিশ পাঠানো হয়েছে।")
        else:
            bot.reply_to(message, "❌ কোনো ইউজার ডাটাবেজ পাওয়া যায়নি।")

# 🚀 মেইন রান এক্সিকিউশন
if __name__ == "__main__":
    keep_alive()  # ব্যাকগ্রাউন্ডে Flask সার্ভার চালু করবে
    print("🚀 বট লাইভ হয়েছে...")
    bot.infinity_polling()
