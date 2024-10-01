from flask import Flask, request, jsonify, render_template, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageOps
import pytesseract
from fuzzywuzzy import process
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image_path):
    try:
        image = Image.open(image_path).convert('L')
        image = ImageOps.autocontrast(image)
        return image
    except FileNotFoundError:
        raise

def extract_patterns(text):
    return re.findall(r'\b[01]-[01]-[01]\b', text)

def find_best_match(query, prescriptions):
    match = process.extractOne(query, prescriptions)
    return match

@app.route('/')
def index():
    return render_template('string_matchingb.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the uploaded image
        image = preprocess_image(file_path)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        prescriptions=["Paracetamol", "Dolo 650", "Cinarest","Amoxicillin","Ropinrole"]

        # Example list of full prescriptions
        prescription = [
                "Aspirin 81mg", "Metformin 500mg", "Lisinopril 10mg", "Amlodipine 5mg", "Simvastatin 20mg", "Omeprazole 20mg",
            "Losartan 50mg", "Hydrochlorothiazide 25mg", "Atorvastatin 40mg", "Levothyroxine 100mcg", "Gabapentin 300mg", "Sertraline 50mg",
            "Prednisone 10mg", "Albuterol 90mcg", "Citalopram 20mg", "Tamsulosin 0.4mg", "Clopidogrel 75mg", "Tramadol 50mg",
            "Zolpidem 10mg", "Metoprolol 100mg", "Azithromycin 500mg", "Doxycycline 100mg", "Cetirizine 10mg", "Naproxen 500mg",
            "Diclofenac 50mg", "Meloxicam 15mg", "Ezetimibe 10mg", "Furosemide 40mg", "Lorazepam 1mg", "Divalproex Sodium 250mg",
            "Hydroxyzine 25mg", "Sildenafil 100mg", "Montelukast 10mg", "Ranitidine 150mg", "Glyburide 5mg", "Chlorthalidone 25mg",
            "Methylprednisolone 4mg", "Valsartan 80mg", "Clonazepam 0.5mg", "Trazodone 50mg", "Insulin Glargine 10units/ml",
            "Bupropion 150mg", "Propoxyphene 100mg", "Risperidone 2mg", "Sulfamethoxazole/Trimethoprim 800mg/160mg", "Ropinirole 1mg", "Nifedipine 30mg",
            "Propranolol 40mg", "Duloxetine 30mg", "Prazosin 2mg", "Metronidazole 500mg", "Chlorpheniramine 4mg", "Amoxicillin/Clavulanate 875mg/125mg",
            "Atenolol 50mg", "Fluticasone 50mcg", "Benzonatate 100mg", "Diphenhydramine 25mg", "Clindamycin 300mg", "Levofloxacin 500mg",
            "Loratadine 10mg", "Fluoxetine 20mg", "Ciprofloxacin 500mg", "Acarbose 50mg", "Cefuroxime 250mg", "Spironolactone 25mg",
            "Colchicine 0.6mg", "Doxazosin 4mg", "Quetiapine 100mg", "Donepezil 10mg", "Lyrica 75mg", "Fentanyl 25mcg/hr",
            "Epinephrine 0.3mg", "Penicillin V 500mg", "Tacrolimus 1mg", "Tetracycline 500mg", "Oxcarbazepine 300mg", "Lyrica 50mg",
            "Verapamil 80mg", "Chlorpromazine 25mg", "Esomeprazole 40mg", "Acarbose 100mg", "Erythromycin 250mg", "Naproxen Sodium 550mg",
            "Propranolol 80mg", "Methotrexate 2.5mg", "Buspirone 10mg", "Hydrocodone 10mg", "Folic Acid 1mg", "Azathioprine 50mg",
            "Nifedipine Extended Release 90mg", "Allopurinol 300mg"
        ]
        
        # Split the extracted text into lines
        lines = text.strip().split('\n')
        
        # Process each line to find the best match
        results = []
        for line in lines:
            best_match = find_best_match(line, prescriptions)
            if best_match:
                results.append({
                    'text': text,
                    'best_match': best_match[0],
                    'score': best_match[1],
                    'image_url': url_for('uploaded_file', filename=filename)
                })
            else:
                results.append({
                    'text': text,
                    'best_match': 'No match found',
                    'score': 0,
                    'image_url': url_for('uploaded_file', filename=filename)
                })
        
        if results:
            return jsonify(results[0])
        else:
            return jsonify({'error': 'No results found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=8000)