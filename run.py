# Main file that runs the application

from blueprints import app
import os
from controllers.crawler import JobSpider
import nltk


if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')
    
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.run(debug=True, threaded=True)
