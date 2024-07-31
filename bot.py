import logging
import re
import datetime
import openai
import requests
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "7230686743:AAFUSeKyeV3-g6g-A6r642jwd08lE03t3UM"
OPENAI_API_KEY = "sk-proj-dgeZZLK3lIHfpsKvRAU1T3BlbkFJ0Cgg1ni9wjpaGhwWUjmw"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

openai.api_key = OPENAI_API_KEY

chat_history = {}


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="/start"
                             .format(update.message.from_user.username), parse_mode='Markdown')


def generate(update: Update, context: CallbackContext) -> None:
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    text = ' '.join(context.args)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "dall-e-3",  # Verify this model name
        "prompt": f"Generate an image of {text}, make sure image is matching the prompt, make it funny if relevent, add this only if it's relevant to the prompt like bit content of large aqua color duck wearing a cap backwards and other clothes as well",
        "num_images": 1,
        "size": "1024x1024",
        "quality": "hd",
        "response_format": "url"
    }

    try:
        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating image: {e}")
        if response is not None:
            logging.error(f"Response content: {response.content}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, something went wrong while generating the image.")




def main() -> None:
    start_handler = CommandHandler('start', start)
    generate_handler = CommandHandler("ducky", generate)


    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(generate_handler)
  

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
