from flask import Blueprint, render_template, request, jsonify, flash, send_file, flash, redirect, current_app
import sys
from secret_key import client
from controllers.db_connections import get_db_connection

from controllers.skill_diagram import soft_skill, hard_skills

import os
from controllers.resume import allowed_file, process_cv
from werkzeug.utils import secure_filename

home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
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
    
    
    # Send the results of the SELECT to the home.html page
    return render_template('home.html',rows=rows,recent_10_rows =recent_10_rows,top_10_rows = top_10_rows)

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