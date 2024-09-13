from flask import Blueprint, render_template, request, jsonify
import sys
from secret_key import client
import sqlite3

home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
register_user_blueprint = Blueprint('register', __name__)
profile_page_blueprint = Blueprint('profile', __name__)
error_blueprint = Blueprint('error', __name__)
error500_blueprint = Blueprint('error500', __name__)

# Route that will SELECT a specific row in the database then load an Edit form 
def edit():
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            id = request.form['id']
            # Connect to the database and SELECT a specific rowid
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM jobdesc WHERE rowid = " + id)

            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            # Send the specific record of data to edit.html
            return render_template("edit.html",rows=rows)

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