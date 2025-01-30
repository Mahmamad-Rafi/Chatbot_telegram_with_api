import google.generativeai as genai
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from config import TOKEN, GEMINI_API_KEY, SERPAPI_KEY
from mongo_db import save_user_info, check_user_exists, store_phone_number, save_chat, save_file_info
from file_processing import process_image, process_pdf, summarize_text, analyze_sentiment, translate_text
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Gemini AI with the Gemini API Key from .env
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-pro")

# Start Command
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat_id = update.message.chat_id

    if check_user_exists(chat_id):
        await update.message.reply_text("You're already registered! 😊")
    else:
        save_user_info(chat_id, user.first_name, user.username)
        phone_request = KeyboardButton("📲 Share Phone Number", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[phone_request]], one_time_keyboard=True)
        await update.message.reply_text("Please share your phone number to continue. 📞", reply_markup=keyboard)

# Process Phone Number
async def process_contact(update: Update, context: CallbackContext) -> None:
    phone_number = update.message.contact.phone_number
    chat_id = update.message.chat_id
    store_phone_number(chat_id, phone_number)
    await update.message.reply_text("✅ Registration complete! Type your queries anytime.")

# Web Search Command
async def web_search(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("🔍 Please enter your search query:")
    return "WAIT_FOR_SEARCH_QUERY"

# Handle the search query from user
async def handle_search_query(update: Update, context: CallbackContext) -> None:
    query = update.message.text
    chat_id = update.message.chat_id

    # Send a request to SerpAPI (or any other search API) to get search results
    try:
        search_results = perform_web_search(query)

        if search_results:
            summary, links = summarize_search_results(search_results)
            response = f"🔎 **Top search results for:** {query}\n\n**Summary:**\n{summary}\n\n**Top Links:**\n" + "\n".join(links)
        else:
            response = "⚠ No relevant search results found. Please try again later."

    except Exception as e:
        response = f"❌ Error while searching: {e}"

    # Save chat history
    save_chat(chat_id, query, response)

    await update.message.reply_text(response)

# Perform web search using SerpAPI or another API
def perform_web_search(query):
    url = f"https://serpapi.com/search?q={query}&api_key={SERPAPI_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get("organic_results", [])
    else:
        raise Exception("Failed to fetch search results")

# Summarize search results and return the top links
def summarize_search_results(results):
    summary = "Here is a brief summary of the search results:"
    links = []

    for result in results[:5]:  # Limiting to top 5 results
        title = result.get("title", "No title")
        snippet = result.get("snippet", "No description")
        link = result.get("link", "No link")
        summary += f"\n\n**{title}:** {snippet}"
        links.append(link)

    return summary, links

# Initialize Bot
app = Application.builder().token(TOKEN).build()

# Register Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.CONTACT, process_contact))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_query))
app.add_handler(CommandHandler("websearch", web_search))

# Start Bot
if __name__ == "__main__":
    print("🚀 Bot is running!")
    app.run_polling()