import openai
from PyPDF2 import PdfReader
import docx
from secret_key import openai_api_key
from blueprints.models import Config

import re
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from controllers.db_connections import get_db_connection
import sqlite3
from controllers.skill_diagram import calculate_score

# Initialize OpenAI API key
openai.api_key = openai_api_key

# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file_path):
    reader = PdfReader(pdf_file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from a .docx file
def extract_text_from_docx(docx_file_path):
    doc = docx.Document(docx_file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

# Function to get CV feedback using OpenAI API, ZACHARY'S CODE
def get_cv_feedback(cv_text,foi):
    prompt = f"""
    You are an expert in recruitment and resume evaluation. Please review the following CV and provide remarks regarding:
    1. Formatting
    2. Grammar and Language
    3. Key Skills Highlighted
    4. Alignment with potential job roles
    5. Areas of improvement
    While considering my interest in the role of an {foi}
    CV: {cv_text}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Ensure this is a valid model name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800  # Adjust as needed
    )
    # Extract the feedback from the response
    feedback = response.choices[0].message.content.strip()
    
    return (f'{feedback}')

def process_cv(file_path, filename,foi):
    if filename.endswith('.pdf'):
        cv_text = extract_text_from_pdf(file_path)
    elif filename.endswith('.docx'):
        cv_text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

    # Get feedback from OpenAI
    feedback = get_cv_feedback(cv_text,foi)
    feedback = format_feedback(feedback)
    return (f'{feedback}')
    

def format_feedback(feedback):
    # Replace ### with <li>
    feedback = re.sub(r'###', '<li>', feedback)
    # Replace ** with <b>
    feedback = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', feedback)
    return feedback

#<-----------------Matthew Codes Start ------------------------>
# Function to get CV feedback using OpenAI API, MATTHEW'S CODE
def suggest_job(cv_text):
    prompt = f"""
    You are an expert career advisor. 
    Based on the following CV, using the candidate's experience, skills, and qualifications. 
    Suggest relevant 3 jobs that align well with their background and expertise.
    CV: {cv_text}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    job_suggestions = response.choices[0].message.content.strip()
    
    return (f'{job_suggestions}')

def ai_suggest_job(cv_text):
    job_feedback = suggest_job(cv_text)
    job_feedback = format_feedback(job_feedback)
    return (f'{job_feedback}')

def extract_text_from_pdf_matthew(pdf_file_path):
    text = ""
    try:
        reader = PdfReader(pdf_file_path)
        for page in reader.pages:
            extracted_text = page.extract_text()
            
            if extracted_text:
                text += extracted_text

        text = re.sub(r'\(cid:\d{3,}\)', ' ', text) # Clean up CID-related errors
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text) # Insert spaces between lower and upper case letters
        text = re.sub(r'\s+', ' ', text).strip() #Normalize multiple spaces, remove newlines
        text = text.lower()
        
    except Exception as e:
        print(f"Error extracting text: {e}")

    return text

def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Remove special characters and numbers
    words = word_tokenize(text) # Tokenize text into words using nltk
    stop_words = set(stopwords.words('english')) # Remove stopwords using nltk
    filtered_words = [word for word in words if word not in stop_words]
    
    return filtered_words

def extract_keywords_from_metrics(file_path, resume_keywords, threshold=80):
    with open(file_path, 'r') as file:
        metrics_text = file.read()

    soup = BeautifulSoup(metrics_text, 'html.parser') # Parse HTML-like content
    skills_list = [li.get_text(strip=True).lower() for li in soup.find_all('li')] # find <li> items, convert to lowercase

    similar_keywords = []
    
    for skill in skills_list:
        # Use fuzzywuzzy to find keywords in the resume that match the skill with a given threshold
        matches = process.extractBests(skill, resume_keywords, scorer=fuzz.ratio, score_cutoff=threshold)
        for match in matches:
            similar_keywords.append(match[0])  

    combined_keywords = skills_list + similar_keywords
    return combined_keywords

def compare_resume_to_metrics(resume_keywords, combined_keywords):
    matching_keywords = [word for word in resume_keywords if word in combined_keywords]
    return matching_keywords

def insert_resume_text(userid, resume_text):
    con = get_db_connection()  
    cur = con.cursor()

    try:
        cur.execute("SELECT 1 FROM userdata WHERE id = ?", (userid,))
        user_exists = cur.fetchone()

        if user_exists:
            cur.execute("UPDATE userdata SET nested_skills = ? WHERE id = ?", (resume_text, userid))
            con.commit()
            calculate_score(userid)
        else:
            return {"status": "error", "message": "User ID not found. Please create an account."}

    except sqlite3.Error as e:
        return {"status": "error", "message": "Database error."}
    
    finally:
        con.close()
        
def insert_recommended_job(cv_text, userid):
    job_feedback = ai_suggest_job(cv_text)

    con = get_db_connection()
    cur = con.cursor()
    cur.execute("UPDATE userdata SET recommended_job = ? WHERE id = ?", (job_feedback, userid))
    con.commit()
    con.close()
    return job_feedback

#<-----------------Matthew Codes End ------------------------>