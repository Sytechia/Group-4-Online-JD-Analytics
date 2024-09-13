import openai
from PyPDF2 import PdfReader
import docx
from secret_key import openai_api_key

# Initialize OpenAI API key
openai.api_key = openai_api_key

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

# Function to get CV feedback using OpenAI API
def get_cv_feedback(cv_text):
    prompt = f"""
    You are an expert in recruitment and resume evaluation. Please review the following CV and provide remarks regarding:
    1. Formatting
    2. Grammar and Language
    3. Key Skills Highlighted
    4. Alignment with potential job roles
    5. Areas of improvement
    
    CV: {cv_text}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",  # Ensure this is a valid model name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500  # Adjust as needed
    )
    print(response)
    print("this is a break between the response and the feedback")
    # Extract the feedback from the response
    feedback = response.choices[0].message.content
    print(feedback)
    return feedback

def process_cv(file_path, filename):
    if filename.endswith('.pdf'):
        cv_text = extract_text_from_pdf(file_path)
    elif filename.endswith('.docx'):
        cv_text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

    # Get feedback from OpenAI
    feedback = get_cv_feedback(cv_text)
    return feedback