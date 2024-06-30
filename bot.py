import logging
import re
import datetime
import openai
import requests
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "7265715640:AAH48RzO321z3_Ks_9DwDYnuDZRLmbanh6E"
OPENAI_API_KEY = "sk-proj-DZ27T8Y3jFpSWDlbKBAiT3BlbkFJZnVFtUnUaDoQLFbIKwSn"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

openai.api_key = OPENAI_API_KEY

chat_history = {}


def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="👋 *Greetings human,* @{}!\n\n🤖 * I'm MonsterBrains AI bot. What can I do to assist you:*\n\n"
                                  "- */ask:* Chat w/AI bot trained on your data/content.\n"
                                  "  E.g., `/ask can you write me a article about the moon`\n"
                                  "- */price:* Get realtime crypto prices. E.g., `/price btc`\n"
                                  "*Coming soon:*\n"
                                  "- */fetch:* Fetch live crypto stats.\n"
                                  "  E.g., `/fetch $MONSTER`\n"
                                  "- */generate:* Generate HD quality images.\n"
                                  "  E.g., `/generate AI robots planning an invasion`\n"
                                  "- */moon:* Detect most trending projects on different blockchain.\n"
                                  "  E.g., `/monster project under $1 million market cap on BASE Chain`\n\n"
                                  "Reply directly to messages with commands or directly chat on group chat."
                             .format(update.message.from_user.username), parse_mode='Markdown')


def ask(update, context):
    chat_id = str(update.message.chat_id)

    user_message = update.message.text[5:].strip()  # Remove "/ask " from the message

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    # Add user's message to chat history
    chat_history[chat_id].append(user_message)

    # Truncate chat history
    MAX_MESSAGES = 50
    if len(chat_history[chat_id]) > MAX_MESSAGES:
        chat_history[chat_id] = chat_history[chat_id][-MAX_MESSAGES:]

    conversation = "\n".join(chat_history[chat_id])

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # Updated model name
        prompt=f"As the MonsterBrains AI BOT, a crypto companion, belonging to MonsterBrains project, Monster Brains is a crypto project Matt Furie performed a fantastic job using his singularly weird creatures to illustrate the Monster Brains theme. Here, we honor him with this coin and express our gratitude for his artwork!, answer this in a funny way:\n{conversation}\n",
        max_tokens=128,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0].text

    # Add the bot's response to chat history
    chat_history[chat_id].append(response)

    # Send the bot's response
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

def generate(update: Update, context: CallbackContext) -> None:
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    text = ' '.join(context.args)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "image-alpha-001",
        "prompt": f"Generate an image of {text}",
        "num_images": 1,
        "size": "256x256",
        "response_format": "url"
    }

    try:
        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, something went wrong while generating the image.")
    
def crypto_price(update, context):
    crypto_symbol = update.message.text[7:].strip().upper()  # Extract the cryptocurrency symbol from the message

    try:
        # Fetch cryptocurrency price from CryptoCompare API
        url = f"https://min-api.cryptocompare.com/data/price?fsym={crypto_symbol}&tsyms=USD"
        response = requests.get(url)
        data = response.json()

        if 'USD' in data:
            price = data['USD']
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"The current price of {crypto_symbol} is {price} USD.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Could not find price information for {crypto_symbol}.")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


def welcome_message(update: Update, context: CallbackContext) -> None:
    new_members = update.message.new_chat_members
    for new_member in new_members:
        start(update, context)  # Calling start function to send the welcome message


def main() -> None:
    start_handler = CommandHandler('start', start)
    ask_handler = CommandHandler('ask', ask)
    crypto_price_handler = CommandHandler('price', crypto_price)
    generate_handler = CommandHandler("generate", generate)
    new_members_handler = MessageHandler(Filters.status_update.new_chat_members, welcome_message)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ask_handler)
    dispatcher.add_handler(crypto_price_handler)
    dispatcher.add_handler(generate_handler)
    dispatcher.add_handler(new_members_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
