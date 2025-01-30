from telegram import Update
from telegram.ext import ContextTypes
from gemini_api import query_gemini

async def gemini_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and respond using Gemini AI."""
    user_input = update.message.text
    response = query_gemini(user_input)

    await update.message.reply_text(response)