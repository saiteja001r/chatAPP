import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import streamlit as st


def process_audio(file_path=None):
    recognizer = sr.Recognizer()
    if file_path:
        # Process pre-recorded audio
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
    else:
        # Process microphone recording
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            st.info("Recording... Speak now!")
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)  # Capture continuous audio
            st.success("Recording completed!")

    try:
        text = recognizer.recognize_google(audio)
        st.write(f"Recognized Text: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Sorry, could not understand the audio.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
        return None