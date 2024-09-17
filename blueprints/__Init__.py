from flask import Flask, request
from blueprints.routes import home_blueprint, login_blueprint, register_user_blueprint, profile_page_blueprint, \
    error_blueprint, error500_blueprint
import sqlite3
import scrapy
import re

app = Flask(__name__)
app.register_blueprint(home_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(register_user_blueprint)
app.register_blueprint(profile_page_blueprint)
app.register_blueprint(error_blueprint)
app.register_blueprint(error500_blueprint)


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
            job_description TEXT,
            company_name TEXT NOT NULL,
            company_link TEXT,
            company_location TEXT NOT NULL,
            unique(job_detail_url,company_name,job_listed)
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


