# Importing Modules and Initial Setup (tokens, initialization, etc.)
import os
import yt_dlp
import telebot
import nest_asyncio
import openai
import logging
from pydub import AudioSegment
import speech_recognition as sr

nest_asyncio.apply()

# Getting Environment Variables
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Setting Up Logging
telebot.logger.setLevel(logging.INFO)

# Initializing the Bot and OpenAI Client
bot = telebot.TeleBot(TOKEN, threaded=False)
openai.api_key = OPENAI_API_KEY



#Functions Block

# Function for Processing and Uploading Video
def download_video(video_url, output_path='video.mp4'):
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': output_path,
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

# Function for Extracting Audio from Video
def extract_audio_from_video(video_path, audio_path='audio.wav'):
    video = AudioSegment.from_file(video_path)
    video.export(audio_path, format='wav')

# Function for Transcribing Audio
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language="ru-RU")

# Function for Sending a Request to GPT-3.5
def send_to_gpt(prompt, transcript):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Ты - помощник."},
            {"role": "user", "content": f"{transcript}\n\n{prompt}"}])
    return response.choices[0].message.content





# User Message Handlers Block


# Handler for /start and /help Commands
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Hi! I'm GPT-powered bot. Send me a YouTube video link, I will transcribe it and also process the resulting text using GPT-3.5.")

# Handler for Receiving a Video Link
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def handle_video_link(message):
    url = message.text
    bot.reply_to(message, "Starting video processing...")
    download_video(url)
    extract_audio_from_video('video.mp4')
    bot.reply_to(message, "Trancribing audio...")
    transcript = transcribe_audio('audio.wav')
    bot.reply_to(message, f"Transcription:\n{transcript}")
    bot.reply_to(message, "Now send me the prompt for GPT that you want to use.")
    bot.transcripts[message.chat.id] = transcript

# Handler for Receiving the Prompt and Sending the Request to GPT
@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_prompt(message):
    transcript = bot.transcripts.get(message.chat.id)
    if transcript:
        prompt = message.text
        bot.reply_to(message, "Sending the request to GPT...")
        gpt_response = send_to_gpt(prompt, transcript)
        bot.reply_to(message, f"Response from GPT:\n{gpt_response}")
        bot.transcripts.pop(message.chat.id, None)
    else:
        bot.reply_to(message, "Please, send a link to the video first")

if __name__ == '__main__':
    bot.transcripts = {}
    bot.polling(none_stop=True)
