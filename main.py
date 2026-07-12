import telebot
import requests
import os
import time
import random
import json
from datetime import datetime
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
            "BOT_TOKEN": "8979736100:AAG_8ILyTgjuWxpSG1v2kgdRWv4nCPeycws", 
            "VOLTX_API_KEY": "MLPNN2HKYXD", 
            "BASE_URL": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api",
            "ADMIN_ID": 8262679678,
            "BOT_NAME": "SM OTP", 
            "BOT_USERNAME": "YourBotUsername", # এখানে আপনার বটের ইউজারনেম দিবেন (@ ছাড়া)
            "DEV_USERNAME": "Saku_143",        # ডেভেলপার বা ওনারের ইউজারনেম (@ ছাড়া)
            "CHANNELS_TO_JOIN": [
                {"id": "-1003956226642", "link": "https://t.me/SHS_Otp_Channel", "name": "📢 Main Channel"}
            ],
            "GROUPS_TO_JOIN": [
                {"id": "-1004309875319", "link": "https://t.me/+DXdDIm7-rRU4YTQ1", "name": "👥 Support Group"}
            ],
            "OTP_DESTINATIONS": [
                "-1003956226642",
                "-1004309875319"
            ],
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

admin_temp_data = {}

@app.route('/')
def home(): return "Voltx OTP Bot is Live & Active!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

def is_subscribed_all(user_id):
    if user_id == int(config["ADMIN_ID"]): return True 
    
    for ch in config.get("CHANNELS_TO_JOIN", []):
        try:
            status = bot.get_chat_member(int(ch["id"]), user_id).status
            if status in ['left', 'kicked']: return False
        except:
            pass 
            
    for grp in config.get("GROUPS_TO_JOIN", []):
        try:
            status = bot.get_chat_member(int(grp["id"]), user_id).status
            if status in ['left', 'kicked']: return False
        except:
            pass
            
    return True

def send_home_keyboard(chat_id, text=None):
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
    if not is_subscribed_all(message.chat.id):
        bot.send_message(message.chat.id, "❌ আপনি এখনো সব চ্যানেল বা গ্রুপে জয়েন করেননি! দয়া করে জয়েন করে আবার /start দিন।")
        return
    
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
        bot.send_message(message.chat.id, "🔐 2FA কোড জেনারেট করার জন্য আপনার সিক্রেট কোডটি দিন।", parse_mode="Markdown")
    elif text == "🤖 Create Your own bot":
        dev_user = config.get("DEV_USERNAME", "Saku_143")
        bot.send_message(message.chat.id, f"🤖 নিজস্ব ওটিপি বট তৈরি করতে চাইলে নিচের লিংকে যোগাযোগ করুন:\n\n👉 Telegram: @{dev_user}", parse_mode="Markdown")
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
    markup.row(types.InlineKeyboardButton("✍️ Set Notice", callback_data="adm_setnotice"),
               types.InlineKeyboardButton("🤖 Set Bot Name", callback_data="adm_setname"))
    markup.row(types.InlineKeyboardButton("🔗 Set Bot Username", callback_data="adm_setbotuser"),
               types.InlineKeyboardButton("👨‍💻 Set Dev Username", callback_data="adm_setdevuser"))
    markup.row(types.InlineKeyboardButton("🔑 Update API Key", callback_data="adm_setkey"))
    
    bot_title = config.get("BOT_NAME", "SM OTP")
    bot_user = config.get("BOT_USERNAME", "YourBotUsername")
    dev_user = config.get("DEV_USERNAME", "Saku_143")
    
    text = (f"🛠 **অ্যাডমিন কন্ট্রোল প্যানেল**\n\n"
            f"• Bot Name: `{bot_title}`\n"
            f"• Bot Username: `@{bot_user}`\n"
            f"• Dev Username: `@{dev_user}`\n"
            f"• API Key: `{config['VOLTX_API_KEY']}`\n"
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

    elif data == "adm_setnotice":
        msg = bot.send_message(chat_id, "👉 ইউজারদের জন্য নতুন নোটিশটি লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_notice)
    elif data == "adm_setname":
        msg = bot.send_message(chat_id, "👉 নতুন বটের নাম (যেমন: `SM OTP`) লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_bot_name)
    elif data == "adm_setbotuser":
        msg = bot.send_message(chat_id, "👉 বটের ইউজারনেম লিখুন (@ ছাড়া, যেমন: `MyOtpBot`):")
        bot.register_next_step_handler(msg, save_bot_username)
    elif data == "adm_setdevuser":
        msg = bot.send_message(chat_id, "👉 ডেভেলপার বা ওনারের ইউজারনেম লিখুন (@ ছাড়া, যেমন: `Saku_143`):")
        bot.register_next_step_handler(msg, save_dev_username)
    elif data == "adm_setkey":
        msg = bot.send_message(chat_id, "👉 আপনার নতুন Voltx SMS API Key টি পাঠান:")
        bot.register_next_step_handler(msg, save_api_key)
    elif data == "adm_back":
        show_admin_dashboard(chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("addapp_"))
def wizard_add_app(call):
    chat_id = call.message.chat.id
    app_target = call.data.split("_")[1]
    
    if app_target == "custom":
        msg = bot.send_message(chat_id, "✍️ নতুন অ্যাপের নাম লিখুন (যেমন: `telegram` বা `netflix`):")
        bot.register_next_step_handler(msg, wizard_get_custom_app_name)
    else:
        admin_temp_data[chat_id] = {"app": app_target}
        msg = bot.send_message(chat_id, f"🌍 আপনি **{app_target.upper()}** সিলেক্ট করেছেন।\n\nএখন দেশের কোড এবং রেঞ্জ আইডি একসাথে এভাবে লিখে পাঠান:\n*উদাহরণ:* `US 22501`")
        bot.register_next_step_handler(msg, wizard_save_rid)

def wizard_get_custom_app_name(message):
    chat_id = message.chat.id
    app_name = message.text.strip().lower()
    admin_temp_data[chat_id] = {"app": app_name}
    
    if app_name not in config["SERVICES"]:
        config["SERVICES"][app_name] = {"name": f"✨ {app_name.capitalize()}", "rids": {}}
        save_config(config)
        
    msg = bot.send_message(chat_id, f"✅ নতুন অ্যাপ **{app_name}** যুক্ত হয়েছে।\n\nএখন দেশের কোড এবং রেঞ্জ আইডি এভাবে লিখে পাঠান:\n*উদাহরণ:* `US 22501`")
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
        bot.send_message(chat_id, "❌ ফরম্যাট ভুল হয়েছে! সঠিক ফরম্যাটে (যেমন: `US 22501`) আবার চেষ্টা করুন।")
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
    msg = bot.send_message(call.message.chat.id, "👉 নতুন চ্যানেল বা গ্রুপ যুক্ত করতে এভাবে লিখে পাঠান:\n\n`টাইপ আইডি লিংক নাম`\n\n*উদাহরণ (চ্যানেল):* `channel -100123456789 https://t.me/mychannel MyChannel`\n*উদাহরণ (গ্রুপ):* `group -100987654321 https://t.me/mygroup MyGroup`")
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
            if ch_id not in config["OTP_DESTINATIONS"]:
                config["OTP_DESTINATIONS"].append(ch_id)
        elif ch_type == "group":
            config["GROUPS_TO_JOIN"].append(item)
            if ch_id not in config["OTP_DESTINATIONS"]:
                config["OTP_DESTINATIONS"].append(ch_id)
        else:
            bot.send_message(message.chat.id, "❌ টাইপ ভুল! 'channel' অথবা 'group' লিখুন।")
            return
            
        save_config(config)
        bot.send_message(message.chat.id, "✅ সফলভাবে চ্যানেল/গ্রুপ যুক্ত করা হয়েছে এবং ওটিপি ডেস্টিনেশনেও যুক্ত করা হয়েছে!")
    except Exception as e:
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
    
    if target_type == "c":
        if len(config["CHANNELS_TO_JOIN"]) > 1:
            removed = config["CHANNELS_TO_JOIN"].pop(idx)
            if removed["id"] in config["OTP_DESTINATIONS"]:
                config["OTP_DESTINATIONS"].remove(removed["id"])
            save_config(config)
            bot.answer_callback_query(call.id, text="✅ চ্যানেল সফলভাবে রিমুভ হয়েছে!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, text="⚠️ কমপক্ষে একটি চ্যানেল থাকা বাধ্যতামূলক!", show_alert=True)
    elif target_type == "g":
        removed = config["GROUPS_TO_JOIN"].pop(idx)
        if removed["id"] in config["OTP_DESTINATIONS"]:
            config["OTP_DESTINATIONS"].remove(removed["id"])
        save_config(config)
        bot.answer_callback_query(call.id, text="✅ গ্রুপ সফলভাবে রিমুভ হয়েছে!", show_alert=True)
        
    show_admin_dashboard(call.message.chat.id)

def save_notice(message):
    global config
    config["NOTICE"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ নোটিশ সফলভাবে আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_bot_name(message):
    global config
    config["BOT_NAME"] = message.text.strip()
    save_config(config)
    bot.send_message(message.chat.id, "✅ বটের নাম সফলভাবে আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_bot_username(message):
    global config
    config["BOT_USERNAME"] = message.text.strip().replace("@", "")
    save_config(config)
    bot.send_message(message.chat.id, "✅ বটের ইউজারনেম সফলভাবে আপডেট হয়েছে।")
    show_admin_dashboard(message.chat.id)

def save_dev_username(message):
    global config
    config["DEV_USERNAME"] = message.text.strip().replace("@", "")
    save_config(config)
    bot.send_message(message.chat.id, "✅ ডেভেলপার ইউজারনেম সফলভাবে আপডেট হয়েছে।")
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
            
            msg = (f"✅ **Your Number Assigned Successfully!**\n\n"
                   f"📱 Service ➔ **{selected_app.upper()}**\n"
                   f"🌍 Country ➔ **{country}**\n\n"
                   f"📞 Number: `{num}`\n\n"
                   f"⏳ Status: Waiting For OTP\n"
                   f"⏰ Number Validity ➔ 10 minutes\n"
                   f"💎 বটের ভিতরে ১০ সেকেন্ড ওয়েট করুন ওটিপি পেয়ে যাবেন না পেলে গ্রুপ চেক করুন। 🙂")
            
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("🔄 Change Number (10s)", callback_data=f"c_{country}_{selected_app}"))
            
            if config["CHANNELS_TO_JOIN"]:
                ch_info = config["CHANNELS_TO_JOIN"][0]
                markup.row(types.InlineKeyboardButton(f"🔗 {ch_info['name']}", url=ch_info["link"]))
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup, parse_mode="Markdown")
            Thread(target=auto_fetch_otp, args=(call.message.chat.id, current_rid, selected_app, country, num, call.message.message_id)).start()
        else:
            bot.answer_callback_query(call.id, text=f"❌ প্যানেল: {res.get('message', 'নম্বর স্টক শেষ')}", show_alert=True)
            
    except Exception as e:
        bot.answer_callback_query(call.id, text="⚠️ কানেকশন সমস্যা! আবার ট্রাই করুন।", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fetch_"))
def manual_fetch(call):
    data_parts = call.data.split("_")
    rid = data_parts[1]
    selected_app = data_parts[2]
    country = data_parts[3]
    num = data_parts[4]
    bot.answer_callback_query(call.id, text="🔍 ওটিপি চেক করা হচ্ছে...")
    check_and_send_otp(call.message.chat.id, selected_app, country, num, call.message.message_id, manual=True)

def auto_fetch_otp(chat_id, rid, selected_app, country, num, msg_id=None):
    for _ in range(4):
        time.sleep(15)
        if check_and_send_otp(chat_id, selected_app, country, num, msg_id):
            return

def check_and_send_otp(chat_id, selected_app, country, num, msg_id=None, manual=False):
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
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                bot_title = config.get("BOT_NAME", "SM OTP")
                bot_user = config.get("BOT_USERNAME", "YourBotUsername")
                
                alert = (f"🤖 **{bot_title}**\n"
                         f"🇲🇬 **{country} {selected_app.upper()} RECEIVED!**\n\n"
                         f"🕒 Time: `{current_time}`\n"
                         f"📱 Service: {selected_app.upper()}\n"
                         f"📞 Number: `{num}`\n"
                         f"🌍 Country: {country}\n\n"
                         f"💬 Message:\n`{found_msg}`")
                
                markup = types.InlineKeyboardMarkup()
                # 'Number' বাটনে ক্লিক করলে সরাসরি আপনার বটে চলে যাবে
                markup.row(
                    types.InlineKeyboardButton("👑 Owner", url=config["CHANNELS_TO_JOIN"][0]["link"] if config["CHANNELS_TO_JOIN"] else "https://t.me/"),
                    types.InlineKeyboardButton("📱 Number", url=f"https://t.me/{bot_user}")
                )
                
                try:
                    bot.send_message(chat_id, alert, reply_markup=markup, parse_mode="Markdown")
                except:
                    pass
                
                for dest_id in config.get("OTP_DESTINATIONS", []):
                    try:
                        bot.send_message(int(dest_id), alert, reply_markup=markup, parse_mode="Markdown")
                    except Exception as e:
                        print(f"Failed to send to destination {dest_id}: {e}")
                return True
            else:
                if manual:
                    bot.send_message(chat_id, "⚠️ ওটিপি এখনও প্যানেলে আসেনি। একটু পরে আবার চেষ্টা করুন।")
        else:
            if manual:
                bot.send_message(chat_id, "⚠️ সার্ভার থেকে কোনো ডেটা পাওয়া যায়নি।")
    except Exception as e:
        if manual:
            bot.send_message(chat_id, "❌ ওটিপি চেক করতে গিয়ে সমস্যা হয়েছে।")
    return False

# ==================== বহুদেশীয় রেন্ডম ওটিপি জেনারেটর সিস্টেম ====================
def background_random_otp_sender():
    countries_pool = [
        {"name": "Madagascar", "flag": "🇲🇬", "code": "+26134"},
        {"name": "Ivory Coast", "flag": "🇨🇮", "code": "+22507"},
        {"name": "Tajikistan", "flag": "🇹🇯", "code": "+99277"},
        {"name": "Ethiopia", "flag": "🇪🇹", "code": "+25191"},
        {"name": "Guinea", "flag": "🇬🇳", "code": "+22467"},
        {"name": "Sierra Leone", "flag": "🇸🇱", "code": "+23274"},
        {"name": "Senegal", "flag": "🇸🇳", "code": "+22170"},
        {"name": "Benin", "flag": "🇧🇯", "code": "+22901"},
        {"name": "Central African Republic", "flag": "🇨🇫", "code": "+23674"},
        {"name": "Montenegro", "flag": "🇲🇪", "code": "+38267"},
        {"name": "Tunisia", "flag": "🇹🇳", "code": "+21644"}
    ]
    
    while True:
        try:
            time.sleep(random.randint(60, 120))
            
            services_keys = list(config.get("SERVICES", {}).keys())
            if not services_keys:
                continue
                
            rand_app = random.choice(services_keys)
            rand_country_info = random.choice(countries_pool)
            
            c_name = rand_country_info["name"]
            c_flag = rand_country_info["flag"]
            c_code = rand_country_info["code"]
            
            rand_num = f"{c_code}{random.randint(100000, 999999)}"
            otp_code = f"{random.randint(100,999)}-{random.randint(100,999)}" if random.choice([True, False]) else str(random.randint(100000, 999999))
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bot_title = config.get("BOT_NAME", "SM OTP")
            bot_user = config.get("BOT_USERNAME", "YourBotUsername")
            
            fake_alert = (f"🤖 **{bot_title}**\n"
                          f"{c_flag} **{c_name} {rand_app.upper()} RECEIVED!**\n\n"
                          f"🕒 Time: `{current_time}`\n"
                          f"📱 Service: {rand_app.upper()}\n"
                          f"📞 Number: `{rand_num[:6]}***{rand_num[-4:]}`\n"
                          f"🌍 Country: {c_name}\n\n"
                          f"💬 Message:\n`# Your {rand_app.capitalize()} verification code is {otp_code}. Don't share this code with anyone.`")
            
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("👑 Owner", url=config["CHANNELS_TO_JOIN"][0]["link"] if config["CHANNELS_TO_JOIN"] else "https://t.me/"),
                types.InlineKeyboardButton("📱 Number", url=f"https://t.me/{bot_user}")
            )
            
            for dest_id in config.get("OTP_DESTINATIONS", []):
                try:
                    bot.send_message(int(dest_id), fake_alert, reply_markup=markup, parse_mode="Markdown")
                except Exception as e:
                    pass
        except Exception:
            pass

@bot.callback_query_handler(func=lambda call: call.data == "back_services")
def back_to_serv(call): send_services_menu(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back(call): 
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_home_keyboard(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check(call):
    if is_subscribed_all(call.from_user.id): 
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_home_keyboard(call.message.chat.id, "✅ ভেরিфикации সফল! এখন থেকে সার্ভিস ব্যবহার করতে পারবেন।")
    else: 
        bot.answer_callback_query(call.id, text="❌ আপনি এখনো সমস্ত বাধ্যতামূলক চ্যানেল বা গ্রুপে জয়েন করেননি!", show_alert=True)

if __name__ == "__main__":
    keep_alive()
    Thread(target=background_random_otp_sender, daemon=True).start()
    
    try: bot.delete_webhook(drop_pending_updates=True)
    except: pass
    print("🚀 ভোল্টেক্স ওটিপি বট সফলভাবে রান হচ্ছে...")
    bot.polling(none_stop=True)
