from flask import Flask
from blueprints.routes import home_blueprint

app = Flask(__name__)
app.register_blueprint(home_blueprint)
