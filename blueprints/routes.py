from flask import Blueprint, render_template, request, jsonify, flash, send_file, flash, redirect, current_app, session
import sys
from secret_key import client
from controllers.db_connections import get_db_connection

from controllers.skill_diagram import check_metrics_for_plot, hard_skills, soft_skills

import os
from controllers.resume import allowed_file, process_cv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, login_required, logout_user
import time
home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
logout_blueprint = Blueprint('logout', __name__)
register_user_blueprint = Blueprint('register', __name__)
profile_page_blueprint = Blueprint('profile', __name__)
error_blueprint = Blueprint('error', __name__)
error500_blueprint = Blueprint('error500', __name__)

@home_blueprint.route('/')
def index():
    # Connect to the database
    con = get_db_connection()
    cur = con.cursor()
    # Fetch all the job descriptions from the database
    cur.execute("SELECT * FROM jobdesc")
    rows = cur.fetchall()
    # Fetch the 10 most recent job descriptions from the database
    cur.execute("SELECT job_title, job_detail_url,job_listed,job_description, company_name, company_location FROM jobdesc order by job_listed asc limit 10")
    recent_10_rows = cur.fetchall()
    # Fetch the 10 most recent job descriptions from the database that contain the word 'data'
    cur.execute("SELECT job_title, job_detail_url,job_listed,job_description, company_name, company_location FROM jobdesc where job_title LIKE '%data%' order by job_listed asc limit 10")
    top_10_rows = cur.fetchall()
    # Commit the changes and close the connection
    con.close()
    
    user = ''
    if 'username' in session:
        user = session
        print(f'Logged in as {user["username"]}')
    

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
            #flash('Logged in successfully.')
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
    if 'username' not in session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            # Handle file upload and process the CV (already correctly implemented)
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
            cur.execute("SELECT * FROM userdata WHERE username = ?", (session['username'],))
            rows = cur.fetchall()
            soft_skills_list, hard_skills_list = check_metrics_for_plot(session['username'])
            con.close()
            
            # Fetch soft and hard skills from the database
            soft_skills_list, hard_skills_list = check_metrics_for_plot(session['username'])
            if  soft_skills_list == [] or hard_skills_list == []:
                return render_template('profile.html', rows=rows)
            else :
                print("Soft skills: ", soft_skills_list)
                print("Hard skills: ", hard_skills_list)
                return render_template('profile.html', rows=rows, soft_skills_list=soft_skills_list,hard_skills_list=hard_skills_list)
# Route for generating the hard skills plot
@profile_page_blueprint.route('/plot.png')
def plot():
        soft_skills_list, hard_skills_list = check_metrics_for_plot(session['username'])
        if soft_skills_list == [] or hard_skills_list == []:
            return render_template('404.html')
        else:
            # Generate the plot using the fetched data
            img_io = hard_skills(hard_skills_list)
            return send_file(img_io, mimetype='image/png')
    

# Route for generating the soft skills plot
@profile_page_blueprint.route('/plotsoftskills.png')
def plot_soft_skills():
        soft_skills_list, hard_skills_list = check_metrics_for_plot(session['username'])
        if soft_skills_list == [] or hard_skills_list == []:
            return render_template('404.html')
        else:
            img_io2 = soft_skills(soft_skills_list)
            return send_file(img_io2, mimetype='image/png')
    
        



@error_blueprint.app_errorhandler(404)
def page_not_found(e): # Return error 404
    return render_template('404.html'), 404

@error500_blueprint.app_errorhandler(500)
def page_not_found(e): # Return error 500
    return render_template('500.html'), 500