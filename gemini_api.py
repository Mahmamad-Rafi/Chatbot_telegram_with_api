import google.generativeai as gemini
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Set up Gemini AI
gemini.configure(api_key=API_KEY)

def ask_gemini(query):
    """Interact with Gemini AI and retrieve a response."""
    try:
        ai_model = gemini.GenerativeModel("gemini-pro")  # Initialize model
        result = ai_model.generate_content(query)  # Generate response
        return result.text if result else "No response received."
    except Exception as error:
        return f"⚠ Something went wrong: {error}"