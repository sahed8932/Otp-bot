import telebot
import requests
import os
import time
import json
from telebot import types
from flask import Flask
from threading import Thread

# --- কনফিগারেশন ---
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return json.load(f)
    return {
        "BOT_TOKEN": "8979736100:AAEQpGeHOEbGVtUyF4enfiGtmxB2DbEh5sQ",
        "VOLTX_API_KEY": "MLPNN2HKYXD",
        "BASE_URL": "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api",
        "ADMIN_ID": 8262679678,
        "CHANNEL_ID": "-1003956226642",
        "SERVICES": {"whatsapp": {"name": "💬 WhatsApp", "rids": {"US": "22501"}}},
        "NOTICE": "স্বাগতম! যেকোনো প্রয়োজনে আমাদের হেল্পলাইন দেখুন।"
    }

config = load_config()
bot = telebot.TeleBot(config["BOT_TOKEN"])
app = Flask('')

@app.route('/')
def home(): return "Bot is Active!"

def run(): app.run(host='0.0.0.0', port=8080)
Thread(target=run).start()

# --- কিবোর্ডস ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("📞 নম্বর নিন"), types.KeyboardButton("📢 নোটিশ"))
    if "ADMIN_ID" in config: markup.row(types.KeyboardButton("⚙️ এডমিন প্যানেল"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"👋 স্বাগতম!\n\n{config['NOTICE']}", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📞 নম্বর নিন")
def services(message):
    markup = types.InlineKeyboardMarkup()
    for s_id, s_info in config["SERVICES"].items():
        markup.add(types.InlineKeyboardButton(s_info["name"], callback_data=f"app_{s_id}"))
    bot.send_message(message.chat.id, "নিচের অ্যাপ থেকে সিলেক্ট করুন:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 নোটিশ")
def send_notice(message):
    bot.send_message(message.chat.id, f"📌 আজকের নোটিশ:\n{config['NOTICE']}")

# --- এডমিন প্যানেল ---
@bot.message_handler(func=lambda m: m.text == "⚙️ এডমিন প্যানেল" and m.from_user.id == config["ADMIN_ID"])
def admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ নতুন অ্যাপ/রেঞ্জ যোগ করুন", callback_data="adm_add"))
    markup.add(types.InlineKeyboardButton("📣 নোটিশ পরিবর্তন", callback_data="adm_notice"))
    bot.send_message(message.chat.id, "🛠 এডমিন কন্ট্রোল:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_actions(call):
    if call.data == "adm_add":
        msg = bot.send_message(call.message.chat.id, "লিখে পাঠান:\n`অ্যাপ_আইডি নাম রেঞ্জ_আইডি দেশ`\nউদাহরণ: `twitter Twitter 50230 US`")
        bot.register_next_step_handler(msg, add_app)
    elif call.data == "adm_notice":
        msg = bot.send_message(call.message.chat.id, "নতুন নোটিশ লিখুন:")
        bot.register_next_step_handler(msg, set_notice)

def add_app(message):
    try:
        parts = message.text.split()
        s_id, name, rid, country = parts[0], parts[1], parts[2], parts[3]
        if s_id not in config["SERVICES"]: config["SERVICES"][s_id] = {"name": name, "rids": {}}
        config["SERVICES"][s_id]["rids"][country] = rid
        with open(CONFIG_FILE, "w") as f: json.dump(config, f)
        bot.send_message(message.chat.id, "✅ সফলভাবে অ্যাড হয়েছে!")
    except: bot.send_message(message.chat.id, "❌ ভুল হয়েছে, আবার ট্রাই করুন।")

def set_notice(message):
    config["NOTICE"] = message.text
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)
    bot.send_message(message.chat.id, "✅ নোটিশ আপডেট হয়েছে!")

# --- নম্বর ফেচিং (অটোমেটেড) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("app_"))
def get_num_process(call):
    s_id = call.data.split("_")[1]
    rid = list(config["SERVICES"][s_id]["rids"].values())[0] # অটো প্রথম রেঞ্জ ধরবে
    url = f"{config['BASE_URL']}/getnum"
    res = requests.post(url, data={"rid": rid}, headers={"mauthapi": config["VOLTX_API_KEY"]}).json()
    
    if res['meta']['status'] == 'ok':
        num = res['data']['full_number']
        bot.send_message(call.message.chat.id, f"✅ নম্বর: `{num}`\n⏳ ওটিপি চেক করা হচ্ছে...")
    else:
        bot.send_message(call.message.chat.id, "❌ নম্বর পাওয়া যায়নি।")

bot.polling(none_stop=True)
