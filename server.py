from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from flask_mail import Mail, Message  # Add this import
import os
import pyotp
import qrcode
import base64
from io import BytesIO
from datetime import datetime
import secrets

# Set up Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Generate a secure random secret key

# Email configuration - Add these lines after app initialization
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ' your username'
app.config['MAIL_PASSWORD'] = 'your app password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# TOTP setup
TOTP_SECRET_FILE = 'totp_secret.txt'

def get_totp_secret():
    if os.path.exists(TOTP_SECRET_FILE):
        with open(TOTP_SECRET_FILE, 'r') as f:
            return f.read().strip()
    else:
        secret = pyotp.random_base32()
        with open(TOTP_SECRET_FILE, 'w') as f:
            f.write(secret)
        return secret

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

TOTP_SECRET = get_totp_secret()
totp = pyotp.TOTP(TOTP_SECRET)

@app.route('/setup')
def setup():
    # Generate a new QR code
    provisioning_url = totp.provisioning_uri("FileShareApp:User", issuer_name="FileShareApp")
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_url)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert image to base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('setup.html', 
                         secret=TOTP_SECRET, 
                         qr_code=img_str,
                         provisioning_url=provisioning_url)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if totp.verify(entered_otp):
            session['verified'] = True
            session['last_activity'] = datetime.now().timestamp()
            return redirect(url_for('file_panel'))
        else:
            flash('Invalid OTP. Please try again.')
    
    return render_template('otp.html')

@app.route('/file_panel')
def file_panel():
    if not session.get('verified'):
        return redirect(url_for('index'))
    
    # Session timeout after 30 minutes of inactivity
    last_activity = session.get('last_activity')
    if last_activity is None or datetime.now().timestamp() - last_activity > 1800:  # 30 minutes
        session.clear()
        flash('Session expired. Please login again.')
        return redirect(url_for('index'))
    
    session['last_activity'] = datetime.now().timestamp()
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Sort files by modification time
    files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)
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

    if file and allowed_file(file.filename):
        # Secure the filename
        filename = file.filename
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            flash(f'{filename} uploaded successfully!')
            
            # Send email notification
            msg = Message('File Uploaded',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=['pasindudewviman59@gmail.com'])
            msg.body = f"A new file '{filename}' has been uploaded."
            mail.send(msg)
        except Exception as e:
            flash(f'Error uploading file: {str(e)}')
    else:
        flash('File type not allowed')
    
    return redirect(url_for('file_panel'))

@app.route('/download/<filename>')
def download_file(filename):
    if not session.get('verified'):
        return redirect(url_for('index'))
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('file_panel'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('verified'):
        return redirect(url_for('index'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'{filename} deleted successfully!')
        else:
            flash(f'File {filename} not found')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}')
    
    return redirect(url_for('file_panel'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='404 - Page Not Found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='500 - Internal Server Error'), 500

@app.before_request
def before_request():
    if session.get('verified'):
        # Update last activity timestamp
        session['last_activity'] = datetime.now().timestamp()

if __name__ == '__main__':
    print(f"TOTP Secret: {TOTP_SECRET}")
    print("Visit /setup to get the Google Authenticator setup URL")
    # In production, use proper SSL certificates
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))