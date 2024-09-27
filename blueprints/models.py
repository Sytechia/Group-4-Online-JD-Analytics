import os
from secret_key import openai_api_key
from controllers.db_connections import get_db_connection
from flask_login import UserMixin

class Config:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # OpenAI API Key (set your OpenAI API key here or through environment variable)
    OPENAI_API_KEY = os.environ.get(openai_api_key)

class User(UserMixin):
    def __init__(self, id, username, hashed_password,nested_skills,soft_skills,hard_skills, is_admin):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password
        self.nested_skills = nested_skills
        self.soft_skills = soft_skills
        self.hard_skills = hard_skills
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM userdata WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return User(user[0], user[1], user[2], user[3],user[4], user[5], user[6])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM userdata WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(user[0], user[1], user[2], user[3],user[4], user[5], user[6])
        return None
    