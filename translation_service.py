import os
from googletrans import Translator, LANGUAGES
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify

app = Flask(__name__)
load_dotenv()

# Initialize translation library
translator = Translator()

# Set up speech recognition
recognizer = sr.Recognizer()

# Initialize logging
logging.basicConfig(filename='translation_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_language_code(language_name):
    if language_name is None:
        return None
    if language_name.lower() == "auto":
        return "auto"
    return next((code for code, name in LANGUAGES.items() if name.lower() == language_name.lower()), None)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    input_text = data.get('text')
    source_lang = get_language_code(data.get('source_lang', 'auto'))
    target_lang = get_language_code(data.get('target_lang'))

    if not input_text or not target_lang:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        if source_lang == "auto":
            detected_lang = translator.detect(input_text).lang
        else:
            detected_lang = source_lang

        translation = translator.translate(input_text, src=detected_lang, dest=target_lang).text
        return jsonify({'translation': translation, 'source_lang': detected_lang, 'target_lang': target_lang})

    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        audio = AudioSegment.from_file(file)
        audio.export("temp.wav", format="wav")

        with sr.AudioFile("temp.wav") as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        os.remove("temp.wav")
        return jsonify({'text': text})

    except Exception as e:
        logging.error(f"Speech recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.json
    translation = data.get('translation')
    target_lang = get_language_code(data.get('target_lang'))

    if not translation or not target_lang:
        return jsonify({'error': 'Invalid input'}), 400

    try:
        tts = gTTS(text=translation, lang=target_lang)
        tts.save("translation.mp3")
        return jsonify({'audio_file': 'translation.mp3'})

    except Exception as e:
        logging.error(f"Text-to-speech error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
