from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageOps
import pytesseract
import re
import schedule
import time
from twilio.rest import Client
import threading
import database
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Configure logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image_path):
    try:
        image = Image.open(image_path).convert('L')
        image = ImageOps.autocontrast(image)
        return image
    except FileNotFoundError:
        logging.error(f"File not found: {image_path}")
        raise

def extract_patterns(text):
    return re.findall(r'\b[01]-[01]-[01]\b', text)

def extract_medicines(text):
    lines = text.strip().split('\n')
    medicines = [line.strip() for line in lines if line.strip()]
    return medicines

def send_sms(body):
    account_sid = 'sid'
    auth_token = 'token'
    from_number = '+***********'
    to_number = '+************'
    
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body=body,
            from_=from_number,
            to=to_number
        )
        logging.info(f"Sent message: {message.sid}")
    except Exception as e:
        logging.error(f"Failed to send SMS: {e}")

def check_and_notify(image_path):
    try:
        image = preprocess_image(image_path)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        patterns = extract_patterns(text)
        for pattern in patterns:
            if re.match(r'[01]-[01]-[01]', pattern):
                parts = pattern.split('-')
                morning_time = '10:09' if parts[0] == '1' else None
                afternoon_time = '13:00' if parts[1] == '1' else None
                evening_time = '08:27' if parts[2] == '1' else None

                if morning_time:
                    schedule.every().day.at(morning_time).do(
                        send_sms, f"Reminder: Take your morning medicine. Pattern: {pattern}")

                if afternoon_time:
                    schedule.every().day.at(afternoon_time).do(
                        send_sms, f"Reminder: Take your afternoon medicine. Pattern: {pattern}")

                if evening_time:
                    schedule.every().day.at(evening_time).do(
                        send_sms, f"Reminder: Take your evening medicine. Pattern: {pattern}")

        medicines = extract_medicines(text)
        for medicine in medicines:
            database.insert_medicine(medicine)
            logging.info(f"Stored medicine: {medicine}")

    except Exception as e:
        logging.error(f"Error in check_and_notify: {e}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(20)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return 'No file part'
    file = request.files['image']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        threading.Thread(target=check_and_notify, args=(file_path,)).start()
        return 'Image uploaded and processing started!'
    return 'Invalid file type'

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    database.init_db()  # Initialize the database
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(debug=True, port=5003)
