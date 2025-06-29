from flask import Flask, render_template, request, send_file
from qr_generator import PersonalQRGenerator
import os
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='static/qr_codes'

generator = PersonalQRGenerator()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #Get form inputs
        url = request.form.get('url', '').strip()
        description = request.form.get('description', '').strip()

        # Validate inputs
        if len(description) > 100:
            return render_template('index.html', error="Description must be 100 characters or less.")
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
        if not url or not description:
            return render_template('index.html', error="Both URL and description are required.")

        try: 
            qr_img= generator.generate_personal_qr(url, description)
            # Ensure URL starts with http:// or https://

            # Ensure description is not too long

            # Generate the personalized QR code
            # Generate QR code\

            # Save QR code to a BytesIO object

            img_io = BytesIO()
            qr_img.save(img_io, 'PNG')
            img_io.seek(0)


            # Generate a unique filename
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"qr_code_{timestamp}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)


            # Save the image to the filesystem
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            qr_img.save(filepath)

            return render_template('index.html',
                                qr_image=filename,
                                original_url=url,
                                description=description)
        except Exception as e:
                return render_template('index.html', error=f"Error generating QR code: {str(e)}")
    
    return render_template('index.html')

@app.route('/downlaod/<filename>')
def download(filename):
    try:
        return send_file(f"static/qr_codes/{filename}", as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
    