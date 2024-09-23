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

app = Flask(__name__)
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

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Use this as initial function to set up the database
def setup_database():
    conn = sqlite3.connect('./database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobdesc (
            id INTEGER PRIMARY KEY,
            job_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_detail_url TEXT NOT NULL,
            job_listed TEXT NOT NULL,
            job_description TEXT,
            company_name TEXT NOT NULL,
            company_link TEXT,
            company_location TEXT NOT NULL,
            job_position_level TEXT,
            unique(job_detail_url,company_name,job_listed)
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
            is_admin INTEGER NOT NULL              
        )
    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS userdata (
                id INTEGER PRIMARY KEY, 
                email TEXT NOT NULL, 
                name TEXT NOT NULL, 
                password TEXT NOT NULL 
        )
    ''')
    conn.commit()
    return conn, cursor

def AddRecord():
    pass

try:
    conn, cursor = setup_database()
    conn.close()
    print("Connected to database successfully")
except sqlite3.Error as e:
    print(e)

setup_database()



