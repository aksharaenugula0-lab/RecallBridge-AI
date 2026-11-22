import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_chatgroq_model():
    """Initialize and return the Groq chat model"""
    try:
        groq_model = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="openai/gpt-oss-120b"
        )
        return groq_model

    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Groq model: {str(e)}"
        )