import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from flask import Flask, send_file, Blueprint, render_template, request, jsonify, flash, redirect, current_app
from werkzeug.utils import secure_filename
import io
import os
from blueprints.jdresume import process_cv 
from blueprints.config import Config
from blueprints.utils import allowed_file
import pdfplumber

home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
register_user_blueprint = Blueprint('register', __name__)
profile_page_blueprint = Blueprint('profile', __name__)
resume_page_blueprint = Blueprint('resume', __name__)
error_blueprint = Blueprint('error', __name__)
error500_blueprint = Blueprint('error500', __name__)

@home_blueprint.route('/')
def index():
    return render_template('home.html')

@login_blueprint.route('/login')
def index():
    return render_template('login.html')

@register_user_blueprint.route('/register')
def index():
    return render_template('register.html')

@profile_page_blueprint.route('/profile')
def index():
    return render_template('profile.html')

@error_blueprint.app_errorhandler(404)
def page_not_found(e): # Return error 404
    return render_template('404.html'), 404

@error500_blueprint.app_errorhandler(500)
def page_not_found(e): # Return error 500
    return render_template('500.html'), 500

@resume_page_blueprint.route('/resume', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the CV and get feedback
            # feedback = process_cv(file_path, filename)

            resume_text = extract_text_from_pdf(file_path)
            resume_text_clean = resume_text.lower()
            resume_text_no_spacing = resume_text_clean.replace('\n', ' ').strip()
            resume_text_no_spacing = resume_text_no_spacing.replace('(cid:425)', 'tt')  # Example for 'better'
            resume_text_no_spacing = resume_text_no_spacing.replace('(cid:332)', 'ft')  # Example for 'Microsoft'
            resume_text_no_spacing = resume_text_no_spacing.replace('(cid:415)', 'ti')  # Example for 'action'

            # Print extracted text to the terminal
            print(f"Extracted Text from {filename}:")
            print(resume_text_no_spacing)

            return render_template('improve_resume.html', feedback=feedback)
    else:
        return render_template('resume_upload.html')
    
# Function to extract text from the uploaded PDF
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text
    
# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Set upload folder path

# Register blueprints
app.register_blueprint(home_blueprint, url_prefix='/')
app.register_blueprint(login_blueprint, url_prefix='/login')
app.register_blueprint(register_user_blueprint, url_prefix='/register')
app.register_blueprint(profile_page_blueprint, url_prefix='/profile')
app.register_blueprint(resume_page_blueprint, url_prefix='/resume')
app.register_blueprint(error_blueprint)
app.register_blueprint(error500_blueprint)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)