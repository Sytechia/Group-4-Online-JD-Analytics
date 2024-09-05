"""
Main file that runs the application 
"""

from blueprints import app


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
