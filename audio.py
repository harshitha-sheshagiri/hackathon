# Step 1: Convert MP3 to WAV
from pydub import AudioSegment
audio = AudioSegment.from_mp3("audio.mp3")
audio.export("converted_audio.wav", format="wav")

# Step 2: Transcribe the WAV Audio
import speech_recognition as sr
recognizer = sr.Recognizer()
with sr.AudioFile("converted_audio.wav") as source:
    audio_data = recognizer.record(source)
try:
    transcript = recognizer.recognize_google(audio_data)
    print("Transcription:\n", transcript)
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand the audio")
except sr.RequestError as e:
    print(f"Could not request results; {e}")

# Step 3: Summarize the Transcript
from transformers import pipeline
summarizer = pipeline("summarization")
summary = summarizer(transcript, max_length=20, min_length=30, do_sample=False)
print("Summary:\n", summary[0]['summary_text'])
