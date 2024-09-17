import sqlite3
from flask import request, jsonify

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
