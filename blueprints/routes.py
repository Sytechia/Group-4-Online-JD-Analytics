from flask import Blueprint, render_template, request, jsonify, flash, send_file, flash, redirect, current_app, session
import sys
from secret_key import client
from controllers.db_connections import get_db_connection
from controllers.skill_diagram import check_metrics_for_plot, hard_skills, soft_skills,calculate_score


import os
from controllers.resume import allowed_file, process_cv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from functools import wraps

from controllers.resume import  compare_resume_to_metrics, extract_keywords_from_metrics, preprocess_text, insert_resume_text, extract_text_from_pdf_matthew
from pathlib import Path


home_blueprint = Blueprint('home', __name__)
login_blueprint = Blueprint('login', __name__)
logout_blueprint = Blueprint('logout', __name__)
register_user_blueprint = Blueprint('register', __name__)
profile_page_blueprint = Blueprint('profile', __name__)
admin_page_blueprint = Blueprint('admin', __name__)
error_blueprint = Blueprint('error', __name__)
error500_blueprint = Blueprint('error500', __name__)

# Custom decorator to restrict access to admin users
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function 

@home_blueprint.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    else:
        id = session['id']
        con = get_db_connection()
        cur = con.cursor()
        cur.execute('SELECT soft_skills, hard_skills,feedback, field_of_interest FROM userdata WHERE id = ?', (id,))
        results = cur.fetchone()
        con.close()
                       
        if results:
            keys = ['soft_skills', 'hard_skills', 'feedback', 'field_of_interest']
            items_to_fill_up = [key for key, value in zip(keys, results) if value is None]
            
            if items_to_fill_up:
                items_to_fill_up_str = ', '.join(items_to_fill_up)
                flash(f'Please complete your profile ({items_to_fill_up_str}) to access this page.', 'danger')
                return redirect('/register')
        
        # Connect to the database
        con = get_db_connection()
        cur = con.cursor()
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

        if 'id' in session:
            user = session
            print(f'Logged in as {user["username"]}')

        return render_template('home.html',user = user,rows=rows,recent_10_rows =recent_10_rows,top_10_rows = top_10_rows)

@login_blueprint.route('/login',methods = ["POST","GET"])
def index():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            con = get_db_connection()  
            cur = con.cursor()
            user = cur.execute('SELECT * FROM userdata WHERE username = ?', (username,)).fetchone()
            con.commit()  
            con.close()

            if user and check_password_hash(user['hashed_password'], password):
                
                userobj = User.get(user['id'])
                login_user(userobj)
                session['id'] = user['id']
                session['username'] = user['username']
                
                return redirect("/")
            else:
                return render_template("login.html", message="Invalid username or password.")
        else:
            name = request.form.get("name")  
            password = request.form.get("password1")
            password2 = request.form.get("password2")

            if not (name and password and password2):
                return render_template("login.html", msg = "All fields are required.")  

            hashed_password = generate_password_hash(password)
           
            con = get_db_connection()  
            cur = con.cursor()   
            cur.execute("INSERT into userdata (username, hashed_password,is_admin) values (?,?,?)",(name,hashed_password,0))  
            con.commit()

            cur.execute('SELECT id FROM userdata WHERE username = ?', (name,))  
            new_user_id = cur.fetchone()['id'] 

            userobj = User.get(new_user_id)
            login_user(userobj)
            session['id'] = new_user_id
            session['username'] = name
            con.close()
            return redirect("/register")
    else:
        return render_template('login.html')

@register_user_blueprint.route('/register',methods = ["POST","GET"])
def index():
    if request.method == "POST":
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
        foi= request.form['foi']
        feedback = str(process_cv(file_path, filename,foi))
        con = get_db_connection()
        cur = con.cursor()
        userid = session['id']
        cur.execute("UPDATE userdata SET feedback = ? ,field_of_interest = ? WHERE id = ?", (feedback,foi,userid,))
        con.commit()
        ROOT_DIR = Path.cwd()
        metrics_file_path = ROOT_DIR / 'metrics.md'  # Path to the metrics.md file

        # Call the function to extract keywords from the metrics.md file
        resume_text = extract_text_from_pdf_matthew(file_path)
        resume_keywords = preprocess_text(resume_text)
        metrics_keywords = extract_keywords_from_metrics(metrics_file_path, resume_keywords, threshold=80)
        matching_keywords = compare_resume_to_metrics(resume_keywords, metrics_keywords)                
        
        #Hard Skill insert
        number_of_hours = request.form['number_of_hours']
        certification_number = request.form['certification_number']
        education_level = request.form['highest_education_obtained']
        matching_keywords_string = ', '.join(matching_keywords)

        stored_text = str({'Resume Text': matching_keywords_string , 'Number of hours': number_of_hours, 'Certification number': certification_number, 'Education level': education_level})
        # Insert resume_text into database
        
        insert_resume_text(userid, stored_text)
        return redirect("/")

    else:
        return render_template('register.html')

@logout_blueprint.route("/logout")
def logout():
    logout_user()
    session.pop("username", None)
    return redirect("/login")

@admin_page_blueprint.route("/admindashboard")
@admin_required
def admindashboard():
    con = get_db_connection()
    cur = con.cursor()
    users = cur.execute('SELECT * FROM userdata').fetchall()
    con.close()
    return render_template('admindashboard.html',users = users)

@admin_page_blueprint.route("/admindashboard/delete/<int:user_id>")
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect('/admindashboard')
    
    con = get_db_connection()
    cur = con.cursor()
    cur.execute('DELETE FROM userdata WHERE id = ?', (user_id,))
    con.commit()
    con.close()
    flash('User deleted successfully.', 'success')
    return redirect(('/admindashboard'))

@admin_page_blueprint.route("/admindashboard/make_admin/<int:user_id>")
@admin_required
def make_admin(user_id):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute('UPDATE userdata SET is_admin = 1 WHERE id = ?', (user_id,))
    con.commit()
    con.close()
    flash('User granted admin rights.', 'success')
    return redirect('/admindashboard')

@profile_page_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if 'username' not in session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            form_type = request.form.get('form_type')
            
            
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
                        
            if form_type == 'get_feedback':
                # Process the CV and get feedback
                con = get_db_connection()
                cur = con.cursor()
                userid = session['id']
                cur.execute('SELECT field_of_interest FROM userdata WHERE id = ?', (userid,))  
                foi = cur.fetchone()['id'] 
                feedback = str(process_cv(file_path, filename,foi))
                cur.execute("UPDATE userdata SET feedback = ? WHERE id = ?", (feedback,userid,))
                con.commit()
                cur.execute("SELECT id,username FROM userdata WHERE id = ?", (userid,))
                rows = cur.fetchall()
                con.close()
            
                # Fetch soft and hard skills from the database
                soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
                if  soft_skills_list == [] or hard_skills_list == []:
                    return render_template('profile.html', rows=rows)
                else :
                    return render_template('profile.html', rows=rows, soft_skills_list=soft_skills_list,hard_skills_list=hard_skills_list)
            elif form_type == 'update_user_skills':
                # Example usage in your function:
                ROOT_DIR = Path.cwd()
                metrics_file_path = ROOT_DIR / 'metrics.md'  # Path to the metrics.md file

                # Call the function to extract keywords from the metrics.md file
                resume_text = extract_text_from_pdf_matthew(file_path)
                resume_keywords = preprocess_text(resume_text)
                metrics_keywords = extract_keywords_from_metrics(metrics_file_path, resume_keywords, threshold=80)
                matching_keywords = compare_resume_to_metrics(resume_keywords, metrics_keywords)                
                
                #Hard Skill insert
                number_of_hours = request.form['number_of_hours']
                certification_number = request.form['certification_number']
                education_level = request.form['highest_education_obtained']
                matching_keywords_string = ', '.join(matching_keywords)

                stored_text = str({'Resume Text': matching_keywords_string , 'Number of hours': number_of_hours, 'Certification number': certification_number, 'Education level': education_level})
                # Insert resume_text into database
                userid = session['id']
                insert_resume_text(userid, stored_text)
                con = get_db_connection()
                cur = con.cursor()
                cur.execute("SELECT id,username FROM userdata WHERE id = ?", (userid,))
                rows = cur.fetchall()
                con.close()
            
                # Fetch soft and hard skills from the database
                soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
                if  soft_skills_list == [] or hard_skills_list == []:
                    return render_template('profile.html', rows=rows)
                else :
                    return render_template('profile.html', rows=rows, soft_skills_list=soft_skills_list,hard_skills_list=hard_skills_list)

        else:
            userid = session['id']
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT id,username,feedback FROM userdata WHERE id = ?", (userid,))
            rows = cur.fetchall()
            con.close()
           
            # Fetch soft and hard skills from the database
            soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
            if  soft_skills_list == [] or hard_skills_list == []:
                return render_template('profile.html', rows=rows)
            else :
                return render_template('profile.html', rows=rows, soft_skills_list=soft_skills_list,hard_skills_list=hard_skills_list)

# Route for generating the hard skills plot
@profile_page_blueprint.route('/plot.png')
def plot():
        userid = session['id']
        soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
        if soft_skills_list == [] or hard_skills_list == []:
            return render_template('404.html')
        else:
            # Generate the plot using the fetched data
            img_io = hard_skills(hard_skills_list)
            return send_file(img_io, mimetype='image/png')
    
# Route for generating the soft skills plot
@profile_page_blueprint.route('/plotsoftskills.png')
def plot_soft_skills():
        userid = session['id']
        soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
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