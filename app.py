import os
from flask import Flask, render_template, request, jsonify, url_for
from gtts import gTTS
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure the static folder exists
os.makedirs(app.static_folder, exist_ok=True)

def text_to_voice(input_text, lang='ta'):
    try:
        # Generate speech from text
        tts = gTTS(text=input_text, lang=lang)
        
        # Create an in-memory file
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        # Generate a filename from the input text
        filename = f"{input_text[:12].replace(' ', '_')}.mp3"
        filepath = os.path.join(app.static_folder, filename)

        # Save the audio file to the static folder
        with open(filepath, "wb") as out_file:
            out_file.write(mp3_fp.read())

        return filename, "Saved audio file successfully"
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('input_page.html')

@app.route('/convert', methods=['POST'])
def convert():
    user_input = request.form.get('text', '').strip()
    if not user_input:
        return render_template('input_page.html', error="Please enter some text")
    
    filename, result = text_to_voice(user_input, 'ta')
    if filename:
        audio_url = url_for('static', filename=filename)
        return render_template('output_page.html', user_input=user_input, url=audio_url)
    else:
        return render_template('input_page.html', error=result)

@app.route('/delete-file', methods=['DELETE'])
def delete_file():
    file_name = request.args.get('file')
    if not file_name:
        return jsonify({'error': 'No file specified'}), 400
    
    file_path = os.path.join(app.static_folder, file_name)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({'message': 'File deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
