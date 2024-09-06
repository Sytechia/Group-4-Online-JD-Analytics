from flask import Blueprint, render_template, request, jsonify
import sys
from secret_key import client

home_blueprint = Blueprint('home', __name__)


def chat_with_gpt(conversation_history):
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-4o-mini",
    )

    return chat_completion

conversation_history = []

@home_blueprint.route('/')
def index():
    return render_template('index.html')  # Your HTML file is named 'chat.html'


@home_blueprint.route('/submit', methods=['POST'])
def submit():
    user_input = request.form.get('user_input')
    conversation_history.append({
        "role": "user",
        "content": user_input,
    })
    # Get GPT's response based on the conversation history
    response = chat_with_gpt(conversation_history)

    # Get GPT's response message and add it to the conversation history
    assistant_response = response.choices[0].message.content.strip()

    conversation_history.append({
        "role": "assistant",
        "content": assistant_response,
    })

    # Process the input (e.g., print to terminal)
    print(f"User Message: {user_input},{assistant_response}")

    # Return the message back to be displayed in the chat interface
    return jsonify(user_input=user_input, assistant_response=assistant_response)

