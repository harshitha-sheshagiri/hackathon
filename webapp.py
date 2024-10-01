from rainbow import Flask, request, jsonify
import os

app = Flask(__name__)

# Your audio processing and summarization logic here
def summarize_audio(file_path):
    # Assuming you already have the code to recognize and summarize the audio
    summary = "This is a dummy summary of the audio"
    return summary

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    audio_file = request.files['audio_file']
    
    # Save the file to process it
    file_path = os.path.join('uploads', audio_file.filename)
    audio_file.save(file_path)
    
    # Get the summary using your audio processing code
    summary = summarize_audio(Users/harshithasheshagiri/hackathon/audio.py)
    
    # Return the summary
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
