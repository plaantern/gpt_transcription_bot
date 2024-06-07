# Импортирование модулей и первичная настройка (токены, инициализация и тд)
import os
import yt_dlp
import telebot
import nest_asyncio
import openai
import logging
from pydub import AudioSegment
import speech_recognition as sr

nest_asyncio.apply()

# Получение переменных окружения
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Настройка логирования
telebot.logger.setLevel(logging.INFO)

# Инициализация бота и OpenAI клиента
bot = telebot.TeleBot(TOKEN, threaded=False)
openai.api_key = OPENAI_API_KEY



#Блок функций

# Функция для обработки и загрузки видео
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

# Функция для извлечения аудио из видео
def extract_audio_from_video(video_path, audio_path='audio.wav'):
    video = AudioSegment.from_file(video_path)
    video.export(audio_path, format='wav')

# Функция для транскрибирования аудио
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language="ru-RU")

# Функция для отправки запроса в GPT-4
def send_to_gpt(prompt, transcript):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Ты - помощник."},
            {"role": "user", "content": f"{transcript}\n\n{prompt}"}])
    return response.choices[0].message.content





# Блок обработчиков пользовательских сообщений


# Обработчик команды /start и /help
@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я ChatGPT бот. Отправь мне ссылку на видео с YouTube, я его транскрибирую, а также обработаю полученный текст с помощью GPT-3.5.")

# Обработчик для получения ссылки на видео
@bot.message_handler(func=lambda message: message.text.startswith("http"))
def handle_video_link(message):
    url = message.text
    bot.reply_to(message, "Начинаю обработку видео...")
    download_video(url)
    extract_audio_from_video('video.mp4')
    bot.reply_to(message, "Транскрибирую аудио...")
    transcript = transcribe_audio('audio.wav')
    bot.reply_to(message, f"Транскрипция:\n{transcript}")
    bot.reply_to(message, "Теперь отправьте мне промпт для ChatGPT, который вы хотите использовать.")
    bot.transcripts[message.chat.id] = transcript

# Обработчик для получения промпта и отправки запроса в GPT
@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_prompt(message):
    transcript = bot.transcripts.get(message.chat.id)
    if transcript:
        prompt = message.text
        bot.reply_to(message, "Отправляю запрос в ChatGPT...")
        gpt_response = send_to_gpt(prompt, transcript)
        bot.reply_to(message, f"Результат от ChatGPT:\n{gpt_response}")
        bot.transcripts.pop(message.chat.id, None)
    else:
        bot.reply_to(message, "Пожалуйста, сначала отправьте ссылку на видео.")

if __name__ == '__main__':
    bot.transcripts = {}
    bot.polling(none_stop=True)
