# Welcome to Group 4's Chatbot!


This project is designed to follow the Flask framework's **blueprint** structure, allowing for better organization, modularity, and collaborative development. While this README is still a work in progress, we will continue to update it as the project evolves.

The goal is to make collaboration seamless by adhering to Flask's best practices. At first, the folder structure may seem confusing, but as we proceed, you should find this structure beneficial as compared to lumping all our code together

## What Are Flask Blueprints?

In Flask, **blueprints** allow us to organize our application into distinct components or modules, which makes the codebase more manageable as the application grows. Blueprints enable us to split different parts of the app (such as routes, templates, static files, etc.) into smaller, self-contained segments.

This approach improves modularity, reusability, and maintainability. It also simplifies collaboration by allowing us to work on separate parts of the application independently, without affecting other components.

Key benefits of using blueprints:

-   **Modularity:** Makes it easier to structure your app into logical components.
-   **Reusability:** Blueprints can be reused across different projects.

Below is an explaination of this folder structure:

**blueprints\static** - This is where css and js will go.
**blueprints\templates** - This is where html will go.
**blueprints\init.py** - This is where connections will go e.g. APIs, database connections
**blueprints\models.py** - This is where objects like forms, classes will go.
**blueprints\routes.py** - This is where will will implement most of the logic there.

## Getting Started with Blueprints

If you're unfamiliar with Flask blueprints, here are some helpful resources to get you up to speed:

-   [Real Python - Flask Blueprints](https://realpython.com/flask-blueprint/)
-   [Flask Documentation: Layouts](https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/)
-   [YouTube - Flask Blueprints Tutorial](https://www.youtube.com/watch?v=_LMiUOYDxzE)

Feel free to explore these links, as they provide a some foundation for understanding how blueprints help in building scalable web applications.