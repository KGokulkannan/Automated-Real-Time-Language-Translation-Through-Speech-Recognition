import os
import tempfile
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import Translator
import pyperclip  # For clipboard functionality

# Initialize translator and mixer
translator = Translator()
pygame.mixer.init()

# Language mapping
language_mapping = {
    "Tamil": "ta",
    "English": "en",
    "Malayalam": "ml",
    "Telugu": "te",
    "Kannada": "kn",
    "hindi" : "hi"
}

def get_language_code(language_name):
    return language_mapping.get(language_name)

def translator_function(spoken_text, from_language, to_language):
    translation = translator.translate(spoken_text, src=from_language, dest=to_language)
    return translation.text

def text_to_voice(text_data, to_language):
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        audio_path = tmp_file.name
        myobj.save(audio_path)

    # Play audio using pygame
    audio = pygame.mixer.Sound(audio_path)
    audio.play()
    pygame.time.wait(int(audio.get_length() * 1000))  # Wait for audio to finish
    os.remove(audio_path)

def speech_to_text(from_language):
    rec = sr.Recognizer()
    with sr.Microphone() as source:
        st.text("Listening...")
        rec.pause_threshold = 1
        try:
            audio = rec.listen(source, phrase_time_limit=10)
            spoken_text = rec.recognize_google(audio, language=from_language)
            return spoken_text
        except sr.UnknownValueError:
            st.error("Could not understand audio")
            return None
        except sr.RequestError:
            st.error("Error with the speech recognition service")
            return None

# Function to copy text to clipboard
def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        st.success("Text copied to clipboard!")
    except Exception as e:
        st.error(f"Failed to copy to clipboard: {e}")

def main_process(output_placeholder, from_language, to_language, mode):
    translated_text = ""

    if mode == "Speech-to-Speech":
        try:
            spoken_text = speech_to_text(from_language)
            if spoken_text:
                output_placeholder.text(f"Detected Speech: {spoken_text}")
                translated_text = translator_function(spoken_text, from_language, to_language)
                output_placeholder.text(f"Translated Text: {translated_text}")
                # Play sound after translation is done
                text_to_voice(translated_text, to_language)
        except Exception as e:
            output_placeholder.text(f"Error: {e}")

    elif mode == "Text-to-Text":
        input_text = st.text_input("Enter text to translate:")
        if input_text:
            translated_text = translator_function(input_text, from_language, to_language)
            output_placeholder.text(f"Translated Text: {translated_text}")

    elif mode == "Text-to-Speech":
        input_text = st.text_input("Enter text to translate and speak:")
        if input_text:
            translated_text = translator_function(input_text, from_language, to_language)
            output_placeholder.text(f"Translated Text: {translated_text}")
            # Play sound after translation is done
            text_to_voice(translated_text, to_language)

    elif mode == "Speech-to-Text":
        try:
            spoken_text = speech_to_text(from_language)
            if spoken_text:
                output_placeholder.text(f"Detected Speech: {spoken_text}")
                translated_text = translator_function(spoken_text, from_language, to_language)
                output_placeholder.text(f"Translated Text: {translated_text}")
        except Exception as e:
            output_placeholder.text(f"Error: {e}")

    # Show the Copy button and copy the translated text to clipboard
    if translated_text:
        st.text_area("Translated Text:", value=translated_text, height=150, key="translation_output")
        if st.button("Copy Output", key="copy_button"):
            # Only copy text; do not play audio here
            copy_to_clipboard(translated_text)

# Initialize session state for controlling start/stop
if 'is_translate_on' not in st.session_state:
    st.session_state.is_translate_on = False

# UI layout
st.title("Language Translator")

# Dropdowns for selecting languages
from_language_name = st.selectbox("Select Source Language:", list(language_mapping.keys()))
to_language_name = st.selectbox("Select Target Language:", list(language_mapping.keys()))

# Convert language names to language codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Select translation mode
mode = st.selectbox("Select Translation Mode:", ["Text-to-Text", "Text-to-Speech", "Speech-to-Text", "Speech-to-Speech"])

# Buttons to control translation
start_button = st.button("Start", key="start_button")
stop_button = st.button("Stop", key="stop_button")

# Start translation if "Start" is pressed
if start_button:
    st.session_state.is_translate_on = True

# Stop translation if "Stop" is pressed
if stop_button:
    st.session_state.is_translate_on = False

# Placeholder for translation output
output_placeholder = st.empty()

# Only start translation after "Start" button is pressed
if st.session_state.is_translate_on:
    main_process(output_placeholder, from_language, to_language, mode)