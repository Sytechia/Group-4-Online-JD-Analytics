from flask import Blueprint, render_template, request, jsonify, flash, send_file, flash, redirect, current_app, session
import sys

from nltk import sent_tokenize

from secret_key import client
from controllers.db_connections import get_db_connection
from controllers.skill_diagram import check_metrics_for_plot, hard_skills, soft_skills,calculate_score
from controllers.crawler import JobSpider

import os
from controllers.resume import allowed_file, process_cv, format_feedback, suggest_job, ai_suggest_job, insert_recommended_job
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

@home_blueprint.route('/', methods=['GET'])
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
        query = "SELECT * FROM jobdesc"
        filters = []

        levels = request.args.getlist('level')
        selected_titles = request.args.getlist('job_title')

        query = "SELECT * FROM jobdesc WHERE 1=1"
        params = []

        print(f'Filtered Levels {levels}')
        print(f'selected titles {selected_titles}')

        if selected_titles:
            title_filters = " OR ".join("job_title LIKE ?" for _ in selected_titles)
            query += " AND (" + title_filters + ")"
            params.extend(['%' + title + '%' for title in selected_titles])  # Wrap titles with wildcards for partial matching

        if levels:
            query += " AND job_position_level IN ({})".format(','.join('?' for _ in levels))
            params.extend(levels)

        rows = con.execute(query, params).fetchall()

        # Fetch the 10 most recent job descriptions from the database
        cur.execute("SELECT job_title, job_detail_url,job_listed,job_description, company_name, company_location FROM jobdesc order by job_listed asc limit 10")
        recent_10_rows = cur.fetchall()
        # Fetch the 10 most recent job descriptions from the database that contain the word 'data'
        cur.execute("SELECT job_title, job_detail_url,job_listed,job_description, company_name, company_location FROM jobdesc where job_title LIKE '%data%' order by job_listed asc limit 10")
        top_10_rows = cur.fetchall()

        # Fetch all the job titles from JobSpider Class
        job_titles = JobSpider.get_job_titles()

        # Commit the changes and close the connection
        con.close()
        
        user = ''

        if 'id' in session:
            user = session
            print(f'Logged in as {user["username"]}')

        return render_template('home.html',user = user, rows = rows, selected_titles=selected_titles, selected_levels = levels, recent_10_rows = recent_10_rows, top_10_rows = top_10_rows, job_titles = job_titles)
    
@home_blueprint.route('/search_suggestions', methods=['GET'])
def search_suggestions():
    query = request.args.get('query', '')  # Get the query string
    suggestions = get_search_suggestions(query) if query else []
    return jsonify(suggestions)  # Return the list as JSON

def get_search_suggestions(query):
    con = get_db_connection()  # Connect to your SQLite or other database
    cur = con.cursor()

    # Query the database for job titles matching the search query
    cur.execute("SELECT job_title FROM jobdesc WHERE job_title LIKE ? LIMIT 10", ('%' + query + '%',))
    results = cur.fetchall()
    con.close()

    # Return a list of matching job titles
    return [result[0] for result in results]

@home_blueprint.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')  # Get the search query from the form
    if query:
        con = get_db_connection()  # Establish a connection to your database
        cur = con.cursor()
        
        # Fetch job titles that match the search query
        cur.execute("SELECT * FROM jobdesc WHERE job_title LIKE ?", ('%' + query + '%',))
        results = cur.fetchall()
        con.close()

        # Prepare the results as JSON data
        job_list = [{
            'job_title': row['job_title'],
            'job_description': row['job_description'],
            'company_name': row['company_name'],
            'job_listed': row['job_listed'],
            'job_detail_url': row['job_detail_url']
        } for row in results]

        return jsonify(job_list)  # Return the list of jobs as JSON data
    
    return jsonify([])  # Return an empty list if no query

@login_blueprint.route('/login',methods = ["POST","GET"])
def index():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'login':
            # Handles Login
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
                session['is_admin'] = user['is_admin']
                
                return redirect("/")
            else:
                flash('User does not exist or wrong password', 'danger')
                return render_template("login.html")
        else:
            # Handles Register
            name = request.form.get("name")  
            password = request.form.get("password1")
            password2 = request.form.get("password2")

            if not (name and password and password2):
                flash('All fields are required.', 'danger')
                return render_template("login.html")  
            if password != password2:
                flash('Password do not match.', 'danger')
                return render_template("login.html")            

            # Demo Purpose
            is_admin = 0

            con = get_db_connection()  
            cur = con.cursor()

            # Check if username already exists
            cur.execute("SELECT * FROM userdata WHERE username = ?", (name,))
            existing_user = cur.fetchone()

            if existing_user:
                flash('Username already exists.', 'danger')
                return render_template("login.html")

            hashed_password = generate_password_hash(password)

            cur.execute("INSERT into userdata (username, hashed_password,is_admin) values (?,?,?)",(name,hashed_password,is_admin)) 
   
            con.commit()

            cur.execute('SELECT id FROM userdata WHERE username = ?', (name,))  
            new_user_id = cur.fetchone()['id'] 

            userobj = User.get(new_user_id)
            login_user(userobj)
            session['id'] = new_user_id
            session['username'] = name
            session['is_admin'] = is_admin
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
        
        # AI Job Suggestions: Extract resume text and get job suggestions
        resume_text = extract_text_from_pdf_matthew(file_path)
        insert_recommended_job(resume_text, userid)
        
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
    session.pop("is_admin", None)
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
            userid = session['id']
            
            # Process CV to update job recommendation
            resume_text = extract_text_from_pdf_matthew(file_path)
            recommended_job = insert_recommended_job(resume_text, userid)
                        
            # Process the CV and get feedback
            con = get_db_connection()
            cur = con.cursor()
            cur.execute('SELECT field_of_interest FROM userdata WHERE id = ?', (userid,))  
            foi = cur.fetchone()['field_of_interest'] 
            feedback = str(process_cv(file_path, filename,foi))
            cur.execute("UPDATE userdata SET feedback = ?, recommended_job = ? WHERE id = ?", (feedback,recommended_job,userid,))
            con.commit()
            cur.execute('SELECT recommended_job FROM userdata WHERE id = ?', (userid,))
            recommended_job = cur.fetchone()['recommended_job']            
            con.close()
        
            # Fetch soft and hard skills from the database
            soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
            if  soft_skills_list == [] or hard_skills_list == []:
                return render_template('profile.html' ,feedback=feedback,recommended_job=recommended_job)
            else :
                return render_template('profile.html', feedback=feedback,soft_skills_list=soft_skills_list,hard_skills_list=hard_skills_list,recommended_job=recommended_job)
        
        elif form_type == 'update_user_skills':
            # Example usage in your function:
            ROOT_DIR = Path.cwd()
            metrics_file_path = ROOT_DIR / 'metrics.md'  # Path to the metrics.md file

            # Call the function to extract keywords from metrics.md file
            resume_text = extract_text_from_pdf_matthew(file_path)
            resume_keywords = preprocess_text(resume_text)
            metrics_keywords = extract_keywords_from_metrics(metrics_file_path, resume_keywords, threshold=80)
            matching_keywords = compare_resume_to_metrics(resume_keywords, metrics_keywords)          
            
            recommended_job = ai_suggest_job(resume_text)
            foi = request.form.get('foi', 'General')  # Use a default or retrieve from form input
            feedback = process_cv(file_path, filename, foi)
            
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
            cur.execute("UPDATE userdata SET nested_skills = ?, recommended_job = ?, feedback = ? WHERE id = ?", (stored_text, recommended_job, feedback, userid))
            con.commit()
            cur.execute('SELECT recommended_job,feedback FROM userdata WHERE id = ?', (userid,))
            result = cur.fetchone()
            recommended_job = result['recommended_job'] 
            feedback = result['feedback'] 
            con.close()
        
            # Fetch soft and hard skills from the database
            soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
            if  soft_skills_list == [] or hard_skills_list == []:
                return render_template('profile.html', feedback=feedback,recommended_job=recommended_job)
            else :
                return render_template('profile.html',feedback=feedback,recommended_job=recommended_job, soft_skills_list=soft_skills_list,hard_skills_list=hard_skills_list)
    else:
        userid = session['id']
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT feedback, recommended_job FROM userdata WHERE id = ?", (userid,))
        result = cur.fetchone()
        
        if result:
            feedback = result['feedback']
            recommended_job = result['recommended_job']
        else:
            feedback = None
            recommended_job = None
        
        con.close()
        
        # Fetch soft and hard skills from the database
        soft_skills_list, hard_skills_list = check_metrics_for_plot(userid)
        if  soft_skills_list == [] or hard_skills_list == []:
            return render_template('profile.html',feedback=feedback, recommended_job=recommended_job)
        else :
            return render_template('profile.html', feedback=feedback, recommended_job=recommended_job, soft_skills_list=soft_skills_list,hard_skills_list=hard_skills_list)

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