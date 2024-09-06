from openai import OpenAI

client = OpenAI(
    api_key="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"
)



def chat_with_gpt(conversation_history):
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="gpt-4o-mini",
    )

    return chat_completion
if __name__ == '__main__':
    conversation_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break

        # Add user's input to the conversation history
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

        # Print GPT's response
        print(f"Chatbot response: {assistant_response}")