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
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, 'id'):
            raise AttributeError("User object must have an 'id' attribute")
        print(f"User created with id: {self.id}")  # Debugging statement

    def get_id(self):
        return str(self.id)  # Ensure the ID is returned as a string
    
    @staticmethod
    def get(user_id):
        print(f"Attempting to fetch user with id: {user_id}")  # Debugging statement
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the column names correctly from the second item of each tuple
        cursor = cursor.execute('PRAGMA table_info(userdata)')
        columns = [column[1] for column in cursor.fetchall()]  # Extract the second element (column name)

        # Fetch the user data
        cursor.execute('SELECT * FROM userdata WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            # Zip the correct column names with the user data to create a dictionary of attributes
            user_dict = dict(zip(columns, user_data))
            return User(**user_dict)
        return None