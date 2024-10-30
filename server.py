from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
import os
import random
import string
app = Flask(__name__, static_folder='static')
# Set up Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Use a more secure key in production

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

OTP = generate_otp()

@app.route('/otp')
def show_otp():
    return f"OTP for server access: {OTP}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if entered_otp == OTP:
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
    print(f"OTP for server access: {OTP}")
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))