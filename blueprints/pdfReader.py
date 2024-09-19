import re
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pdfplumber

# Step 1: Extract text from uploaded PDF using pdfplumber
def extract_text_from_pdf(pdf_file_path):
    text = ""
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text

        # Clean up CID-related errors (patterns like (cid:###)), replacing with space
        text = re.sub(r'\(cid:\d{3,}\)', ' ', text)

        # Remove extra newlines and normalize spaces
        text = re.sub(r'\s+', ' ', text).strip()

        # Convert text to lowercase
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

    # Remove stopwords
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

    # Debugging: print the extracted skills list
    # print(f"Extracted skills from metrics.md: {skills_list}")

    # Use fuzzy matching to include similar keywords
    similar_keywords = []
    
    for skill in skills_list:
        # Use fuzzywuzzy to find keywords in the resume that match the skill with a given threshold
        matches = process.extractBests(skill, resume_keywords, scorer=fuzz.ratio, score_cutoff=threshold)
        # If there are matches, print them for debugging
        if matches:
            print(f"Matches for '{skill}' from resume_keywords: {matches}")
        for match in matches:
            similar_keywords.append(match[0])  # Append matched keyword

    # Debugging: print the similar keywords found by fuzzy matching
    # print(f"Similar keywords found by fuzzywuzzy: {similar_keywords}")

    # Combine skills_list and similar_keywords into one list
    combined_keywords = skills_list + similar_keywords

    # Return the combined list of skills and similar keywords
    return combined_keywords

# Step 4: Compare resume keywords with metrics.md keywords
def compare_resume_to_metrics(resume_keywords, combined_keywords):
    # Debugging: Print the list of combined keywords
    # print(f"Combined Keywords (metrics and fuzzy matches): {combined_keywords}")

    # Step 4: Compare resume keywords with combined keywords
    matching_keywords = [word for word in resume_keywords if word in combined_keywords]

    # Debugging: Print the matching keywords found
    print(f"Matching Keywords from resume: {matching_keywords}")

    return matching_keywords


