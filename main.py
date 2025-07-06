
import telebot
import os
import dotenv
import re
from function.youtube_summarizer import get_video_transcript, summarize_text
from function.your_custom_bot import generate_response
from function.chat2 import chatmodel
from function.res import findlink
from function.qna import doc_qna, chatpdf_chat

# Load environment variables
dotenv.load_dotenv()
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
api_key = os.getenv("CHATPDF_API")

# Define states
STATE_NONE = 0
STATE_WAITING_FOR_RESOURCE = 1
STATE_WAITING_FOR_PDF = 2
STATE_WAITING_FOR_MORE_QUERY = 3
STATE_WAITING_FOR_YOUTUBE_SUMMARY = 4

user_state = STATE_NONE
sourceID = None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """Hello there! I'm NOVA, your personal academic assistant. I can help you with various tasks, including:
# ⁕ Answering your questions on diverse academic topics.
# ⁕ Searching for relevant study materials, articles, and other resources.
# ⁕ Answering your questions directly within uploaded PDF documents.
# ⁕ Summarizing YouTube videos.
# **Just ask me anything!** You can chat with me like you would a friend, or use specific commands for certain functionalities. 
# For more info, click here "/help".""")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, """Hey! Looking for some guidance? Here's how you can use me:
# ⁕ Chat & Ask Questions: Type your queries as you normally would, and I'll do my best to provide helpful answers.
# ⁕ Find Resources: Need articles, books, or other materials? Use the command "/resource".
# ⁕ Ask Questions about PDFs: Upload a PDF and ask your questions directly within the document. Use the command "/pdf_qna"
# ⁕ Summarize YouTube Videos: Send a YouTube video link, and I'll summarize it for you. Use the command "/youtube_summary".
# ⁕ I'm still under development, but I'm learning every day! Feel free to ask anything, and if I can't answer, I'll let you know.""")

@bot.message_handler(commands=['resource'])
def resource(message):
    global user_state
    bot.reply_to(message, "Enter your query to find resource links.")
    user_state = STATE_WAITING_FOR_RESOURCE

@bot.message_handler(commands=['pdf_qna'])
def pdf_qna(message):
    global user_state
    bot.reply_to(message, "Send your file.")
    user_state = STATE_WAITING_FOR_PDF

@bot.message_handler(commands=['youtube_summary'])
def youtube_summary(message):
    global user_state
    bot.reply_to(message, "Send a YouTube video link for summarization.")
    user_state = STATE_WAITING_FOR_YOUTUBE_SUMMARY

@bot.message_handler(content_types=['document'])
def docs(message):
    global user_state, sourceID
    bot.send_message(message.chat.id, f"{message.document.file_name} received. Processing...")
    if user_state == STATE_WAITING_FOR_PDF:
        sourceID = doc_qna(bot.token, message.document.file_id, message.document.file_name, api_key)
        if sourceID:
            bot.send_message(message.chat.id, "Ask questions about the file. Type 'stop' to finish.")
            user_state = STATE_WAITING_FOR_MORE_QUERY
        else:
            bot.reply_to(message, "Failed to process the file. Try again.")
            user_state = STATE_NONE

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    Supports both long (`youtube.com/watch?v=...`) and short (`youtu.be/...`) formats.
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    global user_state, sourceID
    
    if user_state == STATE_WAITING_FOR_RESOURCE:
        bot.reply_to(message, findlink(message.text) or "No resource found.")
        user_state = STATE_NONE
    
    elif user_state == STATE_WAITING_FOR_MORE_QUERY:
        if message.text.lower() == "stop":
            bot.reply_to(message, "Goodbye!")
            user_state = STATE_NONE
        else:
            bot.reply_to(message, chatpdf_chat(api_key, message.text, sourceID))
            bot.send_message(message.chat.id, "Another question? (Type 'stop' to finish)")
    
    elif user_state == STATE_WAITING_FOR_YOUTUBE_SUMMARY:
        bot.reply_to(message, "Validating link...")
        video_id = extract_video_id(message.text)

        if not video_id:
            bot.reply_to(message, "Invalid YouTube link! Please send a valid video URL.")
            user_state = STATE_NONE
            return

        transcript = get_video_transcript(video_id)

        if transcript.startswith("Error fetching transcript"):
            bot.reply_to(message, transcript)  # Return actual error message
            user_state = STATE_NONE
            return

        bot.reply_to(message, "Summarizing... ⏳")  # Show summarizing message
        summary = summarize_text(transcript)

        if summary.startswith("Error summarizing text"):
            bot.reply_to(message, summary)  # Handle summarization errors
        else:
            bot.reply_to(message, f"📌 **Summary:**\n{summary}")

        user_state = STATE_NONE
    
    else:
        bot.reply_to(message, generate_response(message.text) or chatmodel(message.text))

print("Bot is running...")
bot.polling()
