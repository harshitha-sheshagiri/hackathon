from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import os
from pydub import AudioSegment
import speech_recognition as sr
from transformers import pipeline


app = Flask(__name__)

def summarize_audio(file_path):
    print(f"Processing file: {file_path}")
    # Step 1: Convert MP3 to WAV
    wav_path = file_path.replace('.mp3', '.wav')  # Changed to use file_path
    audio = AudioSegment.from_mp3(file_path)  # Changed to use file_path
    audio.export(wav_path, format="wav")  # Export the converted WAV file

    # Step 2: Transcribe the WAV Audio
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Could not request results; {e}"

    # Step 3: Summarize the Transcript
    summarizer = pipeline("summarization")
    summary = summarizer(transcript, max_length=20, min_length=25, do_sample=False)  # Adjusted summarization parameters

    return summary[0]['summary_text']

@app.route('/')
def home():
    return render_template('summaryb.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    audio_file = request.files['audio_file']
    
    # Ensure the uploads folder exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')  # Create 'uploads' directory if it does not exist

    # Save the uploaded file to the 'uploads' directory
    file_path = os.path.join('uploads', audio_file.filename)  # Changed to use 'uploads' directory
    audio_file.save(file_path)  # Save the file to the path
    
    # Get the summary using your audio processing code
    summary = summarize_audio(file_path)  # Changed to use the correct file_path
    
    # Return the summary
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True, port=5001)

