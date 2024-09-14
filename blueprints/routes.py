from flask import Blueprint, render_template, request, jsonify, flash, send_file, flash, redirect, current_app
import sys
from secret_key import client
import sqlite3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import io

import os
from blueprints.resume import allowed_file, process_cv
from werkzeug.utils import secure_filename

home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
register_user_blueprint = Blueprint('register', __name__)
profile_page_blueprint = Blueprint('profile', __name__)
error_blueprint = Blueprint('error', __name__)
error500_blueprint = Blueprint('error500', __name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_job():
    data = request.get_json()

    job_id = data.get('job_id')
    job_title = data.get('job_title')
    job_url = data.get('job_url')

    # if not all([job_id, job_title, job_url]):
    #     return jsonify({"error": "All fields are required"}), 400

    con = get_db_connection()
    con.execute('INSERT INTO jobdesc (job_id, job_title, job_url) VALUES (?, ?, ?)',
                 (job_id, job_title, job_url))
    con.commit()
    con.close()

def get_job(id):
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobdesc WHERE id = ?', (id,)).fetchone()
    conn.close()

def delete_job(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM jobs WHERE id = ?', (id,))
    conn.commit()
    conn.close()

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
    
    con.close()
    # Send the results of the SELECT to the home.html page
    return render_template('home.html',rows = rows)

@login_blueprint.route('/login')
def index():
    # if request.method == 'POST':
    #     email = request.form.get('email')
    #     password = request.form.get('password')

    #     user = User.query.filter_by(email=email).first()
    #     if user:
    #         if check_password_hash(user.password, password):
    #             flash('Logged in successfully!', category='success')
    #             login_user(user, remember=True)
    #             return redirect(url_for('views.home'))
    #         else:
    #             flash('Incorrect password, try again.', category='error')
    #     else:
    #         flash('Email does not exist.', category='error')

    return render_template('login.html')

@register_user_blueprint.route('/register',methods = ["POST","GET"])
def index():
    msg = "msg" 
    if request.method == "POST":  
        try:  
            # email = request.form["email"]  
            # name = request.form["name"]  
            # password = request.form["password1"]  
            # password2 = request.form["password2"]  

            id = 1  
            email = request.form.get('email')  
            name = request.form.get("name")  
            password = request.form.get("password1")
            password2 = request.form.get("password2")  

            # with sqlite3.connect("database.db") as con:
            con = get_db_connection()  
            cur = con.cursor()  
            cur.execute("INSERT into userdata (id, email, name, password) values (?,?,?,?)",(id,email,name,password))  
            con.commit()  
            msg = "User successfully Added" 
            con.close()   
        except:  
            con.rollback()  
            msg = "We can not add the user to the list" 
        finally:  
            return render_template("register.html",msg = msg)  
        
    return render_template('register.html')


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
            feedback = process_cv(file_path, filename)

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
    proportions_hard_skills = [0.6, 0.75, 0.8]
    labels = ['Year(s) of Experience', 'Industry Certifications', 'Qualifications']
    N_HARD_SKILLS = len(proportions_hard_skills)
    proportions_hard_skills = np.append(proportions_hard_skills, 1)
    theta = np.linspace(0, 2 * np.pi, N_HARD_SKILLS, endpoint=False)
    x = np.append(np.sin(theta), 0)
    y = np.append(np.cos(theta), 0)
    triangles_HARD_SKILLS = [[N_HARD_SKILLS, i, (i + 1) % N_HARD_SKILLS] for i in range(N_HARD_SKILLS)]
    triang_backgr = tri.Triangulation(x, y, triangles_HARD_SKILLS)
    triang_foregr = tri.Triangulation(x * proportions_hard_skills, y * proportions_hard_skills, triangles_HARD_SKILLS)
    
    cmap = plt.cm.rainbow_r
    colors = np.linspace(0, 1, N_HARD_SKILLS + 1)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    ax.tripcolor(triang_backgr, colors, cmap=cmap, shading='gouraud', alpha=0.4)
    ax.tripcolor(triang_foregr, colors, cmap=cmap, shading='gouraud', alpha=0.8)
    ax.triplot(triang_backgr, color='white', lw=2)
    
    for label, proportion, xi, yi in zip(labels, proportions_hard_skills[:-1], x, y):
        ax.text(xi * 1.1, yi * 1.1, f'{label}: {int(proportion * 100)}%',
                ha='left' if xi > 0.1 else 'right' if xi < -0.1 else 'center',
                va='bottom' if yi > 0.1 else 'top' if yi < -0.1 else 'center')
    
    ax.axis('off')
    ax.set_aspect('equal')
    plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)

    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', transparent=True, bbox_inches='tight')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

# Route for generating the soft skills plot
@profile_page_blueprint.route('/plotsoftskills.png')
def plot_soft_skills():
    proportions_soft_skills = [0.6, 0.75, 0.8, 0.9, 0.7, 0.8, 0.9]
    labels = ['Collaboration', 'Adaptability', 'Resourcefulness', 'Positive Attitude', 'Work Ethic', 'Willingness to Learn', 'Critical Thinking']
    N_SOFT_SKILLS = len(proportions_soft_skills)
    proportions_soft_skills = np.append(proportions_soft_skills, 1)
    theta = np.linspace(0, 2 * np.pi, N_SOFT_SKILLS, endpoint=False)
    x = np.append(np.sin(theta), 0)
    y = np.append(np.cos(theta), 0)
    triangles_soft_skills = [[N_SOFT_SKILLS, i, (i + 1) % N_SOFT_SKILLS] for i in range(N_SOFT_SKILLS)]
    triang_backgr = tri.Triangulation(x, y, triangles_soft_skills)
    triang_foregr = tri.Triangulation(x * proportions_soft_skills, y * proportions_soft_skills, triangles_soft_skills)
    
    cmap = plt.cm.rainbow_r
    colors = np.linspace(0, 1, N_SOFT_SKILLS + 1)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    ax.tripcolor(triang_backgr, colors, cmap=cmap, shading='gouraud', alpha=0.4)
    ax.tripcolor(triang_foregr, colors, cmap=cmap, shading='gouraud', alpha=0.8)
    ax.triplot(triang_backgr, color='white', lw=2)
    
    for label, proportion, xi, yi in zip(labels, proportions_soft_skills[:-1], x, y):
        ax.text(xi * 1.1, yi * 1.1, f'{label}: {int(proportion * 100)}%',
                ha='left' if xi > 0.1 else 'right' if xi < -0.1 else 'center',
                va='bottom' if yi > 0.1 else 'top' if yi < -0.1 else 'center')
    
    ax.axis('off')
    ax.set_aspect('equal')
    plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)

    img_io2 = io.BytesIO()
    plt.savefig(img_io2, format='png', transparent=True, bbox_inches='tight')
    img_io2.seek(0)
    
    return send_file(img_io2, mimetype='image/png')

@error_blueprint.app_errorhandler(404)
def page_not_found(e): # Return error 404
    return render_template('404.html'), 404

@error500_blueprint.app_errorhandler(500)
def page_not_found(e): # Return error 500
    return render_template('500.html'), 500