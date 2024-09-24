import sqlite3
from flask import request, jsonify
import os


def get_db_connection():
    print("Getting db connection!!!!")
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_PATH = os.path.join(ROOT_DIR, 'database.db')
    if not os.path.exists(CONFIG_PATH):
        print("Error: Database file does not exist")
        return None
    else:
        conn = sqlite3.connect(CONFIG_PATH)
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
