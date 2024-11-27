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

bot = telebot.TeleBot(TOKEN)
timezone = pytz.timezone(TIMEZONE)

# Command to start the bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Type /fetch to get the results.")

@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"Your Chat ID is: {chat_id}")

# Function to fetch results from the API
def fetch_data():
    current_timestamp = int(time.time())
    url = API_URL.format(current_timestamp)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Function to send formatted results to the Telegram group
def send_results_to_group():
    results = fetch_data()
    if not results:
        bot.send_message(GROUP_CHAT_ID, "Failed to fetch lottery data.")
        return

    # Extract the date from the API response (assuming 'M4D' is the relevant section)
    api_date_str = results.get('M4D', {}).get('DD')  # Get the 'DD' field
    if not api_date_str:
        bot.send_message(GROUP_CHAT_ID, "Date not found in the lottery data.")
        return

    # Parse the date string in the format "20-10-2024 (Sun)"
    try:
        api_date = datetime.strptime(api_date_str.split(' ')[0], "%d-%m-%Y").date()  # Extracting date part
    except ValueError:
        return

    # Get the current date in GMT+8
    current_date = datetime.now(timezone).date()

    # Compare dates
    if current_date == api_date:
        # Call the image processing function
        image_path = create_result_image(results)  # Pass relevant section data to the function

        # Send the image to the Telegram group
        with open(image_path, 'rb') as image_file:
            bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image_file)
    else:
        return


# Manually fetch and send results on command
@bot.message_handler(commands=['sendresult'])
def manual_fetch_results(message):
    results = fetch_data()
    if not results:
        bot.reply_to(message, "Failed to fetch lottery data.")
        return

    # Call the image processing function
    image_path = create_result_image(results)  # Pass relevant section data to the function

    # Send the image to the user or group
    with open(image_path, 'rb') as image_file:
        bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image_file)


# Scheduled function to run daily at 8 PM
def job():
    send_results_to_group()


# Run a scheduled job every minute to check time
def run_scheduled_job():
    current_time = datetime.now(timezone).strftime("%H:%M")
    print(f"Current time in GMT+8: {current_time}", flush=True)

    # Check if it's 8 PM in GMT+8
    if current_time == "20:00":  # Schedule for 8 PM
        job()


# Start the bot and schedule the job
if __name__ == "__main__":
    # Start the bot polling in a separate thread
    import threading

    bot_thread = threading.Thread(target=bot.polling, daemon=True)
    bot_thread.start()

    # Run the scheduled job loop
    while True:
        run_scheduled_job()
        time.sleep(60)  # Wait for a minute before checking again
