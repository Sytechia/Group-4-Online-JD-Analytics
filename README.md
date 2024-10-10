# Welcome to Group 4's Chatbot!

In today's competitive job market, numerous popular platforms such as LinkedIn, Indeed, and others are used by companies to post job openings across a variety of industries and regions. These job postings typically contain valuable information including position levels (entry, associate, mid-senior, executive, director), company details, job locations, required qualifications, skillsets, and the date of posting. However, extracting and analyzing this information in a meaningful way to understand the competencies required for different roles across various sectors remains a challenge. 

The purpose of this project is to develop a comprehensive system that analyzes job descriptions from multiple job platforms. By leveraging data crawling techniques, we aim to collect job posting data, including key elements such as job titles, locations, and skill requirements. The gathered data will be processed and cleaned to identify patterns and trends in the skills demanded for specific job levels and industries. Ultimately, this analysis will provide insights into the evolving competency landscape, helping stakeholders better understand the key qualifications and skills necessary for various positions in today’s job market. 

This project will involve building a web application that not only automates the data collection process but also performs data cleaning, topic modelling, keyword extraction, and data visualization with the end goal of providing users with actionable insights into the skills required for different job roles. 

## What Are Flask Blueprints?

In Flask, **blueprints** allow us to organize our application into distinct components or modules, which makes the codebase more manageable as the application grows. Blueprints enable us to split different parts of the app (such as routes, templates, static files, etc.) into smaller, self-contained segments.

This approach improves modularity, reusability, and maintainability. It also simplifies collaboration by allowing us to work on separate parts of the application independently, without affecting other components.

Key benefits of using blueprints:

-   **Modularity:** Makes it easier to structure your app into logical components.
-   **Reusability:** Blueprints can be reused across different projects.


## File Structure 
```

│   README.md
│   requirements.txt
│   secret_key.py
│   run.py    

└───blueprints
│   │   __Init__.py
│   │   models.py
│   │   resume.py
│   │   routes.py
│   │
│   └───static
│   │    │   index.css   
│   │ 
│   └───templates
│        │  404.html
│        │  500.html
│        │  base.html
│        │  feedback.html
│        │  home.html
│        │  login.html
│        │  profile.html
│        │  register.html
|        |  admindashboard.html
|        |  navbar.html
│   
└───uploads
    │   ZacharyPhoonJunZe_Resume.pdf
```
## Explanation For Each File's Purpose
| File Path    | Purpse |
| -------- | ------- |
| **run.py**  | This is where the Flask Web Application is started. |
| **secret_key.py**  | This is where the serect keys and / or API Keys are stored for they are to be called. |
| **requirement.py**  | This is where the required library to be installed. |
| **blueprints/static**  | This is where CSS and JS will go. |
| **blueprints/templates** | This is where HTML will go. |
| **blueprints/__init__.py** | This is where connections will go (e.g., APIs, database connections). |
| **blueprints/models.py** | This is where objects like forms and classes will go. |
| **blueprints/routes.py**| This is where we will implement most of the logic.|

## Guides
Here are Some guides to aid you.

| Library  | Remarks | Links  |
| -------- | ------- |------- |
|  Flask   | If you're unfamiliar with Flask blueprints, here are some helpful resources to get you up to speed.   | <ul> <li> [Real Python - Flask Blueprints](https://realpython.com/flask-blueprint/)</li> <li>[Flask Documentation: Layouts](https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/) </li> <li> [YouTube - Flask Blueprints Tutorial](https://www.youtube.com/watch?v=_LMiUOYDxzE)</li> <ul>|
|OpenAI |  To understand what parameters you require, please refer to the documentation.  | <ul> <li> [OpenAI Documentation](https://platform.openai.com/docs/overview)<ul>|


Feel free to explore these links, as they provide a some foundation for understanding how blueprints help in building scalable web applications.