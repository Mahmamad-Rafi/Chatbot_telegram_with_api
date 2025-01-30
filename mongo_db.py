from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI
import base64
from bson.binary import Binary

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['telegram_bot']
users = db['users']
chat_history = db['chat_history']
files = db['files']

# Save user info
def save_user_info(chat_id, first_name, username):
    if users.find_one({'chat_id': chat_id}):
        return False  # User already exists
    user_data = {'chat_id': chat_id, 'first_name': first_name, 'username': username}
    users.insert_one(user_data)
    return True

# Check if user exists
def check_user_exists(chat_id):
    return users.find_one({'chat_id': chat_id}) is not None

# Store phone number
def store_phone_number(chat_id, phone_number):
    users.update_one({'chat_id': chat_id}, {'$set': {'phone_number': phone_number}}, upsert=True)

# Save chat history
def save_chat(chat_id, user_input, bot_response):
    chat_data = {
        'chat_id': chat_id,
        'user_input': user_input,
        'bot_response': bot_response,
        'timestamp': datetime.utcnow()
    }
    chat_history.insert_one(chat_data)

# Save file metadata and file content (images,  etc.)
def save_file_info(chat_id, file_name, description, file_data=None):
    file_metadata = {
        'chat_id': chat_id,
        'file_name': file_name,
        'description': description,
        'timestamp': datetime.utcnow()
    }

    # If there is file data (for example, an image or document), store it as Binary data
    if file_data:
        file_metadata['file_data'] = Binary(file_data)  # Store binary data (image, PDF, etc.)

    files.insert_one(file_metadata)

# Function to save image as binary
def save_image(chat_id, file_name, image_path):
    try:
        with open(image_path, 'rb') as image_file:
            file_data = image_file.read()
        save_file_info(chat_id, file_name, "Image file", file_data)
        return "Image saved successfully!"
    except Exception as e:
        return f"Error saving image: {e}"

# Function to save PDF as binary
def save_pdf(chat_id, file_name, pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            file_data = pdf_file.read()
        save_file_info(chat_id, file_name, "PDF file", file_data)
        return "PDF saved successfully!"
    except Exception as e:
        return f"Error saving PDF: {e}"

# Function to fetch a file by file_id
def get_file_by_id(file_id):
    file = files.find_one({'_id': file_id})
    if file:
        return file
    return None

# Function to fetch all files for a user
def get_files_by_user(chat_id):
    return list(files.find({'chat_id': chat_id}))

# Function to convert file binary to proper format (for display or further processing)
def convert_binary_to_file(binary_data, file_name):
    try:
        with open(file_name, 'wb') as f:
            f.write(binary_data)
        return f"{file_name} saved successfully."
    except Exception as e:
        return f"Error saving file: {e}"

# Example usage of the functions
if __name__ == "__main__":
    # Example to save image as binary
    print(save_image(12345, 'example_image.jpg', 'path_to_image.jpg'))
    
    # Example to save PDF as binary
    print(save_pdf(12345, 'example_document.pdf', 'path_to_pdf.pdf'))
    
    # Example to get files for a user
    files_for_user = get_files_by_user(12345)
    print(files_for_user)

    # Example to retrieve and save a file from binary data
    file_data = get_file_by_id("file_id_here")  # Example file ID
    if file_data:
        print(convert_binary_to_file(file_data['file_data'], "retrieved_file.pdf"))
