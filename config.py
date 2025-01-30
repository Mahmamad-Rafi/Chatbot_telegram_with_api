from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the values from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')


# Debugging print (Remove this after checking)
print(f"TOKEN: {TOKEN[:10]}**********" if TOKEN else "TOKEN not found!")
print(f"MONGO_URI: {MONGO_URI[:20]}**********" if MONGO_URI else "MONGO_URI not found!")
print(f"GEMINI_API_KEY: {GEMINI_API_KEY[:10]}**********" if GEMINI_API_KEY else "GEMINI_API_KEY not found!")
print(f"SERPAPI_KEY: {SERPAPI_KEY[:10]}**********" if SERPAPI_KEY else "SERPAPI_KEY not found!")
