import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # OpenAI API Key (set your OpenAI API key here or through environment variable)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'your-api-key-here'