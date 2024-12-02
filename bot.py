import logging
import openai
import requests
import time
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "8115620553:AAF0uX8mp9O5765L59YxVvSjf2xkz6B2Qqw"  
OPENAI_API_KEY = "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"  # Your OpenAI API Key
AUTHORIZED_CHAT_ID = [-4583464873, -1002471870655]  

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

openai.api_key = OPENAI_API_KEY

# Timestamp to track the last image generation
last_generated_time = 0

def start(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id in AUTHORIZED_CHAT_ID:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Hello, {update.message.from_user.username}! Use /gen <prompt> to generate a fun conspiracy theory image.",
                                 parse_mode='Markdown')

def generate(update: Update, context: CallbackContext) -> None:
    global last_generated_time

    # Check if enough time has passed since the last image generation (30 seconds)
    current_time = time.time()
    if current_time - last_generated_time < 30:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please wait 30 seconds before trying to generate another image.")
        return

    if update.effective_chat.id not in AUTHORIZED_CHAT_ID:  # Check if the chat ID is authorized
        return

    if len(context.args) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a prompt after /gen.")
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # Display the wait message
    wait_message = context.bot.send_message(chat_id=update.effective_chat.id,
                                            text="Generating your image may take 10 seconds... Please wait.")

    text = ' '.join(context.args)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    RINTARO_DESCRIPTION = (
        "Generate this image, make sure it is a little bit surreal and eerie conspiracy theory image, if people found in image put tinfoil hats on them. It should have solana logo somewhere and now most importantly "
    )

    data = {
        "model": "dall-e-3",  # Verify the correct model
        "prompt": f"{RINTARO_DESCRIPTION} {text}",
        "num_images": 1,
        "size": "1024x1024",
        "response_format": "url"
    }

    try:
        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)

        # Update the timestamp of the last generated image
        last_generated_time = time.time()

        # Delete the wait message once the image is generated
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=wait_message.message_id)
        time.sleep(6)  # Add a delay after each request

    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating image: {e}")
        if response is not None:
            logging.error(f"Response content: {response.content}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, something went wrong while generating the image.")

def main() -> None:
    while True:  # Infinite loop to keep the bot running
        try:
            start_handler = CommandHandler('start', start)
            generate_handler = CommandHandler("gen", generate)

            dispatcher.add_handler(start_handler)
            dispatcher.add_handler(generate_handler)

            updater.start_polling()
            updater.idle()

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(5)  # Delay before restarting to avoid rapid restarts

if __name__ == '__main__':
    main()
