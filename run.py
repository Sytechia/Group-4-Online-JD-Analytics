# Main file that runs the application

from blueprints import app
import os
if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.run(debug=True, threaded=True)
    