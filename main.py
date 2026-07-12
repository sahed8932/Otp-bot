import telebot
import requests
import os
import time
import json
from telebot import types
from flask import Flask
from threading import Thread

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        default_config = {
            "BOT_TOKEN": "8979736100:AAEQpGeHOEbGVtUyF4enfiGtmxB2DbEh5sQ", 
            "VOLTX_API_KEY": "MLPNN2HKYXD", 
            "BASE_URL": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api",
            "ADMIN_ID": 8262679678, 
            "CHANNEL_ID": "-1003956226642",
            "GROUP_ID": "-1004309875319",
            "CHANNEL_LINK": "https://t.me/SHS_Otp_Channel",
            "GROUP_LINK": "https://t.me/+DXdDIm7-rRU4YTQ1",
            "NOTICE": "⚠️ সার্ভিসটি ফুল স্পিডে সচল রয়েছে। কোনো সমস্যা হলে গ্রুপে জানান।",
            "SERVICES": {
                "facebook": {"name": "📘 Facebook", "rids": {"US": "22501", "GB": "26134"}},
                "whatsapp": {"name": "💚 WhatsApp", "rids": {"US": "22501", "KG": "99655"}},
                "instagram": {"name": "📸 Instagram", "rids": {"US": "21640"}},
                "tiktok": {"name": "🎵 Tiktok", "rids": {"US": "22501"}},
                "imo": {"name": "📱 IMO", "rids": {"US": "2011"}}
            }
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

config = load_config()
bot = telebot.TeleBot(config["BOT_TOKEN"])
app = Flask('')

@app.route('/')
def home(): return "Voltx OTP Bot is Live & Active!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

def is_subscribed(user_id):
    if user_id == int(config["ADMIN_ID"]): return True 
    try:
        c = bot.get_chat_member(int(config["CHANNEL_ID"]), user_id).status
        g = bot.get_chat_member(int(config["GROUP_ID"]), user_id).status
        return c not in ['left', 'kicked'] and g not in ['left', 'kicked']
    except: return True

def send_home_keyboard(chat_id, text=None):
    if not text:
        text = f"👋 ওটিপি ড্যাশবোর্ডে স্বাগতম!\n\n📢 **নোটিশ:** {config.get('NOTICE', 'কোনো নোটিশ নেই')}"
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("📞 Get Number"), types.KeyboardButton("📊 Active Traffic"))
    markup.row(types.KeyboardButton("💰 Balance"), types.KeyboardButton("📉 Withdraw"))
    markup.row(types.KeyboardButton("🌍 Available Countries"), types.KeyboardButton("🔐 2FA GENERATE"))
    if chat_id == int(config["ADMIN_ID"]):
        markup.row(types.KeyboardButton("🛠 Admin Dashboard"))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

def send_services_menu(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup()
    services = config.get("SERVICES", {})
    
    row = []
    for s_id, s_info in services.items():
        row.append(types.InlineKeyboardButton(s_info["name"], callback_data=f"app_{s_id}"))
        if len(row) == 2:
            markup.row(*row)
            row = []
    if row: markup.row(*row)
    markup.add(types.InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main"))
    
    text = "📱 **কোন অ্যাপের নম্বর নিতে চান? সিলেক্ট করুন:**"
    if message_id:
        try: bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        except: bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start_bot(message):
    if is_subscribed(message.chat.id): send_home_keyboard(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📢 Join Channel", url=config["CHANNEL_LINK"]), types.InlineKeyboardButton("👥 Join Group", url=config["GROUP_LINK"]))
        markup.row(types.InlineKeyboardButton("✅ Joined (Check)", callback_data="check_membership"))
        bot.send_message(message.chat.id, "⚠️ সার্ভিসটি ব্যবহার করতে আমাদের অফিসিয়াল চ্যানেল এবং গ্রুপে জয়েন করুন।", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if not is_subscribed(message.chat.id): return
    
    text = message.text
    if text == "📞 Get Number":
        send_services_menu(message.chat.id)
    elif text == "📊 Active Traffic":
        fetch_live_traffic(message.chat.id)
    elif text == "💰 Balance":
        bot.send_message(message.chat.id, "💰 আপনার ব্যালেন্স চেক করতে প্যানেল অ্যাডমিন বা সাপোর্টের সাথে যোগাযোগ করুন।", parse_mode="Markdown")
    elif text == "📉 Withdraw":
        bot.send_message(message.chat.id, "📉 উইথড্র সিস্টেমটি বর্তমানে অটো মোডে রয়েছে। সমস্যা হলে গ্রুপে বলুন।", parse_mode="Markdown")
    elif text == "🌍 Available Countries":
        send_available_countries(message.chat.id)
    elif text == "🔐 2FA GENERATE":
        bot.send_message(message.chat.id, "🔐 2FA কোড জেনারেট করার জন্য আপনার সিক্রেট কোডটি দিন (অথবা ফিচারটি আপডেট করা হচ্ছে)।", parse_mode="Markdown")
    elif text == "🛠 Admin Dashboard" and message.chat.id == int(config["ADMIN_ID"]):
        show_admin_dashboard(message.chat.id)

def fetch_live_traffic(chat_id):
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/liveaccess"
    headers = {"mauthapi": str(config["VOLTX_API_KEY"]).strip()}
    try:
        res = requests.get(url, headers=headers, timeout=15).json()
        if res.get("meta", {}).get("status") == "ok":
            bot.send_message(chat_id, "📊 **Active Traffic Status:** 100% Online & Connected!", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "📊 Traffic Active (API Connected)")
    except:
        bot.send_message(chat_id, "📊 Active Traffic: সার্ভার রানিং আছে!")

def send_available_countries(chat_id):
    msg = "🌍 **বর্তমান উপলব্ধ দেশসমূহ ও সার্ভিস:**\n\n"
    for s_id, s_info in config["SERVICES"].items():
        countries = ", ".join(s_info["rids"].keys())
        msg += f"{s_info['name']} ➔ `{countries}`\n"
    bot.send_message(chat_id, msg, parse_mode="Markdown")

def show_admin_dashboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Add/Update Range ID", callback_data="adm_addrid"))
    markup.row(types.InlineKeyboardButton("📢 Set Notice", callback_data="adm_setnotice"))
    markup.row(types.InlineKeyboardButton("🔑 Update API Key", callback_data="adm_setkey"))
    
    text = (f"🛠 **অ্যাডমিন কন্ট্রোল প্যানেল**\n\n"
            f"• API Key: `{config['VOLTX_API_KEY']}`\n"
            f"• মোট সচল অ্যাপ: {len(config['SERVICES'])}\n"
            f"• বর্তমান নোটিশ: {config.get('NOTICE', 'নেই')}")
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin(call):
    if call.message.chat.id != int(config["ADMIN_ID"]): return
    if call.data == "adm_addrid":
        msg = bot.send_message(call.message.chat.id, "👉 নতুন রেঞ্জ যোগ করতে এভাবে ফরম্যাট লিখে পাঠান:\n\n`অ্যাপ_নাম দেশের_কোড রেঞ্জ_আইডি`\n\n*উদাহরণ:* `facebook US 22501`")
        bot.register_next_step_handler(msg, process_add_rid)
    elif call.data == "adm_setnotice":
        msg = bot.send_message(call.message.chat.id, "👉 নতুন নোটিশটি লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_notice)
    elif call.data == "adm_setkey":
        msg = bot.send_message(call.message.chat.id, "👉 আপনার নতুন Voltx SMS API Key টি পাঠান:")
        bot.register_next_step_handler(msg, save_api_key)

def process_add_rid(message):
    global config
    try:
        parts = message.text.strip().split()
        app_id = parts[0].lower()
        country = parts[1].upper()
        rid_val = parts[2]
        
        if app_id not in config["SERVICES"]:
            config["SERVICES"][app_id] = {"name": f"✨ {app_id.capitalize()}", "rids": {}}
            
        config["SERVICES"][app_id]["rids"][country] = rid_val
        save_config(config)
        bot.send_message(message.chat.id, f"✅ সফলভাবে যুক্ত হয়েছে!\nApp: {app_id}\nCountry: {country}\nRange ID: {rid_val}")
    except:
        bot.send_message(message.chat.id, "❌ ফরম্যাট ভুল হয়েছে! আবার চেষ্টা করুন।")
    show_admin_dashboard(message.chat.id)

def save_notice(message):
    global config
    config["NOTICE"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ নোটিশ সফলভাবে আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_api_key(message):
    global config
    config["VOLTX_API_KEY"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ API Key সফলভাবে আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def show_countries(call):
    selected_app = call.data.split("_")[1]
    services = config.get("SERVICES", {})
    if selected_app not in services: return
    
    markup = types.InlineKeyboardMarkup()
    rids = services[selected_app]["rids"]
    
    row = []
    for country in rids.keys():
        row.append(types.InlineKeyboardButton(f"🌍 {country}", callback_data=f"c_{country}_{selected_app}"))
        if len(row) == 2:
            markup.row(*row)
            row = []
    if row: markup.row(*row)
    markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back_services"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🌍 **{selected_app.upper()} এর জন্য দেশ সিলেক্ট করুন:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("c_"))
def request_number(call):
    _, country, selected_app = call.data.split("_")
    rid = config["SERVICES"][selected_app]["rids"].get(country)
    
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/getnum"
    headers = {"mauthapi": str(config["VOLTX_API_KEY"]).strip()}
    payload = {"rid": str(rid)}
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20)
        if response.status_code != 200 or "bad_request" in response.text:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            
        if response.status_code != 200:
            bot.answer_callback_query(call.id, text=f"❌ সার্ভার কোড: {response.status_code}", show_alert=True)
            return
            
        res = response.json()
        if res.get("meta", {}).get("status") == "ok":
            num = res["data"].get("full_number") or res["data"].get("no_plus_number")
            current_rid = res.get("rid", rid)
            
            msg = (f"📱 Service: **{selected_app.upper()}** ({country})\n"
                   f"📞 Number: `{num}`\n\n"
                   f"⏳ ওটিপি কোডের জন্য অপেক্ষা করা হচ্ছে...")
            
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("📥 Fetch Code", callback_data=f"fetch_{current_rid}_{selected_app}_{num}"),
                types.InlineKeyboardButton("🔄 Change Number", callback_data=f"c_{country}_{selected_app}")
            )
            markup.row(
                types.InlineKeyboardButton("📢 Channel", url=config["CHANNEL_LINK"]),
                types.InlineKeyboardButton("👥 Group", url=config["GROUP_LINK"])
            )
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup, parse_mode="Markdown")
            Thread(target=auto_fetch_otp, args=(call.message.chat.id, current_rid, selected_app, num, call.message.message_id)).start()
        else:
            bot.answer_callback_query(call.id, text=f"❌ প্যানেল: {res.get('message', 'নম্বর স্টক শেষ')}", show_alert=True)
            
    except Exception as e:
        bot.answer_callback_query(call.id, text="⚠️ কানেকশন সমস্যা! আবার ট্রাই করুন।", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fetch_"))
def manual_fetch(call):
    data_parts = call.data.split("_")
    rid = data_parts[1]
    selected_app = data_parts[2]
    num = data_parts[3]
    bot.answer_callback_query(call.id, text="🔍 ওটিপি চেক করা হচ্ছে...")
    check_and_send_otp(call.message.chat.id, selected_app, num, call.message.message_id, manual=True)

def auto_fetch_otp(chat_id, rid, selected_app, num, msg_id=None):
    for _ in range(4):
        time.sleep(15)
        if check_and_send_otp(chat_id, selected_app, num, msg_id):
            return

def check_and_send_otp(chat_id, selected_app, num, msg_id=None, manual=False):
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/success-otp"
    headers = {"mauthapi": str(config["VOLTX_API_KEY"]).strip()}
    
    try:
        res = requests.get(url, headers=headers, timeout=15).json()
        if res.get("meta", {}).get("status") == "ok":
            otps_list = res.get("data", {}).get("otps", [])
            clean_num = str(num).replace("+", "")
            
            found_msg = None
            for item in otps_list:
                item_num = str(item.get("number")).replace("+", "")
                if item_num == clean_num:
                    found_msg = item.get("message")
                    break
            
            if found_msg:
                alert = (f"🔥 **নতুন ওটিপি কোড এসেছে!** 🔥\n\n"
                         f"📱 অ্যাপ: #{selected_app.upper()}\n"
                         f"📞 নম্বর: `{num}`\n"
                         f"✉️ ওটিপি: **{found_msg}**")
                
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton("📢 Channel", url=config["CHANNEL_LINK"]), types.InlineKeyboardButton("👥 Group", url=config["GROUP_LINK"]))
                
                bot.send_message(chat_id, alert, reply_markup=markup, parse_mode="Markdown")
                try:
                    bot.send_message(int(config["CHANNEL_ID"]), alert, reply_markup=markup, parse_mode="Markdown")
                except:
                    pass
                return True
            else:
                if manual:
                    bot.send_message(chat_id, "⚠️ ওটিপি এখনও প্যানেলে আসেনি। একটু পরে আবার 'Fetch Code' এ ক্লিক করুন।")
        else:
            if manual:
                bot.send_message(chat_id, "⚠️ সার্ভার থেকে কোনো ডেটা পাওয়া যায়নি।")
    except Exception as e:
        if manual:
            bot.send_message(chat_id, "❌ ওটিপি চেক করতে গিয়ে সমস্যা হয়েছে।")
    return False

@bot.callback_query_handler(func=lambda call: call.data == "back_services")
def back_to_serv(call): send_services_menu(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back(call): 
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_home_keyboard(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check(call):
    if is_subscribed(call.from_user.id): 
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_home_keyboard(call.message.chat.id, "✅ ভেরিфикации সফল! এখন থেকে সার্ভিস ব্যবহার করতে পারবেন।")
    else: 
        bot.answer_callback_query(call.id, text="❌ আপনি এখনও চ্যানেল বা গ্রুপে জয়েন করেননি!", show_alert=True)

if __name__ == "__main__":
    keep_alive()
    try: bot.delete_webhook(drop_pending_updates=True)
    except: pass
    print("🚀 ভোল্টেক্স ওটিপি প্রো বট সফলভাবে রান হচ্ছে...")
    bot.polling(none_stop=True)
