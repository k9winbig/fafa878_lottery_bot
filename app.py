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

# Function to send formatted results to the Telegram group
def send_results_to_group():
    results = fetch_lottery_results(API_URL)
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
        bot.send_message(GROUP_CHAT_ID, "Invalid date format in API response.")
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
        # Optionally notify if dates don't match
        pass

def job():
    send_results_to_group()

def run_scheduled_job():
    # Get the current time in GMT+8
    current_time = datetime.now(timezone).strftime("%H:%M")
    print(f"Current time in GMT+8: {current_time}", flush=True)  # Print the current time

    # Check if it's 8 PM in GMT+8
    if current_time == "20:00":  # Schedule for 8 PM
        job()

if __name__ == "__main__":
    # Start the bot in a separate thread
    import threading

    def start_bot():
        bot.infinity_polling()

    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # Schedule the job
    while True:
        run_scheduled_job()
        time.sleep(60)  # Wait for a minute before checking again
