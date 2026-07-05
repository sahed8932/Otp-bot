import telebot
import requests
import os
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
from threading import Thread

# ১. আপনার আসল বটের টোকেনটি এখানে বসান (অবশ্যই "" এর ভেতরে)
BOT_TOKEN = "8979736100:AAF3FPGSq26C9UdHkPR2oRzE2eBLlmi8CWo"

ADMIN_ID = 8262679678  # আপনার নিজের টেলিগ্রাম ইউজার আইডি
CHANNEL_ID = "-1003956226642" 
GROUP_ID = "-1004309875319"

bot = telebot.TeleBot(BOT_TOKEN)
NEW_API_URL = "https://tools.gtechwb.com/api/otp/v1"
USERS_FILE = "users.txt"

# ইউজারদের সর্বশেষ সিলেক্ট করা অ্যাপ বা অ্যাকশন ট্র্যাক করার ডিকশনারি
user_states = {}

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

# মেইন হোম কিবোর্ড মেনু (স্ক্রিনশটের মতো স্থায়ী বাটন)
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

# টেক্সট বাটন হ্যান্ডলার (Reply Keyboard-এর জন্য)
@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    if not is_subscribed(message.chat.id):
        send_join_request(message.chat.id)
        return

    if message.text == "📞 Get Number":
        send_services_menu(message.chat.id)
    elif message.text == "📊 Active Traffic":
        bot.send_message(message.chat.id, "📊 **Active Traffic:**\n\nবর্তমানে ওটিপি সার্ভারে ট্রাফিক হাই আছে। দ্রুত নম্বর নিয়ে ওটিপি সাবমিট করুন।")
    elif message.text == "🌍 Available Countries":
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            response = requests.get(f"{NEW_API_URL}/countries").json()
            if response.get('status') == 'success' and response.get('countries'):
                countries_list = ", ".join([c['name'] for c in response['countries']])
                bot.send_message(message.chat.id, f"🌍 **বর্তমানে সচল দেশসমূহ:**\n\n{countries_list}")
            else:
                bot.send_message(message.chat.id, "❌ এই মুহূর্তে কোনো দেশ সচল পাওয়া যায়নি।")
        except:
            bot.send_message(message.chat.id, "❌ সার্ভারে সমস্যা হচ্ছে।")
    elif message.text == "🔐 2FA GENERATE":
        bot.send_message(message.chat.id, "🔐 **2FA Generator:**\n\nআপনার অ্যাকাউন্টের সুরক্ষার জন্য টু-ফ্যাক্টর অথেন্টিকেশন কোড জেনারেট করার ফিচারটি খুব শীঘ্রই যুক্ত হচ্ছে।")

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

# নির্দিষ্ট অ্যাপের জন্য দেশ দেখানোর কন্ডিশন
@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def get_countries_for_app(call):
    selected_app = call.data.split("_")[1]
    try:
        response = requests.get(f"{NEW_API_URL}/countries").json()
        if response.get('status') == 'success' and response.get('countries'):
            markup = InlineKeyboardMarkup()
            for country in response['countries']:
                markup.add(InlineKeyboardButton(f"🇲🇳 {country['name']}", callback_data=f"c_{country['code']}_{selected_app}"))
            markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_main"))
            
            text = f"📱 Service: **{selected_app.capitalize()}**\n🌍 **Select Country:**"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    except:
        bot.answer_callback_query(call.id, text="সার্ভার ত্রুটি।")

# স্ক্রিনশটের মতো হুবহু ওটিপি রিকোয়েস্ট ইন্টারফেস জেনারেটর
@bot.callback_query_handler(func=lambda call: call.data.startswith("c_") or call.data.startswith("change_"))
def show_number_interface(call):
    data_parts = call.data.split("_")
    country_code = data_parts[1]
    selected_app = data_parts[2]
    
    url = f"{NEW_API_URL}/numbers/{country_code}"
    try:
        response = requests.get(url).json()
        if response.get('status') == 'success' and response.get('numbers'):
            # এপিআই থেকে দুটি নম্বর নিয়ে সাজানো
            numbers = response['numbers'][:2]
            num_text = ""
            for num in numbers:
                num_text += f"📞Number: `+{num.replace('+', '')}`\n"
            
            # প্রধান ওটিপি উইন্ডো মেসেজ ফরম্যাট (স্ক্রিনশটের মতো হুবহু)
            msg_text = f"🌍Country ➤ {country_code.upper()}\n\n" \
                       f"{num_text}\n" \
                       f"⏳Status: Waiting For OTP\n" \
                       f"⏰Number Validity ➤ 10 minutes\n" \
                       f"🔷 বটের ভিতরে ১০ সেকেন্ড ওয়েট করুন ওটিপি পেয়ে যাবেন না পেলে গ্রুপ চেক করুন।😊"
            
            markup = InlineKeyboardMarkup()
            # নম্বর পরিবর্তন করার ডাইনামিক বাটন
            markup.row(InlineKeyboardButton("🔄 Change Number (10s)", callback_data=f"change_{country_code}_{selected_app}"))
            markup.row(InlineKeyboardButton("🔗 View OTP Group", url="https://t.me/+DXdDIm7-rRU4YTQ1"))
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text, reply_markup=markup, parse_mode="Markdown")
            
            # ব্যাকগ্রাউন্ডে ওটিপি চেক করার জন্য প্রথম নম্বরটি ব্যবহার করা হবে
            target_phone = numbers[0].replace('+', '')
            # ৫ সেকেন্ড পর অটো ওটিপি চেক রান করা (যাতে ইউজার রিফ্রেশ না চাপলেও ওটিপি পায়)
            Thread(target=auto_fetch_otp, args=(call.message.chat.id, target_phone, selected_app)).start()
            
        else:
            bot.answer_callback_query(call.id, text="❌ এই মুহূর্তে নম্বর খালি নেই। অন্য দেশ ট্রাই করুন।", show_alert=True)
    except:
        bot.answer_callback_query(call.id, text="নম্বর লোড করতে সমস্যা হয়েছে।")

# ব্যাকগ্রাউন্ড অটো ওটিপি রিফ্রেশ সিস্টেম
def auto_fetch_otp(chat_id, phone, selected_app):
    time.sleep(8) # ইউজারকে বাটনে ওয়েট করতে বলা সময় অনুযায়ী
    url = f"{NEW_API_URL}/get_sms/{phone}"
    try:
        response = requests.get(url).json()
        if response.get('status') == 'success' and response.get('sms'):
            sms = response['sms'][0]
            msg_text = f"🔥 **নতুন ওটিপি অ্যালার্ট!** 🔥\n\n" \
                       f"📱 অ্যাপ: #{selected_app.capitalize()}\n" \
                       f"📞 নম্বর: `+{phone}`\n" \
                       f"✉️ ওটিপি মেসেজ: {sms.get('text')}"
            
            bot.send_message(chat_id, msg_text, parse_mode="Markdown")
            bot.send_message(int(CHANNEL_ID), msg_text, parse_mode="Markdown")
            bot.send_message(int(GROUP_ID), msg_text, parse_mode="Markdown")
    except:
        pass

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
    print("🚀 প্রফেশনাল আর্নিং ইন্টারফেস ওটিপি বট লাইভ হয়েছে...")
    try: bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e: print(f"বট রানিংয়ে সমস্যা: {e}")
