import os
from secret_key import openai_api_key

class Config:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    # OpenAI API Key (set your OpenAI API key here or through environment variable)
    OPENAI_API_KEY = os.environ.get(openai_api_key)
