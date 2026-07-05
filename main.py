import telebot
import requests
import os
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# ১. আপনার আসল বটের টোকেন এবং Quackr API Key এখানে বসান
BOT_TOKEN = "8979736100:AAF3FPGSq26C9UdHkPR2oRzE2eBLlmi8CWo"
QUACKR_API_KEY = "TfVCAzYa47VQmvxBosMOLUHqlq72"

ADMIN_ID = 8262679678  # আপনার নিজের টেলিগ্রাম ইউজার আইডি
CHANNEL_ID = "-1003956226642" 
GROUP_ID = "-1004309875319"

bot = telebot.TeleBot(BOT_TOKEN)
QUACKR_BASE_URL = "https://api.quackr.io/v1"
USERS_FILE = "users.txt"

# 🖥️ Render-কে ২৪ ঘণ্টা লাইভ রাখার জন্য Flask ওয়েব সার্ভার সেটআপ
app = Flask('')

@app.route('/')
def home():
    return "বট সচল আছে!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

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
    except:
        return True

# জয়েনিং মেনু
def send_join_request(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📢 Join OTP Channel", url="https://t.me/SHS_Otp_Channel"))
    markup.row(InlineKeyboardButton("💬 Join OTP Group", url="https://t.me/+DXdDIm7-rRU4YTQ1"))
    markup.row(InlineKeyboardButton("✅ Joined", callback_data="check_membership"))
    bot.send_message(chat_id, "⚠️ সার্ভিসটি ব্যবহার করতে প্রথমে আমাদের ওটিপি চ্যানেল এবং গ্রুপে জয়েন করুন। তারপর '✅ Joined' বাটনে ক্লিক করুন।", reply_markup=markup)

# মেইন হোম কিবোর্ড মেনু (স্থায়ী বাটন)
def send_home_keyboard(chat_id, text="👋 ওটিপি ড্যাশবোর্ডে স্বাগতম! নিচের বাটন ব্যবহার করুন:"):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📞 Get Number"), KeyboardButton("📊 Active Traffic"))
    markup.row(KeyboardButton("🌍 Available Countries"), KeyboardButton("🔐 2FA GENERATE"))
    bot.send_message(chat_id, text, reply_markup=markup)

# অ্যাপস/সার্ভিস সিলেকশন মেনু
def send_services_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("💬 WhatsApp", callback_data="app_whatsapp"), InlineKeyboardButton("📘 Facebook", callback_data="app_facebook"))
    markup.row(InlineKeyboardButton("📸 Instagram", callback_data="app_instagram"), InlineKeyboardButton("✈️ Telegram", callback_data="app_telegram"))
    markup.row(InlineKeyboardButton("🎵 TikTok", callback_data="app_tiktok"), InlineKeyboardButton("⚙️ Other Apps", callback_data="app_any"))
    
    text = "📱 **ওটিপি সার্ভিস মেনু:**\n\nআপনি কোন অ্যাপের নম্বর নিতে চান? নিচে থেকে সেই অ্যাপটি সিলেক্ট করুন:"
    if message_id:
        try: bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        except: bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start_bot(message):
    save_user(message.chat.id)
    if is_subscribed(message.chat.id): 
        send_home_keyboard(message.chat.id)
    else: 
        send_join_request(message.chat.id)

# টেক্সট বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    if not is_subscribed(message.chat.id):
        send_join_request(message.chat.id)
        return

    if message.text == "📞 Get Number":
        send_services_menu(message.chat.id)
    elif message.text == "📊 Active Traffic":
        bot.send_message(message.chat.id, "📊 **Active Traffic:**\n\nবর্তমানে Quackr ওটিপি সার্ভারে ট্রাফিক স্ট্যাবল আছে।")
    elif message.text == "🌍 Available Countries":
        # Quackr এপিআই থেকে সরাসরি লাইভ দেশের নাম আনা
        headers = {"Authorization": f"Bearer {QUACKR_API_KEY}"}
        try:
            res = requests.get(f"{QUACKR_BASE_URL}/countries", headers=headers, timeout=5).json()
            countries_list = ", ".join([c['name'] for c in res.get('data', [])])
            bot.send_message(message.chat.id, f"🌍 **বর্তমানে সচল দেশসমূহ:**\n\n{countries_list if countries_list else 'USA, UK, Canada'}")
        except:
            bot.send_message(message.chat.id, "🌍 **বর্তমানে সচল দেশসমূহ:**\n\nUSA, UK, Canada, France, Germany")
    elif message.text == "🔐 2FA GENERATE":
        bot.send_message(message.chat.id, "🔐 **2FA Generator:**\n\nএই ফিচারটি খুব শীঘ্রই যুক্ত হচ্ছে।")

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_membership(call):
    if is_subscribed(call.from_user.id):
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_home_keyboard(call.message.chat.id, "✅ ভেরিফিকেশন সফল হয়েছে!")
    else:
        bot.answer_callback_query(call.id, text="❌ আপনি এখনো জয়েন করেননি!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_to_main(call):
    send_services_menu(call.message.chat.id, call.message.message_id)

# Quackr এপিআই এর দেশ লোড করা
@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def get_countries_for_app(call):
    selected_app = call.data.split("_")[1]
    headers = {"Authorization": f"Bearer {QUACKR_API_KEY}"}
    markup = InlineKeyboardMarkup()
    
    try:
        res = requests.get(f"{QUACKR_BASE_URL}/countries", headers=headers, timeout=5).json()
        if res.get('data'):
            for country in res['data'][:6]: # সেরা ৬টি দেশ বাটন করবে
                markup.add(InlineKeyboardButton(f"🌍 {country['name']}", callback_data=f"c_{country['code']}_{selected_app}"))
        else:
            raise Exception()
    except:
        # এপিআই রেসপন্স ব্যাকআপ
        markup.row(InlineKeyboardButton("🇺🇸 United States", callback_data=f"c_US_{selected_app}"), InlineKeyboardButton("🇬🇧 United Kingdom", callback_data=f"c_GB_{selected_app}"))
        markup.row(InlineKeyboardButton("🇨🇦 Canada", callback_data=f"c_CA_{selected_app}"), InlineKeyboardButton("🇫🇷 France", callback_data=f"c_FR_{selected_app}"))

    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_main"))
    text = f"📱 Service: **{selected_app.capitalize()}**\n🌍 **Select Country:**"
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

# Quackr এপিআই থেকে নম্বর নিয়ে স্ক্রিনশটের মতো উইন্ডো সাজানো
@bot.callback_query_handler(func=lambda call: call.data.startswith("c_") or call.data.startswith("change_"))
def show_number_interface(call):
    data_parts = call.data.split("_")
    country_code = data_parts[1]
    selected_app = data_parts[2]
    
    headers = {"Authorization": f"Bearer {QUACKR_API_KEY}"}
    url = f"{QUACKR_BASE_URL}/numbers?country={country_code}"
    
    try:
        res = requests.get(url, headers=headers, timeout=5).json()
        if res.get('data'):
            numbers = res['data'][:2] # ২টি নম্বর তুলে আনা হলো
            num_text = ""
            for num in numbers:
                num_text += f"📞Number: `{num['number']}`\n"
            
            msg_text = f"🌍Country ➤ {country_code.upper()}\n\n" \
                       f"{num_text}\n" \
                       f"⏳Status: Waiting For OTP\n" \
                       f"⏰Number Validity ➤ 10 minutes\n" \
                       f"🔷 বটের ভিতরে ১০ সেকেন্ড ওয়েট করুন ওটিপি পেয়ে যাবেন না পেলে গ্রুপ চেক করুন।😊"
            
            markup = InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton("🔄 Change Number (10s)", callback_data=f"change_{country_code}_{selected_app}"))
            markup.row(InlineKeyboardButton("🔗 View OTP Group", url="https://t.me/+DXdDIm7-rRU4YTQ1"))
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text, reply_markup=markup, parse_mode="Markdown")
            
            # প্রথম নম্বরের ওটিপি ট্র্যাকিং ব্যাকগ্রাউন্ডে চালু করা
            target_phone = numbers[0]['number'].replace('+', '')
            Thread(target=auto_fetch_quackr_otp, args=(call.message.chat.id, target_phone, selected_app)).start()
        else:
            bot.answer_callback_query(call.id, text="❌ এই দেশের নম্বর সাময়িকভাবে অফলাইন।", show_alert=True)
    except:
        bot.answer_callback_query(call.id, text="নম্বর সার্ভার রেসপন্স করছে না।")

# Quackr থেকে ওটিপি মেসেজ রিড করার ব্যাকগ্রাউন্ড টাস্ক
def auto_fetch_quackr_otp(chat_id, phone, selected_app):
    time.sleep(10) # বটের স্ক্রিনশটের রুলস অনুযায়ী ১০ সেকেন্ড পর ওটিপি চেক করবে
    headers = {"Authorization": f"Bearer {QUACKR_API_KEY}"}
    url = f"{QUACKR_BASE_URL}/messages?number={phone}"
    try:
        res = requests.get(url, headers=headers, timeout=5).json()
        if res.get('data'):
            sms = res['data'][0] # একদম লেটেস্ট ওটিপি মেসেজটি নিবে
            msg_text = f"🔥 **নতুন ওটিপি অ্যালার্ট!** 🔥\n\n" \
                       f"📱 অ্যাপ: #{selected_app.capitalize()}\n" \
                       f"📞 নম্বর: `+{phone}`\n" \
                       f"✉️ ওটিপি মেসেজ: {sms.get('message')}"
            
            bot.send_message(chat_id, msg_text, parse_mode="Markdown")
            bot.send_message(int(CHANNEL_ID), msg_text, parse_mode="Markdown")
            bot.send_message(int(GROUP_ID), msg_text, parse_mode="Markdown")
    except:
        pass

if __name__ == "__main__":
    keep_alive()
    print("🚀 Quackr API চালিত ওটিপি বট সফলভাবে লাইভ হয়েছে...")
    try: bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e: print(f"বট রানিংয়ে সমস্যা: {e}")
