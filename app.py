from flask import Flask, request, send_file, jsonify
from spleeter.separator import Separator
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/separate', methods=['POST'])
def separate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    filename = str(uuid.uuid4()) + ".mp3"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Separar en 4 stems: voz, bajo, batería, otros
    separator = Separator('spleeter:4stems')
    output_path = os.path.join(OUTPUT_FOLDER, filename.split('.')[0])
    separator.separate_to_file(filepath, OUTPUT_FOLDER)

    # Devolver rutas de los archivos separados
    stems = ['vocals', 'bass', 'drums', 'other']
    result = {}
    for stem in stems:
        result[stem] = f"/download/{filename.split('.')[0]}/{stem}"

    return jsonify(result)

@app.route('/download/<session>/<stem>')
def download(session, stem):
    file_path = os.path.join(OUTPUT_FOLDER, session, f"{stem}.wav")
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True) 