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
            "BOT_TOKEN": "8979736100:AAGmW4eTItErzMpZBXviuJ_uEHClCwfLtQk", 
            "VOLTX_API_KEY": "MLPNN2HKYXD", 
            "BASE_URL": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api",
            "ADMIN_ID": 8262679678, 
            "CHANNEL_ID": "-1003956226642",
            "GROUP_ID": "-1004309875319",
            "CHANNEL_LINK": "https://t.me/SHS_Otp_Channel",
            "GROUP_LINK": "https://t.me/+DXdDIm7-rRU4YTQ1",
            "SERVICES": {
                "whatsapp": {"name": "💬 WhatsApp", "rids": {"US": "22501", "GB": "26134", "KG": "99655"}},
                "facebook": {"name": "📘 Facebook", "rids": {"US": "22501", "GN": "22465"}},
                "instagram": {"name": "📸 Instagram", "rids": {"US": "21640", "KG": "99622"}},
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
def home(): return "Voltx Form-Data Bot is Live!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

def is_subscribed(user_id):
    if user_id == config["ADMIN_ID"]: return True 
    try:
        c = bot.get_chat_member(int(config["CHANNEL_ID"]), user_id).status
        g = bot.get_chat_member(int(config["GROUP_ID"]), user_id).status
        return c not in ['left', 'kicked'] and g not in ['left', 'kicked']
    except: return True

def send_home_keyboard(chat_id, text="👋 ওটিপি ড্যাশবোর্ডে স্বাগতম!"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("📞 Get Number"), types.KeyboardButton("📊 Active Traffic"))
    if chat_id == config["ADMIN_ID"]:
        markup.row(types.KeyboardButton("🛠 Admin Dashboard"))
    bot.send_message(chat_id, text, reply_markup=markup)

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
        markup.row(types.InlineKeyboardButton("📢 Join Channel", url=config["CHANNEL_LINK"]))
        markup.row(types.InlineKeyboardButton("✅ Joined", callback_data="check_membership"))
        bot.send_message(message.chat.id, "⚠️ সার্ভিসটি ব্যবহার করতে আমাদের চ্যানেলে জয়েন করুন।", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if not is_subscribed(message.chat.id): return
    if message.text == "📞 Get Number": send_services_menu(message.chat.id)
    elif message.text == "📊 Active Traffic": bot.send_message(message.chat.id, "📊 Traffic 100% Active!")
    elif message.text == "🛠 Admin Dashboard" and message.chat.id == config["ADMIN_ID"]:
        show_admin_dashboard(message.chat.id)

def show_admin_dashboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Add/Update Range ID", callback_data="adm_addrid"))
    markup.row(types.InlineKeyboardButton("🔑 Update Voltx API Key", callback_data="adm_setkey"))
    
    text = f"🛠 **অ্যাডমিন কন্ট্রোল প্যানেল**\n\n• API Key: `{config['VOLTX_API_KEY']}`\n• মোট সচল অ্যাপ: {len(config['SERVICES'])}"
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin(call):
    if call.message.chat.id != config["ADMIN_ID"]: return
    if call.data == "adm_addrid":
        msg = bot.send_message(call.message.chat.id, "👉 নতুন রেঞ্জ যোগ করতে এভাবে ফরম্যাট লিখে পাঠান:\n\n`অ্যাপ_নাম দেশের_কোড রেঞ্জ_আইডি`\n\n*উদাহরণ:* `wechat US 50230`")
        bot.register_next_step_handler(msg, process_add_rid)
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
    markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="back_main"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🌍 **কোন দেশের নম্বর নিতে চান?**", reply_markup=markup)

# --- এই ফাংশনটি এখন পিওর POST মেথড এবং প্যানেল ফরম্যাট মেনে ডেটা পাঠাবে ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("c_"))
def request_number(call):
    _, country, selected_app = call.data.split("_")
    rid = config["SERVICES"][selected_app]["rids"].get(country)
    
    base_url = str(config['BASE_URL']).strip().rstrip('/')
    url = f"{base_url}/getnum"
    
    headers = {
        "mauthapi": str(config["VOLTX_API_KEY"]).strip()
    }
    
    # পোস্ট রিকোয়েস্টের বডিতে সরাসরি ডিকশনারি পাস করা হলো (অ্যাপ্লিকেশন/জেসন ওভারহেড ছাড়া)
    payload = {"rid": str(rid)}
    
    try:
        # প্লেগ্রাউন্ডের মতো হুবহু POST রিকোয়েস্ট পাঠানো হচ্ছে
        response = requests.post(url, data=payload, headers=headers, timeout=20)
        
        # যদি প্রথমবার ব্যর্থ হয়, তবে raw json পে-লোড দিয়ে ব্যাকআপ ট্রাই করবে
        if response.status_code != 200 or "bad_request" in response.text:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            
        if response.status_code != 200:
            bot.answer_callback_query(call.id, text=f"❌ সার্ভার কোড: {response.status_code}", show_alert=True)
            return
            
        res = response.json()
        if res.get("meta", {}).get("status") == "ok":
            num = res["data"].get("full_number") or res["data"].get("no_plus_number")
            current_rid = res.get("rid", rid)
            
            msg = f"📱 Service: **{selected_app.upper()}** ({country})\n📞 Number: `{num}`\n\n⏳ ওটিপি কোডের জন্য অপেক্ষা করা হচ্ছে..."
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("📥 Fetch Code", callback_data=f"fetch_{current_rid}_{selected_app}_{num}"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, reply_markup=markup, parse_mode="Markdown")
            
            Thread(target=auto_fetch_otp, args=(call.message.chat.id, current_rid, selected_app, num)).start()
        else:
            bot.answer_callback_query(call.id, text=f"❌ প্যানেল: {res.get('message', 'নম্বর পাওয়া যায়নি')}", show_alert=True)
            
    except Exception as e:
        bot.answer_callback_query(call.id, text="⚠️ কানেকশন সমস্যা! রেন্ডার রিস্টার্ট দিয়ে আবার ট্রাই করুন।", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fetch_"))
def manual_fetch(call):
    _, rid, selected_app, num = call.data.split("_")
    bot.answer_callback_query(call.id, text="🔍 ওটিপি চেক করা হচ্ছে...")
    auto_fetch_otp(call.message.chat.id, rid, selected_app, num, manual=True)

def auto_fetch_otp(chat_id, rid, selected_app, num, manual=False):
    if not manual: time.sleep(15)
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
                if str(item.get("number")) == clean_num:
                    found_msg = item.get("message")
                    break
            
            if found_msg:
                alert = f"🔥 **নতুন ওটিপি কোড এসেছে!** 🔥\n\n📱 অ্যাপ: #{selected_app.upper()}\n📞 নম্বর: `{num}`\n✉️ ওটিপি: **{found_msg}**"
                bot.send_message(chat_id, alert, parse_mode="Markdown")
                bot.send_message(int(config["CHANNEL_ID"]), alert, parse_mode="Markdown")
            else:
                if manual: bot.send_message(chat_id, "⚠️ ওটিপি এখনও সার্ভারে পৌঁছায়নি। আবার ট্রাই করুন।")
        else:
            if manual: bot.send_message(chat_id, "⚠️ প্যানেল সার্ভার থেকে কোনো রেসপন্স পাওয়া যায়নি।")
    except:
        if manual: bot.send_message(chat_id, "❌ ওটিপি সার্ভার রেসপন্স করছে না।")

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back(call): send_services_menu(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check(call):
    if is_subscribed(call.from_user.id): send_home_keyboard(call.message.chat.id, "✅ ভেরিфикации সফল!")
    else: bot.answer_callback_query(call.id, text="❌ আপনি এখনও জয়েন করেননি!", show_alert=True)

if __name__ == "__main__":
    keep_alive()
    try: bot.delete_webhook(drop_pending_updates=True)
    except: pass
    print("🚀 ফর্ম-ডেটা ফিক্সড ডাইনামিক বট সচল...")
    bot.polling(none_stop=True)
