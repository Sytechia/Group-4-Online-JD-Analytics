from flask import Flask
from blueprints.routes import home_blueprint, login_blueprint, register_user_blueprint, profile_page_blueprint, error_blueprint, error500_blueprint, resume_page_blueprint

app = Flask(__name__)
app.register_blueprint(home_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(register_user_blueprint)
app.register_blueprint(profile_page_blueprint)
app.register_blueprint(error_blueprint)
app.register_blueprint(error500_blueprint)
app.register_blueprint(resume_page_blueprint)