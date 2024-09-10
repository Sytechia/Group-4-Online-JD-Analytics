from flask import Blueprint, render_template, request, jsonify
import sys
from secret_key import client

home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
register_user_blueprint = Blueprint('register', __name__)
profile_page_blueprint = Blueprint('profile', __name__)
error_blueprint = Blueprint('error', __name__)
error500_blueprint = Blueprint('error500', __name__)

@home_blueprint.route('/')
def index():
    return render_template('index.html')

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