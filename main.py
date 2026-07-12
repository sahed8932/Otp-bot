import telebot
import requests
import os
import time
import json
from telebot import types
from flask import Flask
from threading import Thread

# --- কনফিগারেশন ফাইল সেটিংস ---
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        default_config = {
            "BOT_TOKEN": "8979736100:AAHti1Q9R3iVKX3M-6-VijfJFs5jWc620A0", 
            "VOLTX_API_KEY": "MGYB4NMYU51", 
            "ADMIN_ID": 8262679678, 
            "CHANNEL_ID": "-1003956226642",
            "GROUP_ID": "-1004309875319",
            "CHANNEL_LINK": "https://t.me/SHS_Otp_Channel",
            "GROUP_LINK": "https://t.me/+DXdDIm7-rRU4YTQ1"
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

config = load_config()
bot = telebot.TeleBot(config["BOT_TOKEN"])
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
    if user_id == config["ADMIN_ID"]:
        return True 
    try:
        channel_status = bot.get_chat_member(int(config["CHANNEL_ID"]), user_id).status
        group_status = bot.get_chat_member(int(config["GROUP_ID"]), user_id).status
        return channel_status not in ['left', 'kicked'] and group_status not in ['left', 'kicked']
    except:
        return True

def send_join_request(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("📢 Join OTP Channel", url=config["CHANNEL_LINK"]))
    markup.row(types.InlineKeyboardButton("💬 Join OTP Group", url=config["GROUP_LINK"]))
    markup.row(types.InlineKeyboardButton("✅ Joined", callback_data="check_membership"))
    bot.send_message(chat_id, "⚠️ সার্ভিসটি ব্যবহার করতে প্রথমে আমাদের ওটিপি চ্যানেল এবং গ্রুপে জয়েন করুন। তারপর '✅ Joined' বাটনে ক্লিক করুন।", reply_markup=markup)

def send_home_keyboard(chat_id, text="👋 ওটিপি ড্যাশবোর্ডে স্বাগতম! নিচের বাটন ব্যবহার করুন:"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("📞 Get Number"), types.KeyboardButton("📊 Active Traffic"))
    markup.row(types.KeyboardButton("🌍 Available Countries"), types.KeyboardButton("🔐 2FA GENERATE"))
    
    if chat_id == config["ADMIN_ID"]:
        markup.row(types.KeyboardButton("🛠 Admin Dashboard"))
        
    bot.send_message(chat_id, text, reply_markup=markup)

def send_services_menu(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("💬 WhatsApp", callback_data="app_whatsapp"), types.InlineKeyboardButton("📘 Facebook", callback_data="app_facebook"))
    markup.row(types.InlineKeyboardButton("📸 Instagram", callback_data="app_instagram"), types.InlineKeyboardButton("✈️ Telegram", callback_data="app_telegram"))
    markup.row(types.InlineKeyboardButton("🎵 TikTok", callback_data="app_tiktok"), types.InlineKeyboardButton("⚙️ Other Apps", callback_data="app_any"))
    
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

def show_admin_dashboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🔑 Change Voltx API Key", callback_data="adm_setvoltx"))
    markup.row(types.InlineKeyboardButton("📢 Change Channel ID", callback_data="adm_setchannel"))
    markup.row(types.InlineKeyboardButton("💬 Change Group ID", callback_data="adm_setgroup"))
    markup.row(types.InlineKeyboardButton("🔗 Change Channel Link", callback_data="adm_setchlink"))
    markup.row(types.InlineKeyboardButton("🔗 Change Group Link", callback_data="adm_setglink"))
    markup.row(types.InlineKeyboardButton("✉️ Broadcast Notice (সবাইকে নোটিশ)", callback_data="adm_notice"))
    
    current_settings = f"🛠 **এডমিন কন্ট্রোল ড্যাশবোর্ড**\n\n" \
                       f"• Voltx API Key: `{config['VOLTX_API_KEY']}`\n" \
                       f"• চ্যানেল আইডি: `{config['CHANNEL_ID']}`\n" \
                       f"• গ্রুপ আইডি: `{config['GROUP_ID']}`\n" \
                       f"• চ্যানেল লিংক: {config['CHANNEL_LINK']}\n" \
                       f"• গ্রুপ লিংক: {config['GROUP_LINK']}\n\n" \
                       f"নিচের বাটনে ক্লিক করে যেকোনো সেটিংস সরাসরি পরিবর্তন করতে পারেন।"
    bot.send_message(chat_id, current_settings, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_clicks(call):
    if call.message.chat.id != config["ADMIN_ID"]: return
    action = call.data
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    
    if action == "adm_setvoltx":
        msg = bot.send_message(call.message.chat.id, "👉 আপনার নতুন **VoltxSMS API Key** টি টাইপ করে পাঠান:")
        bot.register_next_step_handler(msg, save_admin_setting, "VOLTX_API_KEY")
    elif action == "adm_setchannel":
        msg = bot.send_message(call.message.chat.id, "👉 নতুন **চ্যানেল আইডি** টাইপ করে পাঠান:")
        bot.register_next_step_handler(msg, save_admin_setting, "CHANNEL_ID")
    elif action == "adm_setgroup":
        msg = bot.send_message(call.message.chat.id, "👉 নতুন **গ্রুপ আইডি** টাইপ করে পাঠান:")
        bot.register_next_step_handler(msg, save_admin_setting, "GROUP_ID")
    elif action == "adm_setchlink":
        msg = bot.send_message(call.message.chat.id, "👉 নতুন **চ্যানেল লিংক** টাইপ করে পাঠান:")
        bot.register_next_step_handler(msg, save_admin_setting, "CHANNEL_LINK")
    elif action == "adm_setglink":
        msg = bot.send_message(call.message.chat.id, "👉 নতুন **গ্রুপ লিংক** টাইপ করে পাঠান:")
        bot.register_next_step_handler(msg, save_admin_setting, "GROUP_LINK")
    elif action == "adm_notice":
        msg = bot.send_message(call.message.chat.id, "✉️ সব ইউজারের কাছে পাঠানোর জন্য আপনার **নোটিশটি** টাইপ করে পাঠান:")
        bot.register_next_step_handler(msg, process_broadcast_notice)

def save_admin_setting(message, key_name):
    global config
    if message.chat.id != config["ADMIN_ID"]: return
    new_value = message.text.strip()
    config[key_name] = new_value
    save_config(config)
    bot.send_message(message.chat.id, f"✅ সফলভাবে `{key_name}` আপডেট করা হয়েছে।")
    show_admin_dashboard(message.chat.id)

def process_broadcast_notice(message):
    if message.chat.id != config["ADMIN_ID"]: return
    notice_text = message.text.strip()
    bot.send_message(message.chat.id, "⏳ নোটিশ পাঠানো শুরু হয়েছে...")
    count = 0
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            for user in f.read().splitlines():
                try: 
                    bot.send_message(int(user), f"📢 **নোটিশ:**\n\n{notice_text}")
                    count += 1
                except: pass
    bot.send_message(message.chat.id, f"✅ মোট {count} জন ইউজারের কাছে নোটিশ পাঠানো সফল হয়েছে।")
    show_admin_dashboard(message.chat.id)

# --- টেক্সট বাটন হ্যান্ডলার ---
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
    elif message.text == "🛠 Admin Dashboard" and message.chat.id == config["ADMIN_ID"]:
        show_admin_dashboard(message.chat.id)

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
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🇺🇸 United States", callback_data=f"c_US_{selected_app}"), types.InlineKeyboardButton("🇬🇧 United Kingdom", callback_data=f"c_GB_{selected_app}"))
    markup.row(types.InlineKeyboardButton("🇨🇦 Canada", callback_data=f"c_CA_{selected_app}"), types.InlineKeyboardButton("🇫🇷 France", callback_data=f"c_FR_{selected_app}"))
    markup.row(types.InlineKeyboardButton("🇲🇳 Myanmar", callback_data=f"c_MM_{selected_app}"), types.InlineKeyboardButton("🇻🇪 Venezuela", callback_data=f"c_VE_{selected_app}"))
    markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back_main"))
    
    text = f"📱 Service: **{selected_app.capitalize()}**\n🌍 **Select Country:**"
    try: bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    except: bot.send_message(call.message.chat.id, text, reply_markup=markup)

# --- 🛠 উন্নত ডায়াগনস্টিকসহ VoltxSMS নম্বর রিকোয়েস্ট ইন্টারফেস ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("c_") or call.data.startswith("change_"))
def show_number_interface(call):
    data_parts = call.data.split("_")
    country_code = data_parts[1].upper()
    selected_app = data_parts[2]
    
    voltx_url = "https://voltxsms.com/api/v1/get-number" 
    payload = {
        "api_key": config["VOLTX_API_KEY"],
        "country": country_code.lower(),
        "service": selected_app.lower()
    }

    try:
        # Render টার্মিনালে ডিবাগিং ডেটা প্রিন্ট হবে
        print(f"📡 Requesting VoltxSMS API... Payload: {payload}")
        response = requests.get(voltx_url, params=payload, timeout=10)
        print(f"📥 Response Code: {response.status_code} | Raw Text: {response.text}")
        
        raw_res = response.text.strip()

        if response.status_code != 200:
            bot.answer_callback_query(call.id, text=f"❌ সার্ভার এরর! (HTTP Code: {response.status_code})", show_alert=True)
            return

        # ১. রেসপন্সটি যদি JSON ফরম্যাটে হয় (যেমন আধুনিক API কাঠামোর ক্ষেত্রে)
        try:
            res_json = response.json()
            if isinstance(res_json, dict) and (res_json.get('status') == 'success' or 'number' in res_json):
                num1 = res_json.get('number')
                order_id = res_json.get('order_id', 'NO_ID')
                process_successful_number(call, country_code, selected_app, num1, order_id)
                return
            else:
                err_text = res_json.get('message', raw_res) if isinstance(res_json, dict) else raw_res
                bot.answer_callback_query(call.id, text=f"❌ Voltx রেসপন্স: {err_text}", show_alert=True)
                return
        except ValueError:
            # ২. রেসপন্সটি যদি প্লেইন টেক্সট ফরম্যাটে হয় (যেমন: ACCESS_NUMBER:ORDER_ID:NUMBER)
            if ":" in raw_res:
                parts = raw_res.split(":")
                if len(parts) >= 3:
                    order_id = parts[1]
                    num1 = parts[2]
                    process_successful_number(call, country_code, selected_app, num1, order_id)
                    return
            
            # ৩. অন্যান্য সম্ভাব্য টেক্সট এরর মেসেজ হ্যান্ডলিং (যেমন: BAD_KEY, NO_BALANCE)
            bot.answer_callback_query(call.id, text=f"⚠️ সার্ভার মেসেজ: {raw_res[:60]}", show_alert=True)

    except Exception as e:
        print(f"❌ VoltxSMS API Exception: {e}")
        bot.answer_callback_query(call.id, text=f"⚠️ কানেকশন ফেল্ড: {str(e)[:50]}", show_alert=True)

def process_successful_number(call, country_code, selected_app, num1, order_id):
    msg_text = f"🌍 Country ➤ {country_code}\n\n" \
               f"📞 Number: `{num1}`\n\n" \
               f"⏳ Status: Waiting For OTP\n" \
               f"🔷 ওটিপি পেতে নিচের '📥 Fetch Code' বাটনে ক্লিক করুন অথবা ১০ সেকেন্ড অপেক্ষা করুন।"
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{country_code.lower()}_{selected_app}"))
    markup.row(
        types.InlineKeyboardButton("📢 OTP Channel", url=config["CHANNEL_LINK"]),
        types.InlineKeyboardButton("💬 OTP Group", url=config["GROUP_LINK"])
    )
    markup.row(types.InlineKeyboardButton("📥 Fetch Code", callback_data=f"fetch_{order_id}_{selected_app}_{num1}"))
    
    try: bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg_text, reply_markup=markup, parse_mode="Markdown")
    except: bot.send_message(call.message.chat.id, msg_text, reply_markup=markup, parse_mode="Markdown")
    
    Thread(target=auto_fetch_voltx_otp, args=(call.message.chat.id, order_id, selected_app, num1, False)).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("fetch_"))
def manual_fetch_trigger(call):
    data_parts = call.data.split("_")
    order_id = data_parts[1]
    selected_app = data_parts[2]
    phone = data_parts[3]
    bot.answer_callback_query(call.id, text="🔍 ওটিপি কোড খোঁজা হচ্ছে...", show_alert=False)
    auto_fetch_voltx_otp(call.message.chat.id, order_id, selected_app, phone, manual=True)

def auto_fetch_voltx_otp(chat_id, order_id, selected_app, phone, manual=False):
    if not manual: time.sleep(10)
    voltx_otp_url = "https://voltxsms.com/api/v1/get-otp"
    payload = {"api_key": config["VOLTX_API_KEY"], "order_id": order_id}
    
    try:
        res = requests.get(voltx_otp_url, params=payload, timeout=6).json()
        if res.get('status') == 'completed' or res.get('sms'):
            sms_msg = res.get('sms', 'No message body.')
            msg_text = f"🔥 **নতুন ওটিপি অ্যালার্ট!** 🔥\n\n" \
                       f"📱 অ্যাপ: #{selected_app.capitalize()}\n" \
                       f"📞 নম্বর: `{phone}`\n" \
                       f"✉️ ওটিপি মেসেজ: {sms_msg}"
            bot.send_message(chat_id, msg_text, parse_mode="Markdown")
            bot.send_message(int(config["CHANNEL_ID"]), msg_text, parse_mode="Markdown")
            bot.send_message(int(config["GROUP_ID"]), msg_text, parse_mode="Markdown")
        else:
            if manual: bot.send_message(chat_id, "⚠️ ওটিপি এখনো আসেনি! অ্যাপ থেকে রিসেন্ড করে পুনরায় চেষ্টা করুন।")
    except:
        if manual: bot.send_message(chat_id, "❌ ওটিপি সার্ভার রেসপন্স করেনি।")

if __name__ == "__main__":
    keep_alive()
    try: bot.delete_webhook(drop_pending_updates=True); time.sleep(1)
    except: pass
    print("🚀 বাটন-ভিত্তিক ড্যাশবোর্ডসহ ওটিপি বট সম্পূর্ণ রেডি...")
    try: bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e: print(f"বট রানিংয়ে সমস্যা: {e}")
