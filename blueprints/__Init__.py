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
        CREATE TABLE IF NOT EXISTS jobs (
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
            email TEXT NOT NULL, 
            name TEXT NOT NULL, 
            password TEXT NOT NULL 
        )
    ''')
    conn.commit()
    return conn, cursor


def AddRecord():
    pass


sql_statements = [
    '''CREATE TABLE IF NOT EXISTS jobdesc (
            id INTEGER PRIMARY KEY,
            job_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_detail_url TEXT NOT NULL,
            job_listed TEXT NOT NULL,
            company_name TEXT NOT NULL,
            company_link TEXT,
            company_location TEXT NOT NULL,
            unique(job_detail_url,company_name,job_listed)
    )''',
    '''CREATE TABLE IF NOT EXISTS userdata (
            id INTEGER PRIMARY KEY, 
            email TEXT NOT NULL, 
            name TEXT NOT NULL, 
            password TEXT NOT NULL 

    )''']

# create a database connection
conn = sqlite3.connect('database.db')
try:
    for statement in sql_statements:
        conn.execute(statement)

    conn.commit()
    conn.close()
    print("Connected to database successfully")
except sqlite3.Error as e:
    print(e)

# try:
#         # nm = request.form['nm']
#         # addr = request.form['add']
#         # city = request.form['city']
#         # zip = request.form['zip']

#         nm = 1
#         addr = 312
#         city = "Software Engineer"
#         zip = "https://sg.jobstreet.com/software-engineer-jobs?jobId=78833906&type=standard"
#         job_listed = "Software Engineer"
#         company_name = "APPLE"
#         company_link = "IDK"
#         company_location = "SINGAPORE"

#         # Connect to SQLite3 database and execute the INSERT
#         with sqlite3.connect('database.db') as con:
#             cur = con.cursor()
#             cur.execute("INSERT INTO jobdesc (id, job_id, job_title, job_detail_url, job_listed, company_name, company_link, company_location) VALUES (?,?,?,?,?,?,?,?)",
#                         (nm, addr, city, zip, job_listed, company_name, company_link, company_location))

#             con.commit()
#             msg = "Record successfully added to database"
# except:
#     con.rollback()
#     print("Error in the INSERT")

# finally:
#     con.close()


setup_database()


