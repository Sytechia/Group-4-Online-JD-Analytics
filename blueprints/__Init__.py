from flask import Flask,request
from blueprints.routes import home_blueprint, login_blueprint, register_user_blueprint, profile_page_blueprint, error_blueprint, error500_blueprint
import sqlite3

app = Flask(__name__)
app.register_blueprint(home_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(register_user_blueprint)
app.register_blueprint(profile_page_blueprint)
app.register_blueprint(error_blueprint)
app.register_blueprint(error500_blueprint)

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('''CREATE TABLE IF NOT EXISTS jobdesc (
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
            
conn.commit()

conn.close()

def AddRecord():
    # # convert dictionary to data frame
    # df = pd.DataFrame(data = dictionary)

    # # create new database and cursor
    # connection = sqlite3.connect("database.db")
    # cursor = connection.cursor()

    # # create database table and insert all data frame rows
    # cursor.execute("CREATE TABLE jobdesc (Distribution, " + ",".join(column_names)+ ")")
    # for i in range(len(df)):
    #     cursor.execute("insert into jobdesc values (?,?,?,?,?,?,?,?,?,?,?,?)", df.iloc[i])

    # # PERMANENTLY save inserted data in "database.db"
    # connection.commit()

    # connection.close()
    pass


