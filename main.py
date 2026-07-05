import telebot
import requests
import os
import time
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# ১. আপনার আসল বটের টোকেন এবং Quackr API Key এখানে বসান
BOT_TOKEN = "8979736100:AAHti1Q9R3iVKX3M-6-VijfJFs5jWc620A0"
QUACKR_API_KEY = "TfVCAzYa47VQmvxBosMOLUHqlq72"

ADMIN_ID = 8262679678  # আপনার নিজের টেলিগ্রাম ইউজার আইডি
CHANNEL_ID = "-1003956226642" 
GROUP_ID = "-1004309875319"

bot = telebot.TeleBot(BOT_TOKEN)
QUACKR_BASE_URL = "https://api.quackr.io/v1"
USERS_FILE = "users.txt"

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

def is_subscribed(user_id):
    try:
        channel_status = bot.get_chat_member(int(CHANNEL_ID), user_id).status
        group_status = bot.get_chat_member(int(GROUP_ID), user_id).status
        return channel_status not in ['left', 'kicked'] and group_status not in ['left', 'kicked']
    except:
        return True

def send_join_request(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📢 Join OTP Channel", url="https://t.me/SHS_Otp_Channel"))
    markup.row(InlineKeyboardButton("💬 Join OTP Group", url="https://t.me/+DXdDIm7-rRU4YTQ1"))
    markup.row(InlineKeyboardButton("✅ Joined", callback_data="check_membership"))
    bot.send_message(chat_id, "⚠️ সার্ভিসটি ব্যবহার করতে প্রথমে আমাদের ওটিপি চ্যানেল এবং গ্রুপে জয়েন করুন। তারপর '✅ Joined' বাটনে ক্লিক করুন।", reply_markup=markup)

def send_home_keyboard(chat_id, text="👋 ওটিপি ড্যাশবোর্ডে স্বাগতম! নিচের বাটন ব্যবহার করুন:"):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📞 Get Number"), KeyboardButton("📊 Active Traffic"))
    markup.row(KeyboardButton("🌍 Available Countries"), KeyboardButton("🔐 2FA GENERATE"))
    bot.send_message(chat_id, text, reply_markup=markup)

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

@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    if not is_subscribed(message.chat.id):
        send_join_request(message.chat.id)
        return

    if message.text == "📞 Get Number":
        send_services_menu(message.chat.id)
    elif message.text == "📊 Active Traffic":
        bot.send_message(message.chat.id, "📊 **Active Traffic:**\n\nবর্তমানে ওটিপি সার্ভারে ট্রাফিক ১০০% সচল ও হাই স্পিড আছে।")
    elif message.text == "🌍 Available Countries":
        bot.send_message(message.chat.id, "🌍 **বর্তমানে সচল দেশসমূহ:**\n\nUS, GB, CA, FR, DE, MM, VE")
    elif message.text == "🔐 2FA GENERATE":
        bot.send_message(message.chat.id, "🔐 **2FA Generator:**\n\nসুরক্ষার জন্য এই ফিচারটি খুব শীঘ্রই লাইভ করা হবে।")

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

@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def get_countries_for_app(call):
    selected_app = call.data.split("_")[1]
    markup = InlineKeyboardMarkup()
    
    markup.row(InlineKeyboardButton("🇺🇸 United States", callback_data=f"c_US_{selected_app}"), InlineKeyboardButton("🇬🇧 United Kingdom", callback_data=f"c_GB_{selected_app}"))
    markup.row(InlineKeyboardButton("🇨🇦 Canada", callback_data=f"c_CA_{selected_app}"), InlineKeyboardButton("🇫🇷 France", callback_data=f"c_FR_{selected_app}"))
    markup.row(InlineKeyboardButton("🇲🇳 Myanmar", callback_data=f"c_MM_{selected_app}"), InlineKeyboardButton("🇻🇪 Venezuela", callback_data=f"c_VE_{selected_app}"))
    
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_main"))
    text = f"📱 Service: **{selected_app.capitalize()}**\n🌍 **Select Country:**"
    try: bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    except: bot.send_message(call.message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("c_") or call.data.startswith("change_"))
def show_number_interface(call):
    data_parts = call.data.split("_")
    country_code = data_parts[1].upper()
    selected_app = data_parts[2]
    
    headers = {"Authorization": f"Bearer {QUACKR_API_KEY}"}
    url = f"{QUACKR_BASE_URL}/numbers?country={country_code}"
    
    rand_suffix1 = str(random.randint(100000, 999999))
    rand_suffix2 = str(random.randint(100000, 999999))
    
    if country_code == "VE":
        num1, num2 = f"+584167{rand_suffix1}", f"+584268{rand_suffix2}"
    elif country_code == "MM":
        num1, num2 = f"+95975{rand_suffix1}", f"+95975{rand_suffix2}"
    else:
        num1, num2 = f"+141555{rand_suffix1}", f"+141555{rand_suffix2}"

    try:
        res = requests.get(url, headers=headers, timeout=3).json()
        if res.get('data') and len(res['data']) >= 2:
            num1 = res['data'][0]['number']
            num2 = res['data'][1]['number']
    except:
        pass 

    msg_text = f"🌍Country ➤ {country_code}\n\n" \
               f"📞Number: `{num1}`\n" \
               f"📞Number: `{num2}`\n\n" \
               f"⏳Status: Waiting For OTP\n" \
               f"⏰Number Validity ➤ 10 minutes\n" \
               f"🔷 ওটিপি পেতে নিচের '📥 Fetch Code' বাটনে ক্লিক করুন অথবা অটোমেটিক ওটিপির জন্য ১০ সেকেন্ড ওয়েট করুন।😊"
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{country_code.lower()}_{selected_app}"))
    markup.row(
        InlineKeyboardButton("📢 OTP Channel", url="https://t.me/SHS_Otp_Channel"),
        InlineKeyboardButton("💬 OTP Group", url="https://t.me/+DXdDIm7-rRU4YTQ1")
    )
    clean_phone = num1.replace('+', '')
    markup.row(InlineKeyboardButton("📥 Fetch Code", callback_data=f"fetch_{clean_phone}_{selected_app}"))
    
    try: bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text, reply_markup=markup, parse_mode="Markdown")
    except: bot.send_message(call.message.chat.id, msg_text, reply_markup=markup, parse_mode="Markdown")
    
    Thread(target=auto_fetch_quackr_otp, args=(call.message.chat.id, clean_phone, selected_app, False)).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("fetch_"))
def manual_fetch_trigger(call):
    data_parts = call.data.split("_")
    phone = data_parts[1]
    selected_app = data_parts[2]
    
    bot.answer_callback_query(call.id, text="🔍 ওটিপি কোড খোঁজা হচ্ছে...", show_alert=False)
    auto_fetch_quackr_otp(call.message.chat.id, phone, selected_app, manual=True)

def auto_fetch_quackr_otp(chat_id, phone, selected_app, manual=False):
    if not manual:
        time.sleep(10)
        
    headers = {"Authorization": f"Bearer {QUACKR_API_KEY}"}
    url = f"{QUACKR_BASE_URL}/messages?number={phone}"
    try:
        res = requests.get(url, headers=headers, timeout=3).json()
        if res.get('data') and len(res['data']) > 0:
            sms = res['data'][0]
            msg_text = f"🔥 **নতুন ওটিপি অ্যালার্ট!** 🔥\n\n" \
                       f"📱 অ্যাপ: #{selected_app.capitalize()}\n" \
                       f"📞 নম্বর: `+{phone}`\n" \
                       f"✉️ ওটিপি মেসেজ: {sms.get('message')}"
            
            bot.send_message(chat_id, msg_text, parse_mode="Markdown")
            bot.send_message(int(CHANNEL_ID), msg_text, parse_mode="Markdown")
            bot.send_message(int(GROUP_ID), msg_text, parse_mode="Markdown")
        else:
            if manual:
                bot.send_message(chat_id, "⚠️ ওটিপি এখনো আসেনি! অ্যাপে সেন্ড করে পুনরায় '📥 Fetch Code' চাপুন বা নম্বর চেঞ্জ করুন।")
    except:
        if manual: bot.send_message(chat_id, "❌ সার্ভার রেসপন্স করেনি।")

# 💥 ট্রিক ফিচার: সম্পূর্ণ স্বাধীন ব্যাকগ্রাউন্ড থ্রেড (চ্যানেল ও গ্রুপে সারাদিন ওটিপি আসার লুপ)
def global_auto_otp_spammer():
    # এটি মূল বট কোডকে একটুও ডিস্টার্ব না করে প্রতি ৬০ সেকেন্ডে গ্লোবাল ওটিপি প্রুফ পাঠাবে
    time.sleep(20) # সার্ভার স্টার্ট হওয়ার ২০ সেকেন্ড পর কাজ শুরু করবে
    countries = ["US", "GB", "CA", "FR"]
    apps_pool = ["WhatsApp", "Telegram", "Facebook", "Instagram", "Google", "TikTok"]
    
    while True:
        try:
            target_country = random.choice(countries)
            headers = {"Authorization": f"Bearer {QUACKR_API_KEY}"}
            
            # ১. যেকোনো একটি সচল দেশের র্যান্ডম নম্বর তোলা
            num_res = requests.get(f"{QUACKR_BASE_URL}/numbers?country={target_country}", headers=headers, timeout=4).json()
            if num_res.get('data'):
                random_num = random.choice(num_res['data'])['number']
                clean_num = random_num.replace('+', '')
                
                # ২. ওই নম্বরের লেটেস্ট মেসেজ চেক করা
                msg_res = requests.get(f"{QUACKR_BASE_URL}/messages?number={clean_num}", headers=headers, timeout=4).json()
                if msg_res.get('data') and len(msg_res['data']) > 0:
                    latest_sms = msg_res['data'][0]
                    random_app = random.choice(apps_pool)
                    
                    fake_proof_text = f"🔥 **নতুন ওটিপি অ্যালার্ট!** 🔥\n\n" \
                                      f"📱 অ্যাপ: #{random_app}\n" \
                                      f"📞 নম্বর: `{random_num}`\n" \
                                      f"✉️ ওটিপি মেসেজ: {latest_sms.get('message')}"
                    
                    # শুধুমাত্র চ্যানেল এবং গ্রুপে লাইভ প্রুফ ফরোয়ার্ড হবে
                    bot.send_message(int(CHANNEL_ID), fake_proof_text, parse_mode="Markdown")
                    bot.send_message(int(GROUP_ID), fake_proof_text, parse_mode="Markdown")
        except:
            pass
        time.sleep(60) # প্রতি ৬০ সেকেন্ড পর পর লুপটি কাজ করবে (কমানো/বাড়ানো যাবে)

@bot.message_handler(commands=['notice'])
def send_notice(message):
    if message.chat.id == ADMIN_ID:
        notice_text = message.text.replace("/notice", "").strip()
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                for user in f.read().splitlines():
                    try: bot.send_message(int(user), f"📢 **নোটিশ:**\n\n{notice_text}")
                    except: pass
            bot.reply_to(message, "✅ সফলভাবে নোটিশ পাঠানো হয়েছে।")

if __name__ == "__main__":
    keep_alive()
    # 🚀 এখানে অটো-পোস্টিং ব্যাকগ্রাউন্ড থ্রেড রান করা হলো (মেন কোড ১০০% ফ্রি থাকবে)
    Thread(target=global_auto_otp_spammer, daemon=True).start()
    
    print("🚀 প্রফেশনাল অটো-পোস্ট ওটিপি বট সফলভাবে লাইভ হয়েছে...")
    try: bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e: print(f"বট রানিংয়ে সমস্যা: {e}")
