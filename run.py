# Main file that runs the application

from blueprints import app
import os
from controllers.crawler import JobSpider
import nltk
import subprocess

if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')
    subprocess.run('python -m spacy download en_core_web_md', shell=True, check=True)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.run(debug=True, threaded=True)
    