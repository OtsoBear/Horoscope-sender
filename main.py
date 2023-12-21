import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import menaisetwebscraper
import datetime
import pytz

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Set the timezone to Finland (Eastern European Time, EET)
finland_timezone = pytz.timezone('Europe/Helsinki')

# File to store time settings
TIME_SETTINGS_FILE = 'time_settings.txt'

# Global variable to store chat_id and bot token
job_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /settime <HH:MM> to set the daily horoscope time")

async def send_horoscope(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the horoscope message."""
    for chat_id, data in job_data.items():
        if isinstance(data, dict):  # Check if data is a dictionary
            bot_token = data.get('bot_token')
            if bot_token:
                bot = Bot(token=bot_token)

                URL = menaisetwebscraper.pageGetter()
                ennustuslista = menaisetwebscraper.parser(URL)

                # Modify this part based on your actual scraping logic
                horoscope_text = f"Today's horoscope:\n\n"
                for i, prediction in enumerate(ennustuslista):
                    horoscope_text += f"{i + 1}. {prediction}\n"

                await bot.send_message(chat_id, text=horoscope_text)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether the job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to send the horoscope at a specified time."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the horoscope in HH:MM format
        time_str = context.args[0]
        time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()

        # Convert the time to Finland timezone
        time_obj = finland_timezone.localize(datetime.datetime.combine(datetime.date.today(), time_obj))

        job_removed = remove_job_if_exists(str(chat_id), context)

        # Update the global variable with chat_id and bot token
        job_data[chat_id] = {'bot_token': context.bot.token, 'time_str': time_str}  # Use chat_id as a key

        # Run the job
        context.job_queue.run_daily(send_horoscope, time=time_obj, name=str(chat_id))

        # Save time setting to file
        save_time_settings()

        # Print the command used when adding a job
        logging.info(f"Added job for chat_id {chat_id} with command /settime {time_str}")

        text = "Horoscope time successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /settime <HH:MM>")

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Horoscope time successfully cancelled!" if job_removed else "You have no active horoscope time."
    
    # Remove time setting from file
    remove_time_setting(chat_id)
    
    await update.message.reply_text(text)

def save_time_settings() -> None:
    """Save time settings to file."""
    existing_job_data = load_time_settings()
    existing_job_data.update(job_data)  # Update existing data with new data
    with open(TIME_SETTINGS_FILE, 'w') as file:
        for chat_id, data in existing_job_data.items():
            file.write(f"{chat_id} {data['bot_token']} {data['time_str']}\n")

def load_time_settings() -> dict:
    """Load time settings from file."""
    try:
        with open(TIME_SETTINGS_FILE, 'r') as file:
            existing_job_data = {}
            for line in file:
                chat_id, bot_token, time_str = line.strip().split()
                existing_job_data[int(chat_id)] = {'bot_token': bot_token, 'time_str': time_str}
        return existing_job_data
    except (FileNotFoundError, ValueError):
        return {}

def remove_time_setting(chat_id: int) -> None:
    """Remove time setting for a specific chat."""
    existing_job_data = load_time_settings()
    if chat_id in existing_job_data:
        del existing_job_data[chat_id]
        save_time_settings(existing_job_data)

def main() -> None:
    """Run bot."""
    # Load time settings from file
    global job_data
    job_data = load_time_settings()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6908657339:AAH1RM06mzZfOTZhNOMQMf893p2NdigolJI").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("settime", set_time))
    application.add_handler(CommandHandler("unset", unset))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
