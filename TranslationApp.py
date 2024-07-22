import asyncio
import os
from googletrans import Translator, LANGUAGES
import speech_recognition as sr
from gtts import gTTS
import pygame
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from dotenv import load_dotenv

class TranslationApp:
    def __init__(self):
        self.setup()
        self.create_ui()

    def setup(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize translation library
        self.translator = Translator()
        
        # Set up speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize logging
        logging.basicConfig(filename='translation_log.txt', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # Initialize pygame for audio playback
        pygame.mixer.init()

        # Check if pyaudio is available
        try:
            import pyaudio
            self.speech_input_available = True
        except ImportError:
            self.speech_input_available = False
            logging.warning("pyaudio not found. Speech input will be disabled.")

    def create_ui(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("Advanced Translation App")
        self.root.geometry("500x600")

        # Create and place UI elements
        self.input_frame = ttk.LabelFrame(self.root, text="Input")
        self.input_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.input_text = tk.Text(self.input_frame, height=5, width=50)
        self.input_text.pack(pady=10, padx=10, fill="both", expand=True)

        if self.speech_input_available:
            self.speak_input_button = ttk.Button(self.input_frame, text="Speak Input", command=self.speak_input)
            self.speak_input_button.pack(pady=5)

        self.lang_frame = ttk.Frame(self.root)
        self.lang_frame.pack(padx=10, pady=5, fill="x")

        self.source_lang_label = ttk.Label(self.lang_frame, text="Source Language:")
        self.source_lang_label.grid(row=0, column=0, padx=5, pady=5)

        self.source_lang = ttk.Combobox(self.lang_frame, values=["auto"] + list(LANGUAGES.values()), state="readonly")
        self.source_lang.grid(row=0, column=1, padx=5, pady=5)
        self.source_lang.set("auto")

        self.target_lang_label = ttk.Label(self.lang_frame, text="Target Language:")
        self.target_lang_label.grid(row=1, column=0, padx=5, pady=5)

        self.target_lang = ttk.Combobox(self.lang_frame, values=list(LANGUAGES.values()), state="readonly")
        self.target_lang.grid(row=1, column=1, padx=5, pady=5)
        self.target_lang.set("English")

        self.translate_button = ttk.Button(self.root, text="Translate", command=self.run_translation)
        self.translate_button.pack(pady=10)

        self.output_frame = ttk.LabelFrame(self.root, text="Output")
        self.output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.output_text = tk.Text(self.output_frame, height=5, width=50)
        self.output_text.pack(pady=10, padx=10, fill="both", expand=True)

        self.speak_output_button = ttk.Button(self.output_frame, text="Speak Translation", command=self.speak_translation)
        self.speak_output_button.pack(pady=5)

    def run_translation(self):
        asyncio.run(self.translate())

    async def translate(self):
        input_text = self.input_text.get("1.0", tk.END).strip()
        target_lang = self.get_language_code(self.target_lang.get())
        source_lang = self.get_language_code(self.source_lang.get())

        if not input_text:
            messagebox.showwarning("Warning", "Please enter text to translate.")
            return

        if not target_lang:
            messagebox.showwarning("Warning", "Please select a valid target language.")
            return

        try:
            start_time = asyncio.get_event_loop().time()

            # Detect source language if set to auto
            if source_lang == "auto":
                detected_lang = self.translator.detect(input_text).lang
            else:
                detected_lang = source_lang

            # Translate text
            translation = self.translator.translate(input_text, src=detected_lang, dest=target_lang).text

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translation)

            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            # Log the translation
            logging.info(f"Translation from {detected_lang} to {target_lang} took {duration:.2f} seconds")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during translation: {str(e)}")
            logging.error(f"Translation error: {str(e)}")

    def speak_input(self):
        if not self.speech_input_available:
            messagebox.showwarning("Warning", "Speech input is not available. Please install pyaudio.")
            return

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, text)
        except sr.UnknownValueError:
            messagebox.showwarning("Warning", "Could not understand audio")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results from speech recognition service; {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during speech recognition: {str(e)}")
            logging.error(f"Speech recognition error: {str(e)}")

    def speak_translation(self):
        translation = self.output_text.get("1.0", tk.END).strip()
        target_lang = self.get_language_code(self.target_lang.get())

        if not translation:
            messagebox.showwarning("Warning", "No translation to speak.")
            return

        if not target_lang:
            messagebox.showwarning("Warning", "Invalid target language for text-to-speech.")
            return

        try:
            # Convert text to speech
            tts = gTTS(text=translation, lang=target_lang)
            tts.save("translation.mp3")

            # Play the audio
            pygame.mixer.music.load("translation.mp3")
            pygame.mixer.music.play()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during text-to-speech: {str(e)}")
            logging.error(f"Text-to-speech error: {str(e)}")

    def get_language_code(self, language_name):
        if language_name is None:
            return None
        if language_name.lower() == "auto":
            return "auto"
        return next((code for code, name in LANGUAGES.items() if name.lower() == language_name.lower()), None)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TranslationApp()
    app.run()