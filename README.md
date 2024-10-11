# Welcome to Group 4's Chatbot!

In today's competitive job market, numerous popular platforms such as LinkedIn, Indeed, and others are used by companies to post job openings across a variety of industries and regions. These job postings typically contain valuable information including position levels (entry, associate, mid-senior, executive, director), company details, job locations, required qualifications, skillsets, and the date of posting. However, extracting and analyzing this information in a meaningful way to understand the competencies required for different roles across various sectors remains a challenge. 

The purpose of this project is to develop a comprehensive system that analyzes job descriptions from multiple job platforms. By leveraging data crawling techniques, we aim to collect job posting data, including key elements such as job titles, locations, and skill requirements. The gathered data will be processed and cleaned to identify patterns and trends in the skills demanded for specific job levels and industries. Ultimately, this analysis will provide insights into the evolving competency landscape, helping stakeholders better understand the key qualifications and skills necessary for various positions in today’s job market. 

This project will involve building a web application that not only automates the data collection process but also performs data cleaning, topic modelling, keyword extraction, and data visualization with the end goal of providing users with actionable insights into the skills required for different job roles. 

## Core Frameworks and Libraries
| Python Module    | Purpose |
| -------- | ------- |
|Flask| Utilized as the web framework for building the backend application.|
|SQLite| Employed as the database system to store job data and user information.|
|Scrapy| Used for web scraping job postings from online platforms.|
|BeautifulSoup4| Implemented for parsing and extracting information from HTML content.|
|FuzzyWuzzy| Used for keyword matching and similarity scoring in resume analysis.|
|Matplotlib| Employed for creating data visualizations.|
|OpenAI API| Integrated for natural language processing tasks such as resume analysis and standardizing job titles.|
|spaCy| To compare the similarity between two skills (phrases or words) based on their semantic meaning.|
|NLTK| Used for text processing tasks such as tokenization, stopword removal, and stemming/lemmatization in resume analysis.|


## File Structure 
```
Main Folder
│   README.md
│   database.db
│   requirements.txt
│   secret_key.py
│   run.py    

└───blueprints
│   │   __Init__.py
│   │   models.py
│   │   routes.py
│   │
│   └───static
│   │    │   index.css   
│   │ 
│   └───templates
│        │  404.html
│        │  500.html
│        │  base.html
│        │  home.html
│        │  login.html
│        │  profile.html
│        │  register.html
|        |  admindashboard.html
|        |  navbar.html
│   
└───controllers
│   │   resume.py
│   │   crawler.py
│   │   db_connections.py
│   │   parse.py
│   │   skill_diagram.py
│     
└───uploads
    │   ZacharyPhoonJunZe_Resume.pdf
    |   Matthew_Goh_Resume.pdf
    |   Matthew_Goh_Resume_1.pdf
    |   Peter_resume_2024.pdf
    |   Ray_LinkedIn.pdf
    |   Thaedeus_Resume_LinkedIn.pdf
```
## Explanation For Each File's Purpose
| File Path    | Purpose |
| -------- | ------- |
| **run.py**  | This is where the Flask Web Application is started. |
| **secret_key.py**  | This is where the serect keys and / or API Keys are stored for they are to be called. |
| **requirement.txt**  | This is where the required library to be installed. |
|**database.db**|Sample Database Initilised|
|**metric.md**|Metric System for Grading and Scoring for User's Skills|
| **blueprints/static/index.css**  | Web applications Global CSS.|
| **blueprints/templates** | This is where HTML templates will go. |
| **blueprints/__init__.py** | This is where connections will go (e.g., APIs, database connections). |
| **blueprints/models.py** | This is where objects like forms and classes will go. |
| **blueprints/routes.py**| This is where we will implement most of the logic.|
|**controller/crawler.py**| Code related to the web crawler.|
|**controller/parse_data.py**| Code realted to cleaning up the data from the crawler.|
|**controller/db_connections.py**|Database related fucntions. |
|**controller/resume.py**| Code regarding all the resume handling such as Extraction and string manupulation.|
|**controller/skill_diagram.py**| Code regaridng processing of user skills to be scored as well as the plotting of digrams.|


## Setup Guide
1. Clone the Github Repository
2. Extract the content.
3. Locate the Main Folder.
4. run `python pip install -r requiremnt.txt`
5. Replace text with OpenAI API key in `secret_key.py`
6. run `run.py`
7. Enjoy your experience using CareerBridge by using your favourite browser and going to `127.0.0.1:5000`

## User's Guide to usage
- Place link here once video is ready.

# Some Knowledge for sharing

## What Are Flask Blueprints?

In Flask, **blueprints** allow us to organize our application into distinct components or modules, which makes the codebase more manageable as the application grows. Blueprints enable us to split different parts of the app (such as routes, templates, static files, etc.) into smaller, self-contained segments.

This approach improves modularity, reusability, and maintainability. It also simplifies collaboration by allowing us to work on separate parts of the application independently, without affecting other components.

Key benefits of using blueprints:

-   **Modularity:** Makes it easier to structure your app into logical components.
-   **Reusability:** Blueprints can be reused across different projects.

## Reference Guides.
Here are Some guides to aid you.

| Library  | Remarks | Links  |
| -------- | ------- |------- |
|  Flask   | If you're unfamiliar with Flask blueprints, here are some helpful resources to get you up to speed.   | <ul> <li> [Real Python - Flask Blueprints](https://realpython.com/flask-blueprint/)</li> <li>[Flask Documentation: Layouts](https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/) </li> <li> [YouTube - Flask Blueprints Tutorial](https://www.youtube.com/watch?v=_LMiUOYDxzE)</li> <ul>|
|OpenAI |  To understand what parameters you require, please refer to the documentation.  | <ul> <li> [OpenAI Documentation](https://platform.openai.com/docs/overview)<ul>|
|spaCy|To udnerstand what parameters you require, please refer to the documentation|<ul><li>[spaCy Documentation](https://spacy.io/usage/spacy-101)</li></ul> |
|Matplotlib | To udnerstand what parameters you require, please refer to the documentation|[Matplotlib Documentation](https://matplotlib.org/stable/index.html) |


Feel free to explore these links, as they provide a some foundation for understanding how blueprints help in building scalable web applications.