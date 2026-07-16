import telebot
import requests
import os
import time
import json
import re
import collections
from datetime import datetime
from telebot import types
from flask import Flask
from threading import Thread

CONFIG_FILE = "config.json"
USERS_FILE = "users.json"

# In-memory tracking for high speed detection
range_hits_tracker = collections.defaultdict(list)
last_announced_range = {}
seen_console_hits = set()

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_users(users_set):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users_set), f)

def get_country_info_by_range(range_val):
    """রেঞ্জ আইডি দেখে পতাকা ও দেশের নাম শনাক্ত করার ডায়নামিক ট্র্যাকার"""
    if not range_val:
        return "Global 🌐"
    
    clean_range = str(range_val).strip().upper()
    prefix_range = clean_range.replace("XXX", "")
    
    # ১. প্রথমে বটের কনফিগার করা সার্ভিস থেকে চেক করবে
    services = config.get("SERVICES", {})
    for s_id, s_info in services.items():
        rids = s_info.get("rids", {})
        for country, rid_val in rids.items():
            clean_rid = str(rid_val).strip().upper()
            prefix_rid = clean_rid.replace("XXX", "")
            
            if prefix_range == prefix_rid or clean_range == clean_rid or clean_range.startswith(prefix_rid) or prefix_rid.startswith(prefix_range):
                return country
    
    # ২. মিল না পাওয়া গেলে প্রিফিক্স অনুযায়ী কমন কান্ট্রি ম্যাপ করবে
    if prefix_range.startswith("224"):
        return "Guinea 🇬🇳"
    elif prefix_range.startswith("236") or prefix_range.startswith("231"):
        return "Liberia 🇱🇷"
    elif prefix_range.startswith("225"):
        return "Ivory Coast 🇨🇮"
    elif prefix_range.startswith("261"):
        return "Madagascar 🇲🇬"
    elif prefix_range.startswith("996"):
        return "Kyrgyzstan 🇰🇬"
    elif prefix_range.startswith("44"):
        return "United Kingdom 🇬🇧"
    elif prefix_range.startswith("1"):
        return "United States 🇺🇸"
    
    return "Global 🌐"

def load_config():
    # User's exact requested SERVICES structure
    default_config = {
        "BOT_TOKEN": "8979736100:AAG_8ILyTgjuWxpSG1v2kgdRWv4nCPeycws", 
        "FASTX_API_KEY": "MCZJ7C79228",  # Voltxsms API Key
        "BASE_URL": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api", # Voltxsms base path
        "ADMIN_ID": 8262679678,
        "BOT_NAME": "ᏕᎻᏕ ᏕᎷᏕ ᎻᏬᏰ", 
        "BOT_USERNAME": "SHS_SMSHUB_bot", 
        "DEV_USERNAME": "Saku_143",
        "BALANCE_TEXT": "💰 আপনার ব্যালেন্স চেক করতে প্যানেল অ্যাডমিন বা সাপোর্টের সাথে যোগাযোগ করুন।",
        "WITHDRAW_TEXT": "📉 উইথড্র সিস্টেমটি বর্তমানে অটো মোডে রয়েছে। সমস্যা হলে গ্রুপে বলুন।",
        "CHANNELS_TO_JOIN": [
            {"id": "-1003956226642", "link": "https://t.me/SHS_Otp_Channel", "name": "📢 Otp Channel"},
            {"id": "-1002183552076", "link": "https://t.me/winfanti", "name": "💬 Support Channel"}
        ],
        "GROUPS_TO_JOIN": [
            {"id": "-1004309875319", "link": "https://t.me/+DXdDIm7-rRU4YTQ1", "name": "👥 OTP Support Group"}
        ],
        "OTP_DESTINATIONS": [
            "-1003956226642",
            "-1004309875319"
        ],
        "NOTICE": "⚠️ সার্ভিসটি ফুল স্পিডে সচল রয়েছে। কোনো সমস্যা হলে গ্রুপে জানান।",
        "SERVICES": {
            "facebook": {
                "name": "📘 Facebook",
                "rids": {
                    "Guinea 🇬🇳": "22467XXX",
                    "Liberia 🇱🇷": "236744XXX",
                    "Liberia (Lonestar) 🇱🇷": "23674719129XXX"
                }
            },
            "whatsapp": {
                "name": "💚 WhatsApp",
                "rids": {}
            },
            "instagram": {
                "name": "📸 Instagram",
                "rids": {
                    "Guinea 🇬🇳": "22467XXX"
                }
            },
            "tiktok": {
                "name": "🎵 TikTok",
                "rids": {
                    "Liberia (Lonestar) 🇱🇷": "23674719129XXX"
                }
            },
            "imo": {
                "name": "📱 IMO",
                "rids": {
                    "Guinea 🇬🇳": "22465XXX"
                }
            }
        }
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                # Ensure the BASE_URL is set to Voltxsms
                if "2eee7.com" in loaded.get("BASE_URL", ""):
                    loaded["BASE_URL"] = default_config["BASE_URL"]
                return loaded
        except:
            return default_config
    else:
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

config = load_config()
bot = telebot.TeleBot(config["BOT_TOKEN"])
app = Flask('')
admin_temp_data = {}
all_users = load_users()

@app.route('/')
def home(): return "Voltxsms OTP Bot is Live & Active!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

def track_user(user_id):
    global all_users
    if user_id not in all_users:
        all_users.add(user_id)
        save_users(all_users)

def is_subscribed_all(user_id):
    if user_id == int(config["ADMIN_ID"]): return True 
    for ch in config.get("CHANNELS_TO_JOIN", []):
        try:
            status = bot.get_chat_member(int(ch["id"]), user_id).status
            if status in ['left', 'kicked', 'restricted']: return False
        except: pass 
    for grp in config.get("GROUPS_TO_JOIN", []):
        try:
            status = bot.get_chat_member(int(grp["id"]), user_id).status
            if status in ['left', 'kicked', 'restricted']: return False
        except: pass
    return True

def get_api_headers():
    return {
        "mauthapi": str(config.get("FASTX_API_KEY", "")).strip(),
        "Content-Type": "application/json"
    }

def format_rid(rid):
    # Strips trailing "XXX" (case-insensitive) for Voltxsms compatibility
    rid_str = str(rid).strip()
    if rid_str.upper().endswith("XXX"):
        return rid_str[:-3]
    return rid_str

def get_otp_group_link():
    for grp in config.get("GROUPS_TO_JOIN", []):
        if "OTP" in grp.get("name", "") or "Group" in grp.get("name", "") or "+" in grp.get("link", ""):
            return grp["link"]
    if config.get("GROUPS_TO_JOIN"):
        return config["GROUPS_TO_JOIN"][0]["link"]
    return "https://t.me/+DXdDIm7-rRU4YTQ1"

def send_home_keyboard(chat_id, text=None):
    track_user(chat_id)
    if not text:
        text = f"👋 ওটিপি ড্যাশবোর্ডে স্বাগতম!\n\n📢 **নোটিশ:** {config.get('NOTICE', 'কোনো নোটিশ নেই')}"
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("📞 Get Number"), types.KeyboardButton("📊 Active Traffic"))
    markup.row(types.KeyboardButton("💰 Balance"), types.KeyboardButton("📉 Withdraw"))
    markup.row(types.KeyboardButton("🌍 Available Countries"), types.KeyboardButton("🔐 2FA GENERATE"))
    markup.row(types.KeyboardButton("🤖 Create Your own bot"))
    if chat_id == int(config["ADMIN_ID"]):
        markup.row(types.KeyboardButton("🛠 Admin Dashboard"))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

def send_services_menu(chat_id, message_id=None):
    track_user(chat_id)
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
    track_user(message.chat.id)
    if is_subscribed_all(message.chat.id):
        send_home_keyboard(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup()
        for ch in config.get("CHANNELS_TO_JOIN", []):
            markup.row(types.InlineKeyboardButton(ch["name"], url=ch["link"]))
        for grp in config.get("GROUPS_TO_JOIN", []):
            markup.row(types.InlineKeyboardButton(grp["name"], url=grp["link"]))
        markup.row(types.InlineKeyboardButton("✅ Joined (Check)", callback_data="check_membership"))
        bot.send_message(message.chat.id, "⚠️ সার্ভিসটি ব্যবহার করতে নিচের সমস্ত চ্যানেল এবং গ্রুপগুলোতে অবশ্যই জয়েন করুন, এরপর 'Joined' বাটনে ক্লিক করুন।", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    track_user(message.chat.id)
    if not is_subscribed_all(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        for ch in config.get("CHANNELS_TO_JOIN", []):
            markup.row(types.InlineKeyboardButton(ch["name"], url=ch["link"]))
        for grp in config.get("GROUPS_TO_JOIN", []):
            markup.row(types.InlineKeyboardButton(grp["name"], url=grp["link"]))
        markup.row(types.InlineKeyboardButton("✅ Joined (Check)", callback_data="check_membership"))
        bot.send_message(message.chat.id, "❌ আপনি এখনো সমস্ত চ্যানেল বা গ্রুপে জয়েন করেননি!\n\nদয়া করে উপরের সমস্ত চ্যানেল ও গ্রুপগুলোতে জয়েন করুন, এরপর নিচের **Joined** বাটনে ক্লিক করুন।", reply_markup=markup)
        return
    
    text = message.text
    if text == "📞 Get Number":
        send_services_menu(message.chat.id)
    elif text == "📊 Active Traffic":
        fetch_live_traffic(message.chat.id)
    elif text == "💰 Balance":
        bal_text = config.get("BALANCE_TEXT", "💰 আপনার ব্যালেন্স চেক করতে প্যানেল অ্যাডমিন বা সাপোর্টের সাথে যোগাযোগ করুন।")
        bot.send_message(message.chat.id, bal_text, parse_mode="Markdown")
    elif text == "📉 Withdraw":
        wd_text = config.get("WITHDRAW_TEXT", "📉 উইথড্র সিস্টেমটি বর্তমানে অটো মোডে রয়েছে। সমস্যা হলে গ্রুপে বলুন।")
        bot.send_message(message.chat.id, wd_text, parse_mode="Markdown")
    elif text == "🌍 Available Countries":
        send_available_countries(message.chat.id)
    elif text == "🔐 2FA GENERATE":
        bot.send_message(message.chat.id, "🔐 2FA কোড জেনারেট করার জন্য আপনার সিক্রেট কোডটি দিন।", parse_mode="Markdown")
    elif text == "🤖 Create Your own bot":
        dev_user = config.get("DEV_USERNAME", "Saku_143")
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("👨‍💻 Contact Developer", url=f"https://t.me/{dev_user}"))
        bot.send_message(message.chat.id, f"🤖 আপনার নিজস্ব ওটিপি বট বানাতে চাইলে সরাসরি আমার সাথে যোগাযোগ করুন: @{dev_user}", reply_markup=markup, parse_mode="Markdown")
    elif text == "🛠 Admin Dashboard" and message.chat.id == int(config["ADMIN_ID"]):
        show_admin_dashboard(message.chat.id)

def fetch_live_traffic(chat_id):
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/liveaccess"
    try:
        res = requests.get(url, headers=get_api_headers(), timeout=15).json()
        if res.get("meta", {}).get("status") == "ok" or "services" in res.get("data", {}):
            bot.send_message(chat_id, "📊 **Active Traffic Status:** 100% Online & Connected!", parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "📊 Traffic Active (API Connected)")
    except:
        bot.send_message(chat_id, "📊 Active Traffic: সার্ভার রানিং আছে!")

def send_available_countries(chat_id):
    msg = "🌍 **বর্তমান উপলব্ধ দেশসমূহ ও রেঞ্জ আইডি:**\n\n"
    for s_id, s_info in config["SERVICES"].items():
        rids_str = ", ".join([f"{c}: `{r}`" for c, r in s_info["rids"].items()])
        msg += f"{s_info['name']} ➔ {rids_str}\n"
    bot.send_message(chat_id, msg, parse_mode="Markdown")

def show_admin_dashboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Add Range ID", callback_data="adm_addrid"),
               types.InlineKeyboardButton("🗑 Delete Range ID", callback_data="adm_delrid"))
    markup.row(types.InlineKeyboardButton("📢 Manage Channels/Groups", callback_data="adm_channels"))
    markup.row(types.InlineKeyboardButton("📢 Broadcast Message", callback_data="adm_broadcast"))
    markup.row(types.InlineKeyboardButton("✍️ Set Notice", callback_data="adm_setnotice"),
               types.InlineKeyboardButton("🤖 Set Bot Name", callback_data="adm_setname"))
    markup.row(types.InlineKeyboardButton("💰 Edit Balance Text", callback_data="adm_setbal"),
               types.InlineKeyboardButton("📉 Edit Withdraw Text", callback_data="adm_setwd"))
    markup.row(types.InlineKeyboardButton("🔗 Set Bot Username", callback_data="adm_setbotuser"),
               types.InlineKeyboardButton("👨‍💻 Set Dev Username", callback_data="adm_setdevuser"))
    markup.row(types.InlineKeyboardButton("🔑 Update API Key", callback_data="adm_setkey"))
    
    bot_title = config.get("BOT_NAME", "ᏕᎻᏕ ᏕᎷᏕ ᎻᏬᏰ")
    bot_user = config.get("BOT_USERNAME", "SHS_SMSHUB_bot")
    dev_user = config.get("DEV_USERNAME", "Saku_143")
    
    text = (f"🛠 **അഡ്മിന്‍ കണ്ട്രോള്‍ പാനല്‍ (Voltxsms)**\n\n"
            f"• Bot Name: `{bot_title}`\n"
            f"• Bot Username: `@{bot_user}`\n"
            f"• Dev Username: `@{dev_user}`\n"
            f"• Total Users: `{len(all_users)}`\n"
            f"• API Key: `{config.get('FASTX_API_KEY', '')}`\n"
            f"• মোট সচল অ্যাপ: {len(config['SERVICES'])}\n"
            f"• বর্তমান নোটিশ: {config.get('NOTICE', 'নেই')}")
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_callbacks(call):
    if call.message.chat.id != int(config["ADMIN_ID"]): return
    data = call.data
    chat_id = call.message.chat.id
    
    if data == "adm_addrid":
        markup = types.InlineKeyboardMarkup()
        for s_id, s_info in config["SERVICES"].items():
            markup.add(types.InlineKeyboardButton(s_info["name"], callback_data=f"addapp_{s_id}"))
        markup.add(types.InlineKeyboardButton("✨ নতুন অ্যাপ (Custom App) যোগ করুন", callback_data="addapp_custom"))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="📌 **রেঞ্জ আইডি যুক্তকরণ:**\nপ্রথমে কোন অ্যাপের জন্য রেঞ্জ যোগ করবেন তা সিলেক্ট করুন:", reply_markup=markup, parse_mode="Markdown")
        
    elif data == "adm_delrid":
        markup = types.InlineKeyboardMarkup()
        for s_id, s_info in config["SERVICES"].items():
            markup.add(types.InlineKeyboardButton(f"❌ ডিলিট রেঞ্জ: {s_info['name']}", callback_data=f"delapp_{s_id}"))
        markup.add(types.InlineKeyboardButton("⬅️ ব্যাক", callback_data="adm_back"))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="🗑 **রেঞ্জ আইডি মুছে ফেলা:**\nকোন অ্যাপের রেঞ্জ ডিলিট করতে চান সিলেক্ট করুন:", reply_markup=markup, parse_mode="Markdown")

    elif data == "adm_channels":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ নতুন চ্যানেল/গ্রুপ অ্যাড করুন", callback_data="ch_add"))
        markup.add(types.InlineKeyboardButton("🗑 চ্যানেল/গ্রুপ রিমুভ করুন", callback_data="ch_remove"))
        markup.add(types.InlineKeyboardButton("⬅️ ব্যাক", callback_data="adm_back"))
        
        c_list = "\n".join([f"📢 {c['name']} (`{c['id']}`)" for c in config["CHANNELS_TO_JOIN"]])
        g_list = "\n".join([f"👥 {g['name']} (`{g['id']}`)" for g in config["GROUPS_TO_JOIN"]])
        text = f"📢 **চ্যানেল ও গ্রুপ ম্যানেজমেন্ট**\n\n**বর্তমান চ্যানেলসমূহ:**\n{c_list}\n\n**বর্তমান গ্রুপসমূহ:**\n{g_list}"
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

    elif data == "adm_broadcast":
        msg = bot.send_message(chat_id, "📢 আপনি সকল ইউজারদের কাছে যে মেসেজটি পাঠাতে চান তা লিখে বা ফরোয়ার্ড করে পাঠান:")
        bot.register_next_step_handler(msg, process_broadcast)
    elif data == "adm_setnotice":
        msg = bot.send_message(chat_id, "👉 ইউজারদের জন্য নতুন নোটিশটি লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_notice)
    elif data == "adm_setname":
        msg = bot.send_message(chat_id, "👉 নতুন বটের নাম লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_bot_name)
    elif data == "adm_setbal":
        msg = bot.send_message(chat_id, "👉 নতুন Balance মেসেজটি লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_balance_text)
    elif data == "adm_setwd":
        msg = bot.send_message(chat_id, "👉 নতুন Withdraw মেসেজটি লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_withdraw_text)
    elif data == "adm_setbotuser":
        msg = bot.send_message(chat_id, "👉 বটের ইউজারনেম লিখুন (@ ছাড়া):")
        bot.register_next_step_handler(msg, save_bot_username)
    elif data == "adm_setdevuser":
        msg = bot.send_message(chat_id, "👉 ডেভেলপার ইউজারনেম লিখুন (@ ছাড়া):")
        bot.register_next_step_handler(msg, save_dev_username)
    elif data == "adm_setkey":
        msg = bot.send_message(chat_id, "👉 আপনার নতুন Voltxsms API Key টি পাঠান:")
        bot.register_next_step_handler(msg, save_api_key)
    elif data == "adm_back":
        show_admin_dashboard(chat_id)

def process_broadcast(message):
    chat_id = message.chat.id
    success = 0
    failed = 0
    status_msg = bot.send_message(chat_id, "🚀 ব্রডকাস্ট শুরু হয়েছে, দয়া করে অপেক্ষা করুন...")
    
    for uid in list(all_users):
        try:
            bot.copy_message(chat_id=int(uid), from_chat_id=chat_id, message_id=message.message_id)
            success += 1
            time.sleep(0.1)
        except:
            failed += 1
            
    bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, 
                          text=f"✅ ব্রডকাস্ট সম্পন্ন!\n\n• সফলভাবে পাঠানো হয়েছে: `{success}` জনের কাছে\n• ফেইল হয়েছে: `{failed}` জনের কাছে", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("addapp_"))
def wizard_add_app(call):
    chat_id = call.message.chat.id
    app_target = call.data.split("_")[1]
    if app_target == "custom":
        msg = bot.send_message(chat_id, "✍️ নতুন অ্যাপের নাম লিখুন (যেমন: `telegram` বা `netflix`):")
        bot.register_next_step_handler(msg, wizard_get_custom_app_name)
    else:
        admin_temp_data[chat_id] = {"app": app_target}
        msg = bot.send_message(chat_id, f"🌍 আপনি **{app_target.upper()}** সিলেক্ট করেছেন।\n\nএখন দেশের কোড এবং রেঞ্জ আইডি (শেষে XXX সহ) এভাবে লিখে পাঠান:\n*উদাহরণ:* `US 22501XXX`")
        bot.register_next_step_handler(msg, wizard_save_rid)

def wizard_get_custom_app_name(message):
    chat_id = message.chat.id
    app_name = message.text.strip().lower()
    admin_temp_data[chat_id] = {"app": app_name}
    if app_name not in config["SERVICES"]:
        config["SERVICES"][app_name] = {"name": f"✨ {app_name.capitalize()}", "rids": {}}
        save_config(config)
    msg = bot.send_message(chat_id, f"✅ নতুন অ্যাপ **{app_name}** যুক্ত হয়েছে।\n\nএখন দেশের কোড এবং রেঞ্জ আইডি (শেষে XXX সহ) এভাবে লিখে পাঠান:\n*উদাহরণ:* `US 22501XXX`")
    bot.register_next_step_handler(msg, wizard_save_rid)

def wizard_save_rid(message):
    chat_id = message.chat.id
    try:
        parts = message.text.strip().split()
        country = parts[0].upper()
        rid_val = parts[1]
        app_id = admin_temp_data.get(chat_id, {}).get("app")
        if not app_id:
            bot.send_message(chat_id, "❌ সেশন মেয়াদোত্তীর্ণ। আবার চেষ্টা করুন।")
            return
        if app_id not in config["SERVICES"]:
            config["SERVICES"][app_id] = {"name": f"✨ {app_id.capitalize()}", "rids": {}}
        config["SERVICES"][app_id]["rids"][country] = rid_val
        save_config(config)
        bot.send_message(chat_id, f"🎉 সফলভাবে সেভ হয়েছে!\nApp: {app_id.upper()}\nCountry: {country}\nRange ID: {rid_val}")
    except:
        bot.send_message(chat_id, "❌ ফরম্যাট ভুল হয়েছে! সঠিক ফরম্যাটে (যেমন: `US 22501XXX`) আবার চেষ্টা করুন।")
    show_admin_dashboard(chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delapp_"))
def wizard_del_app(call):
    chat_id = call.message.chat.id
    app_id = call.data.split("_")[1]
    if app_id not in config["SERVICES"]:
        bot.answer_callback_query(call.id, text="❌ অ্যাপ পাওয়া যায়নি!", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    rids = config["SERVICES"][app_id]["rids"]
    for country in rids.keys():
        markup.add(types.InlineKeyboardButton(f"❌ ডিলিট দেশ: {country} (RID: {rids[country]})", callback_data=f"delsel_{app_id}_{country}"))
    markup.add(types.InlineKeyboardButton("⬅️ ব্যাক", callback_data="adm_addrid"))
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"🗑 **{app_id.upper()}** এর কোন দেশের রেঞ্জটি ডিলিট করতে চান?", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delsel_"))
def wizard_execute_delete(call):
    chat_id = call.message.chat.id
    _, app_id, country = call.data.split("_")
    if app_id in config["SERVICES"] and country in config["SERVICES"][app_id]["rids"]:
        del config["SERVICES"][app_id]["rids"][country]
        save_config(config)
        bot.answer_callback_query(call.id, text=f"✅ {country} এর রেঞ্জ সফলভাবে ডিলিট করা হয়েছে!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, text="❌ ডিলিট করতে সমস্যা হয়েছে!", show_alert=True)
    show_admin_dashboard(chat_id)

@bot.callback_query_handler(func=lambda call: call.data == "ch_add")
def wizard_add_channel(call):
    msg = bot.send_message(call.message.chat.id, "👉 নতুন চ্যানেল বা গ্রুপ যুক্ত করতে এভাবে লিখে পাঠান:\n\n`টাইপ আইডি লিংক নাম`\n\n*উদাহরণ:* `channel -100123456789 https://t.me/mychannel MyChannel`")
    bot.register_next_step_handler(msg, process_save_channel_group)

def process_save_channel_group(message):
    try:
        parts = message.text.strip().split(maxsplit=3)
        ch_type = parts[0].lower()
        ch_id = parts[1]
        ch_link = parts[2]
        ch_name = parts[3]
        item = {"id": ch_id, "link": ch_link, "name": ch_name}
        if ch_type == "channel":
            config["CHANNELS_TO_JOIN"].append(item)
            if ch_id not in config["OTP_DESTINATIONS"]: config["OTP_DESTINATIONS"].append(ch_id)
        elif ch_type == "group":
            config["GROUPS_TO_JOIN"].append(item)
            if ch_id not in config["OTP_DESTINATIONS"]: config["OTP_DESTINATIONS"].append(ch_id)
        save_config(config)
        bot.send_message(message.chat.id, "✅ সফলভাবে চ্যানেল/গ্রুপ যুক্ত করা হয়েছে!")
    except:
        bot.send_message(message.chat.id, "❌ ফরম্যাট সঠিক নয়! আবার চেষ্টা করুন।")
    show_admin_dashboard(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "ch_remove")
def wizard_remove_channel(call):
    markup = types.InlineKeyboardMarkup()
    for idx, c in enumerate(config["CHANNELS_TO_JOIN"]):
        markup.add(types.InlineKeyboardButton(f"❌ চ্যানেল ডিলিট: {c['name']}", callback_data=f"delch_c_{idx}"))
    for idx, g in enumerate(config["GROUPS_TO_JOIN"]):
        markup.add(types.InlineKeyboardButton(f"❌ গ্রুপ ডিলিট: {g['name']}", callback_data=f"delch_g_{idx}"))
    markup.add(types.InlineKeyboardButton("⬅️ ব্যাক", callback_data="adm_channels"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🗑 যে চ্যানেল বা গ্রুপটি রিমুভ করতে চান তাতে ক্লিক করুন:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delch_"))
def execute_remove_channel(call):
    _, target_type, idx_str = call.data.split("_")
    idx = int(idx_str)
    if target_type == "c" and len(config["CHANNELS_TO_JOIN"]) > 1:
        removed = config["CHANNELS_TO_JOIN"].pop(idx)
        if removed["id"] in config["OTP_DESTINATIONS"]: config["OTP_DESTINATIONS"].remove(removed["id"])
        save_config(config)
        bot.answer_callback_query(call.id, text="✅ চ্যানেল রিমুভ হয়েছে!", show_alert=True)
    elif target_type == "g":
        removed = config["GROUPS_TO_JOIN"].pop(idx)
        if removed["id"] in config["OTP_DESTINATIONS"]: config["OTP_DESTINATIONS"].remove(removed["id"])
        save_config(config)
        bot.answer_callback_query(call.id, text="✅ গ্রুপ রিমুভ হয়েছে!", show_alert=True)
    show_admin_dashboard(call.message.chat.id)

def save_notice(message):
    config["NOTICE"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ নোটিশ আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_bot_name(message):
    config["BOT_NAME"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ বটের নাম আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_balance_text(message):
    config["BALANCE_TEXT"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ ব্যালেন্স টেক্সট আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_withdraw_text(message):
    config["WITHDRAW_TEXT"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ ওটিপি আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_bot_username(message):
    config["BOT_USERNAME"] = message.text.strip().replace("@", "")
    save_config(config)
    bot.send_message(message.chat.id, "✅ বটের ইউজারনেম আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_dev_username(message):
    config["DEV_USERNAME"] = message.text.strip().replace("@", "")
    save_config(config)
    bot.send_message(message.chat.id, "✅ ডেভেলপার ইউজারনেম আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_api_key(message):
    config["FASTX_API_KEY"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ API Key আপডেট হয়েছে।")
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
    formatted_rid = format_rid(rid)
    
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/getnum"
    payload = {"rid": str(formatted_rid)}
    
    try:
        response = requests.post(url, json=payload, headers=get_api_headers(), timeout=20)
        if response.status_code != 200:
            bot.answer_callback_query(call.id, text=f"❌ সার্ভার কোড: {response.status_code}", show_alert=True)
            return
            
        res = response.json()
        if res.get("meta", {}).get("status") == "ok":
            num = res["data"].get("full_number") or res["data"].get("no_plus_number")
            
            msg = (f"✅ **Number Assigned Successfully!**\n\n"
                   f"📱 Service ➔ **{selected_app.upper()}**\n"
                   f"🌍 Country ➔ **{country}**\n\n"
                   f"📞 Number: `{num}`\n\n"
                   f"⏳ Status: Waiting For OTP\n"
                   f"⏰ Validity ➔ 10 minutes\n"
                   f"💎 নিচে 'Fetch Code' বাটনে ক্লিক করে বা অটো ওটিপির জন্য অপেক্ষা করুন।")
            
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("📥 Fetch Code", callback_data=f"fetch_{selected_app}_{country}_{num}"),
                types.InlineKeyboardButton("🔄 Change Number", callback_data=f"c_{country}_{selected_app}")
            )
            markup.row(types.InlineKeyboardButton("📋 Copy Number", callback_data=f"copynum_{num}"))
            markup.row(types.InlineKeyboardButton("🔗 View OTP Group", url=get_otp_group_link()))
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup, parse_mode="Markdown")
            
            # ব্যাকগ্রাউন্ডে ১০ মিনিট ওটিপি চেক করার থ্রেড চালু করা হলো
            Thread(target=background_user_otp_watcher, args=(call.message.chat.id, call.message.message_id, selected_app, country, num), daemon=True).start()
        else:
            bot.answer_callback_query(call.id, text=f"❌ প্যানেল: {res.get('message', 'নম্বর স্টক শেষ')}", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, text="⚠️ কানেকশন সমস্যা! আবার ট্রাই করুন।", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("copynum_"))
def copy_number_alert(call):
    num = call.data.split("_")[1]
    bot.answer_callback_query(call.id, text=f"📞 Number: {num}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("copyotp_"))
def copy_otp_alert(call):
    code = call.data.split("_")[1]
    bot.answer_callback_query(call.id, text=f"🔑 OTP Code: {code}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fetch_"))
def manual_fetch(call):
    data_parts = call.data.split("_")
    selected_app = data_parts[1]
    country = data_parts[2]
    num = data_parts[3]
    bot.answer_callback_query(call.id, text="🔍 ওটিপি চেক করা হচ্ছে...")
    check_and_send_otp_manual(call.message.chat.id, selected_app, country, num)

def check_and_send_otp_manual(chat_id, selected_app, country, num):
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/success-otp"
    
    try:
        res = requests.get(url, headers=get_api_headers(), timeout=15).json()
        if res.get("meta", {}).get("status") == "ok":
            otps_list = res.get("data", {}).get("otps", [])
            clean_num = str(num).replace("+", "").strip()
            
            found_msg = None
            for item in otps_list:
                item_num = str(item.get("number")).replace("+", "").strip()
                if item_num == clean_num or clean_num.endswith(item_num) or item_num.endswith(clean_num):
                    found_msg = item.get("message") or item.get("sms")
                    break
            
            if found_msg:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                bot_title = config.get("BOT_NAME", "ᏕᎻᏕ ᏕᎷᏕ ᎻᏬᏰ")
                bot_user = config.get("BOT_USERNAME", "SHS_SMSHUB_bot")
                dev_user = config.get("DEV_USERNAME", "Saku_143")
                
                code_match = re.search(r'\b\d{4,8}\b', found_msg)
                isolated_code = code_match.group(0) if code_match else found_msg[:10]
                
                alert_text = (f"🤖 **{bot_title}**\n"
                              f"🇲🇬 **{country} {selected_app.upper()} RECEIVED!**\n\n"
                              f"🕒 Time: `{current_time}`\n"
                              f"📱 Service: {selected_app.upper()}\n"
                              f"📞 Number: `{num}`\n"
                              f"🌍 Country: {country}\n"
                              f"🔑 OTP: `{isolated_code}`\n\n"
                              f"💬 Message:\n{found_msg}")
                
                user_markup = types.InlineKeyboardMarkup()
                user_markup.row(
                    types.InlineKeyboardButton("📋 Copy OTP", callback_data=f"copyotp_{isolated_code}"),
                    types.InlineKeyboardButton("📞 Copy Number", callback_data=f"copynum_{num}")
                )
                user_markup.row(types.InlineKeyboardButton("🔗 View OTP Group", url=get_otp_group_link()))
                
                try:
                    bot.send_message(chat_id, alert_text, reply_markup=user_markup, parse_mode="Markdown")
                except: pass
                
                group_markup = types.InlineKeyboardMarkup()
                group_markup.row(
                    types.InlineKeyboardButton("📋 Copy OTP", callback_data=f"copyotp_{isolated_code}"),
                    types.InlineKeyboardButton("📞 Copy Number", callback_data=f"copynum_{num}")
                )
                group_markup.row(types.InlineKeyboardButton("🔗 View OTP Group", url=get_otp_group_link()))
                group_markup.row(
                    types.InlineKeyboardButton("👑 Owner", url=f"https://t.me/{dev_user}"),
                    types.InlineKeyboardButton("📱 Bot", url=f"https://t.me/{bot_user}")
                )
                
                for dest_id in config.get("OTP_DESTINATIONS", []):
                    try:
                        bot.send_message(int(dest_id), alert_text, reply_markup=group_markup, parse_mode="Markdown")
                    except: pass
                return True
            else:
                bot.send_message(chat_id, "⚠️ ওটিপি এখনও প্যানেলে আসেনি। একটু পরে আবার চেষ্টা করুন।")
        else:
            bot.send_message(chat_id, "⚠️ সার্ভার থেকে কোনো ডেটা পাওয়া যায়নি।")
    except:
        bot.send_message(chat_id, "❌ ওটিপি চেক করতে গিয়ে সমস্যা হয়েছে।")
    return False

def background_user_otp_watcher(chat_id, message_id, selected_app, country, num):
    """ইউজার নাম্বার নেওয়ার পর ব্যাকগ্রাউন্ডে ১০ মিনিট ধরে রিয়েল অটো ওটিপি চেক করবে (কোনো ফেক ওটিপি জেনারেট করবে না)"""
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/success-otp"
    
    clean_num = str(num).replace("+", "").strip()
    checks = 0
    while checks < 40: # প্রতি ১৫ সেকেন্ড পর পর মোট ১০ মিনিট চেক করবে
        time.sleep(15)
        checks += 1
        try:
            res = requests.get(url, headers=get_api_headers(), timeout=15).json()
            if res.get("meta", {}).get("status") == "ok":
                otps_list = res.get("data", {}).get("otps", [])
                found_msg = None
                for item in otps_list:
                    item_num = str(item.get("number")).replace("+", "").strip()
                    if item_num == clean_num or clean_num.endswith(item_num) or item_num.endswith(clean_num):
                        found_msg = item.get("message") or item.get("sms")
                        break
                
                if found_msg:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    bot_title = config.get("BOT_NAME", "ᏕᎻᏕ ᏕᎷᏕ ᎻᏬᏰ")
                    bot_user = config.get("BOT_USERNAME", "SHS_SMSHUB_bot")
                    dev_user = config.get("DEV_USERNAME", "Saku_143")
                    
                    code_match = re.search(r'\b\d{4,8}\b', found_msg)
                    isolated_code = code_match.group(0) if code_match else found_msg[:10]
                    
                    alert_text = (f"🤖 **{bot_title}**\n"
                                  f"🇲🇬 **{country} {selected_app.upper()} RECEIVED!**\n\n"
                                  f"🕒 Time: `{current_time}`\n"
                                  f"📱 Service: {selected_app.upper()}\n"
                                  f"📞 Number: `{num}`\n"
                                  f"🌍 Country: {country}\n"
                                  f"🔑 OTP: `{isolated_code}`\n\n"
                                  f"💬 Message:\n{found_msg}")
                    
                    user_markup = types.InlineKeyboardMarkup()
                    user_markup.row(
                        types.InlineKeyboardButton("📋 Copy OTP", callback_data=f"copyotp_{isolated_code}"),
                        types.InlineKeyboardButton("📞 Copy Number", callback_data=f"copynum_{num}")
                    )
                    user_markup.row(types.InlineKeyboardButton("🔗 View OTP Group", url=get_otp_group_link()))
                    
                    try:
                        bot.send_message(chat_id, alert_text, reply_markup=user_markup, parse_mode="Markdown")
                    except: pass
                    
                    group_markup = types.InlineKeyboardMarkup()
                    group_markup.row(
                        types.InlineKeyboardButton("📋 Copy OTP", callback_data=f"copyotp_{isolated_code}"),
                        types.InlineKeyboardButton("📞 Copy Number", callback_data=f"copynum_{num}")
                    )
                    group_markup.row(types.InlineKeyboardButton("🔗 View OTP Group", url=get_otp_group_link()))
                    group_markup.row(
                        types.InlineKeyboardButton("👑 Owner", url=f"https://t.me/{dev_user}"),
                        types.InlineKeyboardButton("📱 Bot", url=f"https://t.me/{bot_user}")
                    )
                    
                    for dest_id in config.get("OTP_DESTINATIONS", []):
                        try:
                            bot.send_message(int(dest_id), alert_text, reply_markup=group_markup, parse_mode="Markdown")
                        except: pass
                    return
        except:
            pass

def background_live_sms_monitor():
    """প্যানেল কনসোল থেকে শুধুমাত্র আসল লাইভ ওটিপিগুলো ফেচ করে এবং হাই-স্পিড রেঞ্জ ডিটেক্ট করে গ্রুপে দেশের নাম ও পতাকাসহ অ্যালার্ট দেয়"""
    global seen_console_hits, range_hits_tracker, last_announced_range
    while True:
        try:
            time.sleep(15)
            base_url = str(config['BASE_URL']).strip().rstrip('/')
            url = f"{base_url}/console"
            res = requests.get(url, headers=get_api_headers(), timeout=15).json()
            
            if res.get("meta", {}).get("status") == "ok":
                data_obj = res.get("data", {})
                hits_list = data_obj.get("hits", [])
                
                for item in hits_list:
                    range_val = item.get("range", "Unknown")
                    platform = item.get("sid", "Global")
                    msg_body = item.get("message") or ""
                    time_val = item.get("time") or time.time()
                    
                    hit_id = f"{msg_body}_{time_val}"
                    if hit_id in seen_console_hits:
                        continue
                    seen_console_hits.add(hit_id)
                    
                    # Keep console logs cache size limited
                    if len(seen_console_hits) > 1000:
                        seen_console_hits.clear()
                        
                    current_time_epoch = time.time()
                    
                    # দেশের নাম ও পতাকা শনাক্তকরণ
                    country_name = get_country_info_by_range(range_val)
                    
                    # --- হাই-স্পিড রেঞ্জ ডিটেকশন লজিক ---
                    key = (range_val, platform)
                    range_hits_tracker[key].append(current_time_epoch)
                    
                    # ৩ মিনিটের বেশি পুরোনো রেকর্ডগুলো বাদ দেওয়া হচ্ছে
                    range_hits_tracker[key] = [t for t in range_hits_tracker[key] if current_time_epoch - t < 180]
                    
                    # যদি ৩ মিনিটে ৩ বা তার বেশি হিট আসে, তবে হাই-স্পিড হিসেবে চিহ্নিত করা হবে
                    if len(range_hits_tracker[key]) >= 3:
                        last_announce = last_announced_range.get(key, 0)
                        # অ্যালার্ট স্প্যামিং রুখতে ১৫ মিনিটের কুলডাউন মেইনটেইন করা হচ্ছে
                        if current_time_epoch - last_announce > 900:
                            last_announced_range[key] = current_time_epoch
                            
                            speed_alert = (
                                f"🚀 **HIGH SPEED RANGE DETECTED!** 🚀\n\n"
                                f"🔥 **Service:** {str(platform).upper()}\n"
                                f"🌍 **Country:** {country_name}\n"
                                f"⚡ **Range:** `{range_val}`\n"
                                f"📶 **Status:** Super Fast OTP Delivery!\n\n"
                                f"💡 এই রেঞ্জে দ্রুত নম্বর নিয়ে কাজ করুন, ওটিপি সাথে সাথে আসছে!"
                            )
                            for dest_id in config.get("OTP_DESTINATIONS", []):
                                try:
                                    bot.send_message(int(dest_id), speed_alert, parse_mode="Markdown")
                                except: pass
                    # ------------------------------------

                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    bot_title = config.get("BOT_NAME", "ᏕᎻᏕ ᏕᎷᏕ ᎻᏬᏰ")
                    bot_user = config.get("BOT_USERNAME", "SHS_SMSHUB_bot")
                    dev_user = config.get("DEV_USERNAME", "Saku_143")
                    
                    code_match = re.search(r'\b\d{4,8}\b', msg_body)
                    isolated_code = code_match.group(0) if code_match else "N/A"
                    
                    live_alert = (f"🤖 **{bot_title}**\n"
                                  f"🌐 **{country_name} {str(platform).upper()} LIVE OTP!**\n\n"
                                  f"🕒 Time: `{current_time}`\n"
                                  f"📱 Service: {str(platform).upper()}\n"
                                  f"⚡ Range: `{range_val}`\n"
                                  f"🌍 Country: {country_name}\n"
                                  f"🔑 OTP: `{isolated_code}`\n\n"
                                  f"💬 Message:\n{msg_body}")
                    
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        types.InlineKeyboardButton("📋 Copy OTP", callback_data=f"copyotp_{isolated_code}")
                    )
                    markup.row(types.InlineKeyboardButton("🔗 View OTP Group", url=get_otp_group_link()))
                    markup.row(
                        types.InlineKeyboardButton("👑 Owner", url=f"https://t.me/{dev_user}"),
                        types.InlineKeyboardButton("📱 Bot", url=f"https://t.me/{bot_user}")
                    )
                    
                    for dest_id in config.get("OTP_DESTINATIONS", []):
                        try:
                            bot.send_message(int(dest_id), live_alert, reply_markup=markup, parse_mode="Markdown")
                        except: pass
        except:
            time.sleep(15)

@bot.callback_query_handler(func=lambda call: call.data == "back_services")
def back_to_serv(call): send_services_menu(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back(call): 
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_home_keyboard(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check(call):
    if is_subscribed_all(call.from_user.id): 
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        send_home_keyboard(call.message.chat.id, "✅ ভেরিфикации সফল! এখন থেকে সার্ভিস ব্যবহার করতে পারবেন।")
    else: 
        bot.answer_callback_query(call.id, text="❌ আপনি এখনো সমস্ত বাধ্যতামূলক চ্যানেল বা গ্রুপে জয়েন করেননি!", show_alert=True)

if __name__ == "__main__":
    keep_alive()
    Thread(target=background_live_sms_monitor, daemon=True).start()
    
    try: bot.delete_webhook(drop_pending_updates=True)
    except: pass
    print("🚀 ᏕᎻᏕ ᏕᎷᏕ ᎻᏬᏰ (Voltxsms version) সফলভাবে রানিং...")
    bot.polling(none_stop=True)
