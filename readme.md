# Secure Flask File Server

This project is a secure file-sharing portal built with Flask, featuring file upload, download, and deletion capabilities, along with strong security measures including Two-Factor Authentication (2FA) and HTTPS support.

## Table of Contents

1. [Core Functionality](#core-functionality)
2. [Security Features](#security-features)
3. [User Interface](#user-interface)
4. [Key Components](#key-components)
5. [Routes and Pages](#routes-and-pages)
6. [Additional Features](#additional-features)
7. [Development and Deployment](#development-and-deployment)
8. [Dependencies](#dependencies)

## Core Functionality

- File upload, download, and deletion capabilities
- Secure file storage in a designated upload folder
- File list display with sorting based on modification time

## Security Features

- Two-Factor Authentication (2FA) using Google Authenticator
- TOTP (Time-based One-Time Password) implementation
- Session management with timeout functionality
- HTTPS support for secure communication

## User Interface

- Clean and responsive design using HTML and CSS
- Flash messages for user feedback
- File upload form with drag-and-drop functionality
- File list with download and delete options

## Key Components

- `server.py`: Main Flask application file
- `templates/`: HTML templates for different pages
- `static/styles.css`: CSS file for styling
- `uploads/`: Directory for storing uploaded files

## Routes and Pages

- `/`: OTP verification page
- `/setup`: Google Authenticator setup page
- `/file_panel`: Main file sharing interface
- `/upload`: File upload endpoint
- `/download/<filename>`: File download endpoint
- `/delete/<filename>`: File deletion endpoint
- `/logout`: Session termination

## Additional Features

- Email notifications for file uploads
- File size limit (16MB)
- Allowed file extensions filtering
- Error handling for 404 and 500 errors

## Development and Deployment

- Debug mode enabled for development
- SSL context for HTTPS (using `cert.pem` and `key.pem`)
- Running on host `0.0.0.0` and port `5000`

## Dependencies

- Flask
- PyOTP for TOTP implementation
- qrcode for generating QR codes
- Flask-Mail for email notifications

## Getting Started

To get a local copy up and running, follow these steps:

1. Clone the repository:
   git clone <repository_url>
   cd <repository_name>

### Install the required dependencies:
   pip install -r requirements.txt

### Set up your SSL certificates (for HTTPS):
Place your cert.pem and key.pem files in the root directory.

### Run the application:
   python server.py

Access the application in your web browser at https://localhost:5000.

### License
This project is licensed under the MIT License - see the LICENSE file for details.