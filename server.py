from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
import os
import pyotp
import qrcode
from io import BytesIO
import base64

# Set up Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Use a more secure key in production

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Generate a random secret key for OTP
SECRET_KEY = pyotp.random_base32()
totp = pyotp.TOTP(SECRET_KEY)

@app.route('/setup-otp')
def setup_otp():
    # Generate the OTP URI
    provisioning_uri = totp.provisioning_uri("FileServer:Admin", issuer_name="FileServer")
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('setup_otp.html', secret_key=SECRET_KEY, qr_code=qr_code)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if totp.verify(entered_otp):
            session['verified'] = True
            return redirect(url_for('file_panel'))
        else:
            flash('Invalid OTP. Please try again.')
    
    return render_template('otp.html')

@app.route('/file_panel')
def file_panel():
    if not session.get('verified'):
        return redirect(url_for('index'))
    
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('verified'):
        return redirect(url_for('index'))
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('file_panel'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('file_panel'))

    # Save the file
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        flash(f'{file.filename} uploaded successfully!')
        return redirect(url_for('file_panel'))

@app.route('/download/<filename>')
def download_file(filename):
    if not session.get('verified'):
        return redirect(url_for('index'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('verified'):
        return redirect(url_for('index'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'{filename} deleted successfully!')
    else:
        flash(f'File {filename} not found')
    return redirect(url_for('file_panel'))

if __name__ == '__main__':
    print(f"OTP Secret Key: {SECRET_KEY}")
    app.run(host='0.0.0.0', port=5000, debug=True)