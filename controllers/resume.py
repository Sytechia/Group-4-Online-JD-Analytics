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
        max_tokens=500  # Adjust as needed
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
    Based on the following CV, please analyze and summarize the candidate's experience, skills, and qualifications. 
    Then, suggest relevant 3 jobs that align well with their background and expertise.
    CV: {cv_text}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Ensure this is a valid model name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500  # Adjust as needed
    )
    # Extract the job suggestions from the response
    job_suggestions = response.choices[0].message.content.strip()
    
    return (f'{job_suggestions}')

def ai_suggest_job(cv_text):
    job_feedback = suggest_job(cv_text)
    job_feedback = format_feedback(job_feedback)
    return (f'{job_feedback}')

def extract_text_from_pdf_matthew(pdf_file_path):
    text = ""
    try:
        # Open the PDF file using PdfReader
        reader = PdfReader(pdf_file_path)
        
        # Iterate over each page and extract text
        for page in reader.pages:
            extracted_text = page.extract_text()
            
            if extracted_text:
                text += extracted_text

        # Step 1: Clean up CID-related errors (patterns like (cid:###)), replacing with space
        text = re.sub(r'\(cid:\d{3,}\)', ' ', text)

        # Step 2: Insert spaces between lowercase and uppercase letters (for concatenated words)
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

        # Step 3: Normalize multiple spaces and remove newlines
        text = re.sub(r'\s+', ' ', text).strip()

        # Step 4: Convert text to lowercase
        text = text.lower()
    except Exception as e:
        print(f"Error extracting text: {e}")

    return text

# Step 2: Preprocess the extracted resume text
def preprocess_text(text):
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Tokenize text into words
    words = word_tokenize(text)

    # Remove stopwords (e.g. "and", "the", "is")
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]

    return filtered_words

# Step 3: Extract skills from metrics.md file by cleaning up the HTML tags
def extract_keywords_from_metrics(file_path, resume_keywords, threshold=80):
    with open(file_path, 'r') as file:
        metrics_text = file.read()

    # Using BeautifulSoup to parse the HTML-like content in the file
    soup = BeautifulSoup(metrics_text, 'html.parser')

    # Find all list items <li> which contain the skills and convert them to lowercase
    skills_list = [li.get_text(strip=True).lower() for li in soup.find_all('li')]


    # Use fuzzy matching to include similar keywords
    similar_keywords = []
    
    for skill in skills_list:
        # Use fuzzywuzzy to find keywords in the resume that match the skill with a given threshold
        matches = process.extractBests(skill, resume_keywords, scorer=fuzz.ratio, score_cutoff=threshold)
        # If there are matches, append the matched keyword to the similar_keywords list
        for match in matches:
            similar_keywords.append(match[0])  

    # Combine skills_list and similar_keywords into one list
    combined_keywords = skills_list + similar_keywords

    # Return the combined list of skills and similar keywords
    return combined_keywords

# Step 4: Compare resume keywords with metrics.md keywords
def compare_resume_to_metrics(resume_keywords, combined_keywords):


    # Step 4: Compare resume keywords with combined keywords
    matching_keywords = [word for word in resume_keywords if word in combined_keywords]

    return matching_keywords

# Function to insert resume text into the nested_skills column where userid = 1
def insert_resume_text(userid, resume_text):
    con = get_db_connection()  # Establish connection using helper function
    cur = con.cursor()

    try:
        # Check if the user with userid 1 exists
        cur.execute("SELECT 1 FROM userdata WHERE id = ?", (userid,))
        user_exists = cur.fetchone()

        if user_exists:
            # Insert the resume text into the nested_skills column where userid = 1
            cur.execute("UPDATE userdata SET nested_skills = ? WHERE id = ?", (resume_text, userid))
            con.commit()
            calculate_score(userid)
        else:
            # If user doesn't exist, return an error for frontend to handle
            print("User ID not found. Trigger JavaScript alert for account creation.")
            return {"status": "error", "message": "User ID not found. Please create an account."}

    except sqlite3.Error as e:
        print(f"An error occurred while interacting with the database: {e}")
        return {"status": "error", "message": "Database error."}
    
    finally:
        con.close()  # Close the connection
        
def insert_recommended_job(cv_text, userid):
    # Get job suggestions using the AI function
    job_feedback = ai_suggest_job(cv_text)
    
    # Connect to the database
    con = get_db_connection()
    cur = con.cursor()

    # Insert job suggestions into the 'recommended_job' column for the current user
    cur.execute("UPDATE userdata SET recommended_job = ? WHERE id = ?", (job_feedback, userid))
    
    # Commit the changes and close the connection
    con.commit()
    con.close()

    # Optionally return a confirmation or success message
    return "Job recommendations saved successfully."

#<-----------------Matthew Codes End ------------------------>