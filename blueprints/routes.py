from flask import Blueprint, render_template, request, jsonify,flash
import sys
from secret_key import client
import sqlite3

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

@profile_page_blueprint.route('/profile')
def index():
    con = get_db_connection()

    cur = con.cursor()
    cur.execute("SELECT * FROM userdata")
    rows = cur.fetchall()
    
    con.close()
    return render_template('profile.html',rows = rows)

@error_blueprint.app_errorhandler(404)
def page_not_found(e): # Return error 404
    return render_template('404.html'), 404

@error500_blueprint.app_errorhandler(500)
def page_not_found(e): # Return error 500
    return render_template('500.html'), 500