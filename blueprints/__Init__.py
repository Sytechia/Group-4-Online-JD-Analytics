from flask import Flask, request
from blueprints.routes import home_blueprint, login_blueprint, register_user_blueprint, profile_page_blueprint, \
    error_blueprint, error500_blueprint, logout_blueprint
import sqlite3
import scrapy
import re
from flask_login import LoginManager

app = Flask(__name__)
app.register_blueprint(home_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(logout_blueprint)
app.register_blueprint(register_user_blueprint)
app.register_blueprint(profile_page_blueprint)
app.register_blueprint(error_blueprint)
app.register_blueprint(error500_blueprint)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return 0


app.secret_key = 'f0d89bc17c879c8b6841607f74129badd0d52a5696cb02992e4e45068a547d62'

# Use this as initial function to set up the database
def setup_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobdesc (
            id INTEGER PRIMARY KEY,
            job_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_detail_url TEXT NOT NULL,
            job_listed TEXT NOT NULL,
            company_name TEXT NOT NULL,
            company_link TEXT,
            company_location TEXT NOT NULL,
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
    conn.commit()
    return conn, cursor

setup_database()


