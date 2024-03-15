import logging
import re
import datetime
import openai
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "6718784818:AAG_seZy5ahVlyAsvtmvNM6rUBv6DbNYml8"
OPENAI_API_KEY = "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"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

openai.api_key = OPENAI_API_KEY

chat_history = {}


def start(update: Update, context: CallbackContext) -> None:
    text = (
    "👋 *Greetings human,* @{}!\n\n🤖 *What can I do to assist you:*\n\n"
    "- */ask:* Chat w/AI bot trained on your data/content.\n"
    "  E.g., `/ask can you write me a article about the moon`\n"
    "- */price:* Get realtime crypto prices. "
    "  E.g., `/price btc`\n"
    "*Coming soon:*\n"
    "- */fetch:* Fetch live crypto stats.\n"
    "  E.g., `/fetch $MoonAI`\n"
    "- */generate:* Generate HD quality images.\n"
    "  E.g., `/generate AI robots planning an invasion`\n"
    "- */moon:* Detect most trending projects on different blockchain.\n"
    "  E.g., `/moon project under $1 million market cap on Ethereum`\n\n"
    "Reply directly to messages with commands or directly chat on group chat."
)

context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(update.message.from_user.username), parse_mode='Markdown')


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
        prompt=f"As the MoonShot AI BOT, a crypto companion, answer this in a funny way:\n{conversation}\n",
        max_tokens=128,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0].text

    # Add the bot's response to chat history
    chat_history[chat_id].append(response)

    # Send the bot's response
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


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


def main():
    start_handler = CommandHandler('start', start)
    ask_handler = CommandHandler('ask', ask)
    crypto_price_handler = CommandHandler('price', crypto_price)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ask_handler)
    dispatcher.add_handler(crypto_price_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
