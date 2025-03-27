import os # for accessing environment variables
import chainlit as cl # web ui framework for chat application
import google.generativeai as genai # Google generative AI library
from dotenv import load_dotenv # for loading environment variables from .env file
from typing import Optional, Dict # Type hints for better code readability

# Load environment variables from .env file
load_dotenv()

# Get Gemini API from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")

# configure gemini with api key
genai.configure(api_key=gemini_api_key)

# intialize gemini model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash"
)

# Decorator to handle OAUTH callback from github
@cl.oauth_callback
def oauth_callback(
    provider_id: str, # id of the Auth provider (e.g. github)
    token: str, # OAuth access token
    raw_user_data: Dict[str, str], # User data from the Github
    default_user: cl.User, # default user object from chainlit
) -> Optional[cl.User]: # return user object or None
    """
    Handle the OAuth callback from GitHub
    Return the user object if authentication is successful, None otherwise
    """

    print(f"Provider: {provider_id}") # print the provider id
    print(f"User_data: {raw_user_data}") # print the user data

    return default_user # return the default user object

# handler for when a new chat session start
@cl.on_chat_start
async def handle_chat_start():

    cl.user_session.set("history", []) # initialize empty chat history

    await cl.Message(
        content="Hello! How can I help you today?"
    ).send() # send a greeting message

# handler for incoming messages
@cl.on_message
async def handle_message(message: cl.Message):

    history = cl.user_session.get("history") # get the chat history

    history.append(
        {"role": "user", "content": message.content} # append the message to the history
    ) # Add the message to the chat history

    # Format chat history for gemini model
    formatted_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model" # determine the role
        formatted_history.append(
            {"role": role, "parts": [{"text":msg["content"]}]}
        ) # format the message

    response = model.generate_content(formatted_history) # generate response

    response_text = (
        response.text if hasattr(response, "text") else ""
    ) # extract the response text

    history.append(
        {"role": "assistant", "content": response_text} # append the response to the history
    )

    cl.user_session.set("history", history) # update the chat history

    await cl.Message(content=response_text).send() # send the response to user


    