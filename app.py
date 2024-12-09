import os
import telebot
import requests
import time
import schedule
import pytz
from datetime import datetime
from image_processor import create_result_image, fetch_lottery_results

# Load environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUP_CHAT_ID = int(os.getenv('TELEGRAM_GROUP_CHAT_ID'))
API_URL = os.getenv('API_URL', "https://4dresult88.com/fetchall?_=")
TIMEZONE = os.getenv('TIMEZONE', "Asia/Singapore")
IMAGE_CAPTION = os.getenv('IMAGE_CAPTION', "Here are the latest results")

bot = telebot.TeleBot(TOKEN)
timezone = pytz.timezone(TIMEZONE)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Type /fetch to get the results.")

@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"Your Chat ID is: {chat_id}")

def fetch_data():
    current_timestamp = int(time.time())
    url = API_URL.format(current_timestamp)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def send_results_to_group():
    results = fetch_data()
    if not results:
        bot.send_message(GROUP_CHAT_ID, "Failed to fetch lottery data.")
        return

    api_date_str = results.get('M4D', {}).get('DD')
    if not api_date_str:
        bot.send_message(GROUP_CHAT_ID, "Date not found in the lottery data.")
        return

    # Parse the date
    try:
        api_date = datetime.strptime(api_date_str.split(' ')[0], "%d-%m-%Y").date()
    except ValueError:
        return

    current_date = datetime.now(timezone).date()

    if current_date == api_date:
        image_path = create_result_image(results)
        with open(image_path, 'rb') as image_file:
            # Send image with caption
            bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image_file, caption=IMAGE_CAPTION)

@bot.message_handler(commands=['sendresult'])
def manual_fetch_results(message):
    results = fetch_data()
    if not results:
        bot.reply_to(message, "Failed to fetch lottery data.")
        return

    image_path = create_result_image(results)
    with open(image_path, 'rb') as image_file:
        # Send image with caption
        bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image_file, caption=IMAGE_CAPTION)

def job():
    send_results_to_group()

def run_scheduled_job():
    current_time = datetime.now(timezone).strftime("%H:%M")
    print(f"Current time in GMT+8: {current_time}", flush=True)

    if current_time == "20:00":  # 8 PM
        job()

if __name__ == "__main__":
    import threading

    bot_thread = threading.Thread(target=bot.polling, daemon=True)
    bot_thread.start()

    while True:
        run_scheduled_job()
        time.sleep(60)
