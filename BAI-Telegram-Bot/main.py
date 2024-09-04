from typing import Final
from telegram import Update , ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes,AIORateLimiter,CallbackContext
from security import token,Bot_username,OpenAI_API_Key
from openai import OpenAI
import numpy as np
import tensorflow as tf
import io
import aiohttp
from PIL import Image


# Constants
TOKEN: Final[str] = token
BOT_USERNAME: Final[str] = Bot_username

"""Image Recognistion Pre-load"""
# Load a pre-trained model (e.g., MobileNetV2)
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Function to preprocess the image
def preprocess_image(image):
    image = image.resize((224, 224))  # Resize to model input size
    image_array = np.array(image)  # Convert to numpy array
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)  # Preprocess
    return image_array

# Function to decode predictions
def decode_predictions(predictions):
    decoded = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=3)[0]
    return decoded

"""Commands""" 
#Send a message when the command /help is issued.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

#Send a message when the command /help is issued.
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text("Help!")


"""Handlers"""
async def photo(update: Update, context: CallbackContext) -> None:
    """Image"""
    # Get the photo file
    file = await update.message.photo[-1].get_file()
    
    # Prepare an in-memory byte stream
    photo_stream = io.BytesIO()
    
    # Download the file content into the byte stream using aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as response:
            if response.status == 200:
                photo_stream.write(await response.read())
    
    # Move the stream's cursor to the beginning
    photo_stream.seek(0)
    
    # Open the image from the byte stream
    image = Image.open(photo_stream)
    
    # Preprocess the image
    preprocessed_image = preprocess_image(image)
    
    # Predict
    predictions = model.predict(preprocessed_image)
    decoded_predictions = decode_predictions(predictions)
    
    # Format the prediction into a message
    result_text = "I think this is:\n"
    for i, (imagenet_id, label, score) in enumerate(decoded_predictions):
        result_text += f"{i+1}: {label} ({score*100:.2f}%)\n"
    
    # Send the result back to the user
    await update.message.reply_text(result_text)

# Handle incoming messages
async def ask_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    message_type: str=update.message.chat.type
    text: str = update.message.text

    # Log users
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    
    #OpenAI ChatGPT API Client
    client = OpenAI(
    api_key= OpenAI_API_Key,
    )
    response = client.chat.completions.with_raw_response.create(
    messages=[{
        "role": "user",
        "content": text,
    }],
    model="gpt-4o-mini",
)
    # get the object that `chat.completions.create()` would have returned
    completion = response.parse()
    bot_reply= completion.choices[0].message.content
    print('Bot:', bot_reply)
    await update.message.reply_text(bot_reply)

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error: {context.error}')


"""Building the Telegram Bot"""
def main() -> None:
    print('Starting up bot...')
    app = (Application
           .builder()
           .token(TOKEN)
           .rate_limiter(AIORateLimiter(max_retries=2))
           .build())

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_chatgpt))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, photo))

    # Errors
    app.add_error_handler(error)

    # Define a poll interval
    print('Polling...')
    app.run_polling()


if __name__ == '__main__':
    main()