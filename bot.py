import requests
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext

# Venice AI API configuration
VENICE_API_URL = "https://api.venice.ai/api/v1/chat/completions"
VENICE_API_HEADERS = {
    "Authorization": "Bearer GULAu2whg71dI5dCWiZGFp-Cb6ay_P0-ViTcGeiAUX",
    "Content-Type": "application/json"
}

# Define the system message
SYSTEM_MESSAGE = (
    "Welcome to PriceGenie, your ultimate assistant for navigating the crypto market! "
    "You specialize in providing real-time market insights, predictive analytics, and actionable advice for cryptocurrencies. "
    "Leverage advanced AI and analytics to help users understand market trends, volatility, and future price predictions. "
    "Always respond professionally, with clear insights tailored for crypto traders and investors."
)

# Function to handle the /ask command
def ask_command(update: Update, context: CallbackContext) -> None:
    # Check if the user provided a query
    if not context.args:
        update.message.reply_text("Please provide a query after the /ask command. Example: /ask What is the BTC trend?")
        return

    # Join the query arguments into a single string
    user_message = " ".join(context.args)

    # Send "typing" action while processing the query
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # Prepare the payload for the Venice AI API
    payload = {
        "model": "llama-3.1-405b",
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_message}
        ]
    }

    # Send request to Venice API
    try:
        response = requests.post(VENICE_API_URL, json=payload, headers=VENICE_API_HEADERS)

        if response.status_code == 200:
            # Get the AI's response
            reply = response.json().get("choices")[0].get("message").get("content")
            # Send the response to the user
            update.message.reply_text(f"PriceGenie (Crypto): {reply}")
            
        else:
            update.message.reply_text(
                f"Error: Unable to fetch a response from PriceGenie. "
                f"Status Code: {response.status_code}"
            )
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Hello! I'm PriceGenie, your crypto market assistant.\n"
        "Use the /ask command followed by your query to get insights. Example:\n"
        "/ask What is future of sol?"
    )

# Main function to start the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you got from BotFather
    TELEGRAM_BOT_TOKEN = "7936190562:AAEhmPmBWQCsWS3vGejiU9LVsbsi6RVJxn4"

    # Set up the Updater and Dispatcher
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ask", ask_command))

    # Start the bot
    print("PriceGenie Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
