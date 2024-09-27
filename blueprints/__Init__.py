from flask import Flask, request
from blueprints.routes import home_blueprint, login_blueprint, register_user_blueprint, profile_page_blueprint, \
    error_blueprint, error500_blueprint, logout_blueprint, admin_page_blueprint
import sqlite3
import scrapy
import re
from flask_login import LoginManager
import os
from flask_session import Session
from .models import User
import subprocess

app = Flask(__name__)
app.secret_key = 'dev'
app.register_blueprint(home_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(logout_blueprint)
app.register_blueprint(register_user_blueprint)
app.register_blueprint(profile_page_blueprint)
app.register_blueprint(admin_page_blueprint)
app.register_blueprint(error_blueprint)
app.register_blueprint(error500_blueprint)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
subprocess.run('python -m spacy download en_core_web_md', shell=True, check=True)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Use this as initial function to set up the database
def setup_database():
    try:
        # Database path needs to be here to avoid circular imports
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        CONFIG_PATH = os.path.join(ROOT_DIR, 'database.db')
        print(f"Database path: {CONFIG_PATH}")

        conn = sqlite3.connect(CONFIG_PATH)
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobdesc (
                    id INTEGER PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    original_job_title TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    job_detail_url TEXT NOT NULL,
                    job_listed TEXT NOT NULL,
                    job_description TEXT,
                    company_name TEXT NOT NULL,
                    company_link TEXT,
                    company_location TEXT NOT NULL,
                    job_position_level TEXT,
                    UNIQUE(job_detail_url, company_name, job_listed)
                )
            ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS userdata (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    nested_skills BLOB NOT NULL,
                    soft_skills BLOB NOT NULL,
                    hard_skills BLOB NOT NULL,
                    is_admin INTEGER NOT NULL,
                    feedback BLOB,
                    field_of_interest TEXT
                )
            ''')
        conn.commit()
        print("Tables created successfully")
        return conn, cursor
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None, None

try:
    conn, cursor = setup_database()
    if conn:
        conn.close()
        print("Connected to database successfully")
    else:
        print("Failed to connect to the database")
except sqlite3.Error as e:
    print(f"Exception: {e}")



