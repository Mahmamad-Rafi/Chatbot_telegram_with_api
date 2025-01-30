import cv2
import pytesseract
from PIL import Image
import PyPDF2
import numpy as np
from pdf2image import convert_from_path
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from textblob import TextBlob
from googletrans import Translator
import google.generativeai as genai
import os
import datetime

# Initialize the Google Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your Gemini API key
gemini_model = genai.GenerativeModel("gemini-pro")

# Initialize Translator
translator = Translator()

# Function to process image files (OCR)
def process_image(image_path):
    try:
        # Load the image using OpenCV
        img = cv2.imread(image_path)
        
        # Convert to grayscale for better OCR accuracy
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to enhance text for OCR
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(gray)
        
        # Use Gemini to describe the content of the image (using generative AI model)
        image_description = describe_image_with_gemini(image_path)
        
        return text.strip(), image_description
    except Exception as e:
        return f"Error processing image: {e}"

# Function to process PDF files
def process_pdf(pdf_path):
    try:
        text = ""
        
        # First, try extracting text from the PDF using PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        
        # If text extraction failed, convert PDF pages to images and extract text from them
        if not text.strip():
            images = convert_from_path(pdf_path)
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
        
        # Use Gemini to describe the content of the PDF (using generative AI model)
        pdf_description = describe_pdf_with_gemini(pdf_path)
        
        return text.strip(), pdf_description
    except Exception as e:
        return f"Error processing PDF: {e}"

# Function to summarize text
def summarize_text(text, num_sentences=3):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, num_sentences)
        return " ".join(str(sentence) for sentence in summary)
    except Exception as e:
        return f"Error summarizing text: {e}"

# Function for sentiment analysis
def analyze_sentiment(text):
    try:
        analysis = TextBlob(text)
        sentiment_score = analysis.sentiment.polarity
        if sentiment_score > 0:
            return "Positive 😊"
        elif sentiment_score < 0:
            return "Negative 😞"
        else:
            return "Neutral 😐"
    except Exception as e:
        return f"Error analyzing sentiment: {e}"

# Function for text translation
def translate_text(text, target_lang="en"):
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception as e:
        return f"Error translating text: {e}"

# Function to describe an image using Google Gemini API
def describe_image_with_gemini(image_path):
    try:
        # Read the image and send it to Gemini for description
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
        
        # Send the image content to Gemini for analysis and description
        response = gemini_model.generate(
            text="Describe the content of this image.", 
            input=image_content
        )
        return response.text
    except Exception as e:
        return f"Error describing image with Gemini: {e}"

# Function to describe a PDF using Google Gemini API
def describe_pdf_with_gemini(pdf_path):
    try:
        # Read the PDF content and send it to Gemini for description
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        # Send the PDF content to Gemini for analysis and description
        response = gemini_model.generate(
            text="Summarize the content of this PDF document.", 
            input=pdf_content
        )
        return response.text
    except Exception as e:
        return f"Error describing PDF with Gemini: {e}"

# Example usage
if __name__ == "__main__":
    # Example for image processing (OCR and Gemini description)
    image_text, image_description = process_image('example_image.jpg')
    print("Extracted Text from Image:", image_text)
    print("Gemini Image Description:", image_description)

    # Example for PDF processing (text extraction and Gemini description)
    pdf_text, pdf_description = process_pdf('example_document.pdf')
    print("\nExtracted Text from PDF:", pdf_text)
    print("Gemini PDF Description:", pdf_description)

    if pdf_text:
        # Summarize the text extracted from PDF
        summary = summarize_text(pdf_text, num_sentences=5)
        print("\nSummary of PDF:", summary)

        # Perform sentiment analysis
        sentiment = analyze_sentiment(pdf_text)
        print("\nSentiment Analysis:", sentiment)

        # Translate extracted text from PDF (Example: translate to Spanish)
        translated_text = translate_text(pdf_text, "es")
        print("\nTranslated Text (Spanish):", translated_text)
