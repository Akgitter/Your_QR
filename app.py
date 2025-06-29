from flask import Flask, render_template, request, send_file
from qr_generator import PersonalQRGenerator
import os
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='static/qr_codes'

generator = PersonalQRGenerator(deepseek_api_key="sk-60fe441fa7434b87b5b084a1c10308fa")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #Get form inputs
        url = request.form['url']
        description = request.form['description']

        # Generate QR code
        qr_img= generator.generate_personal_qr(url, description)

        # Save QR code to a BytesIO object

        img_io = BytesIO()
        qr_img.save(img_io, 'PNG')
        img_io.seek(0)


        # Generate a unique filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"qr_code_{timestamp}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)


        # Save the image to the filesystem
        qr_img.save(filepath)

        return render_template('index.html',
                               qr_image=filename,
                               original_url=url,
                               description=description)
    
    return render_template('index.html')

@app.route('/downlaod/<filename>')
def download(filename):
    return send_file(f"static/qr_codes/{filename}", as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
    