from flask import Blueprint, render_template, request, jsonify, flash, send_file, flash, redirect, current_app, session
import sys
from secret_key import client
from controllers.db_connections import get_db_connection
from controllers.skill_diagram import soft_skill, hard_skills

import os
from controllers.resume import allowed_file, process_cv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, login_required, logout_user

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from controllers.pdfReader import compare_resume_to_metrics, extract_keywords_from_metrics, extract_text_from_pdf, preprocess_text
from controllers.dumpText import insert_resume_text
from pathlib import Path

home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
logout_blueprint = Blueprint('logout', __name__)
register_user_blueprint = Blueprint('register', __name__)
profile_page_blueprint = Blueprint('profile', __name__)
error_blueprint = Blueprint('error', __name__)
error500_blueprint = Blueprint('error500', __name__)


@home_blueprint.route('/')
def index():
    # Connect to the SQLite3 datatabase and 
    # SELECT rowid and all Rows from the jobdesc table.
    # con = sqlite3.connect("database.db")
    # con.row_factory = sqlite3.Row

    con = get_db_connection()

    cur = con.cursor()
    cur.execute("SELECT * FROM jobdesc")
    rows = cur.fetchall()
    
    cur.execute("SELECT job_title, job_detail_url,job_listed,job_description, company_name, company_location FROM jobdesc order by job_listed asc limit 10")
    recent_10_rows = cur.fetchall()
 
    cur.execute("SELECT job_title, job_detail_url,job_listed,job_description, company_name, company_location FROM jobdesc where job_title LIKE '%data%' order by job_listed asc limit 10")
    top_10_rows = cur.fetchall()
    con.close()
    
    user = ''
    if 'username' in session:
        # user = session["username"]
        user = session
        print(f'Logged in as {user["username"]}')
    
    # Send the results of the SELECT to the home.html page
    return render_template('home.html',user = user,rows=rows,recent_10_rows =recent_10_rows,top_10_rows = top_10_rows)

@login_blueprint.route('/login',methods = ["POST","GET"])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        con = get_db_connection()  
        cur = con.cursor()
        user = cur.execute('SELECT * FROM userdata WHERE username = ?', (username,)).fetchone()
        print("Everything: ", user)
        print("Id: ", user[0])
        print("Name: ", user[1])
        print("password: ", user['hashed_password'])

        con.commit()  
        con.close()

        if user and check_password_hash(user['hashed_password'], password):
            # session["user_id"] = user['id']
            session['username'] = request.form['username']
            # flash('Logged in successfully.')
            return redirect("/")
        else:
            return render_template("login.html", message="Invalid username or password.")
    return render_template('login.html')

@register_user_blueprint.route('/register',methods = ["POST","GET"])
def index():
    msg = "msg" 
    if request.method == "POST":

        name = request.form.get("name")  
        password = request.form.get("password1")
        password2 = request.form.get("password2")

        if not (name and password and password2):
            return render_template("register.html", msg = "All fields are required.")  

        hashed_password = generate_password_hash(password)
        # hashed_password = password

        # with sqlite3.connect("database.db") as con:
        con = get_db_connection()  
        cur = con.cursor()   
        cur.execute("INSERT into userdata (username, hashed_password, nested_skills, soft_skills, hard_skills,  is_admin) values (?,?,?,?,?,?)",(name,hashed_password,'','','',1))  
        con.commit()  
        # msg = "User successfully Added" 
        con.close()
        return redirect("/login")
        
    return render_template('register.html')

@logout_blueprint.route("/logout")
def logout():
    # logout_user()
    session.pop("username", None)
    return redirect("/login")

@profile_page_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
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
            print("Text from resume: ", resume_text)

            # Example usage in your function:
            ROOT_DIR = Path.cwd()
            metrics_file_path = ROOT_DIR / 'metrics.md'  # Path to the metrics.md file

            # Call the steps within your function
            resume_text = extract_text_from_pdf(file_path)
            resume_keywords = preprocess_text(resume_text)
            metrics_keywords = extract_keywords_from_metrics(metrics_file_path, resume_keywords, threshold=80)
            matching_keywords = compare_resume_to_metrics(resume_keywords, metrics_keywords)

            # Insert resume_text into database
            userid = 1
            insert_resume_text(userid, resume_text)

            return render_template('feedback.html', feedback=feedback)
    else:
        con = get_db_connection()

        cur = con.cursor()
        cur.execute("SELECT * FROM userdata")
        rows = cur.fetchall()

        con.close()
        return render_template('profile.html',rows = rows)
  
# Route for generating the hard skills plot
@profile_page_blueprint.route('/plot.png')
def plot():
    
    img_io = hard_skills()
    return send_file(img_io, mimetype='image/png')

# Route for generating the soft skills plot
@profile_page_blueprint.route('/plotsoftskills.png')
def plot_soft_skills():
    img_io2  = soft_skill()

    return send_file(img_io2, mimetype='image/png')

@error_blueprint.app_errorhandler(404)
def page_not_found(e): # Return error 404
    return render_template('404.html'), 404

@error500_blueprint.app_errorhandler(500)
def page_not_found(e): # Return error 500
    return render_template('500.html'), 500