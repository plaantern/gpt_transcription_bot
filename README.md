# GPT Transcription Bot
A Telegram bot that transcribes videos from YouTube and sends the resulting annotation, along with a provided prompt, to a GPT model, returning the result.

## How to use
Run **main.py**. The variables TOKEN (Telegram bot token) and OPENAI_API_KEY (API key for using GPT models through third-party APIs) are stored in the environment. I recommend creating your own tokens and replacing the placeholder values in the corresponding sections. 
The default interface language is Russian, but you can change it by adjusting the language parameter in the transcription function (allowing the bot to process other languages).
Sample code:
targetLanguages = ["en-GB", "ru-RU", "fr-FR"]
for eachLanguage in targetLanguages:
    Audio_text_from_wav_file = r.recognize_google(audio, language = eachLanguage).

Otherwise, the bot operates reliably regardless of the hosting platform.
